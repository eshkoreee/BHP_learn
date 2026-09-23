from burp import IBurpExtender
from burp import IContextMenuFactory

from java.net import URL
from java.util import ArrayList
from javax.swing import JMenuItem
from thread import start_new_thread

import json
import socket
import urllib

API_KEY = '<your api key>'
API_HOST = 'api.cognitive.microsoft.com'


class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks # пульт управления для взаимодействия с бурпом
        self._helpers = callbacks.getHelpers() # дает набор инструментов для работы с burp suite
        self.context = None
        callbacks.setExtensionName('BHP Bing') # задаем имя расширению
        callbacks.registerContextMenuFactory(self) # при нажатии ПКМ на HTTP запрос в контексном меню будет появляться наше расширение
        return

    def createMenuItems(self, context_menu):
        self.context = context_menu # сохраняем переданный контекст от бурпа чтобы позже, при нажатии на пункт меню, можно было узнать, какие именно запросы были выделены
        menu_list = ArrayList()
        menu_list.add(JMenuItem('Send to Bing', actionPerformed=self.bing_menu)) # при нажатии на Send to bing в контексном меню бурпа мы выполняем метод bing_menu
        return menu_list

    def bing_menu(self, event):
        http_traffic = self.context.getSelectedMessages() # при нажатии send to bing сохраняем весь переданных трафик в этот список
        print('%d requests highlighted' % len(http_traffic))

        for traffic in http_traffic:
            http_service = traffic.getHttpService() # извлекаем инфу о сервисе: айпи или домен, порт и протокол
            host = http_service.getHost()  # извлекаем из сервиса домен или айпи
            print('User selected host: %s' % host)
            self.bing_search(host)
        return
    
    def bing_search(self, host):
        try:
            is_ip = bool(socket.inet_aton(host)) # пытаемся преобразовать объект в айпи если это правда айпи то получается и возвращает true иначе ошибка следовательно false
        except socket.error:
            is_ip = False
        
        if is_ip:
            ip_address = host # если хост изначально был айпи то присваиваем сразу
            domain = False
        else:
            ip_address = socket.gethostbyname(host) # преобразуем домен в айпи
            domain = True
        start_new_thread(self.bing_query, ('ip:%s' % ip_address,))
        if domain:
            start_new_thread(self.bing_query, ('domain:%s' % host,))

    def bing_query(self, bing_query_string):
        print('Performing Bing search: %s' % bing_query_string)
        http_request = 'GET https://%s/bing/v7.0/search?' % API_HOST
        http_request += 'q=%s HTTP/1.1\r\n' % urllib.quote(bing_query_string) # кодируем айпи или домен в безопасную строку для передачи в URL 
        http_request += 'Host: %s' % API_HOST
        http_request += 'Connection:close\r\n'
        http_request += 'Ocp-Apim-Subscription-Key: %s\r\n' % API_KEY
        http_request += 'User-Agent: Black Hat Python\r\n\r\n'
    
        json_body = self._callbacks.makeHttpRequest(API_HOST, 443, True, # указываем домен сайта, порт, использование TLS и передаем сам вручную собраный HTTP запрос и кодируем в обычную строку
                                                    http_request).tostring()
        json_body = json_body.split('\r\n\r\n', 1)[1] # извлекаем тело ответа из пакета
        try:
            response = json.loads(json_body) # превращает JSON тело в пайтон словарь
        except (TypeError, ValueError) as err:
            print('No results from Bing: %s' % err) # если тела нет т.е. ответа от сервера то оповещаем об этом
        else:
            sites = list()
            if response.get('webPages'): # 1
                sites = response['webPages']['value'] # 2
            if len(sites): # проверяем что сайты найдены (1) и если да то извлекаем список найденых сайтов где в каждом элементе есть 
                for site in sites: # 'name' название сайта, 'url' url адрес сайта, 'snippet' описание сайта (2)
                    print('*'*100) # расписываем данные о найденных сайтах в консоль
                    print('Name: %s       ' % site['name'])
                    print('URL: %s        ' % site['url'])
                    print('Description: %r' % site['snippet'])
                    print('*'*100)

                    java_url = URL(site['url']) # превращаем пайтон объект url адреса в джава объект для проверки что сайт есть в области тестирования burp proxy, intruder
                    if not self._callbacks.isInScope(java_url): # проверяем есть есть ли наш URL в области видимости если нет то добавляем
                        print('Adding %s to Burp scope' % site['url']) # если его не будет в области видимости то он не проксируется и игнорируется в сканерах
                        self._callbacks.includeInScope(java_url)
            else:
                print('Empty response from Bing.: %s' % bing_query_string)
        return
         
# if __name__ == '__main__':
#     p = BurpExtender()
#     p.bing_query('wikipedia.com')