import requests
import time
import random

# CONFIGURACIÓN
API_URL = "http://127.0.0.1:8000/lecturas/"
TOKEN_URL = "http://127.0.0.1:8000/token"

# Cambia este ID si tu estación de prueba tiene un número distinto
ESTACION_ID = 1 

def obtener_token():
    try:
        # Usamos el usuario admin que configuraste en tu backend
        respuesta = requests.post(TOKEN_URL, json={"username": "admin", "password": "admin"})
        if respuesta.status_code == 200:
            return respuesta.json().get("access_token")
    except:
        pass
    return None

def enviar_telemetria():
    print("=========================================")
    print(" Iniciando Sensor IoT Virtual SMAT ")
    print("=========================================")
    
    # 1. Obtener la llave para entrar al backend
    token = obtener_token()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    while True:
        # Simulamos una lectura de nivel de agua (entre 40.0 cm y 90.0 cm)
        nivel_agua = round(random.uniform(40.0, 90.0), 2)
        
        payload = {
            "estacion_id": ESTACION_ID,
            "valor": nivel_agua
        }
        
        # 2. Enviar el dato al servidor
        try:
            respuesta = requests.post(API_URL, json=payload, headers=headers)
            if respuesta.status_code in [200, 201]:
                print(f"[OK] Dato enviado: {nivel_agua} cm")
            else:
                print(f"[ERROR] Código {respuesta.status_code}: {respuesta.text}")
        except Exception as e:
            print(f"[CRÍTICO] No hay conexión con el servidor: {e}")

        # ---------------------------------------------------------
        # RETO DE LA SEMANA 9: "Alerta de Desborde"
        # ---------------------------------------------------------
        if nivel_agua > 70.0:
            # 1. Lógica de Alarma en consola
            print("🚨 [ALERTA] Umbral de inundación superado.")
            # 2. Frecuencia Dinámica: Modo Emergencia (cada 2 segundos)
            tiempo_espera = 2
        else:
            # Frecuencia Dinámica: Modo Normal (cada 10 segundos)
            tiempo_espera = 10
            
        print(f"⏳ Esperando {tiempo_espera} segundos...\n")
        time.sleep(tiempo_espera)

if __name__ == "__main__":
    enviar_telemetria()