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

def getConsoleCookie(console_url):
    req = urllib.request.Request(url=f"{console_url}/login.jsp", method='GET')
    req.add_header('Content-Type', 'application/json')
    gcontext = ssl.SSLContext()
    response = urllib.request.urlopen(req, context=gcontext)
    headers = response.getheaders()
    cookie = headers[5][1].split("=")[1].split(";")[0]
    return cookie

def getConsoleSessionCookie(consoleCookie, uname, pw, console_url):
    body = {
        "screenresolution": '1920x1080', 
        "nexposeccusername" : uname,
        "nexposeccpassword" : pw
    }
    encodedParams = urlencode(body, quote_via=quote_plus).encode('utf-8')
    req = urllib.request.Request(url=f"{console_url}/data/user/login", method='POST')
    req.add_header('Accept', 'application/json, text/javascript, */*; q=0.01')
    req.add_header('X-Requested-With', 'XMLHttpRequest')
    req.add_header('Accept-Language', 'en-us')
    req.add_header('Accept-Encoding', 'gzip, deflate')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    req.add_header('Orgin', console_url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15')
    req.add_header('Connection', 'close')
    req.add_header('Referer', console_url)
    req.add_header('Content-Length', len(encodedParams))
    req.add_header('Cookie', f"nexposeCCSessionID={consoleCookie}")
    gcontext = ssl.SSLContext()
    response = urllib.request.urlopen(req, bytes(encodedParams), context=gcontext)
    headers = response.getheaders()
    cookie = headers[4][1].split("=")[1].split(";")[0]
    return cookie

def getScanEnginePairingKey(sessionCookie, console_url):
    req = urllib.request.Request(url=f"{console_url}/data/admin/global/shared-secret?time-to-live=3600", method='PUT')
    req.add_header('Accept', 'application/json, text/javascript, */*; q=0.01')
    req.add_header('nexposeCCSessionID', sessionCookie)
    req.add_header('X-Requested-With', 'XMLHttpRequest')
    req.add_header('Accept-Language', 'en-us')
    req.add_header('Accept', '*/*')
    req.add_header('Orgin', console_url)
    req.add_header('Content-Length', 0)
    req.add_header('Accept-Encoding', 'gzip, deflate')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    req.add_header('Connection', 'close')
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15')
    req.add_header('Cookie', f"nexposeCCSessionID={sessionCookie}; time-zone-offset=360;  i18next=en-US")
    gcontext = ssl.SSLContext()
    response = urllib.request.urlopen(req, context=gcontext)
    if response.info().get('Content-Encoding') == 'gzip':
        content = gzip.decompress(response.read())
        jsonString = content.decode('utf8')
        data = json.loads(jsonString)
        return data['keyString']
    else:
        result = json.loads(response.read().decode('utf-8'))
        return result['keyString']

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

def CreateScanEngineSecurityGroup():
    if not SecurityGroupExists('ScanEngine'):
        print(f"{bcolors.OKGREEN}Creating ScanEngine Security Group{bcolors.ENDC}")
        # Create Security Group autorizing ssh and 80 to console
        sg = ec2.create_security_group(GroupName='ScanEngine', Description="ScanEngine_Connectivity")
        sg.authorize_ingress(
            IpPermissions=[
                {
                    'FromPort': 22,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'ssh'
                        },
                    ],
                    'ToPort': 22,
                },
                {
                    'FromPort': 80,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'http'
                        },
                    ],
                    'ToPort': 80,
                },
            ],
        )
    else:
        print(f"{bcolors.OKGREEN}ScanEngine Security Group alrady exists{bcolors.ENDC}")

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

def GetConsoleSecret(publicip, privateip, port, uname, pw):
    console_url = f"https://{publicip}:{port}"
    try:
        cookie  = getConsoleCookie(console_url)
        sessionCookie = getConsoleSessionCookie(cookie, uname, pw, console_url)
        key = getScanEnginePairingKey(sessionCookie, console_url)
        userData = f"""
NEXPOSE_CONSOLE_HOST={privateip}
NEXPOSE_CONSOLE_PORT=40815
NEXPOSE_CONSOLE_SECRET={key}
"""
        return userData
    except :
        print(f"{bcolors.FAIL}Failed to retrieve shared secret from: {console_url}{bcolors.ENDC}")
        return False
    

def CreateEC2(keypair, path, userdata):
    print(f"{bcolors.OKGREEN}Creating EC2{bcolors.ENDC}")
    instance = ec2.create_instances(
        ImageId='ami-08eb0e768c488fef4',
        MinCount=1,
        MaxCount=1,
        InstanceType='m5.large',
        KeyName=keypair,
        # SecurityGroupIds=[
        #     'ScanEngine',
        # ],
        UserData=userdata,
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

def Main():
    scriptDir = os.environ['PWD']
    path =f'{os.environ["HOME"]}/.aws'
    keypair_name = "ec2-keypair"
    CreatePreSharedKey(keypair_name, path)
    #CreateScanEngineSecurityGroup()
    CreateSSMMangedRole()
    # First time password is the instance id // This script is dependent on the console online and basic username/passwprd has been changed
    userdata = GetConsoleSecret("IPADD", "IPADD", "3780", "nxadmin", "ecadmin")
    print(userdata)
    if userdata != False:
        instanceid = CreateEC2(keypair_name, scriptDir, userdata)
        WaitForInstance(instanceid)
        publicipv4 = GetPublicIp(instanceid)
        print(f'{bcolors.OKGREEN}\nCheck your console to see if scan engine: {publicipv4} paired{bcolors.ENDC}')
   
Main()