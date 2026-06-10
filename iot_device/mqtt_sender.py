import paho.mqtt.client as mqtt
import json
import time
import random

# Configuración basada en el proyecto SMAT
BROKER = "broker.hivemq.com" # Broker público para pruebas
PORT = 1883
TOPIC = "fisi/smat/estaciones/1"

# Inicialización con la API V2 para evitar advertencias de la librería
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT)

print("📡 Estación SMAT activada. Iniciando transmisión MQTT...")

try:
    while True:
        # Generamos valores simulados entre 20.0 y 60.0 según el laboratorio
        payload = {
            "valor": round(random.uniform(20.0, 60.0), 2),
            "timestamp": time.time()
        }
        
        # Publicar datos en el Topic de SMAT
        client.publish(TOPIC, json.dumps(payload))
        print(f"Enviado por MQTT: {payload}")
        
        # El sensor espera 10 segundos antes de enviar el siguiente dato
        time.sleep(10)
        
except KeyboardInterrupt:
    print("\n🛑 Apagando estación SMAT...")
finally:
    client.disconnect()