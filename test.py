import openai
import json
import singlestoredb as s2
import sqlalchemy as sa


def vectorize_text(api_key, text):
    openai.api_key = api_key

    response = openai.Embedding.create(
        model="text-embedding-ada-002",  # or any other suitable model
        input=text
    )

    embedding_vector = response['data'][0]['embedding']
    return embedding_vector

# Usage
api_key = "sk-proj-tKevZTRcxGUMsVYxwyPkT3BlbkFJF7I8EZT84LdAvW27BTmg"
user_input = "Tell me about first person shooters"
embedding_vector = vectorize_text(api_key, user_input)
print("Embedding vector:", embedding_vector)

def get_db_connection():
    conn = s2.connect(
    host='svc-7376b579-73a5-4640-9a36-b14ad587da17-dml.aws-oregon-3.svc.singlestore.com',
    port='3306',
    user='admin',
    password='SingleStore1!',
    database='ft_demo')
    return conn