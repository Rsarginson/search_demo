import streamlit as st
import singlestoredb as s2
import pandas as pd
import re
import matplotlib.pyplot as plt
import openai
import time

# Usage
api_key = "sk-proj-tKevZTRcxGUMsVYxwyPkT3BlbkFJF7I8EZT84LdAvW27BTmg"

def strip_special_characters(input_string):
    # Define a pattern that matches all non-alphanumeric characters
    pattern = re.compile(r'[^a-zA-Z0-9\s]')
    # Substitute the matched characters with an empty string
    cleaned_string = pattern.sub('', input_string)
    return cleaned_string

def vectorize_text(api_key, text):
    openai.api_key = api_key

    response = openai.Embedding.create(
        model="text-embedding-ada-002",  # or any other suitable model
        input=text
    )
    embedding_vector = response['data'][0]['embedding']
    return embedding_vector

def is_single_word(word):
    # Check if the input matches a single word (no spaces)
    return bool(re.match("^\w+$", word))

## Connection details
def get_db_connection():
    conn = s2.connect(
    host='svc-7376b579-73a5-4640-9a36-b14ad587da17-dml.aws-oregon-3.svc.singlestore.com',
    port='3306',
    user='admin',
    password='SingleStore1!',
    database='ft_demo')
    return conn

## FRONTEND IMPLEMENTATION (streamlit)
def updateTitle(section):
    if section == "Fuzzy Search":
        st.title("Fuzzy Search")
    elif section == "Proximity Search":
        st.title("Proximity Search")
    elif section == "Boosted Search":
        st.title("Boosted Search")
    elif section == "Regex Search":
        st.title("Regex Search")
    elif section == "KNN (no index)":
        st.title("KNN (no index)")
    elif section == "AUTO index":
        st.title("AUTO Index")
    elif section == "ivf_flat":
        st.title("ivf_flat")
    elif section == "ivf_pq":
        st.title("ivf_pq")
    elif section == "ivf_pqfs":
        st.title("ivf_pqfs")
    elif section == "hnsw_flat":
        st.title("hnsw_flat")

st.set_page_config(page_title="Search Demo", layout="wide")

st.sidebar.title("Search Types:")
search_type = st.sidebar.radio("Go to", ["Fulltext Search", "Vector Search", "Hybrid Search"])
if search_type == "Fulltext Search":
    st.title('Text-only Search')
    section = st.selectbox("Go to", ["Fuzzy Search", "Proximity Search", "Boosted Search", "Regex Search"])
elif search_type == "Vector Search":
    st.title('Vector Search')
    section = st.selectbox("Vector Search Algorithm", ["KNN (no index)", "AUTO index", "ivf_flat", "ivf_pq", "ivf_pqfs", "hnsw_flat"])
elif search_type == "Hybrid Search":
    st.title('Hybrid Search')
    section = 'Hybrid Search'
analytics = st.sidebar.radio("Toggle Analytics", ["On", "Off"])
updateTitle(section)

####### FULLTEXT SEARCH UI ########
## Fuzzy Search UI
if (section == "Fuzzy Search"):
    search_term = st.text_input('Enter the word you would like to find matches for')
    if search_term:
        if is_single_word(search_term):
            search_term = strip_special_characters(search_term)
            st.success("Valid input: {}".format(search_term))
        else:
            st.error("Invalid input. Please enter a single word without spaces.")
    edit_number = 1
    checkbox_edit_number = st.checkbox('Custom number of edits?')
    if checkbox_edit_number:
        edit_number = st.number_input('How many edits? (current max: 5)', min_value=1, max_value=5, step=1)
    ## functional once prefix_length is fixed
    checkbox_prefix_length = st.checkbox('Define prefix length?')
    if checkbox_prefix_length:
        prefix_length = st.number_input('How many letters in the prefix? (current max: 5)', min_value=1, max_value=5, step=1)
    # checkbox_transpositions = st.checkbox('Turn off transpositions?')


## Proximity Search UI
proximity_int = 0
if (section == "Proximity Search"):
    search_term = st.text_input('Enter the first term for your search')
    search_term_2 = st.text_input('Enter your second term')
    proximity = st.number_input(f'Set desired proximity', min_value=1, max_value=20,
                                  step=1)

## Boosted Search UI
if (section == "Boosted Search"):
    boost_term = st.text_input('Enter the word or phrase you want to boost')
    if boost_term:
        weight_value = st.slider('Enter the magnitude', min_value=0.1, max_value=10.0, value=1.0, step = 0.1)
        rest_term = st.text_input('Enter the unweighted phrase')

## Regex Search
if (section == "Regex Search"):
    regex = st.text_input('Enter your regular expression to search for')

####### VECTOR SEARCH UI ########
## KNN no index
if (section == "KNN (no index)"):
    search_term = st.text_input('Enter your search term')

## Auto
if (section == "AUTO index"):
    search_term = st.text_input('Enter your search term')

## ivf_flat
if (section == "ivf_flat"):
    search_term = st.text_input('Enter your search term')

## ivf_pq
if (section == "ivf_pq"):
    search_term = st.text_input('Enter your search term')

## ivf_pqfs
if (section == "ivf_pqfs"):
    search_term = st.text_input('Enter your search term')

if (section == "hnsw_flat"):
    search_term = st.text_input('Enter your search term')

##### HYBRID SEARCH UI #####
if (section == "Hybrid Search"):
    search_term = st.text_input('Enter your search term')

## Search functionality
## 'Fuzzy' Search -- Find words close to the given parameter with a ~. roams, foam
def fuzzy_search():
    query = """
        SELECT id, paragraph, MATCH(TABLE vecs) AGAINST (%s) as score
        FROM vecs 
        WHERE MATCH (TABLE vecs) AGAINST (%s)
        ORDER BY score DESC
        LIMIT 10;"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if search_term:
                full_search_term = f'paragraph:{search_term}~{edit_number}'
            elif checkbox_prefix_length and search_term:
                full_search_term = f'paragraph:{search_term}~{edit_number} OPTIONS \'{{"fuzzy_prefix_length": {prefix_length}}}\''
            start_time = time.time()
            st.write(query, (search_term, full_search_term,))
            cursor.execute(query, ('paragraph:' + search_term, full_search_term,))
            end_time = time.time()
            st.write("This took",(end_time - start_time)," seconds.")
            results = cursor.fetchall()
            if results:
                    columns = [desc[0] for desc in cursor.description]  # Extract column names from cursor
                    df = pd.DataFrame(results, columns=columns)
                    st.table(df)
            else:
                    st.write("No results found.")

## Proximity Search -- given two terms, find the sequences in which they occur within n tokens
def proximity_search():
    query = """SELECT id, paragraph, (MATCH (TABLE vecs) AGAINST ('paragraph:{search_term}')) as score
            FROM vecs
            WHERE MATCH (TABLE vecs)
            AGAINST (%s)
            ORDER BY score DESC
            LIMIT 10;"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if search_term and search_term_2:
                full_search_term = f'paragraph:"{search_term} {search_term_2}"~{proximity}'
                start_time = time.time()
                cursor.execute(query, (full_search_term,))
                end_time = time.time()
                st.write("This took",(end_time - start_time)," seconds.")
                st.write(query % full_search_term)
                results = cursor.fetchall()
                if results:
                    columns = [desc[0] for desc in cursor.description]  # Extract column names from cursor
                    df = pd.DataFrame(results, columns=columns)
                    st.table(df)
                else:
                    st.write("No results found.")

## Boosted Search -- given a search term, allow the user to put different weights on tokens. Higher weight = higher priority
def boosted_search():
    query = """SELECT id, paragraph
        FROM vecs
        WHERE MATCH (TABLE vecs)
        AGAINST (%s)
        LIMIT 10;"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if boost_term and rest_term:
                full_search_term = f'paragraph:("{boost_term}"^{weight_value} "{rest_term}")'
                cursor.execute(query, (full_search_term,))
                results = cursor.fetchall()
                st.write(query)
                if results:
                    columns = [desc[0] for desc in cursor.description]  # Extract column names from cursor
                    df = pd.DataFrame(results, columns=columns)
                    st.table(df)
                else:
                    st.write("No results found.")

## regex search function
# * FROM rexsearch1 WHERE MATCH (TABLE rexsearch1) AGAINST ('col1:/[mb]oat/'); 
def regex_search():
    query = """SELECT paragraph
        FROM vecs
        WHERE MATCH (TABLE vecs)
        AGAINST (%s)
        LIMIT 10;"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if regex:
                full_search_term = f'paragraph:/{regex}/'
                cursor.execute(query, (full_search_term,))
                results = cursor.fetchall()
                if results:
                    columns = [desc[0] for desc in cursor.description]  # Extract column names from cursor
                    df = pd.DataFrame(results, columns=columns)
                    st.table(df)
                else:
                    st.write("No results found.")

## VECTOR SEARCH FUNCTIONALITY
## need to vectorize and normalize the search term in order to perform a vector search. functionality works with a correct vector
if search_type == "Vector Search" or search_type == "Hybrid Search":
    embedding_vector = vectorize_text(api_key, search_term)

def knn_search():
    if search_term:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:  
                set_query = f"SET @query_vec = ('{embedding_vector}':>VECTOR(1536):>BLOB);"
                cursor.execute(set_query)
                start_time = time.time()
                cursor.execute("""SELECT id, paragraph, v <*> @query_vec AS score FROM vecs order by score use index () desc LIMIT 5""")
                end_time = time.time()
                st.write("This took",(end_time - start_time)," seconds.")
                results = cursor.fetchall()
                if results:
                    columns = [desc[0] for desc in cursor.description]  # Extract column names from cursor
                    df = pd.DataFrame(results, columns=columns)
                    st.table(df)

def auto_index():
    if search_term:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:  
                set_query = f"SET @query_vec = ('{embedding_vector}':>VECTOR(1536):>BLOB);"
                cursor.execute(set_query)
                start_time = time.time()
                cursor.execute("""SELECT id, paragraph, v <*> @query_vec AS score FROM vecs order by score use index (auto) desc LIMIT 5""")
                end_time = time.time()
                st.write("This took",(end_time - start_time)," seconds.")
                results = cursor.fetchall()
                if results:
                    columns = [desc[0] for desc in cursor.description]  # Extract column names from cursor
                    df = pd.DataFrame(results, columns=columns)
                    st.table(df)

def ivf_flat():
    if search_term:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:  
                set_query = f"SET @query_vec = ('{embedding_vector}':>VECTOR(1536):>BLOB);"
                cursor.execute(set_query)
                start_time = time.time()
                cursor.execute("""SELECT id, paragraph, v <*> @query_vec AS score FROM vecs order by score use index (ivf_flat) desc LIMIT 5""")
                end_time = time.time()
                st.write("This took",(end_time - start_time)," seconds.")
                results = cursor.fetchall()
                if results:
                    columns = [desc[0] for desc in cursor.description]  # Extract column names from cursor
                    df = pd.DataFrame(results, columns=columns)
                    st.table(df)
def ivf_pq():
    if search_term:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:  
                set_query = f"SET @query_vec = ('{embedding_vector}':>VECTOR(1536):>BLOB);"
                cursor.execute(set_query)
                start_time = time.time()
                cursor.execute("""SELECT id, paragraph, v <*> @query_vec AS score FROM vecs order by score use index (ivf_pq) desc LIMIT 5""")
                end_time = time.time()
                st.write("This took",(end_time - start_time)," seconds.")
                results = cursor.fetchall()
                if results:
                    columns = [desc[0] for desc in cursor.description]  # Extract column names from cursor
                    df = pd.DataFrame(results, columns=columns)
                    st.table(df)

def ivf_pqfs():
    if search_term:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:  
                set_query = f"SET @query_vec = ('{embedding_vector}':>VECTOR(1536):>BLOB);"
                cursor.execute(set_query)
                start_time = time.time()
                cursor.execute("""SELECT id, paragraph, v <*> @query_vec AS score FROM vecs order by score use index (iv_pqfs) desc LIMIT 5""")
                end_time = time.time()
                st.write("This took",(end_time - start_time)," seconds.")
                results = cursor.fetchall()
                if results:
                    columns = [desc[0] for desc in cursor.description]  # Extract column names from cursor
                    df = pd.DataFrame(results, columns=columns)
                    st.table(df)

def hnsw_flat():
    if search_term:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:  
                set_query = f"SET @query_vec = ('{embedding_vector}':>VECTOR(1536):>BLOB);"
                cursor.execute(set_query)
                start_time = time.time()
                cursor.execute("""SELECT id, paragraph, v <*> @query_vec AS score FROM vecs order by score use index (hnsw_flat) desc LIMIT 5""")
                end_time = time.time()
                st.write("This took",(end_time - start_time)," seconds.")
                results = cursor.fetchall()
                if results:
                    columns = [desc[0] for desc in cursor.description]  # Extract column names from cursor
                    df = pd.DataFrame(results, columns=columns)
                    st.table(df)

## HYBRID SEARCH FUNCTIONALITY
def hybrid_search():
    if search_term:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:  
                ### set the query vector
                set_query_vec = f"SET @query_vec = ('{embedding_vector}':>VECTOR(1536):>BLOB);"
                cursor.execute(set_query_vec)
                set_query_text = f"SET @query_text = ('paragraph\: ({strip_special_characters(search_term)})')"
                st.write(set_query_text)
                cursor.execute(set_query_text)
                start_time = time.time()
                cursor.execute("""
                            with fts as (
                            SELECT id, paragraph, (MATCH (TABLE vecs) AGAINST (@query_text)) as score
                            FROM vecs WHERE MATCH (TABLE vecs) AGAINST (@query_text) order by score desc LIMIT 5
                            ),
                            vs as (
                                select id, paragraph, v <*> @query_vec as score
                                from vecs
                                order by score use index (auto) desc
                                limit 5
                            )
                        select vs.id,
                            vs.paragraph,
                            .3 * ifnull(fts.score, 0) + .7 * vs.score as hybrid_score,
                            vs.score as vec_score,
                            ifnull(fts.score, 0) as ft_score
                            from fts full outer join vs
                            on fts.id = vs.id
                            order by hybrid_score desc
                        limit 5;""")
                end_time = time.time()
                st.write("This took",(end_time - start_time)," seconds.")
                results = cursor.fetchall()
                if results:
                    columns = [desc[0] for desc in cursor.description]  # Extract column names from cursor
                    df = pd.DataFrame(results, columns=columns)
                    st.table(df)

if section == "Proximity Search":
    proximity_search()
if section == "Fuzzy Search": 
    if (is_single_word(search_term)):
        fuzzy_search()
if section == "Boosted Search":
    boosted_search()    
if section == "Regex Search":
    regex_search()
if section == "KNN (no index)":
    knn_search()
if section == "AUTO index":
    auto_index()
if section == "ivf_flat":
    ivf_flat()
if section == "ivf_pq":
    ivf_pq()
if section == "ivf_pqfs":
    ivf_pqfs()
if section == "hnsw_flat":
    hnsw_flat()
if section == "Hybrid Search":
    hybrid_search()

## nice ##

# hey WAIT a damn minute i actually can commit here!