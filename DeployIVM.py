import botostubs, boto3, sys, os, stat, base64

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
        print("Creating %s" % path)
        os.mkdir(path)
    os.chdir(path) 

def CreatePreSharedKey(keyname, path):
    key_file=f'{path}/{keyname}.pem'
    if not os.path.exists(key_file):
        # call the boto ec2 function to create a key pair
        try:
            print("Attempting to create key")
            if not KeyPairExist(keyname):
                CreatePreSharedKeyFile(key_file, keyname)
            else: 
                print(f"Key: {keyname} alraedy exists")
        except:
            sys.exit("Something went wrong while attempting to create pre-shared key.")
    else:
        print(f"{keyname} at {key_file} already exists. Continuing deployment")

def SecurityGroupExists(SGName):
    try:
        ec2.SecurityGroup(id=SGName)
        return True
    except:
        return False
    
def CreateInsightVMSecurityGroup():

    if not SecurityGroupExists('InsightVM'):
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
        return sg.group_id
    else:
        print("InsightVM Security Group alrady exists")

def CreateEC2(keypair):
    # Read in shell script to execute on startup --runs as root
    if not os.path.exists(f"{path}/startup.sh"):
        print("startup.sh not found. Attempting to pull down....")
        sys.exit("Startup.sh needs to be in the same folder as this script.")

    f = open('./startup.sh', encoding='ascii')
    startUpScript = f.read()
    print("Creating EC2")
    """ instances = ec2.create_instances(
        ImageId='ami-0d5d9d301c853a04a',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName=keypair,
        SecurityGroupIds=[
            'InsightVM',
        ],
        UserData=startUpScript,
    ) """

def Main():
    path =f'{os.environ["HOME"]}/.aws'
    keypair_name = "ec2-keypair"
    SetUpEnv(path)
    CreatePreSharedKey("ec2-keypair", path)
    CreateInsightVMSecurityGroup()
    CreateEC2(keypair_name)

Main()