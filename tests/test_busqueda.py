# tests/test_busqueda.py
import os
import logging
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuración de Logging ---
log_filename = f"test_busqueda_log_{int(time.time())}.log"
log_filepath = os.path.join(os.path.dirname(__file__), log_filename)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filepath),
        logging.StreamHandler()
    ]
)
# --- Fin de configuración de Logging ---

# --- Configuración para Docker Compose ---
SELENIUM_HUB_URL = os.getenv('SELENIUM_HUB_URL', 'http://localhost:4444/wd/hub')

chrome_options = Options()
chrome_options.add_argument("--headless") # Ejecutar Chrome sin interfaz gráfica
chrome_options.add_argument("--no-sandbox") # Necesario en Docker para evitar errores de permisos
chrome_options.add_argument("--disable-dev-shm-usage") # Evita problemas de memoria compartida en Docker
# --- Fin de configuración para Docker Compose ---

driver = None
test_steps_data = [] # Lista para almacenar la información de cada paso de la prueba
test_status = "FALLO" # Estado inicial de la prueba

# Función auxiliar para registrar pasos y tomar capturas de pantalla
def log_step(driver_instance, description, step_type="INFO"):
    timestamp = time.time()
    screenshot_name = f"step_screenshot_{int(timestamp)}.png"
    screenshot_path = os.path.join(os.path.dirname(__file__), screenshot_name)

    # Solo tomar captura de pantalla si el driver está activo
    if driver_instance:
        try:
            driver_instance.save_screenshot(screenshot_path)
            logging.info(f"{description} - Captura: {screenshot_name}")
        except Exception as e:
            logging.warning(f"No se pudo tomar captura de pantalla para '{description}': {e}")
            screenshot_name = "N/A" # Marcar como no disponible si falla
    else:
        screenshot_name = "N/A"

    step_info = {
        "timestamp": timestamp,
        "description": description,
        "type": step_type,
        "screenshot": screenshot_name,
        "url": driver_instance.current_url if driver_instance else "N/A"
    }
    test_steps_data.append(step_info)
    logging.info(description) # También loguear en el archivo de texto/consola

# --- Nueva función para generar el informe HTML ---
def generate_html_report(report_data):
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'report_template.html')
    output_filename = f"final_report_{int(time.time())}.html"
    output_filepath = os.path.join(os.path.dirname(__file__), output_filename) # Guarda el HTML en tests/

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_template = f.read()

        # Convertir los datos de la prueba a una cadena JSON segura para incrustar en HTML
        json_data_str = json.dumps(report_data, indent=4)

        # Inyectar los datos JSON en el script del HTML
        # Busca la línea: const testReportData = window.testReportData;
        # Y la reemplaza por: const testReportData = { ...datos_json... };
        final_html = html_template.replace(
            "const testReportData = window.testReportData;",
            f"const testReportData = {json_data_str};"
        )

        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(final_html)
        logging.info(f"Informe HTML generado en: {output_filepath}")
    except FileNotFoundError:
        logging.error(f"Error: La plantilla '{template_path}' no fue encontrada. Asegúrate de que 'report_template.html' esté en la raíz de tu proyecto.")
    except Exception as e:
        logging.error(f"Error al generar el informe HTML: {e}", exc_info=True)


try:
    log_step(None, "Iniciando prueba de búsqueda en DuckDuckGo.") # No hay driver aún

    logging.info(f"Conectándose a Selenium Hub en: {SELENIUM_HUB_URL}")
    driver = webdriver.Remote(
        command_executor=SELENIUM_HUB_URL,
        options=chrome_options
    )
    log_step(driver, "Navegador lanzado con éxito en el nodo de Chrome.")

    driver.get("https://duckduckgo.com/")
    log_step(driver, f"Abriendo {driver.current_url}")

    # Esperar hasta que el campo de búsqueda esté presente y sea interactuable
    wait = WebDriverWait(driver, 10) # Espera hasta 10 segundos
    buscador = wait.until(EC.presence_of_element_located((By.NAME, "q")))
    log_step(driver, "Campo de búsqueda encontrado.")

    buscador.send_keys("inmuebles en Bogotá")
    log_step(driver, "Texto 'inmuebles en Bogotá' ingresado en el campo de búsqueda.")
    buscador.send_keys(Keys.RETURN)
    log_step(driver, "Presionada la tecla ENTER para iniciar la búsqueda.")

    # Esperar explícitamente a que aparezca al menos un resultado.
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".results--main .result__url")))
    log_step(driver, "Resultados de búsqueda cargados.")

    # Validar que exista algún resultado una vez que la espera ha terminado
    resultados = driver.find_elements(By.CSS_SELECTOR, ".results--main .result__url")
    assert len(resultados) > 0, "No se encontraron resultados para 'inmuebles en Bogotá'."
    log_step(driver, f"Validación: Se encontraron {len(resultados)} resultados. Prueba exitosa.", step_type="ÉXITO")
    test_status = "ÉXITO" # Marcar la prueba como exitosa

except Exception as e:
    # Registra el error en el log con información de la pila (stacktrace)
    logging.error(f"Ocurrió un error durante la prueba: {e}", exc_info=True)
    log_step(driver, f"Error en la prueba: {e}", step_type="ERROR")
finally:
    # Preparar los datos finales del reporte
    report_data = {
        "test_name": "Búsqueda en DuckDuckGo",
        "status": test_status,
        "start_time": test_steps_data[0]["timestamp"] if test_steps_data else time.time(),
        "end_time": time.time(),
        "steps": test_steps_data
    }

    # Generar el informe HTML con los datos incrustados
    generate_html_report(report_data)

    if driver:
        driver.quit()
        logging.info("Navegador cerrado.")
