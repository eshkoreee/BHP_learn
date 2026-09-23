import queue
import requests
import sys
import threading

AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"# указываем что мы не бот а добренький браузер фаерфокс
EXTENSIONS = ['.php', '.bak', '.orig', '.inc'] # расширения которые подставляем к уже имеющимся возможным каталогам
TARGET = "http://testasp.vulnweb.com" # проверяющийся сайт
THREADS = 7 # кол-во потоков
WORDLIST = "/home/roman/downloads/SVNDigger-master/SVNDigger/all.txt" # расположения файла с каталогами

"""
тут мы разбиваем файл на список и проверяем были сбои при прошлой проверке или останавливали ли код
досрочно
Примечание: механизм resume в текущей реализации работает только при ручной передаче слова.
Для полноценного использования требуется сохранение прогресса в файл и автоматическое восстановление.
"""
def get_words(resume=None):
    """
    здесь мы берем 1 каталог и если делаем из него еще 4 доп. каталога с расширениями
    которые все в том числе первоначальный засовываем в очередь обработанных каталогов
    которые уже пойдут на проверку
    """
    def extend_words(word):
        if "." in word:
            words.put(f'/{word}')# если есть точка т.е. расширение то это конечный файл и добавляем его в очередь с одной /
        else:
            words.put(f'/{word}/') # иначе это котолог который можно расширить и кидаем в очередь с двумя /

        for extension in EXTENSIONS:
            words.put(f'/{word}{extension}') # затем берем каталог и превращаем его в 5 слов с им самим и еще 4 расширения и все суем в очередь

    with open(WORDLIST) as f: # читаем файл
        raw_words = f.read()
    found_resume = False
    words = queue.Queue() # будущая очередь с уже обработанными каталогами для дальнейшей проверки
    for word in raw_words.split(): # разбиваем большой файл на большой список каталогов и перебираем каждый
        if resume is not None: # проверка что программа была приостановлена или прервана
            if found_resume: # флаг найден ли каталог в списке если да то продолжаем с этого каталога
                extend_words(word)
            elif word == resume: # если нет продолжаем итерацию пока список каталогов не закончится
                found_resume = True
                print(f'Resuming wordlist from: {resume}')
        else:
            print(word)
            extend_words(word)
    return words # по окончанию возвращаем буфер со всеми каталогами + возможными расширения что умножает вес на 5

"""
тут мы создаем URL адреса с подставлеными каталогами и файлами после чего
начинаем проверять каждый на его наличие на веб сервере
"""
def dir_bruter(words):
    headers = {'User-Agent': AGENT} # говорим сайту что мы добренике и хорошенькие пользователи firefox
    while not words.empty(): # если есть хоть какие то каталоги то
        url = f'{TARGET}{words.get()}' # берем 1 и соединяем с URL адресом
        try:
            r = requests.get(url, headers=headers) # отправляем GET запрос
        except requests.exceptions.ConnectionError:
            sys.stderr.write('x')
            sys.stderr.flush() # если подключение не удалось то выводим что есть и пробуем дальше
            continue

        if r.status_code == 200: # если удачно то оповещаем пользователя что этот каталог открыт
            print(f'\nSuccess ({r.status_code}: {url})')
        elif r.status_code == 404: # если такого каталога нет то пишем точку
            sys.stderr.write('.')
            sys.stderr.flush()
        else: # если какой то другой ответ например 403 forbidden что полезно то тоже выводим об этом
            print(f'{r.status_code} => {url}') 


if __name__ == '__main__':
    words = get_words()
    print('Press return to continue.')
    sys.stdin.readline() # спрашиваем хотим ли начать сканирование
    for _ in range(THREADS): # запускаем указаное кол-во потоков и передаем им список со всеми каталогами
        t = threading.Thread(target=dir_bruter, args=(words,))
        t.start()
