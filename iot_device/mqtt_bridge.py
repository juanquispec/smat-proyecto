import paho.mqtt.client as mqtt
import requests
import json
import time
import threading

BROKER = "broker.hivemq.com"
TOPIC = "fisi/smat/estaciones/#"
API_BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{API_BASE_URL}/lecturas/"

LOGIN_URL = f"{API_BASE_URL}/token" 
API_USER = "tu_usuario"       
API_PASSWORD = "tu_password"  


last_seen = {}
auth_token = None 

def obtener_token():
    """Función que se loguea en FastAPI para obtener el JWT dinámicamente."""
    global auth_token
    print("🔐 Autenticando con el Backend para generar Token JWT...")
    
    credenciales = {
        "username": API_USER,
        "password": API_PASSWORD
    }
    
    try:
        response = requests.post(LOGIN_URL, data=credenciales)
        if response.status_code == 200:
            auth_token = response.json().get("access_token")
            print("✅ Token obtenido con éxito. ¡Bridge autorizado!")
        else:
            print(f"❌ Error de autenticación ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ No se pudo conectar al Backend para el Login: {e}")

def check_deadlines():
    while True:
        current_time = time.time()
        for eid, t in list(last_seen.items()):
            if current_time - t > 30: 
                print(f"⚠️ ALERTA: Estación {eid} está OFFLINE")
        time.sleep(10)

def on_message(client, userdata, msg):
    try:
        if not auth_token:
            print("⏳ Ignorando mensaje, aún no hay token de autorización...")
            return

        payload = json.loads(msg.payload.decode())
        print(f"\n📥 Mensaje recibido en {msg.topic}: {payload}")
        
        partes_topico = msg.topic.split('/')
        
        estacion_id = None
        for parte in partes_topico:
            if parte.isdigit():
                estacion_id = parte
                break

        if not estacion_id:
            print(f"⚠️ No se pudo encontrar un ID numérico en el tópico: {msg.topic}")
            return
        last_seen[estacion_id] = time.time()
        
        data_to_send = {
            "valor": payload["valor"],
            "estacion_id": int(estacion_id)
        }
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(API_URL, json=data_to_send, headers=headers)
        
        if response.status_code in [200, 201]:
            print(f"✅ Dato persistido en DB para estación {estacion_id}")
        elif response.status_code == 401:
            print("🔄 El token expiró. Renovando...")
            obtener_token()
        else:
            print(f"❌ Error API ({response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"❌ Error procesando mensaje: {e}")

def main():

    obtener_token()
    
    threading.Thread(target=check_deadlines, daemon=True).start()

    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    
    print("🌉 Bridge SMAT iniciado. Esperando datos...")
    client.connect(BROKER, 1883)
    client.subscribe(TOPIC)
    client.loop_forever()

if __name__ == "__main__":
    main()
