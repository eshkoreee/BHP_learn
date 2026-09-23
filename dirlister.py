import os

def run(**args):
    print("[*] In dirlister module.")
    files = os.listdir('.') # тут мы собираем информацию о том какие файлы и папки есть в папке в которой находится сам троян
    return str(files)

