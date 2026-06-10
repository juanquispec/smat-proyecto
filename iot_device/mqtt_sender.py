import paho.mqtt.client as mqtt
import json
import time
import random

BROKER = "broker.hivemq.com" 
PORT = 1883
TOPIC = "fisi/smat/estaciones/1"

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT)

print("📡 Estación SMAT activada. Iniciando transmisión MQTT...")

try:
    while True:
        payload = {
            "valor": round(random.uniform(20.0, 60.0), 2),
            "timestamp": time.time()
        }
        
        client.publish(TOPIC, json.dumps(payload))
        print(f"Enviado por MQTT: {payload}")
        
        time.sleep(10)
        
except KeyboardInterrupt:
    print("\n🛑 Apagando estación SMAT...")
finally:
    client.disconnect()
