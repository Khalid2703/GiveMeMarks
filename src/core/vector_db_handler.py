"""
Vector Database Handler for Academic Evaluation System
Stores document embeddings for semantic search

FEATURES:
- Text embeddings generation
- Semantic search across documents
- Student record similarity matching
- Course recommendation based on academic history

IMPLEMENTATION: ChromaDB (local, no API key needed)
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from loguru import logger

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logger.warning("ChromaDB not installed. Install with: pip install chromadb")

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")


class VectorDBHandler:
    """
    Vector Database handler for semantic search on academic documents.
    
    Uses ChromaDB for local vector storage and sentence-transformers for embeddings.
    No API keys required!
    """
    
    def __init__(self, persist_directory: str = "./data/vector_db"):
        """
        Initialize Vector DB handler.
        
        Args:
            persist_directory: Where to store the vector database
        """
        if not CHROMA_AVAILABLE:
            raise ImportError("ChromaDB not installed. Run: pip install chromadb")
        
        if not EMBEDDINGS_AVAILABLE:
            raise ImportError("sentence-transformers not installed. Run: pip install sentence-transformers")
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model (local, fast)
        logger.info("Loading embedding model (this may take a moment)...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✓ Embedding model loaded: all-MiniLM-L6-v2")
        
        # Create/get collections
        self.students_collection = self.client.get_or_create_collection(
            name="students",
            metadata={"description": "Student academic records"}
        )
        
        self.documents_collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"description": "Raw document texts"}
        )
        
        logger.info(f"✓ Vector DB initialized at {self.persist_directory}")
        logger.info(f"  Students collection: {self.students_collection.count()} records")
        logger.info(f"  Documents collection: {self.documents_collection.count()} documents")
    
    def add_student_record(
        self,
        student_data: Dict[str, Any],
        document_filename: str
    ) -> bool:
        """
        Add a student record to vector database.
        
        Args:
            student_data: Parsed student academic data
            document_filename: Source document filename
            
        Returns:
            True if successful
        """
        try:
            # Create unique ID
            roll_number = student_data.get('Roll Number') or student_data.get('roll_number', 'unknown')
            student_id = f"{roll_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create searchable text representation
            text_content = self._create_student_text(student_data)
            
            # Generate embedding
            embedding = self.embedding_model.encode(text_content).tolist()
            
            # Prepare metadata (must be JSON-serializable)
            metadata = {
                "roll_number": str(roll_number),
                "student_name": str(student_data.get('Student Name') or student_data.get('student_name', 'Unknown')),
                "department": str(student_data.get('Department') or student_data.get('department', 'Unknown')),
                "cgpa": str(student_data.get('CGPA') or student_data.get('cgpa', 'N/A')),
                "document_filename": document_filename,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to collection
            self.students_collection.add(
                ids=[student_id],
                embeddings=[embedding],
                documents=[text_content],
                metadatas=[metadata]
            )
            
            logger.info(f"✓ Added student to vector DB: {roll_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add student to vector DB: {e}")
            return False
    
    def add_document(
        self,
        document_text: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a raw document to vector database.
        
        Args:
            document_text: Full text of document
            filename: Document filename
            metadata: Additional metadata
            
        Returns:
            True if successful
        """
        try:
            # Create unique ID
            doc_id = f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Generate embedding (split into chunks if too long)
            text_chunks = self._chunk_text(document_text, max_length=500)
            
            ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for i, chunk in enumerate(text_chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                embedding = self.embedding_model.encode(chunk).tolist()
                
                chunk_metadata = {
                    "filename": filename,
                    "chunk_index": i,
                    "total_chunks": len(text_chunks),
                    "timestamp": datetime.now().isoformat()
                }
                
                if metadata:
                    chunk_metadata.update({k: str(v) for k, v in metadata.items()})
                
                ids.append(chunk_id)
                embeddings.append(embedding)
                documents.append(chunk)
                metadatas.append(chunk_metadata)
            
            # Add all chunks to collection
            self.documents_collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"✓ Added document to vector DB: {filename} ({len(text_chunks)} chunks)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document to vector DB: {e}")
            return False
    
    def search_students(
        self,
        query: str,
        n_results: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for students.
        
        Args:
            query: Natural language search query
            n_results: Number of results to return
            filter_dict: Metadata filters (e.g., {"department": "Computer Science"})
            
        Returns:
            List of matching student records
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search
            results = self.students_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_dict if filter_dict else None
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity_score": 1 - results['distances'][0][i]  # Convert distance to similarity
                })
            
            logger.info(f"Found {len(formatted_results)} students matching: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def search_documents(
        self,
        query: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for documents.
        
        Args:
            query: Natural language search query
            n_results: Number of results to return
            
        Returns:
            List of matching document chunks
        """
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            
            results = self.documents_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity_score": 1 - results['distances'][0][i]
                })
            
            logger.info(f"Found {len(formatted_results)} documents matching: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_similar_students(
        self,
        roll_number: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find students with similar academic profiles.
        
        Args:
            roll_number: Reference student's roll number
            n_results: Number of similar students to find
            
        Returns:
            List of similar student records
        """
        try:
            # Get the reference student's embedding
            results = self.students_collection.get(
                where={"roll_number": str(roll_number)}
            )
            
            if not results['ids']:
                logger.warning(f"Student not found: {roll_number}")
                return []
            
            # Use the student's text to find similar ones
            reference_text = results['documents'][0]
            return self.search_students(reference_text, n_results + 1)  # +1 to exclude self
            
        except Exception as e:
            logger.error(f"Failed to find similar students: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get vector database statistics."""
        return {
            "students_count": self.students_collection.count(),
            "documents_count": self.documents_collection.count(),
            "persist_directory": str(self.persist_directory),
            "embedding_model": "all-MiniLM-L6-v2",
            "embedding_dimension": 384
        }
    
    def reset(self, confirm: bool = False):
        """
        Reset (delete) all data in vector database.
        
        Args:
            confirm: Must be True to actually delete
        """
        if not confirm:
            logger.warning("Reset called without confirmation. Set confirm=True to actually delete.")
            return
        
        self.client.reset()
        logger.info("✓ Vector database reset complete")
    
    # Helper methods
    
    def _create_student_text(self, student_data: Dict[str, Any]) -> str:
        """Create searchable text representation of student data."""
        text_parts = []
        
        # Basic info
        name = student_data.get('Student Name') or student_data.get('student_name')
        if name:
            text_parts.append(f"Name: {name}")
        
        roll = student_data.get('Roll Number') or student_data.get('roll_number')
        if roll:
            text_parts.append(f"Roll Number: {roll}")
        
        dept = student_data.get('Department') or student_data.get('department')
        if dept:
            text_parts.append(f"Department: {dept}")
        
        cgpa = student_data.get('CGPA') or student_data.get('cgpa')
        if cgpa and cgpa != 'N/A':
            text_parts.append(f"CGPA: {cgpa}")
        
        # Courses
        courses = student_data.get('Courses') or student_data.get('courses', [])
        if courses:
            course_texts = []
            for course in courses[:10]:  # Limit to 10 courses
                code = course.get('Course Code') or course.get('course_code', '')
                name = course.get('Course Name') or course.get('course_name', '')
                grade = course.get('Grade') or course.get('grade', '')
                if code or name:
                    course_texts.append(f"{code} {name} (Grade: {grade})")
            if course_texts:
                text_parts.append("Courses: " + ", ".join(course_texts))
        
        return " | ".join(text_parts)
    
    def _chunk_text(self, text: str, max_length: int = 500) -> List[str]:
        """Split text into chunks for embedding."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_length += len(word) + 1
            if current_length > max_length:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks if chunks else [text]


# Example usage
if __name__ == "__main__":
    # Initialize
    vector_db = VectorDBHandler()
    
    # Test data
    test_student = {
        "Student Name": "Test Student",
        "Roll Number": "21CS3001",
        "Department": "Computer Science",
        "CGPA": "8.5",
        "Courses": [
            {"Course Code": "CS301", "Course Name": "Data Structures", "Grade": "A"},
            {"Course Code": "CS302", "Course Name": "Algorithms", "Grade": "A"},
        ]
    }
    
    # Add to vector DB
    vector_db.add_student_record(test_student, "test_doc.pdf")
    
    # Search
    results = vector_db.search_students("computer science student with good grades")
    print("Search results:", results)
    
    # Statistics
    print("Stats:", vector_db.get_statistics())
