import boto3
import json
import requests
from requests_aws4auth import AWS4Auth

region = 'us-east-1' 
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://search-geography-innovation-hg66af3hqcqsvj4pdsll72p4em.us-east-1.es.amazonaws.com/' 
index = 'papers'
url = 'https://' + host + '/' + index + '/_search'

# Lambda execution starts here
def handler(event, context):

    # Put the user query into the query DSL for more accurate search results.
    # Note that certain fields are boosted (^).
    query = {
        "size": 100,
        "query": {
            "multi_match": {
                "query": event['queryStringParameters']['q'],
                "fields": ["fields.paper_title^4", "fields.fos_name^2", "fields.affiliation_name", "fields.author_name"]
            }
        }
    }

    # ES 6.x requires an explicit Content-Type header
    headers = { "Content-Type": "application/json" }

    # Make the signed HTTP request
    r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))

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
