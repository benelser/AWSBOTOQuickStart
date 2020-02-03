import json

# handler function reference name: lambda_function.myFirstLambda (which is the combo of the script name and the handler function)
# Runtime 3.8
# usees test even with event structure 
# {
#   "Name": "Benjamin",
#   "Age": 32,
#   "Food": "Pizza"
# }

def myFirstLambda(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps("Event Has been fired via cloudwatch scheduled job")
    }