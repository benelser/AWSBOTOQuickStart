import botostubs, boto3, sys, os, stat, base64, time, json

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

lambdaClient = boto3.client('lambda', region_name='us-east-2')
iam = boto3.client('iam', region_name='us-east-2')
events = boto3.client('events', region_name='us-east-2')

# Add aditional policies as needed 
def CreateLambdaCloudwatchRole():
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": [
                        "lambda.amazonaws.com",
                        'events.amazonaws.com'
                    ],
                },
                "Action": [
                    "sts:AssumeRole"
                ]
            }
        ]
    }
    try:
        print(f"{bcolors.WARNING}Checking if LambdaCloudwatch-ex Role exists{bcolors.ENDC}")
        role = iam.get_role(RoleName='LambdaCloudwatch-ex')
        print(f"{bcolors.OKGREEN}LambdaCloudwatch-ex Role FOUND{bcolors.ENDC}")
        return role['Role']['Arn']
    except:
        print(f"{bcolors.FAIL}LambdaCloudwatch-ex Role could not be found{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}Attempting to create LambdaCloudwatch-ex Role{bcolors.ENDC}")
        role = iam.create_role(
        Path='/',
        RoleName='LambdaCloudwatch-ex',
        AssumeRolePolicyDocument=json.dumps(AssumeRolePolicyDocument)
        ) 
        result = iam.attach_role_policy(RoleName='LambdaCloudwatch-ex',PolicyArn='arn:aws:iam::aws:policy/AWSLambdaFullAccess')
        result = iam.attach_role_policy(RoleName='LambdaCloudwatch-ex',PolicyArn='arn:aws:iam::aws:policy/CloudWatchEventsFullAccess')
        instance_profile = iam.create_instance_profile(InstanceProfileName='LambdaCloudwatch-ex',Path='/')
        iam.add_role_to_instance_profile(InstanceProfileName='LambdaCloudwatch-ex', RoleName='LambdaCloudwatch-ex')
        print(f"{bcolors.OKGREEN}LambdaCloudwatch-ex Role was created successfully{bcolors.ENDC}")
        time.sleep(10)
        return role['Role']['Arn']

# Build lambda package
# Build steps:
# zip lambda_function.zip lambda_function.py
def CreateLambdaFunction(roleArn):
    try:
        print(f"{bcolors.WARNING}Checking if functions exists{bcolors.ENDC}")
        response = lambdaClient.get_function(
        FunctionName='boto3CreatedLambda',
        )
        print(f"{bcolors.OKGREEN}Function FOUND{bcolors.ENDC}")
        return response['Configuration']['FunctionArn']
    except:
        print(f"{bcolors.OKBLUE}Attempting to create lambda function{bcolors.ENDC}")
        response = lambdaClient.create_function(
        FunctionName = 'boto3CreatedLambda',
        Runtime = 'python3.8',
        Role = roleArn,
        Handler = 'lambda_function.myFirstLambda',
        Code = {
            'ZipFile': open('./lambda_function.zip', 'rb').read(),
        },
        Description = 'Lambda Created Via boto3',
        )
        print(f"{bcolors.OKGREEN}Function Created{bcolors.ENDC}")
        return response['FunctionArn']

def CreateCloudWatchRule(name, rateMinutes, description, roleArn, functionArn):
    print(f"{bcolors.OKBLUE}Attempting to create Cloudwatch Rule {name}{bcolors.ENDC}")
    r = None
    try:
        role = events.put_rule(
        Name=name,
        ScheduleExpression=f'rate({rateMinutes} minutes)',
        State='ENABLED',
        Description=description,
        RoleArn=roleArn
        )
        print(f"{bcolors.OKGREEN}Cloudwatch Rule was created successfully.{bcolors.ENDC}")
        r =  role
    except:
        print(f"{bcolors.FAIL}Failed to create Cloudwatch Rule {name}{bcolors.ENDC}")
    try:
        print(f"{bcolors.OKBLUE}Attempting to map lambda to newly created Cloudwatch Rule {name}{bcolors.ENDC}")
        # maps lambda to rule
        response = events.put_targets(
            Rule=name,
            Targets=[
                {
                    'Id': name,
                    'Arn': functionArn
                },   
            ]
        )
        print(f"{bcolors.OKGREEN}Successfully mapped lambda to newly created Cloudwatch Rule {name}{bcolors.ENDC}")
    except Exception as error:
        print(f"{bcolors.FAIL}Failed to map lambda to newly created Cloudwatch Rule {name}{bcolors.ENDC}")
        print(error)
    return r['RuleArn']

def WireCloudWatchRuleToLambdaTrigger(functionArn, ruleArn):
    print(f"{bcolors.OKBLUE}Attempting to wire up Cloudwatch Rule {ruleArn} to lambda{bcolors.ENDC}")
    try:
        lambdaClient.add_permission(
        FunctionName=functionArn, 
        StatementId='CloudwatchLambdaMapping', 
        Action='lambda:InvokeFunction',
        Principal='events.amazonaws.com', 
        SourceArn=ruleArn
        )
        print(f"{bcolors.OKGREEN}Successfully wired up Cloudwatch Rule {ruleArn} to lambda{bcolors.ENDC}")
    except:
        print(f"{bcolors.FAIL}Failed to wire up Cloudwatch Rule to lambda{ruleArn}{bcolors.ENDC}")
        print(error)
       
# Create the role
roleArn = CreateLambdaCloudwatchRole()
# Create lambda
functionArn = CreateLambdaFunction(roleArn)
# Create rule and map lambda
ruleArn = CreateCloudWatchRule('test3', 2, 'My third Test', roleArn, functionArn)
# wire up rule to lambda
WireCloudWatchRuleToLambdaTrigger(functionArn, ruleArn)