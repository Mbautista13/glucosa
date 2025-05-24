from flask import Flask, render_template, request
import subprocess
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def hhmm_a_decimal(hora_str):
    try:
        partes = hora_str.split(':')
        if len(partes) == 1:
            # Si sólo ingresó hora sin minutos
            horas = int(partes[0])
            minutos = 0
        elif len(partes) == 2:
            horas = int(partes[0])
            minutos = int(partes[1])
        else:
            raise ValueError("Formato de hora inválido")
        if not (0 <= horas < 24 and 0 <= minutos < 60):
            raise ValueError("Hora o minutos fuera de rango")
        return horas + minutos / 60
    except Exception as e:
        raise ValueError(f"Error al convertir hora '{hora_str}': {str(e)}")

def decimal_a_hhmm(hora_decimal):
    horas = int(hora_decimal)
    minutos = round((hora_decimal - horas) * 60)
    return f"{horas:02d}:{minutos:02d}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/procesar', methods=['POST'])
def procesar():
    try:
        horas_str = request.form.getlist('hora[]')
        glucosas = request.form.getlist('glucosa[]')
        hora_interp_str = request.form['hora_interp']
        hora_pred_str = request.form['hora_pred']

        if len(horas_str) < 3 or len(glucosas) < 3:
            return "Debes ingresar al menos 3 puntos de glucosa."
        if not hora_interp_str or not hora_pred_str:
            return "Las horas de interpolación y predicción son obligatorias."

        try:
            horas = [hhmm_a_decimal(h) for h in horas_str]
            glucosas = [float(g) for g in glucosas]
            hora_interp = hhmm_a_decimal(hora_interp_str)
            hora_pred = hhmm_a_decimal(hora_pred_str)
        except ValueError as e:
            return f"Todos los datos deben ser numéricos y en formato válido: {str(e)}"

        data = {
            "horas": horas,
            "glucosas": glucosas,
            "hora_interp": hora_interp,
            "hora_pred": hora_pred
        }

        with open("input_data.json", "w") as f:
            json.dump(data, f)

        resultado = subprocess.run(
            ["octave", "--silent", "scripts/main.m"],
            capture_output=True,
            text=True
        )

        if resultado.returncode != 0:
            return f"Error al ejecutar Octave: {resultado.stderr}"

        lineas = resultado.stdout.strip().split("\n")
        interpolado = lineas[0].split(":")[-1].strip()
        predicho = lineas[1].split(":")[-1].strip()

        # Convertir horas decimales a formato HH:MM para mostrar bonito
        hora_interp_formato = decimal_a_hhmm(hora_interp)
        hora_pred_formato = decimal_a_hhmm(hora_pred)

        return render_template("resultado.html",
                               interpolado=interpolado,
                               predicho=predicho,
                               hora_interp=hora_interp_formato,
                               hora_pred=hora_pred_formato)

    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}")
        return f"Ocurrió un error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
