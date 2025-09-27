from elasticsearch import Elasticsearch

class ESClient:
    def __init__(self, index_name,es_host="http://localhost:9200"):
        self.es = Elasticsearch([es_host])
        self.index_name = index_name

        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name)
        else:
            print(f"Using existing index: {self.index_name}")

    def store_log(self, log: dict):
        """Store log in Elasticsearch"""
        try:
            self.es.index(index=self.index_name, document=log)
        except Exception as e:
           raise RuntimeError(f"Failed to store log: {e}")


