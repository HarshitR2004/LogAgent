from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from datetime import datetime
from VectorStore import VectorStore
import os
import glob


class Indexer:
    def __init__(self, collection_name: str, model_name: str = "all-MiniLM-L6-v2"):
        self.collection_name = collection_name
        self.model_name = model_name
        self.vector_store = VectorStore.get_instance().get_collection(collection_name, model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        
        # Set data folder path relative to project root
        self.data_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")


    def index(self, file_paths: list[str] = None):
        """Index specific files or all txt files from data folder"""
        if file_paths is None:
            file_paths = glob.glob(os.path.join(self.data_folder, "*.txt"))
        else:
            # Convert relative paths to absolute paths if needed
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            absolute_paths = []
            for path in file_paths:
                if not os.path.isabs(path):
                    # If it's a relative path, join with project root
                    absolute_path = os.path.join(project_root, path)
                else:
                    # If it's already absolute, use as is
                    absolute_path = path
                absolute_paths.append(absolute_path)
            file_paths = absolute_paths
        
        documents = []
        current_time = datetime.now()
        
        for file_path in file_paths:
            try:
                loader = TextLoader(file_path)
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

        if not documents:
            print("No documents to index")
            return

        split_docs = self.text_splitter.split_documents(documents)
        
        for doc in split_docs:
            if doc.metadata is None:
                doc.metadata = {}
            doc.metadata["time"] = current_time.isoformat()
        
        self.vector_store.add_documents(split_docs)
        print(f"Successfully indexed {len(split_docs)} document chunks")

    
if __name__ == "__main__":
    indexer = Indexer(collection_name="devops_incidents_demo")
    
    # Index specific incident files (relative paths automatically handled)
    incident_files = [
        "data\\past_incidents\\incident1.txt",
        "data\\past_incidents\\incident2.txt"
    ]
    
    indexer.index(incident_files)
    print(f"Indexed incident files: {incident_files}")
    
