Ecosistema SMAT (Digital Twin & IoT Ecosystem)

Este repositorio contiene la solución completa de telemetría y monitoreo ambiental SMAT (Sistema de Monitoreo de Alerta Temprana) para la Facultad de Ingeniería de Sistemas e Informática (FISI) de la Universidad Nacional Mayor de San Marcos (UNMSM).

El proyecto es un monorepo distribuido en tres grandes componentes:

/backend: API robusta en FastAPI integrada con base de datos SQLite (SQLAlchemy) y protección mediante autenticación JWT.

/mobile: Aplicación móvil multiplataforma desarrollada en Flutter con arquitectura de consumo de APIs segura, control de resiliencia ante errores de conexión y un dashboard adaptativo.

/iot_device: Emulador de dispositivo de hardware IoT inteligente (Edge Computing) que reporta niveles de agua en tiempo real bajo frecuencias de envío dinámicas.

📂 Estructura del Proyecto

smat-ecosystem/
├── .gitignore               # Exclusiones de Git (evita subir build/, venv/, etc.)
├── README.md                # Esta guía de usuario
├── backend/                 # Código del Servidor API
│   ├── auth.py              # Módulo criptográfico y validación JWT
│   ├── database.py          # Configuración de SQLite & SQLAlchemy
│   ├── main.py              # Endpoints, Middlewares (CORS) y ejecución
│   ├── models.py            # Modelos del ORM (Estaciones y Lecturas)
│   └── schemas.py           # Esquemas de validación de datos Pydantic
├── mobile/                  # Código de la Aplicación Móvil
│   ├── lib/
│   │   ├── main.dart        # Interfaz principal, diálogos CRUD y lógica de riesgo
│   │   ├── crear_estacion.dart # Pantalla de formulario para nuevas estaciones
│   │   ├── models/          # Modelos de datos en Dart
│   │   └── services/        # Consumo HTTP y gestión de token JWT silencioso
│   └── test/                # Pruebas automatizadas de la aplicación móvil
└── iot_device/              # Sensor de Hardware Emulado
    └── sensor_emitter.py    # Script de telemetría automatizada con lógica de alerta


🛠️ Requisitos Previos

Antes de ejecutar los servicios, asegúrate de tener instalado en tu sistema:

Python 3.10 o superior

Flutter SDK 3.x

Google Chrome (para pruebas de desarrollo Web)

🚀 Guía de Ejecución Paso a Paso

Para probar el sistema completo sincronizado en tiempo real, deberás abrir tres terminales separadas en tu computadora.

Paso 1: Levantar el Backend (Servidor)

Abre tu terminal y navega a la carpeta del backend:

cd backend


Instala las librerías necesarias de Python (si aún no lo has hecho):

pip install fastapi uvicorn sqlalchemy pyjwt passlib requests


Ejecuta el servidor de desarrollo:

uvicorn main:app --reload


El servidor quedará encendido en el puerto local: http://127.0.0.1:8000
Puedes ingresar a la documentación interactiva e inyectar datos desde: http://127.0.0.1:8000/docs

Paso 2: Iniciar el Sensor Virtual (Dispositivo IoT)

El sensor simula a un microcontrolador físico (como un ESP32) enviando lecturas del nivel de agua del río de forma automatizada hacia el backend.

Abre una segunda terminal y navega a la carpeta del dispositivo IoT:

cd iot_device


Instala el módulo HTTP para Python:

pip install requests


Ejecuta el script del sensor:

python sensor_emitter.py


Lógica del Reto de Alerta de Desborde: El script solicitará un token JWT seguro al endpoint /api/usuarios/login del backend. Si el sensor reporta valores normales (< 70 cm), enviará datos cada 10 segundos. En caso el nivel del agua supere el umbral crítico de peligro (> 70 cm), activará la 🚨 ALERTA en consola y acelerará la tasa de envío a cada 2 segundos (Modo Emergencia).

Paso 3: Lanzar la Aplicación Móvil (Flutter)

Por facilidad de pruebas y velocidad de depuración, la aplicación se ejecutará de forma directa sobre Google Chrome (Web).

Abre una tercera terminal y navega a la carpeta de la app móvil:

cd mobile


Descarga y sincroniza los paquetes de Flutter:

flutter pub get


Ejecuta la aplicación desactivando la seguridad web del navegador. Esto es indispensable para evadir bloqueos de CORS generados por iFrames locales en navegadores en modo debug:

flutter run -d chrome --web-browser-flag "--disable-web-security"


📊 Demostración de Flujos de Pruebas (Checklist Evaluativo)

Puedes verificar el éxito total de tus laboratorios validando los siguientes comportamientos en vivo:

A. Interoperabilidad (CRUD en Vivo)

Presiona el botón flotante azul + de la App de Flutter.

Registra una nueva estación llenando el ID, Nombre y Ubicación.

Al pulsar "Guardar", se enviará la petición POST con cabecera JWT Bearer autorizada. La app regresará automáticamente y la estación aparecerá en la lista al instante.

Si consultas el Swagger de FastAPI o la base de datos smat.db, el nuevo registro ya se encontrará allí de forma persistente.

B. Indicadores de Alerta Temprana (Reto Mobile)

Deja el emulador sensor_emitter.py funcionando en la terminal para el ID de estación 10.

Al pulsar el botón de refrescar 🔄 (esquina superior derecha de la App), el ícono del satélite de la estación 10 cambiará dinámicamente de color:

Verde (NORMAL): Si la telemetría reportada por el sensor es inferior a 20.0 cm.

Naranja (ALERTA): Si la telemetría se encuentra entre 20.0 cm y 50.0 cm.

Rojo (PELIGRO): Si la telemetría supera los 50.0 cm.

C. Resiliencia y Control de Red

Apaga el servidor de Python en la terminal 1 (Ctrl + C).

Ve a tu App de Flutter en Chrome y presiona el botón de refrescar 🔄.

Gracias al sistema timeout de 5 segundos y bloque try-catch, la app no se congelará. Mostrará una pantalla muy pulida con un ícono de Wi-Fi desconectado, un mensaje amigable al usuario y un botón de "Reintentar" para reconectarse en cuanto el servidor vuelva a estar en línea.

⚙️ Resolución de Errores Comunes

1. Error OperationalError: attempt to write a readonly database en Python

Este error de SQLite sucede si la base de datos se bloqueó en modo lectura por visores externos o por ejecución sin credenciales suficientes.

Solución: Apaga el backend (Ctrl + C), elimina físicamente el archivo smat.db de tu carpeta /backend, y vuelve a arrancar tu terminal de comandos con permisos de Administrador antes de encender uvicorn nuevamente.