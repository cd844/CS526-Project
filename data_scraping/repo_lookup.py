import csv
from subprocess import call
import requests
import pprint
import json
import time
from requests.auth import HTTPBasicAuth

#token = put your pa token here

pp = pprint.PrettyPrinter(indent = 4)

class RepoLookup:
    url = 'https://api.github.com'
    tokens = []

    def get_valid_token(self):
        for token in self.tokens:
            response = requests.get(f'{self.url}/rate_limit', headers={'Authorization' : f'token {token}'})
            calls_left = json.loads(response.content.decode('utf-8'))['resources']['core']['remaining']
            #print(calls_left)
            if calls_left > 0:
                return token
        return None
    
    def get_remaining(self):
        remain = []
        for token in self.tokens:
            response = requests.get(f'{self.url}/rate_limit', headers={'Authorization' : f'token {token}'})
            calls_left = json.loads(response.content.decode('utf-8'))['resources']['core']['remaining']
            remain.append(calls_left)
        return remain

    def get_result_dict(self, token, path):
        response = requests.get(f'{self.url}{path}', headers={'Authorization' : f'token {token}'})
        if(response.status_code != 200):
            return None, response.status_code
        page = response.content
        d = json.loads(page.decode('utf-8'))
        return d, response.status_code


    def get_attributes(self, name):
        token = self.get_valid_token()
        if(token == None):
            return 0, None 
        res, code = self.get_result_dict(token, f'/repos/{name}')
        if(res == None):
            return code, None
        row = dict()
        row['name'] = name
        row['description'] = res['description']
        row['languages'] = res['language']
        #langs = get_result_dict(res['languages_url'], "")
        langs = self.get_result_dict(token, f'/repos/{name}/languages')
        row['languages'] = json.dumps(langs)
        #dl = get_result_dict(f'/repos/{name}/downloads')
        #row['downloads'] = json.dumps(langs)
        row['forks'] = res['forks_count']
        row['topics'] = res['topics']
        row['topics'] = json.dumps(row['topics'])
        #cont = get_result_dict(res['contributors_url'], "")
        cont = self.get_result_dict(token, f'/repos/{name}/contributors')
        row['contributors'] = json.dumps(cont)
        row['created'] = res['created_at']
        row['updated'] = res['updated_at']
        row['pushed'] = res['pushed_at']
        row['size'] = res['size']
        branches = self.get_result_dict(token, f'/repos/{name}/branches')
        row['branches'] = json.dumps(branches)
        row['license'] = json.dumps(res['license'])
        row['watchers'] = res['watchers_count']
        return code, row

def main():
    lookup = RepoLookup()
    tokens = json.load(open('tokens.json'))
    for tok in tokens:
        lookup.tokens.append(tok)
    print(lookup.get_remaining())


if __name__=="__main__":
    main()
    