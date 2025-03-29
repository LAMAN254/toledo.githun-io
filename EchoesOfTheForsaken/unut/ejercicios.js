// Ejercicio 1: Crear tu Primer Presupuesto
document.getElementById('presupuesto-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const mesada = parseFloat(document.getElementById('mesada').value) || 0;
    const otrosIngresos = parseFloat(document.getElementById('otros-ingresos').value) || 0;
    const transporte = parseFloat(document.getElementById('transporte').value) || 0;
    const comida = parseFloat(document.getElementById('comida').value) || 0;
    const entretenimiento = parseFloat(document.getElementById('entretenimiento').value) || 0;

    const totalIngresos = mesada + otrosIngresos;
    const totalGastos = transporte + comida + entretenimiento;
    const balance = totalIngresos - totalGastos;

    const resultadoDiv = document.getElementById('resultado');
    resultadoDiv.innerHTML = `
        <h3>Resultado del Presupuesto</h3>
        <p>Ingresos: $${totalIngresos.toFixed(2)}</p>
        <p>Gastos: $${totalGastos.toFixed(2)}</p>
        <p>Balance: $${balance.toFixed(2)}</p>
        <p>${balance >= 0 ? '¡Bien! Tienes un balance positivo.' : '⚠️ Cuidado, tus gastos superan tus ingresos.'}</p>
    `;
});

// Ejercicio 2: Plan de Ahorro
document.getElementById('ahorro-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const ahorroMensual = parseFloat(document.getElementById('ahorro-mensual').value) || 0;
    const periodo = parseInt(document.getElementById('periodo').value) || 0;
    const totalAhorro = ahorroMensual * periodo;

    const resultadoDiv = document.getElementById('resultado-ahorro');
    resultadoDiv.innerHTML = `
        <h3>Resultado del Ahorro</h3>
        <p>Ahorro mensual: $${ahorroMensual.toFixed(2)}</p>
        <p>Periodo: ${periodo} meses</p>
        <p>Total ahorrado: $${totalAhorro.toFixed(2)}</p>
    `;
});

// Ejercicio 3: Plan de Inversión
document.getElementById('inversion-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const inversionInicial = parseFloat(document.getElementById('inversion-inicial').value) || 0;
    const tasaInteres = parseFloat(document.getElementById('tasa-interes').value) / 100 || 0;
    const periodo = parseInt(document.getElementById('periodo-inversion').value) || 0;

    const totalInversion = inversionInicial * Math.pow(1 + tasaInteres, periodo);

    const resultadoDiv = document.getElementById('resultado-inversion');
    resultadoDiv.innerHTML = `
        <h3>Resultado de la Inversión</h3>
        <p>Inversión inicial: $${inversionInicial.toFixed(2)}</p>
        <p>Tasa de interés anual: ${(tasaInteres * 100).toFixed(2)}%</p>
        <p>Periodo: ${periodo} años</p>
        <p>Total acumulado: $${totalInversion.toFixed(2)}</p>
    `;
});