import grpc
from proto import service_pb2, service_pb2_grpc


def run():
    # Создаем канал для соединения с сервером
    channel = grpc.insecure_channel('localhost:8050')

    # Создаем стаб для вызова методов
    stub = service_pb2_grpc.ProfanityFilterStub(channel)

    # Вызываем метод Ping
    response = stub.Ping(service_pb2.Nothing())
    print("Ping response: ", response)

    # Вызываем метод FilterMessage
    text = service_pb2.Text(text="Fuck message")
    response = stub.FilterMessage(text)
    print("FilterMessage response: ", response.text)


if __name__ == "__main__":
    run()
