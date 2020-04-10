import urllib.request
import json 
import re
import base64
import encodings
from getpass import getpass
import ssl
import gzip
from urllib.parse import urlencode, quote_plus
import csv 
import time

# Dirty api client
def client(username, password, ip, meth, endpoint):
    if endpoint != None:
        rooturl = f"https://{ip}:3780/api/3/"
        call = f"{rooturl}{endpoint}"
        creds = f"{username}:{password}"
        base64_creds = base64.b64encode(creds.encode('ascii')).decode()
        try:
            req = urllib.request.Request(url=call, method=meth)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f"Basic {base64_creds}")
            gcontext = ssl.SSLContext()
            response = urllib.request.urlopen(req, context=gcontext)
            content = response.read()
            parsed_json = json.loads(content)
            try:
                return parsed_json['resources']
            except:
                None
        except:
            print("Failed to make api call")

# Get some environment variables
username = input("Console username:")
password = getpass(f"Password for {username}:")
console = input("Console ip address:")

sites = client(username,password,console, "GET", "sites")

# Build site data structure 
sites_to_delete = {}
index = 0 
with open('./site_to_delete.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        sites_to_delete[index] = str.upper(row[0])
        index += 1     

# Delete operation
for site in sites:
    if str.upper(site['name']) in sites_to_delete.values():
        client(username,password,"3.17.29.37", "DELETE", f"sites/{site['id']}")
        time.sleep(2)
