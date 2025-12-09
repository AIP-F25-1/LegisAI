"""
Knowledge Graph Builder Service
Auto-builds graph of precedents, statutes, and clauses, highlighting influential cases
"""

import logging
import asyncio
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

# Try to import networkx for graph structure
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None
    logger.warning("⚠️ networkx not available. Install with: pip install networkx")

@dataclass
class GraphNode:
    """Node in the knowledge graph"""
    node_id: str
    node_type: str  # "case", "statute", "clause", "principle"
    title: str
    text: str
    metadata: Dict[str, Any]
    citation_count: int = 0
    influence_score: float = 0.0

@dataclass
class GraphEdge:
    """Edge in the knowledge graph"""
    source_id: str
    target_id: str
    edge_type: str  # "cites", "overrules", "distinguishes", "relates_to"
    weight: float = 1.0
    evidence: str = ""

class KnowledgeGraphBuilder:
    """Builds and maintains a knowledge graph of legal documents"""
    
    def __init__(self, vector_store=None, hybrid_retriever=None):
        """
        Initialize knowledge graph builder
        
        Args:
            vector_store: VectorStore instance for document access
            hybrid_retriever: HybridRetriever instance for search
        """
        self.vector_store = vector_store
        self.hybrid_retriever = hybrid_retriever
        
        # Graph structure (use networkx if available, otherwise dict-based)
        if NETWORKX_AVAILABLE:
            self.graph = nx.DiGraph()
        else:
            self.graph = {}  # Dict-based graph: {node_id: {neighbors: [edge_info]}}
        
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.citation_map: Dict[str, Set[str]] = defaultdict(set)  # cited_by -> {cites}
        self.is_built = False
        
        # Patterns for extracting citations
        self.citation_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+v\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # Case v. Case
            r'(\d+)\s+([A-Z][a-Z]+)\s+(\d+)',  # Volume Reporter Page
            r'([A-Z]{2,})\s+§\s+(\d+)',  # Statute citation
        ]
    
    async def build_graph_async(self, max_documents: Optional[int] = None) -> Dict[str, Any]:
        """
        Build knowledge graph from available documents asynchronously
        
        Args:
            max_documents: Maximum number of documents to process (None for all)
            
        Returns:
            Dictionary with build statistics
        """
        logger.info("🔗 Building knowledge graph from documents...")
        
        if not self.vector_store:
            return {
                "status": "error",
                "message": "Vector store not available",
                "nodes": 0,
                "edges": 0
            }
        
        try:
            # Get all documents
            doc_count = self.vector_store.get_document_count()
            if max_documents:
                doc_count = min(doc_count, max_documents)
            
            logger.info(f"📚 Processing {doc_count} documents for graph construction...")
            
            # Process documents
            nodes_created = 0
            edges_created = 0
            
            for i in range(doc_count):
                try:
                    doc = self.vector_store.get_document(i)
                    if not doc:
                        continue
                    
                    # Create node
                    node = self._create_node_from_document(doc, i)
                    if node:
                        self.nodes[node.node_id] = node
                        if NETWORKX_AVAILABLE:
                            self.graph.add_node(node.node_id, **{
                                'type': node.node_type,
                                'title': node.title,
                                'citation_count': node.citation_count,
                                'influence_score': node.influence_score
                            })
                        else:
                            if node.node_id not in self.graph:
                                self.graph[node.node_id] = []
                        nodes_created += 1
                    
                    # Extract citations and create edges
                    citations = self._extract_citations(doc.get('text', ''))
                    for citation in citations:
                        edge = self._create_edge_from_citation(node.node_id, citation, doc.get('text', ''))
                        if edge:
                            self.edges.append(edge)
                            self.citation_map[edge.target_id].add(edge.source_id)
                            
                            if NETWORKX_AVAILABLE:
                                self.graph.add_edge(
                                    edge.source_id,
                                    edge.target_id,
                                    edge_type=edge.edge_type,
                                    weight=edge.weight,
                                    evidence=edge.evidence
                                )
                            else:
                                if edge.source_id not in self.graph:
                                    self.graph[edge.source_id] = []
                                self.graph[edge.source_id].append({
                                    'target': edge.target_id,
                                    'type': edge.edge_type,
                                    'weight': edge.weight
                                })
                            edges_created += 1
                    
                    # Update citation counts
                    if node and node.node_id in self.citation_map:
                        node.citation_count = len(self.citation_map[node.node_id])
                        node.influence_score = self._calculate_influence_score(node)
                
                except Exception as e:
                    logger.warning(f"Error processing document {i}: {e}")
                    continue
            
            self.is_built = True
            
            logger.info(f"✅ Knowledge graph built: {nodes_created} nodes, {edges_created} edges")
            
            return {
                "status": "success",
                "nodes": nodes_created,
                "edges": edges_created,
                "is_built": True
            }
            
        except Exception as e:
            logger.error(f"Error building knowledge graph: {e}")
            return {
                "status": "error",
                "message": str(e),
                "nodes": len(self.nodes),
                "edges": len(self.edges)
            }
    
    def _create_node_from_document(self, doc: Dict[str, Any], doc_id: int) -> Optional[GraphNode]:
        """Create a graph node from a document"""
        try:
            metadata = doc.get('metadata', {})
            text = doc.get('text', '')
            
            # Determine node type
            doc_type = metadata.get('type', 'unknown')
            if doc_type == 'case_law':
                node_type = "case"
            elif doc_type == 'legislation':
                node_type = "statute"
            elif doc_type == 'clause':
                node_type = "clause"
            else:
                node_type = "principle"
            
            # Get title
            title = metadata.get('title', metadata.get('case_name', f"Document {doc_id}"))
            
            # Create node ID
            node_id = f"{node_type}_{doc_id}_{hash(title) % 100000}"
            
            return GraphNode(
                node_id=node_id,
                node_type=node_type,
                title=title,
                text=text[:500],  # Store first 500 chars
                metadata=metadata,
                citation_count=0,
                influence_score=0.0
            )
        except Exception as e:
            logger.warning(f"Error creating node: {e}")
            return None
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract case citations from text"""
        citations = []
        
        # Pattern 1: Case v. Case format
        case_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+v\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        matches = re.finditer(case_pattern, text)
        for match in matches:
            case_name = f"{match.group(1)} v. {match.group(2)}"
            citations.append(case_name)
        
        # Pattern 2: Citation format (Volume Reporter Page)
        citation_pattern = r'(\d+)\s+([A-Z][a-z]+)\s+(\d+)'
        matches = re.finditer(citation_pattern, text)
        for match in matches:
            citation = f"{match.group(1)} {match.group(2)} {match.group(3)}"
            citations.append(citation)
        
        return list(set(citations))  # Remove duplicates
    
    def _create_edge_from_citation(self, source_id: str, citation: str, source_text: str) -> Optional[GraphEdge]:
        """Create an edge from a citation"""
        try:
            # Try to find target node by citation
            target_id = None
            for node_id, node in self.nodes.items():
                if citation.lower() in node.title.lower() or citation.lower() in node.text.lower():
                    target_id = node_id
                    break
            
            # If not found, create a placeholder node
            if not target_id:
                target_id = f"cited_{hash(citation) % 100000}"
                # Don't create placeholder nodes, just skip
                return None
            
            # Determine edge type
            edge_type = "cites"
            if "overrul" in source_text.lower():
                edge_type = "overrules"
            elif "distinguish" in source_text.lower():
                edge_type = "distinguishes"
            
            # Extract evidence sentence
            evidence = self._extract_citation_evidence(source_text, citation)
            
            return GraphEdge(
                source_id=source_id,
                target_id=target_id,
                edge_type=edge_type,
                weight=1.0,
                evidence=evidence
            )
        except Exception as e:
            logger.warning(f"Error creating edge: {e}")
            return None
    
    def _extract_citation_evidence(self, text: str, citation: str) -> str:
        """Extract sentence containing citation"""
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            if citation.lower() in sentence.lower():
                return sentence.strip()[:200]
        return f"References {citation}"
    
    def _calculate_influence_score(self, node: GraphNode) -> float:
        """Calculate influence score based on citations and connections"""
        score = 0.0
        
        # Base score from citation count
        citation_count = node.citation_count
        score += min(citation_count * 0.1, 0.5)  # Max 0.5 from citations
        
        # Boost for being cited by many different cases
        if node.node_id in self.citation_map:
            unique_citers = len(self.citation_map[node.node_id])
            score += min(unique_citers * 0.05, 0.3)  # Max 0.3 from unique citers
        
        # Boost for node type (cases are more influential)
        if node.node_type == "case":
            score += 0.1
        elif node.node_type == "statute":
            score += 0.05
        
        return min(score, 1.0)
    
    def get_influential_cases(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most influential or cited cases
        
        Args:
            top_n: Number of top cases to return
            
        Returns:
            List of influential cases with scores
        """
        if not self.is_built:
            return []
        
        # Calculate influence scores for all nodes
        for node in self.nodes.values():
            node.influence_score = self._calculate_influence_score(node)
        
        # Sort by influence score
        influential = sorted(
            self.nodes.values(),
            key=lambda n: (n.influence_score, n.citation_count),
            reverse=True
        )
        
        # Filter to cases only
        cases = [n for n in influential if n.node_type == "case"]
        
        return [
            {
                "case_id": node.node_id,
                "case_name": node.title,
                "influence_score": node.influence_score,
                "citation_count": node.citation_count,
                "node_type": node.node_type,
                "metadata": node.metadata
            }
            for node in cases[:top_n]
        ]
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        if not self.is_built:
            return {
                "is_built": False,
                "nodes": 0,
                "edges": 0
            }
        
        node_types = Counter(n.node_type for n in self.nodes.values())
        
        edge_types = Counter(e.edge_type for e in self.edges)
        
        return {
            "is_built": True,
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": dict(node_types),
            "edge_types": dict(edge_types),
            "most_cited": len([n for n in self.nodes.values() if n.citation_count > 0]),
            "networkx_available": NETWORKX_AVAILABLE
        }
    
    def get_case_connections(self, case_id: str, max_connections: int = 10) -> Dict[str, Any]:
        """
        Get connections for a specific case
        
        Args:
            case_id: ID of the case
            max_connections: Maximum number of connections to return
            
        Returns:
            Dictionary with connected cases and relationship types
        """
        if case_id not in self.nodes:
            return {
                "case_id": case_id,
                "found": False,
                "connections": []
            }
        
        connections = []
        
        # Get outgoing edges (cases this case cites)
        outgoing = [e for e in self.edges if e.source_id == case_id][:max_connections]
        for edge in outgoing:
            target_node = self.nodes.get(edge.target_id)
            if target_node:
                connections.append({
                    "case_id": edge.target_id,
                    "case_name": target_node.title,
                    "relationship": edge.edge_type,
                    "direction": "cites",
                    "evidence": edge.evidence
                })
        
        # Get incoming edges (cases that cite this case)
        incoming = [e for e in self.edges if e.target_id == case_id][:max_connections]
        for edge in incoming:
            source_node = self.nodes.get(edge.source_id)
            if source_node:
                connections.append({
                    "case_id": edge.source_id,
                    "case_name": source_node.title,
                    "relationship": edge.edge_type,
                    "direction": "cited_by",
                    "evidence": edge.evidence
                })
        
        return {
            "case_id": case_id,
            "case_name": self.nodes[case_id].title,
            "found": True,
            "total_connections": len(connections),
            "connections": connections[:max_connections]
        }

