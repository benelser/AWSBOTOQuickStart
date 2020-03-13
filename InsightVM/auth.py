import urllib.request
import json 
import re
import base64
import encodings
from getpass import getpass
import ssl
import gzip
from urllib.parse import urlencode, quote_plus

# Dirty api client
def authToAPI():
    username = input("Console username:")
    password = getpass(f"Password for {username}:")
    creds = f"{username}:{password}"
    base64_creds = base64.b64encode(creds.encode('ascii')).decode()
    console_url = "https://13.59.237.127:3780/api/3/"

    # body = {"channel": channel_id, "text" : message}
    # jsondata = json.dumps(body)
    # jsondataasbytes = jsondata.encode('utf-8') 
    req = urllib.request.Request(url=console_url, method='GET')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f"Basic {base64_creds}")
    gcontext = ssl.SSLContext()
    #req.add_header('Content-Length', len(jsondataasbytes))
    #response = urllib.request.urlopen(req, jsondataasbytes)
    response = urllib.request.urlopen(req, context=gcontext)

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

console_url = "https://3.14.141.157:3780"
cookie  = getConsoleCookie(console_url)
sessionCookie = getConsoleSessionCookie(cookie, "nxadmin", "ecadmin", console_url)
key = getScanEnginePairingKey(sessionCookie, console_url)
print(key)
