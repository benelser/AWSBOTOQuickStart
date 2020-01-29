import botostubs, boto3, sys, os, stat, base64, time

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
        
def SetUpEnv(path):
    if not os.path.exists(path):
        print(f"{bcolors.OKGREEN}Creating %s{bcolors.ENDC}" % path)
        os.mkdir(path)
    os.chdir(path) 

def CreatePreSharedKey(keyname, path):
    key_file=f'{path}/{keyname}.pem'
    # call the boto ec2 function to create a key pair
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
    
def CreateInsightVMSecurityGroup():

    if not SecurityGroupExists('InsightVM'):
        print(f"{bcolors.OKGREEN}Creating InsightVM Security Group{bcolors.ENDC}")
        # Create Security Group autorizing ssh and 3780 to console
        sg = ec2.create_security_group(GroupName='InsightVM', Description="Console/Engine_Connectivity")
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
                    'FromPort': 3780,
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
        print(f"{bcolors.OKGREEN}InsightVM Security Group alrady exists{bcolors.ENDC}")

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

def CreateEC2(keypair, path):
    # Read in shell script to execute on startup --runs as root
    if not os.path.exists(f"{path}/startup.sh"):
        print(f"{bcolors.FAIL}startup.sh not found.{bcolors.ENDC}")
        sys.exit(f"{bcolors.FAIL}Startup.sh needs to be in the same folder as this script.{bcolors.ENDC}")

    f = open('./startup.sh', encoding='ascii')
    startUpScript = f.read()
    print(f"{bcolors.OKGREEN}Creating EC2{bcolors.ENDC}")
    instance = ec2.create_instances(
        ImageId='ami-0d5d9d301c853a04a',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.medium',
        KeyName=keypair,
        SecurityGroupIds=[
            'InsightVM',
        ],
        UserData=startUpScript,
    )
    return instance[0].id
    
def Main():
    path =f'{os.environ["HOME"]}/.aws'
    keypair_name = "ec2-keypair"
    SetUpEnv(path)
    CreatePreSharedKey("ec2-keypair", path)
    CreateInsightVMSecurityGroup()
    instanceid = CreateEC2(keypair_name, path)
    publicipv4 = GetPublicIp(instanceid)
    print(f"{bcolors.OKGREEN}\n\nUSING your browser navigate to:\n\thttps://{publicipv4}:3780{bcolors.ENDC}")

Main()