import argparse
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

    def censor_text(self, text: str):
        return self.prof_filter.censor(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Сервис для фильтрации текста от непристойностей')
    parser.add_argument('--addr', type=str, default="0.0.0.0:8050",
                        help='На каком адресе будет работать grpc сервер')
    args = parser.parse_args()

    service = RouteGuideServicer()
    service.serve(args.addr)
    censor = Censor()

