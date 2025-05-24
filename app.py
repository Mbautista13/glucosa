from flask import Flask, render_template, request
import json
import numpy as np

app = Flask(__name__)

# Función para convertir 'HH:MM' a decimal
def hora_a_decimal(hora_str):
    horas, minutos = map(int, hora_str.split(':'))
    return horas + minutos / 60

# Interpolación de Lagrange
def lagrange(x, y, xi):
    yi = 0
    n = len(x)
    for i in range(n):
        L = 1
        for j in range(n):
            if i != j:
                L *= (xi - x[j]) / (x[i] - x[j])
        yi += y[i] * L
    return yi

# Regresión lineal
def regresion(x, y):
    n = len(x)
    m = (n*np.sum(x*y) - np.sum(x)*np.sum(y)) / (n*np.sum(x**2) - (np.sum(x))**2)
    b = (np.sum(y) - m*np.sum(x)) / n
    return m, b

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resultados', methods=['POST'])
def resultados():
    try:
        # Obtener las horas y valores de glucosa del formulario
        horas_str = request.form.getlist('hora[]')
        glucosas_str = request.form.getlist('glucosa[]')

        # Convertir a formato numérico
        horas = [hora_a_decimal(h) for h in horas_str]
        glucosas = [float(g) for g in glucosas_str]

        # Guardar los datos en un JSON
        with open('input_data.json', 'w') as f:
            json.dump({'horas': horas, 'glucosas': glucosas}, f)

        # Obtener horas para interpolar y predecir
        hora_interp_str = request.form['hora_interp']
        hora_pred_str = request.form['hora_pred']
        xi = hora_a_decimal(hora_interp_str)
        xp = hora_a_decimal(hora_pred_str)

        # Convertir a arrays NumPy
        x = np.array(horas)
        y = np.array(glucosas)

        # Calcular interpolado y predicho
        interpolado = lagrange(x, y, xi)
        m, b = regresion(x, y)
        predicho = m * xp + b

        # Redondear
        interpolado = round(interpolado, 2)
        predicho = round(predicho, 2)

        return render_template('resultados.html',
            hora_interp=hora_interp_str,
            hora_pred=hora_pred_str,
            interpolado=interpolado,
            predicho=predicho
        )
    
    except Exception as e:
        return f"Ocurrió un error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
