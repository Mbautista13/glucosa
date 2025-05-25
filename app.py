from flask import Flask, render_template, request
import logging
import numpy as np

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def hhmm_a_decimal(hora_str):
    try:
        partes = hora_str.split(':')
        horas = int(partes[0])
        minutos = int(partes[1])
        if not (0 <= horas < 24 and 0 <= minutos < 60):
            raise ValueError("Hora o minutos fuera de rango")
        return horas + minutos / 60
    except Exception as e:
        raise ValueError(f"Error al convertir hora '{hora_str}': {str(e)}")

def decimal_a_hhmm(hora_decimal):
    horas = int(hora_decimal)
    minutos = round((hora_decimal - horas) * 60)
    return f"{horas:02d}:{minutos:02d}"

def lagrange(x, y, xi):
    n = len(x)
    yi = 0
    for i in range(n):
        L = 1
        for j in range(n):
            if i != j:
                L *= (xi - x[j]) / (x[i] - x[j])
        yi += y[i] * L
    return yi

def regresion(x, y):
    x = np.array(x)
    y = np.array(y)
    n = len(x)
    m = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - (np.sum(x))**2)
    b = (np.sum(y) - m * np.sum(x)) / n
    return m, b

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/procesar', methods=['POST'])
def procesar():
    try:
        horas_str = request.form.getlist('hora[]')
        glucosas = request.form.getlist('glucosa[]')
        hora_interp_str = request.form.get('hora_interp')
        hora_pred_str = request.form.get('hora_pred')

        if len(horas_str) < 3 or len(glucosas) < 3:
            return "Debes ingresar al menos 3 puntos de glucosa."

        horas = [hhmm_a_decimal(h) for h in horas_str]
        glucosas = [float(g) for g in glucosas]

        resultado_interp = None
        resultado_pred = None
        hora_interp_fmt = None
        hora_pred_fmt = None

        if hora_interp_str:
            hora_interp = hhmm_a_decimal(hora_interp_str)
            resultado_interp = lagrange(horas, glucosas, hora_interp)
            hora_interp_fmt = decimal_a_hhmm(hora_interp)

        if hora_pred_str:
            hora_pred = hhmm_a_decimal(hora_pred_str)
            m, b = regresion(horas, glucosas)
            resultado_pred = m * hora_pred + b
            hora_pred_fmt = decimal_a_hhmm(hora_pred)

        return render_template("resultado.html",
                               interpolado=round(resultado_interp, 2) if resultado_interp is not None else None,
                               predicho=round(resultado_pred, 2) if resultado_pred is not None else None,
                               hora_interp=hora_interp_fmt,
                               hora_pred=hora_pred_fmt)

    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}")
        return f"Ocurrió un error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
