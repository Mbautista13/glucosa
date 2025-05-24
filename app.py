from flask import Flask, render_template, request
import numpy as np
from datetime import datetime

app = Flask(__name__)

# Convierte hora "HH:MM" a decimal, ej: "13:30" -> 13.5
def hora_a_decimal(hora_str):
    hora = datetime.strptime(hora_str, "%H:%M")
    return hora.hour + hora.minute / 60

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/procesar", methods=["POST"])
def procesar():
    # Obtén listas de horas y glucosas del formulario
    horas_str = request.form.getlist("hora[]")
    glucosa_str = request.form.getlist("glucosa[]")

    # Validar que tengamos al menos 3 mediciones
    if len(horas_str) < 3 or len(glucosa_str) < 3:
        return "Error: Debes ingresar al menos 3 mediciones.", 400

    # Convertir glucosa a float
    try:
        glucosa = [float(g) for g in glucosa_str]
    except ValueError:
        return "Error: Valores de glucosa inválidos.", 400

    # Convertir horas a decimales
    horas_dec = [hora_a_decimal(h) for h in horas_str]

    # Datos para la interpolación y predicción
    hora_interp_str = request.form.get("hora_interp")
    hora_pred_str = request.form.get("hora_pred")

    # Validar horas para interpolar y predecir
    if not hora_interp_str or not hora_pred_str:
        return "Error: Debes ingresar las horas para interpolar y predecir.", 400

    hora_interp_dec = hora_a_decimal(hora_interp_str)
    hora_pred_dec = hora_a_decimal(hora_pred_str)

    # Interpolación lineal
    estimado = float(np.interp(hora_interp_dec, horas_dec, glucosa))

    # Predicción por regresión lineal (polinomio grado 1)
    coef = np.polyfit(horas_dec, glucosa, 1)
    m, b = coef
    prediccion = float(m * hora_pred_dec + b)

    # Redondear resultados a 2 decimales
    estimado = round(estimado, 2)
    prediccion = round(prediccion, 2)

    # Renderizar template con resultados
    return render_template("resultados.html",
                           estimado=estimado,
                           prediccion=prediccion,
                           hora_interp=hora_interp_str,
                           hora_pred=hora_pred_str)

if __name__ == "__main__":
    app.run(debug=True)
