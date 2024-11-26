import pika
import sqlite3
import json

# Connect to the SQLite database (or create a new one if it doesn't exist)
conn = sqlite3.connect('temperaturas.db')
cursor = conn.cursor()

# Create the table to store temperature data if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS temperaturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    valor REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# Function to save temperature to the database
def salvar_temperatura(tipo, valor):
    cursor.execute("INSERT INTO temperaturas (tipo, valor) VALUES (?, ?)", (tipo, valor))
    conn.commit()

# Callback function for RabbitMQ, without sending ACK
def callback(ch, method, properties, body):
    # Convert the message from JSON to dictionary
    message = json.loads(body.decode())
    tipo = message['type']
    valor = message['value']
    
    print(f"Mensagem recebida - Tipo: {tipo}, Valor: {valor}")
    
    # Save the message to the database
    salvar_temperatura(tipo, valor)

    # Do not send ACK so that the message stays in the queue for reprocessing
    # This means the message can be read again in the future until manually removed or reprocessed

# Function to consume messages from RabbitMQ using publish/subscribe without removing messages
def consumir_sem_ack():
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare the exchange for temperatures
    channel.exchange_declare(exchange='temperaturas', exchange_type='fanout')

    # Create a unique, temporary queue for this consumer
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Bind the temporary queue to the exchange
    channel.queue_bind(exchange='temperaturas', queue=queue_name)

    # Set up a consumer for the bound queue
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)

    print('Aguardando mensagens...')
    channel.start_consuming()

if __name__ == "__main__":
    try:
        consumir_sem_ack()
    except KeyboardInterrupt:
        print("\nConsumo encerrado.")
    finally:
        conn.close()  # Close the connection to the database when the process ends

