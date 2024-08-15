from elasticsearch_serverless import Elasticsearch
import time
import boto3
from botocore import UNSIGNED
from botocore.client import Config
from elasticsearch import Elasticsearch, helpers

from elasticsearch_serverless import Elasticsearch

client = Elasticsearch(
  "https://cf8df7584e9a403a98204b20debfcb3b.es.us-west-2.aws.elastic.cloud:443",
  api_key="aGNma1VaRUJOYUZsM3RheTduRl86emk3M3B2OEpRblN4WTBsS1JGU2Y1UQ=="
)

client.info()

# # Initialize the S3 and Elasticsearch clients
# s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
# es = Elasticsearch(
#     hosts=["https://2a86c5a3e9174d4299ab6718cf3993be.us-east-2.aws.elastic-cloud.com"],
#       http_auth=('rsarginson@singlestore.com', 'Supdude02!'))

# # S3 bucket and file details
# bucket_name = 'fulltextdemo'
# file_key = 'news-discuss-v1.en.txt'

# # Initialize a list to hold the documents
# documents = []

# # Read and process the file line by line
# s3_object = s3.get_object(Bucket=bucket_name, Key=file_key)
# streaming_body = s3_object['Body']

# for idx, line in enumerate(streaming_body.iter_lines()):
#     # Assuming each line is a document, customize as needed
#     document = {
#         "_index": "fts_index",
#         "_source": {"content": line.decode('utf-8')}
#     }
#     documents.append(document)

#     # Bulk index every 1000 documents (tune this number based on your needs)
#     if len(documents) >= 1000:
#         helpers.bulk(es, documents)
#         documents = []

# # Index any remaining documents
# if documents:
#     helpers.bulk(es, documents)

# print("Data has been successfully ingested into Elasticsearch.")

