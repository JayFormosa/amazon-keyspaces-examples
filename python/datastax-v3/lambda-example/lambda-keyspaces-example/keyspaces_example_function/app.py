from cassandra.cluster import Cluster, EXEC_PROFILE_DEFAULT, ConsistencyLevel
from cassandra.policies import RoundRobinPolicy
from ssl import SSLContext, PROTOCOL_TLSv1_2 , CERT_REQUIRED
from cassandra.auth import PlainTextAuthProvider
import boto3
from cassandra_sigv4.auth import SigV4AuthProvider

import json
import os

import base64
from botocore.exceptions import ClientError

aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
aws_session_token = os.environ['AWS_SESSION_TOKEN']

ssl_context = SSLContext(PROTOCOL_TLSv1_2)
ssl_context.load_verify_locations('/opt/certificate/sf-class2-root.crt')
ssl_context.verify_mode = CERT_REQUIRED

# region name wil have to become an envronment variable in the lambda function configuration
auth_provider = SigV4AuthProvider(aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key,
                                  aws_session_token=aws_session_token,
                                  region_name='eu-west-2')
    
# the cluster will have to become an environemtn variable in the lambda function configuration
cluster = Cluster(['cassandra.eu-west-2.amazonaws.com'], ssl_context=ssl_context, auth_provider=auth_provider,
                  port=9142, protocol_version=4, load_balancing_policy=RoundRobinPolicy())
                  
session = cluster.connect()

def lambda_handler(event, context):
    record = json.loads(event['Records'][0]['body'])
    print(record)
    
    # add code here to test for a session
    
    stmt = session.prepare("INSERT INTO securities.dividend_history (symbol, company) VALUES (?, ?)")
    stmt.consistency_level = consistency_level=ConsistencyLevel.LOCAL_QUORUM
    session.execute(stmt, (record['symbol'],record['company']))
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
