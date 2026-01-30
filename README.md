# Security Awareness Platform (Phishing Simulator)

Este proyecto es una plataforma integral de simulación de phishing diseñada para evaluar y mejorar la conciencia de seguridad dentro de una organización. Permite a los administradores crear, gestionar y rastrear campañas de phishing simuladas, proporcionando métricas detalladas y educación inmediata a los usuarios que caen en la simulación.

## 🚀 Propósito

El objetivo principal es educativo y preventivo. La herramienta ayuda a:

- Identificar vulnerabilidades en el comportamiento de los empleados frente a correos de phishing.
- Entrenar a los usuarios mediante la exposición práctica a ataques simulados.
- Medir la efectividad de los programas de concientización de seguridad a lo largo del tiempo.

## ✨ Características Principales

- **Gestión de Campañas**: Creación y orquestación de campañas de phishing enviadas por correo electrónico.
- **Seguimiento Detallado**: Monitorización de eventos clave:
  - Apertura de correo (Tracking Pixel).
  - Clic en enlaces (Landing Page).
  - Envío de credenciales (Captura de datos).
- **Captura Segura**: Las credenciales capturadas se **hashean inmediatamente** (usando bcrypt/Argon2 via Passlib) y nunca se almacenan en texto plano, garantizando la privacidad y seguridad, incluso en simulaciones.
- **Educación "Just-in-Time"**: Redirección automática a una página educativa cuando un usuario compromete sus credenciales.
- **Infraestructura Robusta**: Uso de colas de tareas asíncronas para el envío masivo de correos y la rotación de IPs.

## 🛠️ Arquitectura

El proyecto utiliza una arquitectura moderna basada en microservicios y contenedores:

- **Backend**: Python con **FastAPI** para una API RESTful de alto rendimiento.
- **Base de Datos**: **PostgreSQL** (async) para el almacenamiento persistente de campañas y resultados.
- **Colas de Tareas**: **Celery** con **Redis** para el manejo de tareas en segundo plano (envío de emails, procesamiento de eventos).
- **Proxy Inverso**: **Traefik** para el enrutamiento de tráfico y gestión automática de certificados SSL (configurado para Let's Encrypt).
- **Contenedores**: Todo el sistema está orquestado con **Docker Compose**.

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 🚀 Instalación y Uso (Docker)

La forma recomendada de desplegar la aplicación es utilizando Docker Compose.

1.  **Clonar el repositorio**:

    ```bash
    git clone https://github.com/tu-usuario/phishing-orchestrator-platform.git
    cd phishing-orchestrator-platform
    ```

2.  **Configuración de Entorno**:
    Es **CRÍTICO** configurar las variables de entorno antes de iniciar.

    ```bash
    cp .env.example .env
    ```

    Edita el archivo `.env` y define contraseñas seguras para:
    - `POSTGRES_PASSWORD`
    - `SECRET_KEY` (si aplica en el futuro)

3.  **Iniciar Servicios**:
    ```bash
    docker-compose up --build -d
    ```

## 💻 Desarrollo Local

Si deseas ejecutar la aplicación localmente para desarrollo:

1.  **Preparar Entorno Virtual**:

    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

2.  **Instalar Dependencias**:

    ```bash
    pip install -r requirements.txt
    ```

3.  **Iniciar Dependencias (DB & Redis)**:
    Puedes usar Docker solo para la infraestructura:

    ```bash
    docker-compose up -d db redis
    ```

4.  **Ejecutar Aplicación**:
    ```bash
    uvicorn app.main:app --reload
    ```

## 🧪 Pruebas

Para verificar que todo funciona correctamente, ejecuta la suite de pruebas:

1.  Asegúrate de tener las dependencias instaladas y el archivo `.env` configurado.
2.  Ejecuta `pytest`:

    ```bash
    pytest
    ```

3.  **Verificar Estado**:
    Los servicios principales estarán disponibles en:
    - **API Backend**: `http://localhost:8000` (o a través de Traefik en `http://localhost` / `https://localhost`)
    - **Traefik Dashboard**: `http://localhost:8080` (si está habilitado insecure mode)

4.  **Documentación de la API**:
    Para ver y probar los endpoints disponibles, visita la documentación interactiva generada automáticamente por Swagger UI:
    - URL: `http://localhost:8000/docs`

## 🛡️ Notas de Seguridad

- Esta herramienta debe ser utilizada **UNICAMENTE** con autorización explícita y propósitos educativos.
- El almacenamiento de credenciales, aunque sea en forma de hash, debe tratarse con la máxima sensibilidad y cumplir con las regulaciones de protección de datos aplicables.

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue o envía un pull request para mejoras o correcciones.
