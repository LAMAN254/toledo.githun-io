# Biblioteca Digital Inteligente (BDI)

Sistema de gestión para bibliotecas escolares que ayuda a prevenir la pérdida de libros y optimizar recursos educativos.

## Características

- Gestión de libros (agregar, modificar, eliminar)
- Sistema de préstamos y devoluciones
- Reportes en tiempo real
- Interfaz gráfica intuitiva
- Base de datos SQLite

## Requisitos

- Python 3.8 o superior
- Tkinter (incluido en la instalación estándar de Python)
- Dependencias adicionales listadas en requirements.txt

## Instalación

1. Clonar o descargar este repositorio
2. Crear un entorno virtual (recomendado):
```bash
python -m venv .venv
```

3. Activar el entorno virtual:
- Windows:
```bash
.venv\Scripts\activate
```
- Linux/Mac:
```bash
source .venv/bin/activate
```

4. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Ejecutar el programa:
```bash
python main.py
```

2. La interfaz principal tiene tres pestañas:
   - Gestión de Libros: Agregar y gestionar libros
   - Préstamos: Registrar préstamos y devoluciones
   - Reportes: Ver informes de libros prestados, no devueltos e inventario

## Estructura del Proyecto

```
biblioteca-digital/
│
├── main.py           # Archivo principal del programa
├── requirements.txt  # Dependencias del proyecto
├── biblioteca.db    # Base de datos SQLite (se crea automáticamente)
└── README.md        # Este archivo
```

## Contribuir

Si deseas contribuir al proyecto:

1. Haz un fork del repositorio
2. Crea una rama para tu función: `git checkout -b nueva-funcion`
3. Haz commit de tus cambios: `git commit -am 'Agrega nueva función'`
4. Haz push a la rama: `git push origin nueva-funcion`
5. Envía un pull request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles. 