"""
to update deployment
zip es_search_deployment.zip search.py

aws --profile innogeo lambda update-function-code --function-name search_es --zip-file fileb://es_search_deployment.zip
"""
import base64
import boto3
import json
import os
import requests
from requests_aws4auth import AWS4Auth

region = 'us-east-1' 
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'search-geography-innovation-hg66af3hqcqsvj4pdsll72p4em.us-east-1.es.amazonaws.com' 
# index = 'papers'
url = 'https://' + host + '/_search'

# Lambda execution starts here
def handler(event, context):

    # Put the user query into the query DSL for more accurate search results.
    # Note that certain fields are boosted (^).
    print(event)
    if "queryStringParameters" in event:
        query = {
            "size": 100,
            "query": {
                "multi_match": {
                    "query": event['queryStringParameters']['q'],
                    "fields": ["paper_title^4", "fos_name^2", "affiliation_name", "author_name"]
                }
            }
        }
    else:
        if event.get("isBase64Encoded", False):
            data = json.loads(base64.b64decode(event["body"]))
        else:
            data = json.loads(event["body"])
        print(data)
        query = {
            "size": data["size"],
            "query": data["query"]
        }

    # ES 6.x requires an explicit Content-Type header
    headers = { "Content-Type": "application/json" }

    # Make the signed HTTP request
    auth = (os.environ["ES_USER"], os.environ["ES_PW"])
    r = requests.post(url, auth=auth, headers=headers, data=json.dumps(query))

    # Create the response and add some extra content to support CORS
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }

    # Add the search results to the response
    response['body'] = r.text
    return response
