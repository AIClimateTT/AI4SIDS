"""
Document Knowledge Base
=======================
RAG (Retrieval-Augmented Generation) system for climate and flood knowledge
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import pickle

from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# FAISS for vector store
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("WARNING: FAISS or sentence-transformers not available. RAG system disabled.")

from config.settings import settings


class DocumentKnowledgeBase:
    """
    Manages PDF documents and provides semantic search capabilities
    """

    def __init__(self, knowledge_dir: Optional[Path] = None):
        """
        Initialize the knowledge base

        Args:
            knowledge_dir: Directory containing PDF files (default: data/knowledge/)
        """
        self.knowledge_dir = knowledge_dir or settings.DATA_DIR / "knowledge"
        self.vector_store_path = settings.DATA_DIR / "vector_store"
        self.vector_store_path.mkdir(exist_ok=True)

        # Embedding model
        self.embedding_model = None
        self.index = None
        self.documents = []
        self.document_texts = []

        if FAISS_AVAILABLE:
            self._initialize()
        else:
            print("RAG system not initialized - missing dependencies")

    def _initialize(self):
        """Initialize or load the vector store"""
        index_file = self.vector_store_path / "faiss.index"
        docs_file = self.vector_store_path / "documents.pkl"

        if index_file.exists() and docs_file.exists():
            print("Loading existing vector store...")
            self._load_vector_store()
        else:
            print("Building new vector store from PDFs...")
            self._build_vector_store()

    def _load_vector_store(self):
        """Load pre-built vector store from disk"""
        try:
            # Load embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

            # Load FAISS index
            index_file = str(self.vector_store_path / "faiss.index")
            self.index = faiss.read_index(index_file)

            # Load documents
            docs_file = self.vector_store_path / "documents.pkl"
            with open(docs_file, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.document_texts = data['texts']

            print(f"Loaded {len(self.documents)} document chunks from vector store")
        except Exception as e:
            print(f"Error loading vector store: {e}")
            print("Rebuilding vector store...")
            self._build_vector_store()

    def _build_vector_store(self):
        """Build vector store from PDF documents"""
        if not FAISS_AVAILABLE:
            return

        # Load embedding model
        print("Loading embedding model (all-MiniLM-L6-v2)...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Load and process PDFs
        documents = self._load_pdfs()

        if not documents:
            print("No documents found to index")
            return

        # Split into chunks
        print("Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        chunks = []
        for doc in documents:
            splits = text_splitter.split_text(doc.page_content)
            for split in splits:
                chunks.append(Document(
                    page_content=split,
                    metadata=doc.metadata
                ))

        print(f"Created {len(chunks)} chunks from {len(documents)} documents")

        # Generate embeddings
        print("Generating embeddings...")
        self.document_texts = [chunk.page_content for chunk in chunks]
        embeddings = self.embedding_model.encode(self.document_texts, show_progress_bar=True)

        # Create FAISS index
        print("Building FAISS index...")
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

        self.documents = chunks

        # Save to disk
        self._save_vector_store()

        print(f"Vector store built successfully with {len(chunks)} chunks")

    def _load_pdfs(self) -> List[Document]:
        """Load all PDF files from the knowledge directory"""
        documents = []

        if not self.knowledge_dir.exists():
            print(f"Knowledge directory not found: {self.knowledge_dir}")
            return documents

        pdf_files = list(self.knowledge_dir.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF files")

        for pdf_path in pdf_files:
            try:
                print(f"Processing: {pdf_path.name}")
                reader = PdfReader(str(pdf_path))

                # Extract text from all pages
                text = ""
                for page_num, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

                if text.strip():
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "source": pdf_path.name,
                            "pages": len(reader.pages)
                        }
                    ))
                    print(f"  Extracted {len(text)} characters from {len(reader.pages)} pages")
                else:
                    print(f"  No text extracted from {pdf_path.name}")

            except Exception as e:
                print(f"  Error processing {pdf_path.name}: {str(e)}")

        return documents

    def _save_vector_store(self):
        """Save vector store to disk"""
        try:
            # Save FAISS index
            index_file = str(self.vector_store_path / "faiss.index")
            faiss.write_index(self.index, index_file)

            # Save documents
            docs_file = self.vector_store_path / "documents.pkl"
            with open(docs_file, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'texts': self.document_texts
                }, f)

            print("Vector store saved to disk")
        except Exception as e:
            print(f"Error saving vector store: {e}")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for relevant documents

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of relevant document chunks with metadata
        """
        if not FAISS_AVAILABLE or self.index is None:
            return []

        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])

            # Search FAISS index
            distances, indices = self.index.search(query_embedding, top_k)

            # Build results
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.documents):
                    doc = self.documents[idx]
                    results.append({
                        'content': doc.page_content,
                        'source': doc.metadata.get('source', 'Unknown'),
                        'score': float(distances[0][i])
                    })

            return results

        except Exception as e:
            print(f"Error during search: {e}")
            return []

    def rebuild_index(self):
        """Force rebuild of the vector store"""
        print("Rebuilding vector store...")
        self._build_vector_store()


# Global knowledge base instance
_knowledge_base: Optional[DocumentKnowledgeBase] = None


def get_knowledge_base() -> DocumentKnowledgeBase:
    """Get or create the global knowledge base instance"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = DocumentKnowledgeBase()
    return _knowledge_base


def search_knowledge(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Search the knowledge base for relevant information

    Args:
        query: Search query
        top_k: Number of results to return

    Returns:
        List of relevant document chunks
    """
    kb = get_knowledge_base()
    return kb.search(query, top_k)
