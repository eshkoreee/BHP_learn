import contextlib
import os
import queue
import requests
import sys
import threading
import time

FILTERS = [".jpg", ".gif", ".png", ".css"] # мусорные файлы
TARGET = "http://boodelyboo.com/wordpress" # атакуемый сайт
THREADS = 10 # указываем сколько будет потоков

answers = queue.Queue() 
web_paths = queue.Queue()

def gather_paths():
    for root, _, files in os.walk('.'): # читаем каждый возможный путь в директории итеративно от папки до папки по одному. возвращает путь в текущую папку, подпапки хранащиеся там и сами файлы внутри папки
        for fname in files:
            if os.path.splitext(fname)[1] in FILTERS: # отбираем только файлы имеющие скрипты и текст
                continue
            path = os.path.join(root, fname)
            if path.startswith('.'): # если путь начинается с точки то создаем новый путь где добавляем символы начиная с второго где первый символ это точка
                path = path[1:]
            print(path)
            web_paths.put(path) # добавляем путь к файлу в очередь web_paths

@contextlib.contextmanager
def chdir(path):
    """
    On enter, change directory to specified path.
    On exit, change direcgory to original.
    """
    this_dir = os.getcwd() # запоминаем текущий путь
    os.chdir(path) # переходим в директорию нашей CMS
    try:
        yield # тут выполняется код внутри блока with
    finally:
        os.chdir(this_dir) # по окончанию переходим обратно в прошлую открытую директорию

def test_remote():
    while not web_paths.empty(): # проверяем что есть хоть какие то файлы
        path = web_paths.get() # вытаскиваем их из очереди
        url = f'{TARGET}{path}' # соединяем URL адресс сайта с путем файла
        time.sleep(2) # ждем что бы бана от спама не было
        r = requests.get(url) # отправляем GET запрос сайту
        if r.status_code == 200: # если удачно то:
            answers.put(url) # засовываем рабочий путь в очередь
            sys.stdout.write('+')
        else:
            sys.stdout.write('x') # если неудачно пишим крестик и выводим то что есть
        sys.stdout.flush()
            
def run():
    mythreads = list()
    for i in range(THREADS):
        print(f'Spawning thread {i}')
        t = threading.Thread(target=test_remote)
        mythreads.append(t) # создаем 10 потоков (в нашем случае) и добавляем их в список и запускаем
        t.start()

    for thread in mythreads:
        thread.join() # говорим что пока эти потоки не отработают программу не завершаем
        

if __name__ == '__main__':
    with chdir("/home/tim/Downloads/wordpress"): # выполняем код инициализации передавая путь к дистрибутиву wordpress
        gather_paths()
    input('Press return to continue.')
    run()
    
    with open('myanswers.txt', 'w') as f:
        while not answers.empty(): # открываем текстовый файл и записываем в него все рабочие каталоги сайта
            f.write(f'{answers.get()}\n')
    print('done')