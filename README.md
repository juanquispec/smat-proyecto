# 🌊 Ecosistema SMAT 
Este repositorio contiene la solución completa de telemetría y monitoreo ambiental **SMAT** (Sistema de Monitoreo de Alerta Temprana)

El proyecto está diseñado bajo una arquitectura de Monorepo distribuido en tres grandes componentes interactivos:

* 🚀 **/backend**: API robusta construida con FastAPI, integrada a una base de datos SQLite (SQLAlchemy ORM) y protegida de extremo a extremo mediante autenticación basada en tokens JWT.
* 📱 **/mobile**: Aplicación móvil multiplataforma desarrollada en Flutter. Implementa consumo seguro de APIs con inyección de cabeceras de autorización, control estricto de resiliencia (timeouts/fallos de red) y un dashboard dinámico.
* 📟 **/iot_device**: Emulador de hardware IoT inteligente (Edge Computing en Python) que simula sensores físicos, reportando telemetría en tiempo real con frecuencias de envío dinámicas.

---

## 📂 Estructura del Proyecto

```text
smat-ecosystem/
├── .gitignore               # Exclusiones de Git (build/, venv/, etc.)
├── README.md                # Esta guía de usuario optimizada
├── backend/                 # Código del Servidor API (Python)
│   ├── auth.py              # Módulo criptográfico y validación JWT
│   ├── database.py          # Configuración de conexiones SQLite & SQLAlchemy
│   ├── main.py              # Endpoints principales, controladores de CORS y lógica de negocio
│   ├── models.py            # Modelos de tablas de Base de Datos (Estaciones y Lecturas)
│   └── schemas.py           # Esquemas de validación de datos Pydantic
├── mobile/                  # Aplicación Móvil / Web (Flutter)
│   ├── lib/
│   │   ├── main.dart        # Dashboard principal, formularios CRUD y semáforo de riesgos
│   │   ├── crear_estacion.dart # Interfaz de formulario para el registro de estaciones
│   │   ├── models/          # Entidades y mapeadores de datos en Dart
│   │   └── services/        # Cliente HTTP y gestión automática del Token JWT
│   └── test/                # Pruebas de integración y testing de widgets
└── iot_device/              # Sensor Remoto Emulado
    └── sensor_emitter.py    # Script de telemetría automatizada con lógica de alerta adaptativa
```
## 🛠️ Requisitos Previos

Antes de proceder con la inicialización del ecosistema, asegúrate de contar con el siguiente entorno instalado:

| Herramienta / Tecnología | Versión Requerida | Propósito |
| :--- | :--- | :--- |
| **Python** | 3.10 o superior | Entorno de ejecución para Backend e IoT |
| **Flutter SDK** | 3.x o superior | Compilación de la interfaz de usuario |
| **Google Chrome** | Última versión | Target ideal para la ejecución del cliente móvil en modo debug |
## 🚀 Guía de Ejecución Paso a Paso

> [!IMPORTANT]
> Para visualizar el flujo de datos sincronizado en tiempo real, es indispensable que abras **tres terminales o pestañas de comandos independientes** en tu sistema operativo.

### 1️⃣ Paso 1: Levantar el Backend (Servidor API)

Navega hacia la sección del servidor:
```Bash
cd backend
```
Instala las dependencias principales del ecosistema de Python (si aún no los instalaste):
```Bash
pip install fastapi uvicorn sqlalchemy pyjwt passlib requests
```
Arranca el motor del servidor local con autorecarga habilitada:
```Bash
uvicorn main:app --reload
```
🖥️ API Host: http://127.0.0.1:8000

📄 Swagger Interactive UI: http://127.0.0.1:8000/docs

2️⃣ Paso 2: Iniciar el Sensor Virtual (Dispositivo IoT)
Desplázate hacia el directorio del dispositivo perimetral:
```Bash
cd iot_device
```
Instala la dependencia de transporte de red HTTP:
```Bash
pip install requests
```
Ejecuta el script emulador del microcontrolador:
```Bash
python sensor_emitter.py
```
>[!NOTE]
>El script se autentica automáticamente en /api/usuarios/login para adquirir su firma JWT. Si detecta valores estables (< 70.0 cm), transmite datos de forma pasiva cada 10 segundos. Si el nivel hídrico rompe el umbral de peligro (> 70.0 cm), dispara una 🚨 ALERTA visual por consola y acelera las ráfagas de envío a cada 2 segundos (Modo Emergencia).

3️⃣ Paso 3: Lanzar la Aplicación Móvil (Flutter)
Para optimizar los tiempos de despliegue y saltearse dependencias de emuladores móviles, compilaremos el entorno sobre la plataforma Web (Chrome).

Ingresa a la carpeta del frontend:
```Bash
cd mobile
```
Restaura los paquetes de Flutter definidos en el archivo pubspec.yaml:
```Bash
flutter pub get
```
Lanza la aplicación desactivando temporalmente las restricciones de políticas de origen cruzado en el navegador local. (Paso crítico para eludir bloqueos CORS accidentales en localhost):
```Bash
flutter run -d chrome --web-browser-flag "--disable-web-security"
```
## 📊 Demostración de Flujos de Pruebas (Checklist Evaluativo)

Verifica que el flujo integrado de datos funcione de extremo a extremo comprobando los siguientes hitos en tu pantalla:

### A. Interoperabilidad (Acciones CRUD en Vivo)
1. Haz clic en el botón de acción flotante azul `+` dentro del cliente de Flutter.
2. Ingresa los valores solicitados para una estación inédita (ID, Nombre, Ubicación) y guárdala.
3. La aplicación enviará el payload vía `POST` insertando el token Bearer en el Header. Al completarse, la tabla se actualizará automáticamente mostrando la nueva estación sin necesidad de reiniciar la app.
4. Los datos quedarán inmediatamente guardados en la persistencia local de `smat.db`.

### B. Semáforo de Riesgo (Indicadores de Alerta Temprana)
1. Mantén corriendo el script `sensor_emitter.py` apuntando al ID de estación 10.
2. Pulsa el comando de actualización manual 🔄 ubicado en el extremo superior derecho del menú móvil.
3. El ícono de la antena satelital mutará dinámicamente según la severidad del último registro extraído de la telemetría:
   * 🟢 **Verde (NORMAL):** Lecturas estables inferiores a 20.0 cm.
   * 🟠 **Naranja (ALERTA):** Lecturas moderadas posicionadas entre 20.0 cm y 50.0 cm.
   * 🔴 **Rojo (PELIGRO):** Lecturas críticas que superan el límite de 50.0 cm.

### C. Mecanismos de Resiliencia ante Caídas de Red
1. Simula un fallo masivo apagando repentinamente el Backend en tu terminal principal mediante la combinación `Ctrl + C`.
2. Regresa al cliente web en Flutter e intenta refrescar el listado 🔄.
3. La aplicación mitigará el error mediante el controlador timeout integrado (límite de 5s). En lugar de congelar la pantalla, renderizará un modal limpio advirtiendo sobre la desconexión del servidor y ofreciendo un botón interactivo de "Reintentar".

---

## ⚙️ Resolución de Errores Comunes

❌ **Error `OperationalError: attempt to write a readonly database` en Python**
Ocurre cuando el motor de SQLite se bloquea en modo de solo lectura por haber sido inspeccionado por herramientas externas (como DB Browser for SQLite) o por un conflicto de privilegios en el guardado local.
💡 **Solución:** Cierra cualquier visor externo de base de datos. Detén el servidor uvicorn (`Ctrl + C`), remueve completamente el archivo físico `smat.db` de tu entorno `/backend`, y vuelve a ejecutar tu terminal de comandos con Privilegios de Administrador antes de encender el backend de nuevo.

# El proyecto aún está en proceso
