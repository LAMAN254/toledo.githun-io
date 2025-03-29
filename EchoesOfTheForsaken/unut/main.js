// Animación suave para los enlaces de navegación
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Sistema de progreso
const progress = {
    nivel1: 0,
    nivel2: 0,
    nivel3: 0
};

// Actualizar progreso
function updateProgress(nivel, valor) {
    progress[nivel] = valor;
    localStorage.setItem('financialProgress', JSON.stringify(progress));
    updateProgressUI();
}

// Mostrar progreso en la interfaz
function updateProgressUI() {
    const niveles = ['nivel1', 'nivel2', 'nivel3'];
    niveles.forEach(nivel => {
        const steps = document.querySelectorAll(`#${nivel} .step-check`);
        steps.forEach((step, index) => {
            if (index < progress[nivel]) {
                step.classList.add('completed');
            } else {
                step.classList.remove('completed');
            }
        });
    });
}

// Cargar progreso guardado
function loadProgress() {
    const savedProgress = localStorage.getItem('financialProgress');
    if (savedProgress) {
        Object.assign(progress, JSON.parse(savedProgress));
        updateProgressUI();
    }
}

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', loadProgress);