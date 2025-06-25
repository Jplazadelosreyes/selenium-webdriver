[![Selenium Python Tests with Docker](https://github.com/Jplazadelosreyes/selenium-webdriver/actions/workflows/test.yml/badge.svg)](https://github.com/Jplazadelosreyes/selenium-webdriver/actions/workflows/test.yml)
# Proyecto de Pruebas de Selenium con Python y Docker Compose

Este proyecto proporciona un entorno aislado y reproducible para ejecutar pruebas automatizadas de Selenium utilizando Python, Docker y Selenium Grid. El objetivo es simular interacciones de usuario en un navegador web (Chrome) y generar informes detallados con capturas de pantalla de cada paso.

## 🚀 Inicio Rápido

Sigue estos pasos para poner en marcha y ejecutar las pruebas en tu máquina local.

### Prerrequisitos

Asegúrate de tener instalado lo siguiente en tu sistema:

- **Git**: Para clonar el repositorio.
- **Docker Desktop** (o Docker Engine y Docker Compose): El motor de contenedores necesario para construir y ejecutar los servicios. Puedes descargarlo desde [Docker Official Site](https://www.docker.com/).

### Configuración del Proyecto

1. **Clona el Repositorio:**

```bash
git clone https://github.com/tu-usuario/tu-repositorio.git
cd tu-repositorio
```

*(Reemplaza `https://github.com/tu-usuario/tu-repositorio.git` con la URL real de tu repositorio)*

2. **Estructura de Archivos:**

Asegúrate de que la estructura de tu proyecto sea similar a esta:

```
tu-proyecto-selenium/
├── .github/
│   └── workflows/
│       └── test.yml                 # Configuración para GitHub Actions
├── Dockerfile                       # Define la imagen para tu entorno Python de pruebas
├── docker-compose.yml               # Orquesta Selenium Grid y tu servicio de pruebas
├── requirements.txt                 # Dependencias de Python (ej. `selenium`)
├── report_template.html             # Plantilla HTML para generar el informe final
└── tests/
    └── test_busqueda.py             # Tu script de pruebas de Selenium
    # Aquí se guardarán también los logs, capturas de pantalla y el informe HTML final.
```

3. **Contenido de requirements.txt:**

Este archivo debe contener las librerías de Python necesarias. Para este proyecto:

```
selenium
```

## ⚙️ Ejecución Local de las Pruebas

Para ejecutar las pruebas en tu máquina local, sigue estos comandos:

### 1. Construye las Imágenes y Levanta los Servicios

Desde el directorio raíz de tu proyecto (donde está `docker-compose.yml`), ejecuta:

```bash
docker-compose up --build
```

Este comando:
- Construirá la imagen de Docker para tu entorno Python (basada en el Dockerfile y requirements.txt).
- Descargará las imágenes oficiales de Selenium Hub y Chrome Node si no las tienes.
- Lanzará tres servicios: `selenium-hub` (el orquestador de Selenium Grid), `chrome-node` (el navegador Chrome en modo headless) y `python-tests` (tu contenedor Python que ejecuta el script `test_busqueda.py`).
- La opción `--build` asegura que Docker reconstruya tus imágenes, lo cual es útil si has hecho cambios en el Dockerfile o requirements.txt.

### 2. Observa la Salida

Verás los logs de todos los servicios en tu terminal. Presta atención a la sección de logs del servicio `python-selenium-tests`, ya que es la salida de tu script de prueba.

> **Nota**: Mensajes esperados del chrome-node: Es normal ver mensajes como `exited: xvfb, vnc, novnc`, y `gave up` en el log del chrome-node. Esto se debe a que el nodo de Chrome está configurado para ejecutarse en modo headless (`SE_VNC_ENABLED=false`, `SE_START_XVFB=false`), deshabilitando intencionalmente las herramientas de interfaz gráfica que vienen por defecto en la imagen. Estos mensajes indican que esas herramientas no se están ejecutando, lo cual es el comportamiento deseado para la automatización.

### 3. Accede a los Resultados y el Informe

Una vez que la ejecución del `python-tests` termine (verás `python-selenium-tests exited with code 0` si todo fue bien), se habrán generado los archivos de resultados:

- **Archivo de Log**: `tests/test_busqueda_log_*.log`
- **Informe HTML**: `tests/final_report_*.html`
- **Capturas de Pantalla**: `tests/step_screenshot_*.png` y `tests/error_screenshot_*.png`

Gracias al mapeo de volúmenes en `docker-compose.yml` (`./tests:/app/tests`), estos archivos se guardan directamente en tu carpeta local `tests/`.

Para ver el informe, simplemente abre el archivo `tests/final_report_XXXX.html` (donde XXXX es un timestamp numérico) en tu navegador web preferido. Este informe contendrá una línea de tiempo de cada paso, sus descripciones, la URL en ese momento y miniaturas de las capturas de pantalla tomadas.

### 4. Detén los Servicios

Para detener todos los servicios de Docker Compose, presiona `Ctrl + C` en la terminal donde los iniciaste.

## 🚀 Integración Continua con GitHub Actions

Este proyecto está configurado para la integración continua (CI) utilizando GitHub Actions, lo que automatizará la ejecución de tus pruebas cada vez que hagas un push a la rama principal (o manualmente).

### ¿Cómo Funciona test.yml?

El archivo `.github/workflows/test.yml` define el flujo de trabajo de GitHub Actions:

- **name: Selenium Python Tests with Docker**: El nombre que verás en la pestaña "Actions" de tu repositorio.
- **on: push**: El flujo de trabajo se activará automáticamente cada vez que se haga un push a las ramas `main` o `master`.
- **on: workflow_dispatch**: Permite iniciar el flujo de trabajo manualmente desde la interfaz web de GitHub Actions.
- **jobs.run-tests**: Define un único trabajo que se ejecutará.
- **runs-on: ubuntu-latest**: El trabajo se ejecutará en una máquina virtual Linux (Ubuntu) proporcionada por GitHub, que ya tiene Docker y Docker Compose preinstalados.

#### Steps (Pasos):

1. **Checkout Repository**: Clona tu código en la máquina virtual de GitHub.
2. **Set up Docker Buildx / Set up QEMU**: Pasos opcionales para una construcción de Docker más avanzada/compatible con múltiples arquitecturas.
3. **Build and Run Docker Compose Services**: Ejecuta `docker-compose up --build --abort-on-container-exit`. Este es el paso clave que levanta tu entorno de Selenium y ejecuta tus pruebas. `--abort-on-container-exit` detiene el Compose si el contenedor de pruebas (`python-tests`) sale.
4. **Show Python Test Logs**: Muestra los logs completos de tu contenedor `python-tests` directamente en la salida del flujo de trabajo de GitHub Actions.
5. **Upload Test Reports and Screenshots**: Después de que las pruebas se completen, este paso recopila automáticamente todos los archivos de log, informes HTML y capturas de pantalla generados en la carpeta `tests/` y los adjunta como "artefactos" a la ejecución del flujo de trabajo.

### Visualización de los Resultados en GitHub Actions

1. Después de hacer un push a tu rama `main` (o ejecutarlo manualmente a través de `workflow_dispatch`), ve a la pestaña "Actions" de tu repositorio en GitHub.

2. Haz clic en la ejecución del flujo de trabajo más reciente (tendrá el nombre `Selenium Python Tests with Docker`).

3. En la página de resumen de la ejecución, verás los diferentes pasos y sus logs. Puedes expandir el paso `Show Python Test Logs` para ver la salida de tu script de prueba.

4. Para descargar los informes y capturas de pantalla, busca la sección "Artifacts" (normalmente en la parte inferior de la página de resumen de la ejecución). Allí encontrarás un archivo `.zip` con un nombre como `selenium-test-results-XXXX.zip` (donde XXXX es el ID de la ejecución). Descárgalo, descomprímelo, y podrás abrir el `final_report_*.html` para ver el informe.

## 📝 Conclusión

¡Listo! Con esta documentación, cualquier persona debería poder entender, configurar y ejecutar tus pruebas de Selenium tanto en local como en GitHub Actions de forma automatizada.
