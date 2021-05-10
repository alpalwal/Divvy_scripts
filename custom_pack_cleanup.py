# Script to list all organizations in DivvyCloudf
import json
from botocore.vendored import requests
import boto3
#from collections import defaultdict
import os
from base64 import b64decode

requests.packages.urllib3.disable_warnings() # verify=False throws warnings otherwise

def lambda_handler(event, context):
    # API URL
    base_url = "https://sales-demo.divvycloud.com"

    username = os.environ['USERNAME']
    
    ENCRYPTED = os.environ['PASSWORD']
    # Decrypt code should run once and variables stored outside of the function
    # handler so that these are decrypted once per container
    password = boto3.client('kms').decrypt(
        CiphertextBlob=b64decode(ENCRYPTED),
        EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']}
    )['Plaintext'].decode('utf-8')
    
    login_url = base_url + '/v2/public/user/login'

    # Shorthand helper function
    def get_auth_token():
        response = requests.post(
            url=login_url,
            data=json.dumps({"username": username, "password": password}),
            headers={
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': 'application/json'
            })
        return response.json()['session_id']
    auth_token = get_auth_token()

    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json',
        'X-Auth-Token': auth_token
    }

    def get_packs():
        data = {}
        response = requests.get(
            url=base_url + '/v2/public/insights/packs/list',
            data=json.dumps(data),
            verify=False,
            headers=headers
            )
        return response.json()    


    def delete_pack(pack_id):
        data = {}
        response = requests.delete(
            url=base_url + '/v2/public/insights/pack/' + str(pack_id) + '/delete',
            data=json.dumps(data),
            verify=False,
            headers=headers
            )
        return response #.json()    


    for pack in get_packs():
        if pack["source"] == "custom":
            if "-keep" in pack['name'] or "- keep" in pack['name']: # keep packs with "keep" in the name
                continue
            
            if pack['inserted_at'] < "2021-03-01T16:00:00Z": # keep old packs
                continue

            print("Deleting old pack. Pack name: " + pack['name'])
            print(delete_pack(pack['pack_id']))

            
            