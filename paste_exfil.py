from win32com import client

import os
import random
import requests
import time


username = 'eshkoreee'
password = 'qaz1WSX2edc3RFV4!'
api_dev_key = 'cd3xxx001xxxx02'

def plain_paste(title, contents):
    login_url = 'https://pastebin.com/api/api_login.php'
    login_data = {
        'api_dev_key': api_dev_key,
        'api_user_name': username,
        'api_user_password': password,
    }
    r = requests.post(login_url, data=login_data)
    api_user_key = r.text

    paste_url = 'https://pastebin.com/api/api_post.php'
    paste_data = {
        'api_paste_name': title,
        'api_paste_code': contents.decode(),
        'api_dev_key': api_dev_key,
        'api_user_key': api_user_key,
        'api_option': 'paste',
        'api_paste_private': 0,
        }
    r = requests.post(paste_url, data=paste_data)
    print(r.status_code)
    print(r.text)

def wait_for_browser(browser):
    while browser.ReadyState != 4 and browser.ReadyState != 'complete':
        time.sleep(0.1)

def random_sleep():
    time.sleep(random.randint(5,10))

def login(ie):
    full_doc = ie.Document.all # получаем коллекцию распарщеной HTML страницы
    for elem in full_doc: # перебираем каждый элемент
        if elem.id == 'loginform-username':
            elem.setAttribute('value', username)
        elif elem.id == 'loginform-password': # заполняем форму входа
            elem.setAttribute('value', password)
    
    random_sleep()
    if ie.Document.forms[0].id == 'w0': # проверяем что мы работаем именно с той формой с которой надо
        ie.document.forms[0].submit() # и отправляем
    wait_for_browser(ie) # опять ждем загрузки страницы

def submit(ie, title, contents):
    full_doc = ie.Document.all
    for elem in full_doc:
        if elem.id == 'postform-name': # имя файла
            elem.setAttribute('value', title)
            
        elif elem.id == 'postform-text': # текст файла
            elem.setAttribute('value', contents)

    if ie.Document.forms[0].id == 'w0': # проверку на подлинность формы
        ie.document.forms[0].submit() # отправляем
    random_sleep()
    wait_for_browser(ie)

def ie_paste(title, contents):
    ie = client.Dispatch('InternetExplorer.Application') # создаем экземпляр браузера для взаимодействия с сайтами и формами
    ie.Visible = 1

    ie.Navigate('https://pastebin.com/login') # програмно заходим на логин страницы pastebin
    wait_for_browser(ie) # ждем пока полностью не загрузится страница (код 4)
    login(ie) # логиним аккаунт

    ie.Navigate('https://pastebin.com/') # открываем главную страницу по новой т.к. мы залогинились
    wait_for_browser(ie) # опять ждем загрузки
    submit(ie, title, contents.decode()) # коммитим наши данные в пастебин

    ie.Quit() # закрываем системный браузер

if __name__ == '__main__':
    ie_paste('title', 'contents')
