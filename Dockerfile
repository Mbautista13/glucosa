# Usa una imagen oficial de Python como base
FROM python:3.10-slim

# Instala Octave y dependencias necesarias
RUN apt-get update && \
    apt-get install -y octave && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copia los archivos de tu proyecto al contenedor
WORKDIR /app
COPY . /app

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expón el puerto que usa tu app (ajusta si usas otro)
EXPOSE 5000

# Comando para iniciar tu aplicación (ajusta si usas otro)
CMD ["python", "app.py"]
