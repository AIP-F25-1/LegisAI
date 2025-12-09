"""
Speech-to-Text + TTS Agent - Multi-Modal Legal Intelligence
Whisper for court transcript ingestion and EdgeTTS for spoken summaries
"""

import logging
import asyncio
import re
from typing import Dict, Optional, Any, AsyncGenerator
from pathlib import Path
import tempfile
import os

logger = logging.getLogger(__name__)

# Whisper (Speech-to-Text)
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None
    logger.warning("⚠️ Whisper not available. Install with: pip install openai-whisper")

# EdgeTTS (Text-to-Speech)
try:
    import edge_tts
    EDGETTS_AVAILABLE = True
except ImportError:
    EDGETTS_AVAILABLE = False
    edge_tts = None
    logger.warning("⚠️ EdgeTTS not available. Install with: pip install edge-tts")


class SpeechTTSAgent:
    """Speech-to-Text and Text-to-Speech Agent for legal documents"""
    
    def __init__(self):
        self.whisper_available = WHISPER_AVAILABLE
        self.edgetts_available = EDGETTS_AVAILABLE
        self.whisper_model = None
        
        if WHISPER_AVAILABLE:
            try:
                # Load Whisper model (base model for speed)
                self.whisper_model = whisper.load_model("base")
                logger.info("✅ Whisper model loaded (base)")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load Whisper model: {e}")
                self.whisper_available = False
        
        if EDGETTS_AVAILABLE:
            logger.info("✅ EdgeTTS available")
        
        logger.info("✅ Speech TTS Agent initialized")
    
    async def transcribe_audio(self, audio_path: str, language: str = "en") -> Dict[str, Any]:
        """Transcribe audio file to text using Whisper
        
        Args:
            audio_path: Path to audio file
            language: Language code (default: "en")
        
        Returns:
            Transcription result with text and metadata
        """
        if not self.whisper_available or not self.whisper_model:
            return {
                "success": False,
                "error": "Whisper not available. Install with: pip install openai-whisper",
                "text": ""
            }
        
        try:
            # Transcribe audio
            result = self.whisper_model.transcribe(audio_path, language=language)
            
            text = result.get("text", "").strip()
            segments = result.get("segments", [])
            
            return {
                "success": True,
                "text": text,
                "language": result.get("language", language),
                "segments": [
                    {
                        "id": seg.get("id", i),
                        "start": seg.get("start", 0),
                        "end": seg.get("end", 0),
                        "text": seg.get("text", "").strip()
                    }
                    for i, seg in enumerate(segments)
                ],
                "duration": segments[-1].get("end", 0) if segments else 0,
                "word_count": len(text.split())
            }
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    async def transcribe_court_transcript(self, audio_path: str) -> Dict[str, Any]:
        """Specialized transcription for court transcripts with speaker identification"""
        result = await self.transcribe_audio(audio_path, language="en")
        
        if not result.get("success"):
            return result
        
        # Try to identify speakers (basic pattern matching)
        text = result["text"]
        speakers = self._identify_speakers(text)
        
        result["speakers"] = speakers
        result["transcript_type"] = "court_transcript"
        
        return result
    
    def _identify_speakers(self, text: str) -> list:
        """Identify speakers in transcript (basic pattern matching)"""
        speakers = []
        
        # Common patterns for court transcripts
        patterns = [
            r'(?:THE COURT|COURT):',
            r'(?:MR\.|MRS\.|MS\.|DR\.)\s+[A-Z][A-Z\s]+:',
            r'(?:ATTORNEY|COUNSEL|PLAINTIFF|DEFENDANT):',
            r'Q\s*:',
            r'A\s*:'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                speaker_text = match.group().rstrip(':').strip()
                if speaker_text not in speakers:
                    speakers.append(speaker_text)
        
        return speakers
    
    async def text_to_speech(
        self, 
        text: str, 
        voice: str = "en-US-AriaNeural",
        output_path: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ) -> Dict[str, Any]:
        """Convert text to speech using EdgeTTS
        
        Args:
            text: Text to convert to speech
            voice: Voice name (default: en-US-AriaNeural)
            output_path: Optional output file path
            rate: Speech rate (e.g., "+0%", "+10%", "-10%")
            pitch: Speech pitch (e.g., "+0Hz", "+5Hz")
        
        Returns:
            TTS result with audio file path
        """
        if not self.edgetts_available:
            return {
                "success": False,
                "error": "EdgeTTS not available. Install with: pip install edge-tts",
                "audio_path": None
            }
        
        try:
            # Generate output path if not provided
            if not output_path:
                temp_dir = tempfile.gettempdir()
                output_path = os.path.join(temp_dir, f"tts_{hash(text) % 100000}.mp3")
            
            # Generate speech
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            await communicate.save(output_path)
            
            # Get file size
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            
            return {
                "success": True,
                "audio_path": output_path,
                "file_size": file_size,
                "voice": voice,
                "text_length": len(text),
                "word_count": len(text.split())
            }
        except Exception as e:
            logger.error(f"EdgeTTS error: {e}")
            return {
                "success": False,
                "error": str(e),
                "audio_path": None
            }
    
    async def summarize_and_speak(
        self, 
        text: str, 
        summary_length: str = "short",
        voice: str = "en-US-AriaNeural"
    ) -> Dict[str, Any]:
        """Generate spoken summary of text
        
        Args:
            text: Text to summarize and speak
            summary_length: "short" (2 min), "medium" (5 min), "long" (10 min)
            voice: TTS voice to use
        
        Returns:
            Summary text and audio file path
        """
        # Estimate target length based on summary_length
        target_lengths = {
            "short": 300,  # ~2 minutes at normal speaking pace
            "medium": 750,  # ~5 minutes
            "long": 1500   # ~10 minutes
        }
        
        target_words = target_lengths.get(summary_length, 300)
        
        # Simple summarization (truncate to target length)
        # In production, use AI summarization
        words = text.split()
        if len(words) > target_words:
            summary_text = " ".join(words[:target_words]) + "..."
        else:
            summary_text = text
        
        # Generate speech
        tts_result = await self.text_to_speech(summary_text, voice=voice)
        
        return {
            "success": tts_result.get("success", False),
            "summary_text": summary_text,
            "summary_length": len(summary_text),
            "word_count": len(summary_text.split()),
            "audio_path": tts_result.get("audio_path"),
            "voice": voice,
            "error": tts_result.get("error")
        }
    
    async def get_available_voices(self, language: str = "en") -> Dict[str, Any]:
        """Get available TTS voices"""
        if not self.edgetts_available:
            return {
                "success": False,
                "voices": [],
                "error": "EdgeTTS not available"
            }
        
        try:
            voices = await edge_tts.list_voices()
            
            # Filter by language
            filtered_voices = [
                {
                    "name": v["Name"],
                    "locale": v["Locale"],
                    "gender": v["Gender"],
                    "short_name": v["ShortName"]
                }
                for v in voices
                if v["Locale"].startswith(language)
            ]
            
            return {
                "success": True,
                "voices": filtered_voices,
                "total": len(filtered_voices)
            }
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return {
                "success": False,
                "voices": [],
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "whisper_available": self.whisper_available,
            "edgetts_available": self.edgetts_available,
            "whisper_model_loaded": self.whisper_model is not None,
            "features": {
                "speech_to_text": self.whisper_available,
                "text_to_speech": self.edgetts_available,
                "court_transcript": self.whisper_available,
                "spoken_summaries": self.edgetts_available
            }
        }

