# Usa una imagen base de Python oficial. La versión 'slim-buster' es ligera.
FROM python:3.9-slim-buster

# Establece el directorio de trabajo dentro del contenedor.
WORKDIR /app

# Copia el archivo de requisitos e instala las dependencias de Python.
# Esto se hace primero para aprovechar el cacheado de capas de Docker.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de tu aplicación (tus scripts de prueba, etc.).
# Asumimos que tus pruebas estarán en una subcarpeta 'tests' dentro de '/app'.
COPY . .

# Comando por defecto para ejecutar un script de prueba de ejemplo.
# Puedes cambiar esto a lo que necesites para tus pruebas.
# Nota: La ejecución real se definirá en docker-compose.yml
CMD ["python", "tests/example_test.py"]
