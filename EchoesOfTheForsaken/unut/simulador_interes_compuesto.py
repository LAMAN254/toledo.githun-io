def interes_compuesto(capital_inicial, tasa_anual, años):
    return capital_inicial * (1 + tasa_anual/12) ** (años*12)

# Ejemplo: $1000 al 5% anual en 3 años
print(interes_compuesto(1000, 0.05, 3))  # Resultado: $1161.47
