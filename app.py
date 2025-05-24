from flask import Flask, render_template, request
import json
import numpy as np

app = Flask(__name__)

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
    # Leer datos del JSON
    with open('input_data.json') as f:
        data = json.load(f)

    x = np.array(data['horas'])
    y = np.array(data['glucosas'])

    # Obtener datos del formulario y convertir a float
    try:
        xi = float(request.form['hora_interp'])
        xp = float(request.form['hora_pred'])
    except:
        return "Por favor ingresa valores numéricos válidos."

    # Calcular interpolado y predicho
    interpolado = lagrange(x, y, xi)
    m, b = regresion(x, y)
    predicho = m * xp + b

    # Opcional: redondear para mostrar
    interpolado = round(interpolado, 2)
    predicho = round(predicho, 2)

    # Renderizar resultados con etiquetas personalizadas
    return render_template('resultados.html', 
        hora_interp=xi, 
        hora_pred=xp,
        estimado=interpolado,
        prediccion=predicho
    )

if __name__ == '__main__':
    app.run(debug=True)
