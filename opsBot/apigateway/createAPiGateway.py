import botostubs, boto3, sys, os, stat, base64, time, json

client = boto3.client('apigateway', region_name='us-east-1')

client.create_rest_api(
    name='test',
    description='Simple regional PetStore API',
    endpointConfiguration={ "types": ["REGIONAL"] }
)

