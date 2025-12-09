"""
Document OCR Agent - Multi-Modal Legal Intelligence
Handles OCR for scanned documents and entity extraction
"""

import logging
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# OCR Library (Tesseract)
try:
    import pytesseract
    from PIL import Image
    import pdf2image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    pytesseract = None
    Image = None
    pdf2image = None
    logger.warning("⚠️ OCR libraries not available. Install with: pip install pytesseract pillow pdf2image")

# Entity Extraction (spaCy or regex-based)
try:
    import spacy
    SPACY_AVAILABLE = True
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        logger.warning("⚠️ spaCy model not found. Using regex-based extraction.")
        SPACY_AVAILABLE = False
        nlp = None
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None
    logger.warning("⚠️ spaCy not available. Using regex-based entity extraction.")


class OCRAgent:
    """OCR Agent for scanned legal documents with entity extraction"""
    
    def __init__(self):
        self.ocr_available = OCR_AVAILABLE
        self.spacy_available = SPACY_AVAILABLE
        self.nlp = nlp
        
        if not OCR_AVAILABLE:
            logger.warning("⚠️ OCR Agent initialized but OCR libraries not available")
        else:
            logger.info("✅ OCR Agent initialized")
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, Any]:
        """Extract text from scanned image using OCR"""
        if not OCR_AVAILABLE:
            return {
                "success": False,
                "error": "OCR libraries not available. Install pytesseract, pillow, and pdf2image",
                "text": ""
            }
        
        try:
            # Load image
            image = Image.open(image_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang='eng')
            
            # Get confidence scores (if available)
            try:
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            except:
                avg_confidence = 0
            
            return {
                "success": True,
                "text": text.strip(),
                "confidence": avg_confidence,
                "char_count": len(text),
                "word_count": len(text.split())
            }
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    def extract_text_from_pdf(self, pdf_path: str, dpi: int = 300) -> Dict[str, Any]:
        """Extract text from scanned PDF by converting to images and OCR"""
        if not OCR_AVAILABLE:
            return {
                "success": False,
                "error": "OCR libraries not available",
                "text": "",
                "pages": []
            }
        
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path, dpi=dpi)
            
            all_text = []
            page_results = []
            
            for page_num, image in enumerate(images, 1):
                # Perform OCR on each page
                page_text = pytesseract.image_to_string(image, lang='eng')
                all_text.append(page_text)
                
                page_results.append({
                    "page": page_num,
                    "text": page_text.strip(),
                    "char_count": len(page_text),
                    "word_count": len(page_text.split())
                })
            
            full_text = "\n\n".join(all_text)
            
            return {
                "success": True,
                "text": full_text.strip(),
                "pages": page_results,
                "total_pages": len(images),
                "char_count": len(full_text),
                "word_count": len(full_text.split())
            }
        except Exception as e:
            logger.error(f"PDF OCR extraction error: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "pages": []
            }
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities (parties, dates, monetary values) from text"""
        entities = {
            "parties": [],
            "dates": [],
            "monetary_values": [],
            "locations": [],
            "organizations": [],
            "persons": []
        }
        
        # Use spaCy if available
        if self.spacy_available and self.nlp:
            try:
                doc = self.nlp(text)
                
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        entities["persons"].append({
                            "text": ent.text,
                            "start": ent.start_char,
                            "end": ent.end_char
                        })
                    elif ent.label_ == "ORG":
                        entities["organizations"].append({
                            "text": ent.text,
                            "start": ent.start_char,
                            "end": ent.end_char
                        })
                    elif ent.label_ == "DATE":
                        entities["dates"].append({
                            "text": ent.text,
                            "start": ent.start_char,
                            "end": ent.end_char,
                            "parsed": self._parse_date(ent.text)
                        })
                    elif ent.label_ == "MONEY":
                        entities["monetary_values"].append({
                            "text": ent.text,
                            "start": ent.start_char,
                            "end": ent.end_char,
                            "parsed": self._parse_money(ent.text)
                        })
                    elif ent.label_ in ["GPE", "LOC"]:
                        entities["locations"].append({
                            "text": ent.text,
                            "start": ent.start_char,
                            "end": ent.end_char
                        })
            except Exception as e:
                logger.warning(f"spaCy entity extraction error: {e}, falling back to regex")
        
        # Regex-based fallback extraction
        entities.update(self._regex_entity_extraction(text))
        
        # Deduplicate entities
        for key in entities:
            if isinstance(entities[key], list):
                seen = set()
                unique_entities = []
                for ent in entities[key]:
                    ent_text = ent.get("text", "") if isinstance(ent, dict) else str(ent)
                    if ent_text and ent_text not in seen:
                        seen.add(ent_text)
                        unique_entities.append(ent)
                entities[key] = unique_entities
        
        # Identify parties (combine persons and organizations)
        entities["parties"] = entities["persons"] + entities["organizations"]
        
        return {
            "entities": entities,
            "party_count": len(entities["parties"]),
            "date_count": len(entities["dates"]),
            "monetary_count": len(entities["monetary_values"]),
            "location_count": len(entities["locations"])
        }
    
    def _regex_entity_extraction(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Regex-based entity extraction fallback"""
        entities = {
            "dates": [],
            "monetary_values": [],
            "locations": []
        }
        
        # Date patterns
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
            r'\b\d{4}-\d{2}-\d{2}\b'  # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities["dates"].append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "parsed": self._parse_date(match.group())
                })
        
        # Monetary value patterns
        money_patterns = [
            r'\$[\d,]+(?:\.\d{2})?',  # $1,234.56
            r'[\d,]+(?:\.\d{2})?\s*(?:USD|dollars?|EUR|euros?|GBP|pounds?)',  # 1,234.56 USD
            r'(?:USD|EUR|GBP)\s*[\d,]+(?:\.\d{2})?'  # USD 1,234.56
        ]
        
        for pattern in money_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities["monetary_values"].append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "parsed": self._parse_money(match.group())
                })
        
        return entities
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format"""
        try:
            # Try common date formats
            formats = [
                "%m/%d/%Y",
                "%m-%d-%Y",
                "%Y-%m-%d",
                "%B %d, %Y",
                "%b %d, %Y"
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.isoformat()
                except:
                    continue
        except:
            pass
        return None
    
    def _parse_money(self, money_str: str) -> Optional[float]:
        """Parse monetary value to float"""
        try:
            # Extract numbers
            numbers = re.findall(r'[\d,]+\.?\d*', money_str.replace(',', ''))
            if numbers:
                return float(numbers[0])
        except:
            pass
        return None
    
    def process_document(self, file_path: str, extract_entities: bool = True) -> Dict[str, Any]:
        """Process document (image or PDF) with OCR and entity extraction"""
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        result = {
            "file_path": str(file_path),
            "file_type": file_path_obj.suffix.lower(),
            "ocr_available": self.ocr_available
        }
        
        # Perform OCR based on file type
        if file_path_obj.suffix.lower() in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            ocr_result = self.extract_text_from_image(str(file_path))
        elif file_path_obj.suffix.lower() == '.pdf':
            ocr_result = self.extract_text_from_pdf(str(file_path))
        else:
            return {
                "success": False,
                "error": f"Unsupported file type: {file_path_obj.suffix}"
            }
        
        result.update(ocr_result)
        
        # Extract entities if requested and OCR was successful
        if extract_entities and ocr_result.get("success") and ocr_result.get("text"):
            entity_result = self.extract_entities(ocr_result["text"])
            result["entities"] = entity_result["entities"]
            result["entity_summary"] = {
                "parties": entity_result["party_count"],
                "dates": entity_result["date_count"],
                "monetary_values": entity_result["monetary_count"],
                "locations": entity_result["location_count"]
            }
        
        return result

