from flask import Flask, render_template, request
import numpy as np

app = Flask(__name__)

# Lagrange Interpolation
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

# Linear Regression
def regresion(x, y):
    n = len(x)
    m = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x ** 2) - (np.sum(x)) ** 2)
    b = (np.sum(y) - m * np.sum(x)) / n
    return m, b

# Convierte hora tipo 'HH:MM' a decimal (ej. '14:30' → 14.5)
def hora_a_decimal(hora_str):
    partes = hora_str.split(':')
    return int(partes[0]) + int(partes[1]) / 60

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resultados', methods=['POST'])
def resultados():
    try:
        # Obtener horas y glucosas como listas
        horas_str = request.form.getlist('hora[]')
        glucosas_str = request.form.getlist('glucosa[]')

        # Convertir a float
        x = np.array([hora_a_decimal(h) for h in horas_str])
        y = np.array([float(g) for g in glucosas_str])

        # Hora a interpolar y predecir
        xi = hora_a_decimal(request.form['hora_interp'])
        xp = hora_a_decimal(request.form['hora_pred'])

        # Calcular
        interpolado = round(lagrange(x, y, xi), 2)
        m, b = regresion(x, y)
        prediccion = round(m * xp + b, 2)

        return render_template('resultados.html',
                               hora_interp=request.form['hora_interp'],
                               hora_pred=request.form['hora_pred'],
                               estimado=interpolado,
                               prediccion=prediccion)
    except Exception as e:
        return f"Ocurrió un error: {e}"

if __name__ == '__main__':
    app.run(debug=True)

