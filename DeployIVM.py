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

def KeyPairExist(name):
    try:
        ec2.KeyPair(name)
        return True
    except:
        return False

def CreatePreSharedKeyFile(f, name):
    outfile = open(f, 'w')
    key_pair = ec2.create_key_pair(KeyName=name)
    key_pair_out = str(key_pair.key_material)
    outfile.write(key_pair_out)
    os.chmod(f, stat.S_IREAD)

def SetUpEnv(path):
    if not os.path.exists(path):
        print(f"{bcolors.OKGREEN}Creating %s{bcolors.ENDC}" % path)
        os.mkdir(path)
    os.chdir(path) 

def CreatePreSharedKey(keyname, path):
    key_file=f'{path}/{keyname}.pem'
    if not os.path.exists(key_file):
        # call the boto ec2 function to create a key pair
        try:
            print(f"{bcolors.WARNING}Attempting to create key{bcolors.ENDC}")
            if not KeyPairExist(keyname):
                CreatePreSharedKeyFile(key_file, keyname)
            else: 
                print(f"{bcolors.OKGREEN}Key: {keyname} alraedy exists{bcolors.ENDC}")
        except:
            sys.exit(f"{bcolors.FAIL}Something went wrong while attempting to create pre-shared key.{bcolors.ENDC}")
    else:
        print(f"{bcolors.OKGREEN}{keyname} at {key_file} already exists. Continuing deployment{bcolors.ENDC}")

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