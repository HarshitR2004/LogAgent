from langchain_chroma import Chroma
import chromadb
import os

# Import Embeddings directly to avoid relative import issues
try:
    from .Embeddings import Embeddings
except ImportError:
    from Embeddings import Embeddings


class VectorStore:
    """Singleton class for local persistent ChromaDB client."""
    _instance = None
    _client = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the ChromaDB client with local persistent storage"""
        self.persist_directory = os.path.join(os.getcwd(), "chroma_db")
        os.makedirs(self.persist_directory, exist_ok=True)
        self._client = chromadb.PersistentClient(path=self.persist_directory)
    
    def get_collection(self, collection_name: str, model_name: str = "all-MiniLM-L6-v2"):
        """Get or create a Chroma collection with embeddings"""
        embeddings = Embeddings.get_embeddings(model_name)
        
        return Chroma(
            collection_name=collection_name,
            client=self._client,
            persist_directory=self.persist_directory,
            embedding_function=embeddings
        )
    
    def list_collections(self):
        """List all available collections"""
        return [col.name for col in self._client.list_collections()]
    
    def delete_collection(self, collection_name: str):
        """Delete a collection"""
        try:
            self._client.delete_collection(name=collection_name)
            return True
        except:
            return False