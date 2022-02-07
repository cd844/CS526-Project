import csv
import requests
import pprint
import json
import time
from requests.auth import HTTPBasicAuth

#token = put your pa token here

pp = pprint.PrettyPrinter(indent = 4)

def get_result_dict(path, url = "https://api.github.com"):
    response = requests.get(f'{url}{path}', headers={'Authorization' : f'token {token}'})
    if(response.status_code != 200):
        return None, response.status_code
    page = response.content
    d = json.loads(page.decode('utf-8'))
    return d, response.status_code

def get_rate_limit(url = "https://api.github.com"):
    return get_result_dict("/rate_limit")

def get_search_page(term, page=1):
    term = term.replace(" ", "+")
    path = f"/search/repositories?q={term}&p={page}"
    return get_result_dict(path)


def get_attributes(name):
    res, code = get_result_dict(f'/repos/{name}')
    print(f'{name}:{code}')
    if(res == None):
        return code
    row = dict()
    row['name'] = name
    row['description'] = res['description']
    row['languages'] = res['language']
    #langs = get_result_dict(res['languages_url'], "")
    langs = get_result_dict(f'/repos/{name}/languages')
    row['languages'] = json.dumps(langs)
    #dl = get_result_dict(f'/repos/{name}/downloads')
    #row['downloads'] = json.dumps(langs)
    row['forks'] = res['forks_count']
    row['topics'] = res['topics']
    #cont = get_result_dict(res['contributors_url'], "")
    cont = get_result_dict(f'/repos/{name}/contributors')
    row['contributors'] = json.dumps(cont)
    row['created'] = res['created_at']
    row['updated'] = res['updated_at']
    row['pushed'] = res['pushed_at']
    row['size'] = res['size']
    branches = get_result_dict(f'/repos/{name}/branches')
    row['branches'] = json.dumps(branches)
    row['license'] = json.dumps(res['license'])
    row['watchers'] = res['watchers_count']
    return row

def main():
    with open("bq-results-20220203-212826-iq0do5yddqd.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        total = 10000
        outfile = f"bq_results_{total}.json"
        rows = []
        next(reader)
        with open(outfile, mode='w') as out:
            count = 0
            name = next(reader)[0]
            while count < total:
                #print(name)
                row = get_attributes(name)
                if row == 404: #hidden repo?
                    name = next(reader)[0]
                elif(row == 403): #api limit, wait ten minutes
                    print("Sleeping")
                    time.sleep(600)
                elif(row != None):
                    #pp.pprint(row)
                    rows.append(row)
                    count += 1
                    name = next(reader)[0]
                else:
                    print(f"Unknown code: {row}")
                    
        
            print(len(rows))
            json.dump(rows, out)

if __name__=="__main__":
    main()
    