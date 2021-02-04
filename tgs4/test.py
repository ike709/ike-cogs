import json
import requests
import urllib.parse

#headers = {'User-Agent': 'test', 'Api': 'Tgstation.Server.Api/8.2.0'}
#r = requests.get('http://golden.beestation13.com:26504/', headers = headers)
#print(r.json())

def get_url():
    try:
        url = 'http://golden.beestation13.com' + ":" + str(26504)
        return url
    except:
        print("fuck url")

def get_headers():
    try:
        headers = {'User-Agent': 'test', 'Api': 'Tgstation.Server.Api' + '/' + '8.2.0'}
        return headers
    except:
        print("fuck headers")

r = requests.get(get_url(), headers = get_headers())
print(r.text)