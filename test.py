from elasticsearch_serverless import Elasticsearch

client = Elasticsearch(
    'https://c6a6bda1758f4b9bb0517c731e9f6f97.es.us-east-1.aws.elastic.cloud:443',
    api_key="MzgxVkNwRUJVRzZDTDRITnJqcGw6UDN3MGVtaXVRSDZkMGk1MWJ5XzZXUQ=="
)

client.info()