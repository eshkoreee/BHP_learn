from burp import IBurpExtender
from burp import IContextMenuFactory

from java.util import ArrayList
from javax.swing import JMenuItem

from datetime import datetime
from HTMLParser import HTMLParser

import re


class TagStripper(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self) # инифиализируем родительский класс
        self.page_text = list()

    def handle_data(self, data):
        self.page_text.append(data) # переопределяем методы из парсера
                                    # полиморфизм
    def handle_comment(self, data): # переопределяем методы из парсера
        self.page_text.append(data)

    def strip(self, html):
        self.feed(html)# передаем методу класса HTMLParser HTML код страницы а он парсит ее и затем вызывает прошлые 2 метода
        return ' '.join(self.page_text)# затем берет список слов и соединяет в 1 строку через пробел


class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks): # инициализируем расширение в бурпе
        self._callbacks = callbacks # инстрмент что бы использовать бурп в расширении
        self._helpers = callbacks.getHelpers() # набор утилит бурпа для работы с HTTP
        self.context = None
        self.hosts = set()
        self.wordlist = set(['password']) # инициализируем множество и сразу добавляем 1 элемент

        callbacks.setExtensionName('BHP Wordlist') # даем имя расширению
        callbacks.registerContextMenuFactory(self) # при нажатии правой кнопкой мыши в любом месте программы будет высвечиваться наше расширение
        return

    def createMenuItems(self, context_menu):
        self.context = context_menu # сохраняем то что передал пользователь
        menu_list = ArrayList()
        # создаем окошко при нажатии ПКМ  с именем create Wordlist и при нажатии на него вызываем метод wordlist_menu
        menu_list.add(JMenuItem('Create Wordlist', actionPerformed=self.wordlist_menu)) # при нажатии пкм и выбора create wordlist начинается цепочка методов
        return menu_list

    def wordlist_menu(self, event):
        http_traffic = self.context.getSelectedMessages() # извлекаем все HTTP пакеты которые выделил пользователь
        for traffic in http_traffic:
            http_service = traffic.getHttpService() # извлекаем служебку по типу хоста порта и протокола
            host = http_service.getHost() # тут извлекаем именно хост
            self.hosts.add(host)

            http_response = traffic.getResponse() # возвращает сырые байты HTTP ответа. если пакет был типа GET или что то еще то вернет none
            if http_response: # если это был ответ(post) вызываем get_words если что то еще вызываем display_wordlist
                self.get_words(http_response)
        self.display_wordlist()
        return
    
    def get_words(self, http_response):
        headers, body = http_response.tostring().split('\r\n\r\n', 1) # разбиваем сырой HTTP ответ на заголовки и тело
        if headers.lower().find('content-type: text') == -1: # если в заголовках 'content-type: text' не найдено то возвращает индекс -1 следовательно это не то что нам надо
            return
        tag_stripper = TagStripper()
        page_text = tag_stripper.strip(body) # кидает методу strip HTML код страницы а возвращает 1 строку текста разделенной через пробел
        words = re.findall(r'[a-zA-Z]\w{2,}', page_text) # извлекаем из строки все слова начинающиеся на латиннскую букву и с возможным содержанием букв, цифр или нижним подчеркиванием и минимальной длинной 3
        for word in words:
            if len(word) <= 12: # фильтруем слишком длинные слова
                self.wordlist.add(word.lower()) # затем добавляем в множество по нижнему регистру
        return

    def mangle(self, word):
        year = datetime.now().year
        suffixes = ['', '1', '!', year]
        mangled = list()
        for password in (word, word.capitalize()): # берем нашел слово и его же с заглавной первой буквой
            for suffix in suffixes: # тут мы подставляем еще к каждому слову по 4 суффикса и 1 из них пустой
                mangled.append('%s%s' % (password, suffix)) # сохраняем по 8 вариантов к каждому слову
        return mangled
    
    def display_wordlist(self):
        print('#!comment: BHP Wordlist for site(%s)' % ', '.join(self.hosts)) # оповещаем для какого сайта сделан вордлист
        for word in sorted(self.wordlist):
            for password in self.mangle(word): # превращаем 1 вариант в 8 вариантов
                print(password) # тут мы выводим все возможные варианты в консоль
        return
# примечание: мы бурпу не отдаем список паролей а выводим в консоль бурпа где оттуда можем скопировать и делать с ним что хотим