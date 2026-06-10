import paho.mqtt.client as mqtt
import requests
import json
import time
import threading

# CONFIGURACIÓN SMAT
BROKER = "broker.hivemq.com"
TOPIC = "fisi/smat/estaciones/#"

# Configuración del Backend HTTP
API_BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{API_BASE_URL}/lecturas/"

# --- CONFIGURACIÓN DE AUTENTICACIÓN AUTOMÁTICA ---
# Cambia "/token" o "/login" según cómo se llame el endpoint en tu FastAPI
LOGIN_URL = f"{API_BASE_URL}/token" 
API_USER = "tu_usuario"       # Reemplaza con un usuario válido en tu BD
API_PASSWORD = "tu_password"  # Reemplaza con la contraseña de ese usuario

# Variables globales
last_seen = {}
auth_token = None # Aquí se guardará el token generado

def obtener_token():
    """Función que se loguea en FastAPI para obtener el JWT dinámicamente."""
    global auth_token
    print("🔐 Autenticando con el Backend para generar Token JWT...")
    
    # FastAPI con OAuth2 espera datos de formulario (x-www-form-urlencoded)
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

# Hilo para monitorear estaciones caídas (Lógica de Resiliencia)
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
        
        estacion_id = msg.topic.split('/')[-1]
        last_seen[estacion_id] = time.time()
        
        data_to_send = {
            "valor": payload["valor"],
            "estacion_id": int(estacion_id)
        }
        
        # Enviar usando el token generado automáticamente
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(API_URL, json=data_to_send, headers=headers)
        
        if response.status_code in [200, 201]:
            print(f"✅ Dato persistido en DB para estación {estacion_id}")
        # Si el token expiró (ej: status 401), intentamos renovarlo
        elif response.status_code == 401:
            print("🔄 El token expiró. Renovando...")
            obtener_token()
        else:
            print(f"❌ Error API ({response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"❌ Error procesando mensaje: {e}")

def main():
    # 1. Autenticarse ANTES de escuchar MQTT
    obtener_token()
    
    # 2. Lanzar el hilo de monitoreo en segundo plano
    threading.Thread(target=check_deadlines, daemon=True).start()
    
    # 3. Configuración del Cliente MQTT
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    
    print("🌉 Bridge SMAT iniciado. Esperando datos...")
    client.connect(BROKER, 1883)
    client.subscribe(TOPIC)
    client.loop_forever()

if __name__ == "__main__":
    main()