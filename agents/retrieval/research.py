import asyncio
import json
import logging
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import numpy as np
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

try:
    from rank_bm25 import BM25Okapi

    BM25_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    BM25Okapi = None  # type: ignore[assignment]
    BM25_AVAILABLE = False

from . import common as common_utils
from .common import (
    EMBEDDINGS_AVAILABLE,
    SentenceTransformer,
    generate_ai_response,
    generate_ai_response_stream,
    ollama_client,
)

router = APIRouter()
logger = logging.getLogger(__name__)

BASE_PATH = Path(__file__).resolve().parents[1]
CASELAW_PATHS = [
    BASE_PATH / "data" / "caselaw_sample.json",
]

DEFAULT_CASES: List[Dict[str, Any]] = [
    {
        "id": "fallback_case_001",
        "title": "Model Contract Performance Guidance",
        "citation": "Model Contract Guidance (Fallback)",
        "jurisdiction": "Model Jurisdiction",
        "year": 2021,
        "summary": "Illustrative precedent emphasizing measurable performance metrics for technology contracts.",
        "facts": "A public agency disputed performance metrics in a technology rollout lacking objective acceptance criteria.",
        "holding": "The tribunal required objective measurements and documentation to enforce milestone obligations.",
        "analysis": "Clear milestone definitions, shared dashboards, and acceptance testing mitigate ambiguity.",
        "issues": [
            "Ambiguous performance clauses",
            "Objective milestone documentation",
        ],
        "statutes": ["Model Procurement Code 4.1"],
        "tags": ["contract", "technology", "performance"],
        "precedent_direction": "supports_claim",
        "outcome": "Supports agencies enforcing measurable contractual obligations.",
        "related_cases": [],
    },
    {
        "id": "fallback_case_002",
        "title": "Illustrative Data Privacy Enforcement",
        "citation": "Illustrative Privacy Enforcement (Fallback)",
        "jurisdiction": "Model Regulatory Authority",
        "year": 2020,
        "summary": "Illustrative enforcement highlights need for consent specificity and audit tracing in automated processing.",
        "facts": "A multinational processed personal data for automated scoring without tracking consent scope.",
        "holding": "Regulators fined the controller for inadequate consent records and DPIA documentation.",
        "analysis": "Shared governance with vendors, auditable pipelines, and responsive DPIAs are essential.",
        "issues": ["Consent management", "AI governance"],
        "statutes": ["Model Privacy Act 12.3"],
        "tags": ["privacy", "compliance", "automation"],
        "precedent_direction": "cautionary",
        "outcome": "Warns enterprises about shared responsibility for automated data processing.",
        "related_cases": [],
    },
]


@dataclass
class CaseDocument:
    """Normalized representation of a legal authority used for retrieval."""

    doc_id: str
    title: str
    citation: str
    jurisdiction: str
    year: Optional[int]
    summary: str
    text: str
    issues: List[str] = field(default_factory=list)
    statutes: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    precedent_direction: str = "neutral"
    outcome: str = ""
    related_cases: List[str] = field(default_factory=list)

    def context_snippet(self, max_chars: int = 700) -> str:
        content = self.summary or self.text
        if len(content) <= max_chars:
            return content
        return content[: max_chars - 3] + "..."


class LegalResearchEngine:
    """Hybrid retrieval, knowledge graph building, and precedent reasoning."""

    def __init__(self, documents: List[CaseDocument]):
        self.documents = documents
        self.doc_index: Dict[str, CaseDocument] = {
            doc.doc_id: doc for doc in documents if doc.doc_id
        }
        self.ordered_ids: List[str] = [doc.doc_id for doc in documents if doc.doc_id]

        self.embeddings_model: Optional[SentenceTransformer] = None
        self.embeddings: Optional[np.ndarray] = None
        self.bm25: Optional[BM25Okapi] = None

        self.tag_index: Dict[str, Set[str]] = defaultdict(set)
        self.statute_index: Dict[str, Set[str]] = defaultdict(set)
        self.relationships: Dict[str, Set[str]] = defaultdict(set)

        self._ensure_embeddings_model()
        self._build_indices()
        self._build_knowledge_graph()

    def _ensure_embeddings_model(self) -> None:
        if not EMBEDDINGS_AVAILABLE or SentenceTransformer is None:
            logger.warning("SentenceTransformer embeddings are unavailable.")
            return

        if common_utils.embeddings_model is not None:
            self.embeddings_model = common_utils.embeddings_model
            return

        try:
            self.embeddings_model = SentenceTransformer("all-MiniLM-L6-v2")
            common_utils.embeddings_model = self.embeddings_model
            logger.info("Loaded SentenceTransformer embeddings for research engine.")
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning("Failed to initialize embeddings model: %s", exc)
            self.embeddings_model = None

    def _build_indices(self) -> None:
        if not self.ordered_ids:
            return

        self.text_corpus: List[str] = [
            (self.doc_index[doc_id].text or self.doc_index[doc_id].summary or "")
            for doc_id in self.ordered_ids
        ]

        if BM25_AVAILABLE and self.text_corpus:
            tokenized_corpus = [self._tokenize(text) for text in self.text_corpus]
            if tokenized_corpus:
                self.bm25 = BM25Okapi(tokenized_corpus)
                logger.info("BM25 index initialised with %s documents.", len(self.text_corpus))
        else:
            logger.warning("BM25 is unavailable; lexical search will be skipped.")

        if self.embeddings_model is not None and self.text_corpus:
            try:
                self.embeddings = self.embeddings_model.encode(
                    self.text_corpus,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                )
                logger.info("Dense embeddings computed for %s documents.", len(self.text_corpus))
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Embedding generation failed: %s", exc)
                self.embeddings = None

    def _build_knowledge_graph(self) -> None:
        for document in self.documents:
            doc_id = document.doc_id
            if not doc_id:
                continue

            for tag in document.tags:
                self.tag_index[tag.lower()].add(doc_id)

            for statute in document.statutes:
                self.statute_index[statute.lower()].add(doc_id)

            for related in document.related_cases:
                if related and related in self.doc_index:
                    self.relationships[doc_id].add(related)
                    self.relationships[related].add(doc_id)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [token.lower() for token in text.split()]

    def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not query.strip():
            return []

        lexical_scores = self._compute_bm25_scores(query)
        dense_scores = self._compute_dense_scores(query)
        blended = self._blend_scores(lexical_scores, dense_scores)

        results: List[Dict[str, Any]] = []
        for doc_id, score in blended[:top_k]:
            case = self.doc_index[doc_id]
            results.append(
                {
                    "case": case,
                    "score": score,
                    "lexical_score": lexical_scores.get(doc_id, 0.0),
                    "dense_score": dense_scores.get(doc_id, 0.0),
                    "snippet": case.context_snippet(),
                    "matching_terms": self._extract_matching_terms(query, case),
                }
            )

        return results

    def _compute_bm25_scores(self, query: str) -> Dict[str, float]:
        if self.bm25 is None:
            return {}

        tokens = self._tokenize(query)
        if not tokens:
            return {}

        raw_scores = self.bm25.get_scores(tokens)
        max_score = float(np.max(raw_scores)) if raw_scores.size else 0.0

        scores: Dict[str, float] = {}
        for doc_id, raw in zip(self.ordered_ids, raw_scores):
            scores[doc_id] = float(raw / max_score) if max_score else 0.0

        return scores

    def _compute_dense_scores(self, query: str) -> Dict[str, float]:
        if self.embeddings_model is None or self.embeddings is None:
            return {}

        normalized_query = query.strip()
        if not normalized_query:
            return {}

        try:
            query_vector = self.embeddings_model.encode(
                [normalized_query],
                normalize_embeddings=True,
                show_progress_bar=False,
            )[0]
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning("Failed to encode query for dense search: %s", exc)
            return {}

        dense_scores = np.dot(self.embeddings, query_vector)
        max_score = float(np.max(dense_scores)) if dense_scores.size else 0.0

        scores: Dict[str, float] = {}
        for doc_id, raw in zip(self.ordered_ids, dense_scores):
            scores[doc_id] = float(raw / max_score) if max_score else 0.0

        return scores

    @staticmethod
    def _blend_scores(
        lexical_scores: Dict[str, float],
        dense_scores: Dict[str, float],
    ) -> List[tuple]:
        combined: Dict[str, float] = {}

        use_dense = bool(dense_scores)
        use_lexical = bool(lexical_scores)

        for doc_id in set(list(lexical_scores.keys()) + list(dense_scores.keys())):
            dense = dense_scores.get(doc_id, 0.0)
            lexical = lexical_scores.get(doc_id, 0.0)

            if use_dense and use_lexical:
                combined[doc_id] = 0.55 * dense + 0.45 * lexical
            elif use_dense:
                combined[doc_id] = dense
            else:
                combined[doc_id] = lexical

        return sorted(combined.items(), key=lambda item: item[1], reverse=True)

    def _extract_matching_terms(self, query: str, case: CaseDocument) -> Set[str]:
        query_terms = set(self._tokenize(query))
        doc_terms = set(self._tokenize(f"{case.summary} {case.text}"))

        return {term for term in query_terms if term in doc_terms and len(term) > 2}

    def build_knowledge_graph_payload(
        self,
        focus_doc_ids: List[str],
        max_related: int = 12,
    ) -> Dict[str, Any]:
        nodes: List[Dict[str, Any]] = []
        edges: Set[tuple] = set()
        added: Set[str] = set()

        for doc_id in focus_doc_ids:
            case = self.doc_index.get(doc_id)
            if not case:
                continue

            nodes.append(
                {
                    "id": case.doc_id,
                    "label": case.title,
                    "citation": case.citation,
                    "jurisdiction": case.jurisdiction,
                    "year": case.year,
                    "tags": case.tags,
                    "statutes": case.statutes,
                    "precedent_direction": case.precedent_direction,
                }
            )
            added.add(case.doc_id)

        for doc_id in list(added):
            case = self.doc_index.get(doc_id)
            if not case:
                continue

            related_candidates: Set[str] = set(case.related_cases)

            for tag in case.tags:
                related_candidates.update(self.tag_index.get(tag.lower(), set()))

            for statute in case.statutes:
                related_candidates.update(self.statute_index.get(statute.lower(), set()))

            for target in list(related_candidates):
                if target == doc_id or target not in self.doc_index:
                    continue

                if target not in added and len(nodes) < max_related:
                    related_case = self.doc_index[target]
                    nodes.append(
                        {
                            "id": related_case.doc_id,
                            "label": related_case.title,
                            "citation": related_case.citation,
                            "jurisdiction": related_case.jurisdiction,
                            "year": related_case.year,
                            "tags": related_case.tags,
                            "statutes": related_case.statutes,
                            "precedent_direction": related_case.precedent_direction,
                        }
                    )
                    added.add(related_case.doc_id)

                edge_key = tuple(sorted((doc_id, target)))
                edges.add(edge_key)

        edge_payload = [{"source": source, "target": target, "type": "related"} for source, target in edges]
        insights = self._summarize_graph(focus_doc_ids, nodes, edge_payload)

        return {"nodes": nodes, "edges": edge_payload, "insights": insights}

    @staticmethod
    def _summarize_graph(
        focus_ids: List[str],
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
    ) -> List[str]:
        tag_counter: Counter = Counter()
        statute_counter: Counter = Counter()
        direction_counter: Counter = Counter()

        lookup = {node["id"]: node for node in nodes}

        for doc_id in focus_ids:
            node = lookup.get(doc_id)
            if not node:
                continue

            tag_counter.update(tag.lower() for tag in node.get("tags", []))
            statute_counter.update(statute.lower() for statute in node.get("statutes", []))
            direction_counter.update([node.get("precedent_direction", "neutral")])

        insights: List[str] = []

        if tag_counter:
            top_tags = ", ".join(tag for tag, _ in tag_counter.most_common(3))
            insights.append(f"Dominant themes: {top_tags}.")

        if statute_counter:
            top_statutes = ", ".join(statute for statute, _ in statute_counter.most_common(3))
            insights.append(f"Frequently cited statutes or regulations: {top_statutes}.")

        if direction_counter:
            direction_summary = ", ".join(
                f"{direction}:{count}" for direction, count in direction_counter.most_common()
            )
            insights.append(f"Precedent signals - {direction_summary}.")

        if not insights:
            insights.append("No significant graph patterns detected.")

        return insights

    def build_precedent_reasoning(
        self,
        query: str,
        retrieval: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        buckets: Dict[str, List[Dict[str, Any]]] = {
            "supports_claim": [],
            "contrasts_claim": [],
            "cautionary": [],
            "neutral": [],
        }

        direction_labels = {
            "supports_claim": "Supporting authorities or aligned precedent",
            "contrasts_claim": "Contrary or limiting precedent",
            "cautionary": "Cautionary or compliance warnings",
            "neutral": "Background and contextual authorities",
        }

        for item in retrieval:
            case = item["case"]
            direction = case.precedent_direction.lower()
            if direction not in buckets:
                direction = "neutral"

            buckets[direction].append(
                {
                    "case_id": case.doc_id,
                    "title": case.title,
                    "citation": case.citation,
                    "summary": case.summary,
                    "outcome": case.outcome,
                }
            )

        summary_lines: List[str] = []
        for key in ("supports_claim", "contrasts_claim", "cautionary"):
            if buckets[key]:
                summary_lines.append(f"{direction_labels[key]}: {len(buckets[key])} case(s).")

        if not summary_lines:
            summary_lines.append("No decisive precedent signals identified; treat retrieval as contextual guidance.")

        return {
            "summary": " ".join(summary_lines),
            "buckets": buckets,
            "query": query,
        }

    @staticmethod
    def render_context_block(
        query: str,
        retrieval: List[Dict[str, Any]],
        knowledge_graph: Dict[str, Any],
        precedent: Dict[str, Any],
    ) -> str:
        if not retrieval:
            return f"Query Focus: {query}\n\nNo authorities retrieved by the hybrid engine."

        lines: List[str] = [f"Query Focus: {query}", "", "Retrieved Authorities:"]

        for index, item in enumerate(retrieval, start=1):
            case = item["case"]
            lines.append(
                f"{index}. {case.title} ({case.citation}) — Score {item['score']:.2f}, Direction: {case.precedent_direction}"
            )
            lines.append(f"   Jurisdiction: {case.jurisdiction} | Year: {case.year}")

            if case.tags:
                lines.append("   Tags: " + ", ".join(case.tags))
            if case.statutes:
                lines.append("   Statutes: " + ", ".join(case.statutes))
            if item["matching_terms"]:
                lines.append("   Matched Terms: " + ", ".join(sorted(item["matching_terms"])))

            lines.append("   Key Insight: " + case.summary)

        lines.append("")
        lines.append("Knowledge Graph Highlights:")
        for insight in knowledge_graph.get("insights", []):
            lines.append(f"- {insight}")

        lines.append("")
        lines.append("Precedent Reasoning Summary:")
        lines.append(precedent.get("summary", ""))

        return "\n".join(lines)

    @staticmethod
    def build_prompt(query: str, context_block: str) -> str:
        return (
            "You are a legal research strategist. Analyse the query below using the retrieved authorities, hybrid search "
            "signals, and knowledge graph insights.\n\n"
            f'Query: "{query}"\n\n'
            "Context from retrieval engine:\n"
            f"{context_block}\n\n"
            "Deliverable requirements:\n"
            "1. EXECUTIVE SUMMARY – concise synopsis tied to the retrieved authorities.\n"
            "2. KEY LEGAL PRINCIPLES – cite statutes, regulations, or doctrinal rules surfaced.\n"
            "3. RELEVANT LEGAL CONSIDERATIONS – highlight jurisdictional differences and procedural posture.\n"
            "4. RISK ASSESSMENT – categorise risk levels with rationale grounded in precedent.\n"
            "5. COMPLIANCE REQUIREMENTS – link concrete obligations to governing instruments.\n"
            "6. PRACTICAL RECOMMENDATIONS – actionable steps referencing the retrieved authorities.\n"
            "7. CASE LAW REFERENCES – cite the most relevant cases with short parentheticals.\n"
            "8. NEXT STEPS – strategic follow-up actions.\n\n"
            "Incorporate precedent signalling (supporting, contrasting, cautionary) and note data gaps. "
            "Write in a professional tone suitable for in-house counsel."
        )

    def prepare_context(self, query: str, top_k: int = 6) -> Dict[str, Any]:
        retrieval = self.hybrid_search(query, top_k=top_k)
        focus_ids = [item["case"].doc_id for item in retrieval]

        knowledge_graph = self.build_knowledge_graph_payload(focus_ids)
        precedent = self.build_precedent_reasoning(query, retrieval)

        context_block = self.render_context_block(query, retrieval, knowledge_graph, precedent)
        prompt = self.build_prompt(query, context_block)

        return {
            "query": query,
            "retrieval": retrieval,
            "knowledge_graph": knowledge_graph,
            "precedent": precedent,
            "context_block": context_block,
            "prompt": prompt,
        }


async def _load_case_documents() -> List[CaseDocument]:
    def _load_raw_cases() -> List[Dict[str, Any]]:
        for path in CASELAW_PATHS:
            if path.exists():
                try:
                    with path.open("r", encoding="utf-8") as file:
                        data = json.load(file)
                        if isinstance(data, list):
                            return data
                except Exception as exc:  # pragma: no cover - defensive logging
                    logger.warning("Failed to load case law file %s: %s", path, exc)
        return DEFAULT_CASES

    def _normalize(entry: Dict[str, Any]) -> CaseDocument:
        raw_id = (
            entry.get("id")
            or entry.get("doc_id")
            or entry.get("case_id")
            or entry.get("title")
            or entry.get("citation")
            or f"case_{abs(hash(entry.get('summary', 'fallback')))}"
        )
        direction = (entry.get("precedent_direction") or entry.get("outcome_category") or "neutral").lower()
        allowed_directions = {"supports_claim", "contrasts_claim", "cautionary", "neutral"}
        if direction not in allowed_directions:
            direction = "neutral"

        text_parts = [
            entry.get("facts", ""),
            entry.get("analysis", ""),
            entry.get("holding", ""),
            entry.get("summary", ""),
        ]
        combined_text = "\n".join(part.strip() for part in text_parts if part and part.strip())

        return CaseDocument(
            doc_id=str(raw_id),
            title=entry.get("title") or entry.get("name") or "Untitled Authority",
            citation=entry.get("citation")
            or (entry.get("citations", [None])[0] if entry.get("citations") else "")
            or "Unknown citation",
            jurisdiction=entry.get("jurisdiction") or entry.get("court") or "Unknown jurisdiction",
            year=entry.get("year"),
            summary=entry.get("summary", ""),
            text=combined_text or entry.get("summary", ""),
            issues=list(entry.get("issues", [])),
            statutes=list(entry.get("statutes", [])),
            tags=list(entry.get("tags", [])),
            precedent_direction=direction,
            outcome=entry.get("outcome", ""),
            related_cases=list(entry.get("related_cases", [])),
        )

    raw_cases = await asyncio.to_thread(_load_raw_cases)
    documents = [_normalize(entry) for entry in raw_cases]

    logger.info("Loaded %s case law documents for research engine.", len(documents))
    return documents


_research_engine: Optional[LegalResearchEngine] = None
_engine_lock = asyncio.Lock()


async def get_research_engine() -> Optional[LegalResearchEngine]:
    global _research_engine

    if _research_engine is None:
        async with _engine_lock:
            if _research_engine is None:
                documents = await _load_case_documents()
                if not documents:
                    logger.warning("No legal documents available for research engine.")
                    return None
                _research_engine = await asyncio.to_thread(LegalResearchEngine, documents)

    return _research_engine


async def prepare_research_context(query: str, top_k: int = 6) -> Dict[str, Any]:
    engine = await get_research_engine()
    if engine is None:
        fallback_prompt = _basic_prompt(query)
        return {
            "query": query,
            "retrieval": [],
            "knowledge_graph": {"nodes": [], "edges": [], "insights": ["Retrieval engine unavailable."]},
            "precedent": {
                "summary": "Retrieval engine unavailable; provide general legal guidance.",
                "buckets": {},
                "query": query,
            },
            "context_block": "Retrieval engine unavailable.",
            "prompt": fallback_prompt,
        }

    return await asyncio.to_thread(engine.prepare_context, query, top_k)


async def generate_structured_legal_research(query: str) -> Dict[str, Any]:
    """Generate structured legal research using hybrid RAG, knowledge graph, and precedent reasoning."""
    context_bundle = await prepare_research_context(query, top_k=8)
    prompt = context_bundle.get("prompt") or _basic_prompt(query)

    try:
        ai_research = await asyncio.wait_for(
            generate_ai_response(prompt, max_tokens=900, use_full_response=True),
            timeout=600.0,
        )

        if ai_research and "FALLBACK RESPONSE" not in ai_research and "LLM NOT WORKING" not in ai_research:
            report_text = _format_report(query, ai_research, context_bundle)
            return {
                "report": report_text,
                "prompt": prompt,
                "context": context_bundle,
                "source": "llm",
            }
    except asyncio.TimeoutError:
        logger.warning("AI generation timed out for query: %s", query)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("AI generation failed: %s", exc)

    fallback_report = _build_fallback_report(query, context_bundle)
    return {"report": fallback_report, "prompt": prompt, "context": context_bundle, "source": "fallback"}


def _format_report(query: str, body: str, context_bundle: Dict[str, Any]) -> str:
    header = (
        "LEGAL RESEARCH ANALYSIS\n"
        f"Query: {query}\n"
        f"Date: {time.strftime('%B %d, %Y')}\n\n"
    )
    appendix = _render_appendix(context_bundle)
    footer = "\n---\nThis research analysis is provided for informational purposes only and does not constitute legal advice."

    return header + body.strip() + appendix + footer


def _render_appendix(context_bundle: Dict[str, Any]) -> str:
    retrieval = context_bundle.get("retrieval", [])
    knowledge_graph = context_bundle.get("knowledge_graph", {})
    precedent = context_bundle.get("precedent", {})

    lines: List[str] = [
        "\nAPPENDIX A – Retrieved Authorities",
    ]

    if not retrieval:
        lines.append("No documents retrieved by the hybrid research engine.")
    else:
        for item in retrieval:
            case = item["case"]
            lines.append(f"- {case.title} ({case.citation}) | Score {item['score']:.2f}")
            if case.summary:
                lines.append(f"  Summary: {case.summary}")

    lines.append("\nAPPENDIX B – Knowledge Graph Insights")
    for insight in knowledge_graph.get("insights", []):
        lines.append(f"- {insight}")

    lines.append("\nAPPENDIX C – Precedent Signals")
    lines.append(precedent.get("summary", ""))

    return "\n".join(lines) + "\n"


def _build_fallback_report(query: str, context_bundle: Dict[str, Any]) -> str:
    body = _template_body_for_query(query)
    return _format_report(query, body, context_bundle)


def _template_body_for_query(query: str) -> str:
    lowered = query.lower()

    if "liability" in lowered and "service" in lowered:
        return (
            "EXECUTIVE SUMMARY:\n"
            "This analysis examines liability limitations in service agreements, focusing on legal frameworks, risk allocation, and compliance requirements.\n\n"
            "KEY LEGAL PRINCIPLES:\n"
            "- Limitation of liability clauses vary by jurisdiction and must preserve gross negligence exceptions.\n"
            "- Standard of care and implied warranties inform enforceability.\n"
            "- Indemnification provisions must allocate third-party claims clearly.\n"
            "- Force majeure and disclosure duties influence liability scope.\n"
            "- Consequential damage waivers require conspicuous drafting.\n\n"
            "RELEVANT LEGAL CONSIDERATIONS:\n"
            "- Jurisdictional public-policy constraints on liability caps.\n"
            "- Industry-specific disclosure requirements and insurance mandates.\n"
            "- Contract formation essentials and bargaining power documentation.\n"
            "- Regulatory expectations for critical infrastructure and data custodians.\n"
            "- Interplay between liability caps and statutory consumer protections.\n\n"
            "RISK ASSESSMENT:\n"
            "- High: Unlimited exposure where caps are absent or void for public policy.\n"
            "- Medium: Caps lacking carve-outs or backed by inadequate insurance.\n"
            "- Low: Balanced provisions with clear exceptions, insurance, and disclosures.\n\n"
            "COMPLIANCE REQUIREMENTS:\n"
            "- Align limitation clauses with industry and regulatory guidance.\n"
            "- Maintain documented risk disclosures and redundancy plans.\n"
            "- Preserve gross negligence carve-outs and statutory warranties where mandated.\n"
            "- Review insurance certificates and coverage alignment.\n\n"
            "PRACTICAL RECOMMENDATIONS:\n"
            "1. Draft measurable performance obligations and acceptance criteria.\n"
            "2. Pair liability caps with mitigation strategies and insurance documentation.\n"
            "3. Conduct counterparty due diligence on operational risk disclosures.\n"
            "4. Refresh contractual language following regulatory updates.\n"
            "5. Escalate high-risk services for legal review before execution.\n\n"
            "CASE LAW REFERENCES:\n"
            "- Include authorities that uphold balanced liability caps with carve-outs.\n"
            "- Cite decisions voiding caps for nondisclosure or unequal bargaining.\n\n"
            "NEXT STEPS:\n"
            "1. Inventory existing service agreements for liability provisions.\n"
            "2. Benchmark clause language against current regulatory and industry guidance.\n"
            "3. Engage subject-matter counsel for high-risk or critical infrastructure services.\n"
            "4. Update playbooks to embed disclosure and insurance checkpoints."
        )

    if any(term in lowered for term in ("marriage", "marital", "divorce", "family")):
        return (
            "EXECUTIVE SUMMARY:\n"
            "This analysis examines family law procedures covering marriage validity, divorce, custody, and support obligations.\n\n"
            "KEY LEGAL PRINCIPLES:\n"
            "- Capacity, consent, and formalities govern marriage validity.\n"
            "- No-fault and fault-based divorce standards vary by state.\n"
            "- Property division follows community-property or equitable-distribution regimes.\n"
            "- Spousal maintenance depends on statutory factors and case law.\n"
            "- Custody determinations apply a best-interests standard with statutory factors.\n"
            "- Child support uses guideline formulas subject to deviation criteria.\n\n"
            "RELEVANT LEGAL CONSIDERATIONS:\n"
            "- Jurisdiction-specific residency, filing, and waiting-period requirements.\n"
            "- Disclosure obligations for marital assets and debts.\n"
            "- Enforcement of prenuptial and postnuptial agreements.\n"
            "- Mediation, parenting plans, and parenting coordination requirements.\n"
            "- Interplay between state family courts and protective-order proceedings.\n\n"
            "RISK ASSESSMENT:\n"
            "- High: Contested divorces with complex assets or cross-border elements.\n"
            "- Medium: Cases with disputed custody or support modifications.\n"
            "- Low: Uncontested matters with thorough disclosures and agreements.\n\n"
            "COMPLIANCE REQUIREMENTS:\n"
            "- File requisite petitions and affidavits under local rules.\n"
            "- Observe mandatory disclosures and financial statement formats.\n"
            "- Follow court-ordered mediation where required.\n"
            "- Secure final decrees and register interstate orders when needed.\n\n"
            "PRACTICAL RECOMMENDATIONS:\n"
            "1. Confirm jurisdictional prerequisites before filing.\n"
            "2. Compile comprehensive financial records early.\n"
            "3. Evaluate alternative dispute resolution options.\n"
            "4. Tailor parenting plans to statutory custody factors.\n"
            "5. Engage specialist counsel for complex asset division or relocation issues.\n\n"
            "CASE LAW REFERENCES:\n"
            "- Highlight leading cases on custody, support, and property distribution.\n"
            "- Include authorities on enforceability of marital agreements.\n\n"
            "NEXT STEPS:\n"
            "1. Map procedural timelines and statutory waiting periods.\n"
            "2. Coordinate with financial advisors for asset valuations.\n"
            "3. Draft proposed orders aligned with local rules.\n"
            "4. Plan post-judgment compliance and enforcement strategies."
        )

    if any(term in lowered for term in ("employment", "termination", "workplace")):
        return (
            "EXECUTIVE SUMMARY:\n"
            "This analysis reviews employment termination law, focusing on discrimination risks, due process, and automated decisioning safeguards.\n\n"
            "KEY LEGAL PRINCIPLES:\n"
            "- Employment-at-will may be narrowed by contracts, handbooks, or statutes.\n"
            "- Anti-discrimination laws prohibit terminations based on protected characteristics.\n"
            "- Retaliation protections cover whistleblowers and leave takers.\n"
            "- Automated employment decisions must comply with validation and bias-audit duties.\n"
            "- Notice statutes (WARN, mini-WARN) may apply to group terminations.\n\n"
            "RELEVANT LEGAL CONSIDERATIONS:\n"
            "- Federal frameworks: Title VII, ADA, ADEA, FMLA, NLRA, and wage laws.\n"
            "- State-law wrongful termination torts and privacy rights.\n"
            "- Collective bargaining agreements mandating progressive discipline.\n"
            "- Documentation standards for performance management and appeals.\n"
            "- Cross-border data privacy and employee-monitoring restrictions.\n\n"
            "RISK ASSESSMENT:\n"
            "- High: Terminations lacking documentation or involving protected classes.\n"
            "- Medium: Reductions in force without disparate-impact analysis.\n"
            "- Low: Well-documented terminations with legal review and appeal rights.\n\n"
            "COMPLIANCE REQUIREMENTS:\n"
            "- Maintain compliant personnel files and performance reviews.\n"
            "- Provide final pay and benefit notices within statutory timelines.\n"
            "- Issue COBRA or state continuation notices.\n"
            "- Validate AI or scoring tools and retain audit trails.\n"
            "- Coordinate with unemployment response protocols.\n\n"
            "PRACTICAL RECOMMENDATIONS:\n"
            "1. Standardise termination checklists with legal sign-off.\n"
            "2. Conduct disparate-impact analysis for group events.\n"
            "3. Offer appeal or review of automated scoring outcomes.\n"
            "4. Train supervisors on documentation and protected-activity handling.\n"
            "5. Preserve custodian communications for potential litigation holds.\n\n"
            "CASE LAW REFERENCES:\n"
            "- Reference leading burden-shifting and wrongful termination cases.\n"
            "- Include recent AI bias or automated decisioning enforcement actions.\n\n"
            "NEXT STEPS:\n"
            "1. Audit termination policies against current statutory changes.\n"
            "2. Update technology governance policies for HR analytics.\n"
            "3. Schedule training on documentation and accommodation processes.\n"
            "4. Engage employment counsel for high-risk separations."
        )

    return (
        "EXECUTIVE SUMMARY:\n"
        f"This analysis provides a structured review of the legal issues arising from \"{query}\", integrating statutory, regulatory, and precedent-based insights.\n\n"
        "KEY LEGAL PRINCIPLES:\n"
        "- Identify governing statutes, regulations, and doctrinal tests relevant to the query.\n"
        "- Distinguish between mandatory and persuasive authorities across jurisdictions.\n"
        "- Highlight industry-specific standards or guidance where applicable.\n\n"
        "RELEVANT LEGAL CONSIDERATIONS:\n"
        "- Jurisdictional scope and conflict-of-laws factors.\n"
        "- Procedural posture, evidentiary burdens, and limitation periods.\n"
        "- Stakeholder obligations, including counterparties, regulators, and consumers.\n\n"
        "RISK ASSESSMENT:\n"
        "- Categorise regulatory, civil liability, and operational risks.\n"
        "- Note aggravating or mitigating factors derived from precedent.\n"
        "- Identify data gaps impacting confidence in the assessment.\n\n"
        "COMPLIANCE REQUIREMENTS:\n"
        "- Map statutory and regulatory obligations to responsible functions.\n"
        "- Outline required documentation, reporting, and audit steps.\n"
        "- Address monitoring requirements and escalation triggers.\n\n"
        "PRACTICAL RECOMMENDATIONS:\n"
        "1. Conduct targeted fact gathering to close identified gaps.\n"
        "2. Align internal controls with the applicable regulatory framework.\n"
        "3. Engage subject-matter experts for complex or high-risk elements.\n"
        "4. Prepare stakeholder communications and approval pathways.\n"
        "5. Establish ongoing monitoring and review cadence.\n\n"
        "CASE LAW REFERENCES:\n"
        "- Summarise the most relevant authorities with short parentheticals.\n"
        "- Distinguish between supportive and contrasting precedent.\n\n"
        "NEXT STEPS:\n"
        "1. Validate assumptions with the business sponsor or client.\n"
        "2. Prioritise remediation tasks by risk severity and timelines.\n"
        "3. Schedule follow-up review once additional facts are gathered."
    )


def _basic_prompt(query: str) -> str:
    return (
        "As a legal research assistant, provide a comprehensive analysis of the following legal query:\n\n"
        f'Query: "{query}"\n\n'
        "Please provide:\n"
        "1. EXECUTIVE SUMMARY - Brief overview of the topic\n"
        "2. KEY LEGAL PRINCIPLES - Important legal concepts and rules\n"
        "3. RELEVANT LEGAL CONSIDERATIONS - Jurisdiction-specific requirements and variations\n"
        "4. RISK ASSESSMENT - Potential legal risks and their severity\n"
        "5. COMPLIANCE REQUIREMENTS - Regulatory and statutory obligations\n"
        "6. PRACTICAL RECOMMENDATIONS - Actionable steps\n"
        "7. CASE LAW REFERENCES - Relevant precedents (if applicable)\n"
        "8. NEXT STEPS - Recommended actions\n\n"
        "Format the response in a clear, professional manner with proper sections. "
        "Be specific to the query and provide jurisdiction-specific details where mentioned."
    )


def _serialize_case_item(item: Dict[str, Any]) -> Dict[str, Any]:
    case = item["case"]

    return {
        "id": case.doc_id,
        "score": float(round(item["score"], 4)),
        "lexical_score": float(round(item["lexical_score"], 4)),
        "dense_score": float(round(item["dense_score"], 4)),
        "content": item["snippet"],
        "title": case.title,
        "tags": case.tags,
        "jurisdiction": case.jurisdiction,
        "year": case.year,
        "citation": case.citation,
        "statutes": case.statutes,
        "precedent_direction": case.precedent_direction,
        "outcome": case.outcome,
    }


def _estimate_confidence(retrieval: List[Dict[str, Any]]) -> float:
    if not retrieval:
        return 0.35

    top_score = max(item["score"] for item in retrieval)
    coverage_bonus = min(len(retrieval) / 10.0, 0.2)

    return float(min(0.6 + top_score * 0.3 + coverage_bonus, 0.95))


@router.post("/api/research/stream")
async def research_legal_query_stream(request: Dict[str, Any]):
    """Stream research results word-by-word with hybrid retrieval context."""
    query = request.get("query", "")

    context_bundle = await prepare_research_context(query, top_k=6)
    prompt = context_bundle.get("prompt") or _basic_prompt(query)

    return StreamingResponse(
        generate_ai_response_stream(prompt),
        media_type="text/event-stream",
    )


@router.post("/api/research")
async def research_legal_query(request: Dict[str, Any]) -> Dict[str, Any]:
    """Perform legal research using hybrid retrieval, knowledge graph, and AI summarization."""
    try:
        query = request.get("query", "")
        max_results = max(1, int(request.get("max_results", 10)))

        research_bundle = await asyncio.wait_for(
            generate_structured_legal_research(query),
            timeout=600.0,
        )

        context = research_bundle.get("context", {})
        retrieval = context.get("retrieval", [])

        documents = [_serialize_case_item(item) for item in retrieval[:max_results]]

        response_payload: Dict[str, Any] = {
            "query": query,
            "documents": documents,
            "summary": research_bundle["report"],
            "confidence_score": _estimate_confidence(retrieval),
            "knowledge_graph": context.get("knowledge_graph"),
            "precedent_analysis": context.get("precedent"),
            "ai_generated": ollama_client is not None and research_bundle.get("source") == "llm",
        }

        return response_payload

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out. Please try again with a simpler query.")
    except Exception as exc:  # pragma: no cover - defensive logging
        raise HTTPException(status_code=500, detail=str(exc))


__all__ = [
    "router",
    "generate_structured_legal_research",
    "prepare_research_context",
]