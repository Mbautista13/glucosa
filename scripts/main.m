pkg load io;
addpath("jsonlab-master");
data = loadjson('input_data.json');

x = data.horas;
y = data.glucosas;
xi = data.hora_interp;
xp = data.hora_pred;

function yi = lagrange(x, y, xi)
  n = length(x);
  yi = 0;
  for i = 1:n
    L = 1;
    for j = 1:n
      if i != j
        L *= (xi - x(j)) / (x(i) - x(j));
      end
    end
    yi += y(i) * L;
  end
end

function [m, b] = regresion(x, y)
  n = length(x);
  m = (n*sum(x.*y) - sum(x)*sum(y)) / (n*sum(x.^2) - sum(x)^2);
  b = (sum(y) - m*sum(x)) / n;
end

yi = lagrange(x, y, xi);
[m, b] = regresion(x, y);
yp = m * xp + b;

printf("Resultado de interpolacion en hora %.2f: %.2f\n", xi, yi);
printf("Prediccion por regresion lineal para hora %.2f: %.2f\n", xp, yp);
