from flask import Flask, jsonify
import requests
import pika
import threading
import json

app = Flask(__name__)

port = 5001
temperature_measure = "C"
url = f"http://127.0.0.1:{port}/"

# Variável global para armazenar a última temperatura em Celsius recebida
latest_temperature_celsius = None

def callback_celsius(ch, method, properties, body):
    global latest_temperature_celsius
    # Decodifica a mensagem e atualiza a última temperatura em Celsius
    data = json.loads(body.decode())  # Converte de JSON para dicionário
    if data.get("type") == "C":  # Verifica se é temperatura em Celsius
        latest_temperature_celsius = data.get("value")
        print(f"Temperatura Celsius recebida: {latest_temperature_celsius} °C")

def consume_temperature_celsius():
    # Conecta ao RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declara um exchange do tipo 'fanout'
    channel.exchange_declare(exchange='temperaturas', exchange_type='fanout')

    # Cria uma fila exclusiva para este consumidor
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Liga a fila ao exchange
    channel.queue_bind(exchange='temperaturas', queue=queue_name)

    # Configura um consumidor para a fila de temperaturas em Celsius
    channel.basic_consume(queue=queue_name, on_message_callback=callback_celsius, auto_ack=True)

    print('Aguardando mensagens de temperatura em Celsius...')
    channel.start_consuming()

@app.route('/', methods=['GET'])
def get_data():
    data = {'key': latest_temperature_celsius} if latest_temperature_celsius else {'key': 'No data received'}
    return jsonify(data)

if __name__ == '__main__':
    data = {"type": temperature_measure, "url": url}
    print(data)
    requests.post("http://127.0.0.1:5020/services", data=data)

    # Inicia o consumidor RabbitMQ em uma thread separada
    consumer_thread = threading.Thread(target=consume_temperature_celsius)
    consumer_thread.start()

    # Inicia o aplicativo Flask
    app.run(debug=True, port=port, use_reloader=False)
