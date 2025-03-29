// Calculadora de Presupuesto
function calcularPresupuesto() {
    const ingresos = parseFloat(document.getElementById('ingresos').value) || 0;
    const gastos = parseFloat(document.getElementById('gastos').value) || 0;
    const balance = ingresos - gastos;

    const resultadoDiv = document.getElementById('resultado-presupuesto');
    resultadoDiv.innerHTML = `
        <h3>Resultado del Presupuesto</h3>
        <p>Ingresos: $${ingresos.toFixed(2)}</p>
        <p>Gastos: $${gastos.toFixed(2)}</p>
        <p>Balance: $${balance.toFixed(2)}</p>
        <p>${balance >= 0 ? '¡Bien! Tienes un balance positivo.' : '⚠️ Cuidado, tus gastos superan tus ingresos.'}</p>
    `;
}

// Calculadora de Ahorro
function calcularAhorro() {
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
}

// Calculadora de Inversión
function calcularInversion() {
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
}