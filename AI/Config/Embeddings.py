from langchain_huggingface import HuggingFaceEmbeddings

class Embeddings:
    """Singleton class to manage the embeddings model instance."""
    _embeddings = None

    @classmethod
    def get_embeddings(cls, model_name):
        if cls._embeddings is None:
            cls._embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                encode_kwargs={"normalize_embeddings": True}
            )
        return cls._embeddings