import argparse
import re
import string
from concurrent import futures

import grpc

from profanity_filter import ProfanityFilter
from profanity_filter import AVAILABLE_ANALYSES
from proto import service_pb2, service_pb2_grpc

from profanity_filter.analysis.morphological import *
from profanity_filter.analysis.multilingual import *


class RouteGuideServicer(service_pb2_grpc.ProfanityFilterServicer):
    def __init__(self):
        print("Доступные анализаторы текста: ", ', '.join(sorted(analysis.value for analysis in AVAILABLE_ANALYSES)))
        self.prof_filter = Censor()
        print("ProfanityFilter инициализирован.")

    def FilterMessage(self, request, context):
        response = self.prof_filter.censor_text(request.text)
        return service_pb2.Text(text=response)

    def Ping(self, request, context):
        return service_pb2.Nothing()

    def serve(self, addr: str):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        service_pb2_grpc.add_ProfanityFilterServicer_to_server(self, server)
        server.add_insecure_port(addr)
        server.start()
        print(f"Сервер запущен на адресе {addr}")
        server.wait_for_termination()


class Censor:
    def __init__(self):
        self.prof_filter = ProfanityFilter(languages=["en", "ru"])
        with open('profanity_filter/data/regex.txt', 'r') as f:
            self.regexes = [
                re.compile(line.strip()) for line in f
            ]
        with open('profanity_filter/data/regex_white.txt', 'r') as f:
            self.white_list_regexes = [
                re.compile(r'\b' + line.strip() + r'\b') for line in f
            ]

    def censor_text(self, text: str):
        # цензурим в два этапа - сначала морфологический анализ с нейронкой, потом регулярками
        censored = self.prof_filter.censor(text.strip())
        tokens = censored.split()

        for i, token in enumerate(tokens):
            if any(regex.search(token.lower()) for regex in self.white_list_regexes):
                continue
            for regex in self.regexes:
                if regex.search(token.lower()):
                    print(token)
                    tokens[i] = re.sub(regex, lambda m: '*' * len(m.group(0)), token.lower())

        return ' '.join(tokens)

    def censor_token(self, token):
        if any(regex.search(token) for regex in self.white_list_regexes):
            return token
        for regex in self.regexes:
            if regex.search(token):
                return re.sub(regex, lambda m: m.group(1) + '*' * len(m.group(2)) + m.group(3), token)
        return token


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Сервис для фильтрации текста от непристойностей')
    parser.add_argument('--addr', type=str, default="0.0.0.0:8050",
                        help='На каком адресе будет работать grpc сервер')
    args = parser.parse_args()

    while True:
        try:
            service = RouteGuideServicer()
            service.serve(args.addr)
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            continue

