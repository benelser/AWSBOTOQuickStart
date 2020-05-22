## Attempt to Containerize Rapid7 Nexpose
1. Deploy t3.2xl 32GB
2. Get host ready
```bash
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get install docker-ce docker-ce-cli containerd.io -y
sudo docker run hello-world
sudo docker images # list available images
sudo docker pull centos:centos7 # install a base image
```
3. Pre-stage dependencies
    - license file
    - scripts etc.
4. Build
```bash
sudo docker build --no-cache --pull -f Dockerfile . # Build ref'n current directory for dependencies
```
5. Run
```bash
sudo docker run <imageid>
sudo docker run  -p 7777:3780 ec7c5096b99e # Exposing port
```
5. Run commands 
```bash
sudo docker inspect -f '{{.State.Pid}}' frosty_newton # Get pid
sudo nsenter -t <pid> -n netstat -anop | grep 3780 # specifically if the container does not have the tool on it
sudo docker stop <CONTAINER ID> # stop container
```