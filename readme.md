# Getting Started with AWS SDK (boto3) and Rapid7 Products
This repo is a collection of python code that levarages the boto3 aws sdk to provision services. This code is not production ready or intended to be used in production. This code is not supported by Rapid7. If you are still exited please continue reading.

1. Create [AWS free-tier account](https://aws.amazon.com/free/?all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc) 

2. Install Dependencies (python3 boto3)
    * MAC
        Install brew [brew](https://brew.sh/)
        ```bash
        /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
        ```
        Install python3 & AWS SDK [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html)
        ```bash
        brew install python3
        python3 -m pip install --upgrade pip
        python3 -m pip install boto3
        python3 -m pip install boto3 botostubs
        ```
    * ubuntu
        Install python3 & AWS SDK [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html)
        ```bash
        sudo apt-get install python3-pip
        python3 -m pip install --upgrade pip
        python3 -m pip install boto3
        python3 -m pip install boto3 botostubs
        ```
    * Windows
        Install [chocolatey](https://chocolatey.org)
        Run from an elevated Administrator Session (right click runas Administrator)
        ```powershell
        Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Confirm:$false -Force
        iwr https://chocolatey.org/install.ps1 -UseBasicParsing | iex
        choco upgrade chocolatey
        ```
        Install python3 & AWS SDK [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html)
        ```powershell
        choco install -y python3
        $pythonPath = (Get-ChildItem C:\ | Where-Object {$_.Name -like "*python3*"}).FullName
        $oldpath = (Get-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH).path
        $newpath += $oldpath + $pythonPath + ";"
        Set-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH -Value $newPath
        python -m pip install --upgrade pip
        python -m pip install boto3
        python -m pip install boto3 botostubs
        ```

4. Set Up Access in [IAM](https://console.aws.amazon.com/iam/)
    - Delete your root access keys
    - Activate MFA on your root account (Okta works great)
    - Create and Apply IAM password policy
    - Create Individual IAM User
        - Provide username 
        - Grant programmatic access and AWS Management Conosle Access
        - Set password
        - Uncheck require password reset.
    - Create Group
        - Provide Group Name
        - Grant full AdministratorAccess 
    - Take note of and or securely store:
        - Access key ID
        - Secret

5. Set up Dev Env
- Install [VS Code](https://code.visualstudio.com/)
- Install the [Python extension for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- At the top of your Python script file: 
```python
import botostubs, boto3
```
- When declaring a boto3 client object, add a type hint comment: 
```python
iam = boto3.client('iam') # type: botostubs.IAM
```
- Disbale the default Jedi python engine in VS Code settings.json
```json
"python.jediEnabled": false
```

Write up of the steps can be found below:
[Enable Intellisense for AWS Boto3 Type Hints in Microsoft Visual Studio Code](https://trevorsullivan.net/2019/06/11/intellisense-microsoft-vscode-aws-boto3-python/)

6. Create AWS Credential File
    * MAC & Linux
        ```bash
        mkdir -p ~/.aws/ 
        cd ~/.aws/ 
        touch credentials
        code credentials
        ```
    * Windows
        ```powershell
        cd $env:USERPROFILE
        mkdir .\.aws  
        cd .\.aws\
        New-Item -Type File -Name credentials 
        code credentials
        ```
    Add the following lines to credentials file (Make sure you save it!!!):
    ```bash
    [default]
    aws_access_key_id=MYACCESSKEYHERE
    aws_secret_access_key=MYSUPERSECRETACCESSKEYHERE
    ```

7. Kicking the Tires Test Setup

Create new .py file containing the following code
```python
import botostubs, boto3

s3 = boto3.client('s3') # type: botostubs.S3
s3.create_bucket(Bucket="myboto3createdbucket")
response = s3.list_buckets()
print("Existing S3 buckets....")

# Repsonse is of type dict
for bucket in response['Buckets']:
    print(f'{bucket["Name"]}')
```
Execute your code:
```bash
python3 MYCODESNIPPET.py
```
#### Expected Output
```bash
Existing S3 buckets....
myboto3createdbucket
```

## Rapid7 Builds 
1. [InsightVM](./InsightVM)
2. [AppSpider Pro](./AppSpiderPro)