"""
CourtListener API Service
Fetches case law in real-time from CourtListener API
"""
import requests
import time
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

COURTLISTENER_API_BASE = "https://www.courtlistener.com/api/rest/v4"
API_TOKEN = "3558be5dcf356c1ae3edc13061471f67615ef367"

class CourtListenerService:
    """Service for querying CourtListener API for case law"""
    
    def __init__(self, api_token: str = API_TOKEN):
        self.api_token = api_token
        self.base_url = COURTLISTENER_API_BASE
        self.headers = {
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json"
        }
    
    def search_cases(
        self,
        query: str,
        max_results: int = 10,
        court_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for cases on CourtListener API
        
        Args:
            query: Search query
            max_results: Maximum number of cases to return
            court_type: Optional court filter
        
        Returns:
            List of case dictionaries
        """
        try:
            cases = []
            url = f"{self.base_url}/search/"
            page = 1
            
            params = {
                "type": "o",  # 'o' for opinions
                "ordering": "-date_filed",  # Most recent first
                "page_size": min(100, max_results * 2),  # Fetch extra for filtering
                "q": query
            }
            
            if court_type:
                params["court"] = court_type
            
            # Fetch pages until we have enough results
            while len(cases) < max_results:
                params["page"] = page
                
                try:
                    response = requests.get(
                        url,
                        params=params,
                        headers=self.headers,
                        timeout=15
                    )
                    
                    if response.status_code == 401:
                        logger.error("CourtListener API: Authentication failed")
                        break
                    
                    if response.status_code == 403:
                        logger.error("CourtListener API: Access forbidden")
                        break
                    
                    if response.status_code != 200:
                        logger.warning(f"CourtListener API: Status {response.status_code}")
                        break
                    
                    data = response.json()
                    results = data.get("results", [])
                    
                    if not results:
                        break
                    
                    # Process results
                    for result in results:
                        # Extract case ID properly
                        raw_id = result.get('id', '')
                        if isinstance(raw_id, (int, str)) and str(raw_id).strip():
                            case_id = f"courtlistener_{raw_id}"
                        else:
                            # Generate ID from case name
                            case_name = result.get("caseName", "") or result.get("title", "") or ""
                            if case_name:
                                case_id = f"courtlistener_{hash(case_name) % 1000000}"
                            else:
                                case_id = f"courtlistener_{len(cases)}"
                        
                        # Extract case information
                        case_data = {
                            "id": case_id,
                            "case_name": result.get("caseName", "") or result.get("title", ""),
                            "court": result.get("court_name", "") or result.get("court", ""),
                            "jurisdiction": result.get("jurisdiction", ""),
                            "date_filed": result.get("date_filed", "") or result.get("dateFiled", ""),
                            "citation": result.get("citation", ""),
                            "url": result.get("absolute_url", "") or result.get("url", ""),
                            "docket_number": result.get("docket_number", ""),
                            # Extract opinion text (preview)
                            "opinion_text": self._extract_opinion_preview(result),
                            "source": "CourtListener API",
                            # Better scoring based on relevance to query
                            "api_score": max(0.5, 1.0 - (len(cases) / max_results))  # Start high, decrease as more results
                        }
                        
                        # Only add if we have meaningful data
                        if case_data["case_name"] or case_data["opinion_text"]:
                            cases.append(case_data)
                        
                        if len(cases) >= max_results:
                            break
                    
                    # Check if there are more pages
                    if not data.get("next"):
                        break
                    
                    page += 1
                    time.sleep(0.3)  # Rate limiting
                    
                    if len(cases) >= max_results:
                        break
                
                except requests.exceptions.Timeout:
                    logger.warning("CourtListener API: Request timeout")
                    break
                except requests.exceptions.RequestException as e:
                    logger.warning(f"CourtListener API: Request error: {e}")
                    break
                except Exception as e:
                    logger.error(f"CourtListener API: Unexpected error: {e}")
                    break
            
            logger.info(f"CourtListener API: Found {len(cases)} cases for query: {query[:50]}")
            return cases[:max_results]
        
        except Exception as e:
            logger.error(f"CourtListener search error: {e}")
            return []
    
    def _extract_opinion_preview(self, result: Dict[str, Any]) -> str:
        """Extract opinion text preview from API result"""
        # Try different fields that might contain the opinion text
        text_fields = [
            "plain_text",
            "html",
            "html_with_citations",
            "html_lawbox",
            "html_columbia",
            "html_anon_2020",
            "text",
            "content"
        ]
        
        for field in text_fields:
            text = result.get(field, "")
            if text and isinstance(text, str) and len(text.strip()) > 100:
                # Return preview (first 1500 chars for more context)
                preview = text.strip()[:1500]
                # Remove HTML tags if present (simple version)
                import re
                preview = re.sub(r'<[^>]+>', '', preview)
                # Clean up extra whitespace
                preview = re.sub(r'\s+', ' ', preview)
                return preview.strip()
        
        # Fallback: try any text-like field
        for key, value in result.items():
            if isinstance(value, str) and len(value) > 100 and "text" in key.lower():
                import re
                preview = value[:800]
                preview = re.sub(r'<[^>]+>', '', preview)
                return preview.strip()
        
        return ""
    
    def get_case_by_id(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get full case details by ID"""
        try:
            # Remove prefix if present
            case_id = case_id.replace("courtlistener_", "")
            
            url = f"{self.base_url}/opinions/{case_id}/"
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "id": f"courtlistener_{result.get('id', '')}",
                    "case_name": result.get("caseName", "") or result.get("title", ""),
                    "court": result.get("court_name", "") or result.get("court", ""),
                    "date_filed": result.get("date_filed", ""),
                    "citation": result.get("citation", ""),
                    "opinion_text": self._extract_opinion_preview(result),
                    "full_data": result
                }
        except Exception as e:
            logger.error(f"Error fetching case {case_id}: {e}")
        
        return None
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = requests.options(
                f"{self.base_url}/dockets/",
                headers=self.headers,
                timeout=10
            )
            return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"CourtListener connection test failed: {e}")
            return False

# Global instance
_courtlistener_service: Optional[CourtListenerService] = None

def get_courtlistener_service() -> Optional[CourtListenerService]:
    """Get global CourtListener service instance"""
    global _courtlistener_service
    if _courtlistener_service is None:
        _courtlistener_service = CourtListenerService()
        # Test connection
        if not _courtlistener_service.test_connection():
            logger.warning("CourtListener API connection test failed")
            return None
    return _courtlistener_service

COURTLISTENER_AVAILABLE = True  # Set to False if API is unavailable

