import urllib.request, json, encodings, ssl, gzip, botostubs, boto3, sys, os, stat, base64, time
from getpass import getpass
from urllib.parse import urlencode, quote_plus

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

def CreateCollectorSecurityGroup():
    if not SecurityGroupExists('Collector'):
        print(f"{bcolors.OKGREEN}Creating Collector Security Group{bcolors.ENDC}")
        try:
            sg = ec2.create_security_group(GroupName='Collector', Description="Collector to Insight Platform")
            sg.authorize_ingress(
                IpPermissions=[
                {'IpProtocol': '-1',
                'FromPort': 0,
                'ToPort': 65535,
                'IpRanges': [{'CidrIp': '0.0.0.0/0','Description': 'Temporary inbound rule for Guardrail Testing'}]}
            ])
        except:
            print(f"{bcolors.OKGREEN}Collector Security Group alrady exists{bcolors.ENDC}")
    else:
        print(f"{bcolors.OKGREEN}Collector Security Group alrady exists{bcolors.ENDC}")

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
    print(f"{bcolors.OKGREEN}Creating EC2{bcolors.ENDC}")
    instance = ec2.create_instances(
        ImageId='ami-0fc20dd1da406780b',
        MinCount=1,
        MaxCount=1,
        InstanceType='m5.large',
        KeyName=keypair,
        SecurityGroupIds=[
            'Collector',
        ],
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
    waiter.wait(InstanceIds=[i])

def get_user_input(selection):
    if selection == 1:
        answer = "n"
        while answer != 'y':
            os.system("clear")
            org = input("Enter Rapid7 Insight Platform Organization Name:\n")
            answer = input(f"Is {org} correct y/n\n")
        return org
    if selection == 2:
        answer = "n"
        while answer != 'y':
            os.system("clear")
            email = input("Enter Rapid7 Insight Platform email:\n")
            answer = input(f"Is {email} correct y/n\n")
        return email
    if selection == 3:
        os.system("clear")
        return getpass("Enter Rapid7 Insight Platform password:\n")

def pair_collector(i, email, password, organization):
    cmd = f'python3 ipims_client.py --email "{email}" --password "{password}" --organization "{organization}" --hostname $(curl -s http://169.254.169.254/latest/meta-data/public-hostname)'
    response = ssm_client.send_command(
        InstanceIds=[
            i,
            ],
        DocumentName="AWS-RunShellScript",
        Parameters={
            'commands':[
                'cd /opt',
                'sudo apt-get update -y && apt-get upgrade -y;',
                'wget https://github.com/benelser/AWSBOTOQuickStart/blob/master/InsightIDR/InsightSetup-Linux64.tar.gz?raw=true -O ./InsightSetup-Linux64.tar.gz && sudo tar -C /opt -xf ./InsightSetup-Linux64.tar.gz && sudo chmod 755 /opt/InsightSetup-Linux64.sh && sudo /opt/InsightSetup-Linux64.sh -q;',
                'AGENT_KEY_FILE=/opt/rapid7/collector/agent-key/Agent_Key.html;',
                'if test -f "$AGENT_KEY_FILE"; then sudo cat "$AGENT_KEY_FILE" | cut -d " " -f 4 | cut -d ">" -f2 | cut -d "<" -f1 > /opt/rapid7/collector/agent-key/Agent_Key.txt; fi;',
                'git clone https://github.com/benelser/IPIMSClient.git;',
                'cd IPIMSClient/;',
                './bootstrap.sh 1',
                cmd,
            ]
        }
    )
    
    command_id = response['Command']['CommandId']
    return command_id

def Main():
    organization = get_user_input(1)
    email = get_user_input(2)
    password = get_user_input(3)
    scriptDir = os.environ['PWD']
    path =f'{os.environ["HOME"]}/.aws'
    keypair_name = "ec2-keypair"
    CreatePreSharedKey(keypair_name, path)
    CreateCollectorSecurityGroup()
    CreateSSMMangedRole()
    instanceid = CreateEC2(keypair_name, scriptDir)
    WaitForInstance(instanceid)
    publicipv4 = GetPublicIp(instanceid)
    pair_collector(instanceid, email, password, organization)
    print(f'{bcolors.OKGREEN}\nssh -i "~/.aws/ec2-keypair.pem" ubuntu@{publicipv4} {bcolors.ENDC}')
   
Main()