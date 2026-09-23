from scapy.all import TCP, rdpcap
import collections
import os
import re
import sys
import zlib

OUTDIR = 'pictures'
PCAPS = '/mydownloads'

Response = collections.namedtuple('Response', ['header', 'payload'])


def get_header(payload):
    try:
        header_raw = payload[:payload.index(b'\r\n\r\n')+2]
    except ValueError:
        sys.stdout.write('-')
        sys.stdout.flush()
        return None

    header = dict(re.findall(r'(?P<name>.*?): (?P<value>.*?)\r\n', header_raw.decode()))
    if 'Content-Type' not in header:
        return None
    return header


def extract_content(Response, content_name='image'):
    content, content_type = None, None
    if content_name in Response.header['Content-Type']: # проверяем есть ли в заголовке Content-Type слово image
        content_type = Response.header['Content-Type'].split('/')[1] # из image/jpeg в 'jpeg'
        content = Response.payload[Response.payload.index(b'\r\n\r\n')+4:]# отсеиваем заголовки от реально полезной загрузки

        if 'Content-Encoding' in Response.header: # было ли сжатие картинки
            if Response.header['Content-Encoding'] == "gzip":
                content = zlib.decompress(Response.payload, zlib.MAX_WBITS | 32) # расшифровываем методом gzip
            elif Response.header['Content-Encoding'] == "deflate":
                content = zlib.decompress(Response.payload) # расшифровываем методом deflate

    return content, content_type


class Recapper:
    def __init__(self, fname):
        pcap = rdpcap(fname) # превращает гору данных на список пакетов
        self.sessions = pcap.sessions() # создает словарь где ключ это айпи и порт жертвы и сервера а значение это список пакетов в определенной TCP сессии
        self.responses = list()

    def get_responses(self):
        for session in self.sessions:
            payload = b''
            for packet in self.sessions[session]:
                try:
                    if packet[TCP].dport == 80 or packet[TCP].sport == 80: # проверка что порт жертвы и сервера 80 (HTTP)
                        payload += bytes(packet[TCP].payload) # убирает мусор ввиде заголовков параметров и т.п. и загружает полезные данные
                except IndexError:
                    sys.stdout.write('x')
                    sys.stdout.flush()

            if payload:
                header = get_header(payload) # парсит полезные данные в словарь где находятся HTTP заголовки
                if header is None:
                    continue
                self.responses.append(Response(header=header, payload=payload)) # сохраняем HTTP заголовки и всю полезную нагрузку ввиде именованого кортежа

    def write(self, content_name):
        for i, response in enumerate(self.responses): # поля i = счетчик а response кортеж с ключами header и payload
            content, content_type = extract_content(response, content_name) # второй параметр это image
            if content and content_type:
                fname = os.path.join(OUTDIR, f'ex_{i}.{content_type}')
                print(f'Writing {fname}')
                with open(fname, 'wb') as f:
                    f.write(content)


if __name__ == '__main__':
    pfile = 'pcap.pcap'  # os.path.join(PCAPS, 'pcap.pcap')
    recapper = Recapper(pfile)
    recapper.get_responses()
    recapper.write('image')
