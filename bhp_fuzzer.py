# -*- coding: utf-8 -*-
from burp import IBurpExtender
from burp import IIntruderPayloadGeneratorFactory
from burp import IIntruderPayloadGenerator
from java.util import List, ArrayList
import random
"""
при помощи этого класса мы общаемся с burp suite.
в registerExtenderCallbacks мы получаем ключ для общения с бурпом
bи говорим ему что можем предоставить список пейлоадов
"""
class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks # этот метод вызывается во время инициализации самого расширения
        # callbaks это ключ или мост для использования или вызова других функций burp suite
        self._helpers = callbacks.getHelpers()
        # helpers предоставляет набор методов для работы с HTTP запросами
        callbacks.registerIntruderPayloadGeneratorFactory(self)
        # говорим burp suite что мы можем дать свои списки с полезными нагрузками которые можно выбрать в intruder
        return
    
    def getGeneratorName(self): # говорим бурпу свое имя
        return 'BHP Payload Generator'

    def createNewInstance(self, attack): # возваращем сам объект генератора BHPFuzzer
        return BHPFuzzer(self, attack)
"""
этот класс является сердцем фаззера тут мы задаем 
ему переменные такие как объект расширения для прямого взаимодействия с burp

"""
class BHPFuzzer(IIntruderPayloadGenerator):
    def __init__(self, extender, attack):
        self._extender = extender # сам объект расширения для взаимодействия с burp
        self.helpers = extender._helpers
        self._attack = attack # предоставляет какие параметры выбраны в intruder
        self.max_payloads = 10
        self.num_iterations = 0

        return
    
    def hasMorePayloads(self):
        if self.num_iterations == self.max_payloads:
            return False
        else:# счетчик полезных нагрузок
            return True
    
    def getNextPayload(self, current_payload):
        payload = ''.join(chr(x) for x in current_payload) # превращает байты в строку
        payload = self.mutate_payload(payload)
        self.num_iterations += 1 # преобразуем оригинальный запрос в мутированый запрос

        return payload
    
    def reset(self):
        self.num_iterations = 0
        return
    
    def mutate_payload(self, original_payload): # параметр который мы принимает это значение которое мы хотим мутировать
        picker = random.randint(1, 3)
        # выбираем случайный способ атаки
        offset = random.randint(0, len(original_payload) - 1) # выбираем рандомное место для мутации
        front, back = original_payload[:offset], original_payload[offset:]

        if picker == 1: # если 1 то внедряем SQL код
            front += "'"
        elif picker == 2: # если 2 внедряем XSS тест
            front += "<script>alert('BHP!');</script>"
        elif picker == 3:# если 3 то копируем 2 половину запроса, копируем случайное кол-во раз и прикрепляем к самому запросу
            chunk_length = random.randint(0, len(back)-1) # выбирает длинну копируемого куска для 3 способа мутации
            repeater = random.randint(1, 10)
            for _ in range(repeater):
                front += original_payload[:offset + chunk_length]

        return front + back
