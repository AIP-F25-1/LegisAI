import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    import ollama
    from ollama import AsyncClient

    LLM_AVAILABLE = True
    USE_ASYNC_CLIENT = True
except ImportError:
    ollama = None
    AsyncClient = None
    LLM_AVAILABLE = False
    USE_ASYNC_CLIENT = False
    print("⚠️ Ollama not available. Install with: pip install ollama")

try:
    from sentence_transformers import SentenceTransformer

    EMBEDDINGS_AVAILABLE = True
except Exception as e:  # pragma: no cover - optional dependency
    SentenceTransformer = None
    EMBEDDINGS_AVAILABLE = False
    print(f"⚠️ Sentence transformers not available. Install with: pip install sentence-transformers ({e})")

try:
    from services.vector_store import VectorStore

    FAISS_AVAILABLE = True
except Exception as e:  # pragma: no cover - optional dependency
    VectorStore = None
    FAISS_AVAILABLE = False
    print(f"⚠️ FAISS not available. Install with: pip install faiss-cpu ({e})")

ollama_client = None
embeddings_model = None
ollama_model = "llama3.1:8b"
vector_store = None


async def load_llm_models() -> None:
    """Load LLM, embeddings, and vector store resources."""
    global ollama_client, embeddings_model, ollama_model, vector_store

    if not LLM_AVAILABLE or ollama is None:
        logger.warning("LLM libraries not available, using fallback responses")
        return

    try:
        logger.info("🤖 Loading Ollama models...")

        try:
            if USE_ASYNC_CLIENT and AsyncClient is not None:
                ollama_client = AsyncClient(host="http://127.0.0.1:11434")
                logger.info("✅ Ollama async client created")
            else:
                ollama_client = ollama.Client(host="http://127.0.0.1:11434")
                logger.info("✅ Ollama sync client created")

            try:
                if USE_ASYNC_CLIENT and AsyncClient is not None:
                    models = await asyncio.wait_for(ollama_client.list(), timeout=5.0)
                else:
                    import concurrent.futures

                    loop = asyncio.get_event_loop()
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = loop.run_in_executor(executor, ollama_client.list)
                        models = await asyncio.wait_for(future, timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Ollama list() call timed out")
                models = None
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Ollama list() call failed: %s", exc)
                models = None

            if models is None:
                logger.warning("Could not get models list, continuing anyway...")
                models = {"models": []}

            logger.info("✅ Ollama client connected successfully")
            logger.info("🔍 Raw models response: %s", models)

            def _extract_model_name(model_entry: Any) -> str:
                if hasattr(model_entry, "model"):
                    return getattr(model_entry, "model", "").strip()
                if isinstance(model_entry, dict):
                    return (model_entry.get("model") or model_entry.get("name") or "").strip()
                return str(model_entry).strip()

            model_names: List[str] = []

            if hasattr(models, "models") and getattr(models, "models"):
                logger.info("📋 Found 'models' attribute in response")
                for model in models.models:
                    name = _extract_model_name(model)
                    logger.info("🔍 Found model: '%s' (raw: %s)", name, model)
                    if name and name != "unknown":
                        model_names.append(name)
                        logger.info("✅ Added model: %s", name)
                    else:
                        logger.warning("⚠️ Skipped model: '%s' (empty or unknown)", name)

            elif isinstance(models, dict):
                logger.info("📋 Response is a dict, inspecting 'models' key")
                for model in models.get("models", []):
                    name = _extract_model_name(model)
                    logger.info("🔍 Found model: '%s' (raw: %s)", name, model)
                    if name and name != "unknown":
                        model_names.append(name)
                        logger.info("✅ Added model: %s", name)
                    else:
                        logger.warning("⚠️ Skipped model: '%s' (empty or unknown)", name)

            elif isinstance(models, list):
                logger.info("📋 Response is a list, checking directly")
                for model in models:
                    name = _extract_model_name(model)
                    logger.info("🔍 Found model: '%s' (raw: %s)", name, model)
                    if name and name != "unknown":
                        model_names.append(name)
                        logger.info("✅ Added model: %s", name)
                    else:
                        logger.warning("⚠️ Skipped model: '%s' (empty or unknown)", name)

            if not model_names:
                logger.warning("⚠️ No models found in parsing, but trying default model anyway")
                logger.info("🎯 Attempting to use default model: %s", ollama_model)
            else:
                logger.info("📋 Available models: %s", model_names)
                ollama_model = model_names[0]
                logger.info("🎯 Using model: %s", ollama_model)

        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("❌ Failed to connect to Ollama: %s", exc)
            logger.error("Make sure Ollama is installed and running: ollama serve")
            ollama_client = None
            return

        if EMBEDDINGS_AVAILABLE and SentenceTransformer is not None:
            logger.info("Loading embeddings model...")
            try:
                embeddings_model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("✅ Embeddings model loaded successfully")
            except Exception as exc:  # pragma: no cover - optional dependency
                logger.warning("⚠️ Embeddings model failed: %s", exc)
                embeddings_model = None
        else:
            logger.info("Embeddings model not available (sentence_transformers not installed)")
            embeddings_model = None

    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("❌ Failed to load LLM models: %s", exc)
        ollama_client = None
        embeddings_model = None

    if FAISS_AVAILABLE and VectorStore is not None:
        try:
            logger.info("🔍 Initializing Vector Store...")
            vector_store = VectorStore()
            logger.info("✅ Vector Store initialized successfully")
        except Exception as exc:  # pragma: no cover - optional dependency
            logger.warning("⚠️ Failed to initialize Vector Store: %s", exc)
            vector_store = None
    else:
        logger.warning("⚠️ Vector Store not available (FAISS not installed)")


async def generate_ai_response(prompt: str, max_tokens: int = 1000, use_full_response: bool = True) -> str:
    """Generate AI response using Ollama or enhanced fallback."""
    global ollama_model

    if ollama_client is None:
        logger.warning("Ollama client is None - using fallback")
        return generate_enhanced_fallback_response(prompt)

    try:
        logger.info("🤖 Generating AI response for prompt: %s...", prompt[:50])

        try:
            if USE_ASYNC_CLIENT and AsyncClient is not None:
                models = await ollama_client.list()
            else:
                models = ollama_client.list()

            available_models: List[str] = []

            def _extract_model_name(model_entry: Any) -> str:
                if hasattr(model_entry, "model"):
                    return getattr(model_entry, "model", "").strip()
                if isinstance(model_entry, dict):
                    return (model_entry.get("model") or model_entry.get("name") or "").strip()
                return str(model_entry).strip()

            if hasattr(models, "models") and getattr(models, "models"):
                for model in models.models:
                    name = _extract_model_name(model)
                    if name and name != "unknown":
                        available_models.append(name)
            elif isinstance(models, dict):
                for model in models.get("models", []):
                    name = _extract_model_name(model)
                    if name and name != "unknown":
                        available_models.append(name)
            elif isinstance(models, list):
                for model in models:
                    name = _extract_model_name(model)
                    if name and name != "unknown":
                        available_models.append(name)

            if not available_models:
                logger.error("❌ No valid models found. Install a model with: ollama pull llama3.1:8b")
                return generate_enhanced_fallback_response(prompt)

            if ollama_model not in available_models:
                logger.warning("⚠️ Model %s not found. Using first available: %s", ollama_model, available_models[0])
                ollama_model = available_models[0]
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("❌ Failed to check available models: %s", exc)
            return generate_enhanced_fallback_response(prompt)

        timeout_seconds = 600.0

        try:
            gen_options: Dict[str, Any] = {
                "temperature": 0.7,
                "top_p": 0.9,
                "stop": ["\n\n---", "\n\n##", "---"],
            }

            if not use_full_response:
                gen_options["num_predict"] = max_tokens

            if USE_ASYNC_CLIENT and AsyncClient is not None:
                response = await asyncio.wait_for(
                    ollama_client.generate(model=ollama_model, prompt=prompt, options=gen_options),
                    timeout=timeout_seconds,
                )
            else:
                import concurrent.futures

                loop = asyncio.get_event_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = loop.run_in_executor(
                        executor,
                        lambda: ollama_client.generate(model=ollama_model, prompt=prompt, options=gen_options),
                    )
                    response = await asyncio.wait_for(future, timeout=timeout_seconds)
        except asyncio.TimeoutError:
            logger.warning("Ollama generation timed out after %ss (using faster fallback)", timeout_seconds)
            return generate_enhanced_fallback_response(prompt)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Ollama generation failed: %s", exc)
            return generate_enhanced_fallback_response(prompt)

        if isinstance(response, dict):
            generated_text = response.get("response", "").strip()
        elif hasattr(response, "response"):
            generated_text = response.response.strip()
        else:
            generated_text = str(response).strip()

        if generated_text:
            logger.info("✅ AI response generated successfully: %s...", generated_text[:100])
            logger.info("✅ Full response length: %s characters", len(generated_text))
            return generated_text

        logger.warning("AI generated empty response - using fallback")
        return generate_enhanced_fallback_response(prompt)

    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("❌ AI generation failed: %s", exc)
        logger.error("❌ Ollama client: %s", ollama_client)
        return generate_enhanced_fallback_response(prompt)


async def generate_ai_response_stream(prompt: str):
    """Generate AI response with streaming for word-by-word display."""
    global ollama_model

    if ollama_client is None:
        yield "data: " + json.dumps({"content": "LLM not available", "done": True}) + "\n\n"
        return

    try:
        logger.info("🌊 Starting streaming AI response for: %s...", prompt[:50])

        async def get_stream():
            if USE_ASYNC_CLIENT and AsyncClient is not None:
                async for chunk in await ollama_client.generate(
                    model=ollama_model,
                    prompt=prompt,
                    stream=True,
                    options={
                        "temperature": 0.7,
                        "top_p": 0.9,
                    },
                ):
                    yield chunk
            else:
                for chunk in ollama_client.generate(
                    model=ollama_model,
                    prompt=prompt,
                    stream=True,
                    options={
                        "temperature": 0.7,
                        "top_p": 0.9,
                    },
                ):
                    yield chunk

        async for chunk in get_stream():
            try:
                if hasattr(chunk, "response"):
                    content = chunk.response
                elif isinstance(chunk, dict):
                    content = chunk.get("response", "")
                else:
                    content = str(chunk) if chunk else ""

                if content:
                    logger.info("📤 Streaming chunk: '%s...' (%s chars)", content[:20], len(content))
                    yield "data: " + json.dumps({"content": content, "done": False}) + "\n\n"

                if hasattr(chunk, "done") and getattr(chunk, "done"):
                    break
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.error("❌ Error processing chunk: %s", exc)
                continue

        logger.info("✅ Streaming complete")
        yield "data: " + json.dumps({"content": "", "done": True}) + "\n\n"

    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("❌ Streaming error: %s", exc)
        import traceback

        logger.error(traceback.format_exc())
        yield "data: " + json.dumps({"error": str(exc), "done": True}) + "\n\n"


def generate_enhanced_fallback_response(query: str) -> str:
    """Simple fallback response used when LLM is unavailable."""
    return f"""🚨 FALLBACK RESPONSE - LLM NOT WORKING 🚨

Query: {query[:100]}

This is a fallback response because the LLM models failed to load.
If you see this message, the AI integration is not working properly.

Expected: Real AI-generated legal analysis
Actual: This fallback response

Please check:
1. LLM models are loaded
2. ollama_client is not None
3. AI response generation is working

Status: LLM Integration Failed"""


__all__ = [
    "FAISS_AVAILABLE",
    "LLM_AVAILABLE",
    "AsyncClient",
    "EMBEDDINGS_AVAILABLE",
    "SentenceTransformer",
    "VectorStore",
    "embeddings_model",
    "generate_ai_response",
    "generate_ai_response_stream",
    "generate_enhanced_fallback_response",
    "load_llm_models",
    "ollama_client",
    "ollama_model",
    "vector_store",
]


