import json
import pandas as pd
from collections import defaultdict
from flask import Flask, request
from flask_cors import CORS
from datetime import datetime

from infra.LRUCache import LRUCache

print(0)
from core_algorithms.query_expansion import get_query_extension
from core_algorithms.ir_eval.ranking import ranking_query_tfidf as ranking_query_tfidf_dataset
from core_algorithms.ir_eval.ranking_paper import ranking_query_tfidf as ranking_query_tfidf_paper
from core_algorithms.ir_eval.ranking_paper import phrase_search as phrase_search_paper
from core_algorithms.ir_eval.ranking import phrase_search as phrase_search_dataset
from core_algorithms.ir_eval.ranking_paper import proximity_search as proximity_search_paper
from core_algorithms.ir_eval.ranking import proximity_search as proximity_search_dataset
from core_algorithms.mongoDB_API import MongoDBClient
from core_algorithms.ir_eval.preprocessing import preprocess

print(0.1)
import scann
from sentence_transformers import SentenceTransformer
app= Flask(__name__)
CORS(app)
print(0.2)
# json_boi = open('example.json')

# test_json = json.load(json_boi)

# print(test_json.keys())
# @app.route("/test", methods=['GET', 'POST'])
# def test():
#     print("in_test")
#     return test_json

# Load paper index
searcher = scann.scann_ops_pybind.load_searcher('/home/stylianosc/scann/papers/')
print(0.3)
# Load transformer encoder
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load paper indices
df_papers = pd.read_csv("/home/stylianosc/scann/papers/df.csv")


client = MongoDBClient("34.142.18.57") # (this is an example)
_preprocessing_cache = LRUCache(1000)
_results_cache = LRUCache(200)

_today = datetime.today().strftime('%d/%m/%Y')
_no_match_sample = {"title": "No Matching Documents Were Found", "abstract": "Try expanding your query with our search suggestion", "url":"", "authors":"","date":_today}
_no_results_dict = {"Results": [_no_match_sample]}

## Create DB instance


def author_search(query):
    pass

@app.route("/<query>", methods = ['POST', 'GET'])
def search(search_query):


    parameters = _deseralize(search_query)
    # {
    # query: search_query : DOME
    # from_date: DD-MM-YYYY (last) : 
    # to_date: DD-MM-YYYY :  
    # Authors: [str1, str2] : DONE
    # search_type: str (default, proximity, phrase, author) : DONE
    # algorithm: str (approx_nn, bm25, tf-idf) : DONE
    # result_type: str
    # datasets: bool
    # }

    ## search_type
    ### algorithm_type
    ### 

    if parameters["search_type"] == "author":

        if parameters["datasets"]:
            results = author_search_papers(parameters['query'])
        else:
            results = author_search_datasets(parameters['query'])

    elif parameters["search_type"] == "PHRASE":

        if parameters["datasets"]:
            results = phrase_search_dataset(parameters['query'])
        else:
            results = phrase_search_paper(parameters['query'])

    elif parameters["search_type"] == "PROXIMITY":
        if parameters["datasets"]:
            results = proximity_search_dataset(parameters['query'])
        else:
            results = proximity_search_paper(parameters['query'])
    elif parameters["search_type"] == "DEFAULT":

        if parameters["datasets"]:

            if parameters["algorithm"] == "APPROX_NN":
                results = approx_nn_search_datasets(parameters['query'])
            elif parameters["algorithm"] == "BM25":
                results = bm25_search_datasets(parameters['query'])
            elif parameters["algorithm"] == "TF_IDF":
                results = tf_idf_search_datasets(parameters['query'])
        
        else:

            if parameters["algorithm"] == "APPROX_NN":
                results = approx_nn_search_datasets(parameters['query'])
            elif parameters["algorithm"] == "BM25":
                results = bm25_search_datasets(parameters['query'])
            elif parameters["algorithm"] == "TF_IDF":
                results = tf_idf_search_datasets(parameters['query'])

    # results = filter_dates(results, parameters["start_date"], parameters["end_date"])
    return results



    


@app.route("/QE/<query>", methods=['GET', 'POST'])
def query_expansion(query):

    expanded_queries = list(get_query_extension(query))
    if not expanded_queries:
        return {"QEResults": ["No matching synonyms were found!", ""]}
    else:
        expanded_queries = ", ".join(expanded_queries)
        return {"QEResults": [expanded_queries, ""]}

# # def deserialize(query: str) -> dict:
# #     """


# #     """
# #     return {"test": "test"}


#@app.route("/<query>", methods = ['POST', 'GET'])
#def get_papers_results(query: str) -> dict:
    """
    Input: query (type: string)
    Output: Dictionary (HashMap)
    Output Format:
    { Results:[internal_dict] }
    internal_dict format:
    {
        title: string,
        abstract: string,
        authors: array of strings or empty array,
        url: string
        ...
        any other information
    }
    """
#    print("2.1 - query")
#    print(query)
#    cached_results = _results_cache.get(query)

#    if cached_results != -1:
#        return cached_results

#    query_params = _preprocess_query(query)
#    scores = ranking_query_tfidf_paper(query_params, client)

#    output_dict = {"Results":[]}
#    for result in scores[:10]:
#        output = client.get_one(data_type='paper', filter={'_id':result[0]}, fields=['title', 'abstract','authors', 'url', 'date'])
#        output_dict["Results"].append(output)
#
#    _results_cache.put(query, output_dict)
#
#    if len(output_dict['Results']) == 0:
#        return _no_results_dict
#    else: return output_dict
#print(1)
# @app.route("/QE/<query>", methods=['GET', 'POST'])

@app.route("/<query>", methods = ['POST', 'GET'])
def get_papers_results_deep(query: str) -> dict:
    """
    This is used when the user provides the query & wants to query different papers.
    Input: query (type: string)
    Example: "covid" or "covid vaccine"
    Output: Dictionary (HashMap)
    Format:
    {
        title: string,
        abstract/description: string,
        authors: array of strings or empty array,
        url: string
        ...
        any other information
    } 
    """
    print("in pog")
    query = model.encode(query, convert_to_tensor=True)
    neighbors, distances = searcher.search(query, final_num_neighbors=100)
    neighbors = list(reversed(neighbors))
    print("t1")
    output_dict = {"Results":[]}

    for i in neighbors[:100]:
        id = str(df_papers.iloc[i]._id)
        output = client.get_one(data_type='paper', filter={'_id':id}, fields=['title', 'abstract','authors', 'url', 'date'])
        output_dict["Results"].append(output)

    return output_dict

print(2)
@app.route("/dataset/<query>", methods = ['POST', 'GET'])
def get_dataset_results(query: str) -> dict:
    """
    Input: query (str)
    Output: dict
    """
    cached_results = _results_cache.get(query)

    if cached_results != -1:
        return cached_results

    processed_query = _preprocess_query(query)

    scores = ranking_query_tfidf_dataset(processed_query, client)
    output_dict = {"Results":[]}

    for result in scores[:10]:
        output = client.get_one(data_type='dataset', filter={'_id':result[0]}, fields=['title', 'abstract','authors', 'url', 'date'])
        output_dict["Results"].append(output)

    _results_cache.put(query, output_dict)

    if len(output_dict['Results']) == 0:
        return _no_results_dict
    else: return output_dict

@app.route("/papers/proximity/<query>", methods = ['POST', 'GET'])
def get_proximity_papers_results(query: str, proximity=10) -> dict:
    """
    By default, this function get the result of proximity=10
    Input: query (type: string)
    Example: "covid" or "covid vaccine"

    Output: Dictionary (HashMap)
    Format:
    {
        title: string,
        abstract/description: string,
        authors: array of strings or empty array,
        url: string
        ...
        any other information
    } 
    """
    query = preprocess(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    # Don't worry about input parsing. Use query_params for now.
    outputs = proximity_search_paper(query_params, client, proximity=proximity) # return: list of ids of paper
    output_dict = {"Results":[]}
    for result in outputs[:10]:
        output = client.get_one(data_type='paper', filter={'_id':result}, fields=['title', 'abstract','authors', 'url', 'date'])
        output_dict["Results"].append(output)
    
    return output_dict
print(3)
def get_phrase_papers_results(query: str) -> dict:
    """
    This is used when the user provides the query & wants to query different papers.
    This function is using phrase search, not ranking algorithm
    Input: query (type: string)
    Example: "covid" or "covid vaccine"

    Output: Dictionary (HashMap)
    Format:
    {
        title: string,
        abstract/description: string,
        authors: array of strings or empty array,
        url: string
        ...
        any other information
    }
    """
    query = preprocess(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    # Don't worry about input parsing. Use query_params for now.
    outputs = phrase_search_paper(query_params, client) # return: list of ids of paper
    output_dict = {"Results":[]}
    for result in outputs[:10]:
        output = client.get_one(data_type='paper', filter={'_id':result}, fields=['title', 'abstract','authors', 'url', 'date'])
        output_dict["Results"].append(output)
    
    return output_dict

def get_phrase_datasets_results(query: str) -> dict:
    """
    Input: query (type: string)
    Example: "covid" or "covid vaccine"

    Output: Dictionary (HashMap)
    Format:
    {
        title: string,
        abstract/description: string,
        authors: array of strings or empty array,
        url: string
        ...
        any other information
    } 
    """
    query = preprocess(query,True, True) # stemming, removing stopwords
    query_params = {'query': query}
    
    # These parts (getting dataset info like subtitle) must be changed to mongodb in the future
    kaggle_df = pd.read_csv('core_algorithms/ir_eval/kaggle_dataset_df_page500.csv')
    kaggle_df['Source'] = 'Kaggle'
    paperwithcode_df = pd.read_csv('core_algorithms/ir_eval/paperwithcode_df.csv')
    paperwithcode_df['Source'] = 'Paper_with_code'
    df = pd.concat([kaggle_df, paperwithcode_df])
    df = df.reset_index(drop=True)
    
    # Don't worry about input parsing. Use query_params for now.
    outputs = phrase_search_dataset(query_params) # return: list of ids of paper
    output_dict = {"Results":[]}
    for result in outputs[:10]:
        output = df.iloc[result][['title','subtitle','description']].to_dict()
        output_dict['Results'].append(output)
    return output_dict

def _preprocess_query(query: str) -> dict:
    """
    Input: query (str)
    Output: dict
    Helper function to preprocess queries efficiently with local cache.
    """
    cached_data = _preprocessing_cache.get(query)
    query_params = None
    if cached_data != -1:
        query_params = cached_data
    else:
        query_params = preprocess(query, True, True) # stemming, removing stopwords
        query_params = {'query': query_params}
        _preprocessing_cache.put(query, query_params)

    return query_params

@app.route("/")
def hello_world():
    return "Change PORT to 3000 to access the React frontend!"



# if __name__ == "__main__":
#     pass
