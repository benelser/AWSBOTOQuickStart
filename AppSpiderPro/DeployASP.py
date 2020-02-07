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

ec2 = boto3.resource('ec2', region_name='us-east-2')
client = boto3.client('ec2', region_name='us-east-2')
iam = boto3.client('iam')
ssm_client = boto3.client('ssm', region_name="us-east-2") 

def CreatePreSharedKey(keyname, path):
    if not os.path.exists(path):
        print(f"{bcolors.OKGREEN}Creating %s{bcolors.ENDC}" % path)
        os.mkdir(path)
    os.chdir(path) 
    key_file=f'{path}/{keyname}.pem'
    print(f"{bcolors.WARNING}Attempting to create key{bcolors.ENDC}")
    try:
        key = ec2.create_key_pair(KeyName=keyname)
        print(f"{bcolors.OKGREEN}Creating key name: {keyname} {bcolors.ENDC}")
        print(f"{bcolors.WARNING}Checking to see if: {key_file} exists. {bcolors.ENDC}")
        if not os.path.exists(key_file):
            print(f"{bcolors.FAIL}{key_file} does not exists. {bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}Creating: {key_file}{bcolors.ENDC}")
            outfile = open(key_file, 'w')
            key_pair_out = str(key.key_material)
            print(f"{bcolors.WARNING}Writing key: {keyname} to {key_file} {bcolors.ENDC}")
            outfile.write(key_pair_out)
            os.chmod(key_file, stat.S_IREAD)
    except:
        print(f"{bcolors.OKGREEN}Key name: {keyname} already exists. Make sure you have access to .pem{bcolors.ENDC}")
               
def SecurityGroupExists(SGName):
    try:
        security_groups = ec2.security_groups
        for sg in security_groups.all(): 
            if sg.group_name == SGName:
                return True
            else:
                return False
    except:
        return False
    
def CreateASPSecurityGroup():
    try:
        if not SecurityGroupExists('ASP'):
            print(f"{bcolors.OKGREEN}Creating ASP Security Group{bcolors.ENDC}")
            # Create Security Group autorizing ssh and 3780 to console
            sg = ec2.create_security_group(GroupName='ASP', Description="RDP")
            sg.authorize_ingress(
                IpPermissions=[
                    {
                        'FromPort': 3389,
                        'IpProtocol': 'tcp',
                        'IpRanges': [
                            {
                                'CidrIp': '0.0.0.0/0',
                                'Description': 'console'
                            },
                        ],
                        'ToPort': 3780,
                    },
                ],
            )
        else:
            print(f"{bcolors.OKGREEN}ASP Security Group alrady exists{bcolors.ENDC}")
    except:
        print(f"{bcolors.OKGREEN}ASP Security Group alrady exists{bcolors.ENDC}")

def GetPublicIp(instanceid):
    time.sleep(5)
    os.system('clear')
    print(f"{bcolors.OKGREEN}Fetching public ipv4 address for instance: {instanceid}{bcolors.ENDC}")
    time.sleep(10)
    publicIpv4 = ""
    instances = ec2.instances
    for i in instances.all():
        if i.id == instanceid:
            publicIpv4 += i.public_ip_address
            os.system('clear')
            return publicIpv4

def CreateSSMMangedRole():
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": [
                        "ec2.amazonaws.com"
                    ]
                },
                "Action": [
                    "sts:AssumeRole"
                ]
            }
        ]
    }
    try:
        print(f"{bcolors.WARNING}Checking if SSMManaged Role exists{bcolors.ENDC}")
        role = iam.get_role(RoleName='SSMManaged')
        print(f"{bcolors.OKGREEN}SSMManaged Role FOUND{bcolors.ENDC}")
    except:
        print(f"{bcolors.FAIL}SSMManaged Role could not be found{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}Attempting to create SSMManged Role{bcolors.ENDC}")
        role = iam.create_role(
        Path='/',
        RoleName='SSMManaged',
        AssumeRolePolicyDocument=json.dumps(AssumeRolePolicyDocument)
        ) 
        result = iam.attach_role_policy(RoleName='SSMManaged',PolicyArn='arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore')
        instance_profile = iam.create_instance_profile(InstanceProfileName='SSMManaged',Path='/')
        iam.add_role_to_instance_profile(InstanceProfileName='SSMManaged', RoleName='SSMManaged')
        print(f"{bcolors.OKGREEN}SSMManaged Role was created successfully{bcolors.ENDC}")

def CreateEC2(keypair, path):
    # Read in shell script to execute on startup --runs as root
    if not os.path.exists(f"{path}/install.ps1"):
        print(f"{bcolors.FAIL}install.ps1 not found.{bcolors.ENDC}")
        sys.exit(f"{bcolors.FAIL}install.ps1 needs to be in the same folder as this script.{bcolors.ENDC}")
    os.chdir(path)
    f = open('./install.ps1', encoding='UTF-8')
    startUpScript = f.read()
    print(f"{bcolors.OKGREEN}Creating EC2{bcolors.ENDC}")
    instance = ec2.create_instances(
        ImageId='ami-0833104f83deab338',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.medium',
        KeyName=keypair,
        SecurityGroupIds=[
            'ASP',
        ],
        UserData=startUpScript,
        IamInstanceProfile={
            'Name':'SSMManaged'
        }
    )
    return instance[0].id

def HookUpIAMProfile(i):
    try:
        print(f"{bcolors.OKGREEN}Attempting to connect IAM Role SSMManaged to EC2: {i}{bcolors.ENDC}")
        ip = iam.get_instance_profile(InstanceProfileName="SSMManaged")
        client.associate_iam_instance_profile(IamInstanceProfile={'Arn':ip['InstanceProfile']['Arn']}, InstanceId=i)
        print(f"{bcolors.OKGREEN}Successfully connected IAM Role SSMManaged Role to EC2: {i}{bcolors.ENDC}")
    except:
        print(f"{bcolors.FAIL}SSMManaged Role could not be attached to EC2: {i}{bcolors.ENDC}")

def DisconnectIAMProfile(i):
    try:
        ip = iam.get_instance_profile(InstanceProfileName="SSMManaged")
        associations = client.describe_iam_instance_profile_associations()
        for assoc in associations['IamInstanceProfileAssociations']:
            if assoc['InstanceId'] == i:
                print(f"{bcolors.OKGREEN}Attempting to disconnect IAM Role SSMManaged Role from EC2: {i}{bcolors.ENDC}")
                client.disassociate_iam_instance_profile(AssociationId=assoc['AssociationId'])
                print(f"{bcolors.OKGREEN}Successfully disconnected IAM Role SSMManaged Role from EC2: {i}{bcolors.ENDC}")
    except:
        print(f"{bcolors.FAIL}SSMManaged Role could not be disconnected to EC2: {i}{bcolors.ENDC}")

def WaitForInstance(i):
    time.sleep(5)
    os.system('clear')
    print(f"{bcolors.WARNING}\n\nWaiting for instance: {i} to be ready. You should go grab a coffee{bcolors.ENDC}")
    waiter = client.get_waiter('instance_status_ok')
    waiter.config.max_attempts = 50
    waiter.config.delay = 30
    waiter.wait(InstanceIds=[i])

def Main():
    scriptDir = os.environ['PWD']
    path =f'{os.environ["HOME"]}/.aws'
    keypair_name = "ec2-keypair"
    CreatePreSharedKey(keypair_name, path)
    CreateASPSecurityGroup()
    CreateSSMMangedRole()
    instanceid = CreateEC2(keypair_name, scriptDir)
    WaitForInstance(instanceid)
    publicipv4 = GetPublicIp(instanceid)
    print(f"{bcolors.OKGREEN}\n\nUSING you RDP client connect to {publicipv4}{bcolors.ENDC}")
   
Main()