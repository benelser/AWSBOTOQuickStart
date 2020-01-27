import botostubs, boto3

s3 = boto3.client('s3') # type: botostubs.S3
s3.create_bucket(Bucket="myboto3createdbucket")
response = s3.list_buckets()
print("Existing S3 buckets....")

# Repsonse is of type dict
for bucket in response['Buckets']:
    print(f'{bucket["Name"]}')
