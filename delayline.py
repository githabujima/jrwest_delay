import json
import urllib.request
import requests
import bs4
import sys
import re

args = sys.argv

# Set Line Notify token and API
line_notify_token = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
line_notify_api = 'https://notify-api.line.me/api/notify'
headers = {'Authorization': 'Bearer ' + line_notify_token}

dictst = {}
dictline = {}
payloadstr = ''
line = {}

#APIのありか
jsonbase = 'https://www.train-guide.westjr.co.jp/api/v3/'

#近畿各路線のjson特定
try:
    pages = requests.get('https://www.train-guide.westjr.co.jp/area_kinki.html')
    pages.raise_for_status()
    soup = bs4.BeautifulSoup(pages.content, "html.parser")
    
    for i in soup.select(".routeList_item-link"):
        linename = i['title']
        lineurl = i['href'].replace('.html','.json')
        line[linename] = lineurl
except:
    #何もせず終了する
    pass
url = jsonbase + line[args[1]] 
url_st = url.replace('.json','_st.json')

#遅延取得
try:
    res = urllib.request.urlopen(url)
    res_st = urllib.request.urlopen(url_st)
    data = json.loads(res.read().decode('utf-8'))
    data_st = json.loads(res_st.read().decode('utf-8'))

    for station in data_st['stations']:
        dictst[station['info']['code']] = station['info']['name']
    for item in data['trains']:
        if item['delayMinutes'] > 0:
            stn = item['pos'].split('_')
            try:
                position = dictst[stn[0]] + '辺り'
            except KeyError:
                position = "どこかよくわかんない"
            payload = [item['displayType'], item['dest']['text'],'行き:',item['delayMinutes'],'分遅れ',position]
            payloadstr += ' '.join(map(str,payload)) + '\n'
    if not payloadstr:
        linepald = {'message':args[1] + 'に電車遅延はありません'}
        line_notify = requests.post(line_notify_api, data=linepald, headers=headers)
    else:
        linepald = {'message':'【' + args[1] + 'の遅延情報】\n' + payloadstr}
        line_notify = requests.post(line_notify_api, data=linepald, headers=headers)

except urllib.error.HTTPError as err:
    print('HTTPError: ', err)
except json.JSONDecodeError as err:
    print('JSONDecodeError: ', err)
