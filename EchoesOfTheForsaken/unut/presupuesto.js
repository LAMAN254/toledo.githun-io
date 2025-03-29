function calcularPresupuesto() {
    // Obtener ingresos
    const salario = parseFloat(document.getElementById('salario').value) || 0;
    const otrosIngresos = parseFloat(document.getElementById('otros-ingresos').value) || 0;
    
    // Obtener gastos
    const transporte = parseFloat(document.getElementById('transporte').value) || 0;
    const alimentacion = parseFloat(document.getElementById('alimentacion').value) || 0;
    const educacion = parseFloat(document.getElementById('educacion').value) || 0;
    const otrosGastos = parseFloat(document.getElementById('otros-gastos').value) || 0;
    const entretenimiento = parseFloat(document.getElementById('entretenimiento').value) || 0;
    const ropa = parseFloat(document.getElementById('ropa').value) || 0;
    const otrosLujos = parseFloat(document.getElementById('otros-lujos').value) || 0;

    // Calcular totales
    const totalIngresos = salario + otrosIngresos;
    const totalGastosNecesarios = transporte + alimentacion + educacion + otrosGastos;
    const totalGastosDiscrecionales = entretenimiento + ropa + otrosLujos;
    const totalGastos = totalGastosNecesarios + totalGastosDiscrecionales;
    const balance = totalIngresos - totalGastos;
    const porcentajeGastos = (totalGastos / totalIngresos) * 100;
    
    // Mostrar resultados
    const resultadoDiv = document.getElementById('resultado-presupuesto');
    resultadoDiv.innerHTML = `
        <h3>Resumen de tu Presupuesto</h3>
        <p>Total Ingresos: $${totalIngresos.toFixed(2)}</p>
        <p>Total Gastos Necesarios: $${totalGastosNecesarios.toFixed(2)}</p>
        <p>Total Gastos Discrecionales: $${totalGastosDiscrecionales.toFixed(2)}</p>
        <p>Total Gastos: $${totalGastos.toFixed(2)}</p>
        <p>Balance: $${balance.toFixed(2)}</p>
        <p>Porcentaje de gastos: ${porcentajeGastos.toFixed(1)}%</p>
        
        <div class="recomendacion">
            <h4>Recomendación:</h4>
            <p>${generarRecomendacion(porcentajeGastos, balance)}</p>
        </div>
    `;
}

function generarRecomendacion(porcentajeGastos, balance) {
    if (balance < 0) {
        return "⚠️ Tus gastos superan tus ingresos. Considera reducir gastos no esenciales.";
    } else if (porcentajeGastos > 80) {
        return "⚠️ Tus gastos son muy altos. Intenta ahorrar al menos el 20% de tus ingresos.";
    } else if (porcentajeGastos > 60) {
        return "👍 Tu presupuesto es razonable, pero podrías aumentar tus ahorros.";
    } else {
        return "¡Excelente! Estás manejando bien tu dinero y ahorrando una buena cantidad.";
    }
}