# SportFit

Este es un proyecto Django con integración de Tailwind CSS.

## Requisitos

- Python 3.10+
- Node.js y npm
- Django 5.0
- Tailwind CSS

## Instalación

1. Clona el repositorio:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd SportFit
   ```

2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias de Python:
   ```bash
   pip install -r requirements.txt
   ```

4. Instala las dependencias de Tailwind:
   ```bash
   python manage.py tailwind install
   ```

5. Genera los estilos de Tailwind:
   ```bash
   python manage.py tailwind build
   ```

6. Ejecuta el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

## Uso

- Accede a `http://127.0.0.1:8000/` para ver la aplicación.
- Usa `python [manage.py](http://_vscodecontentref_/0) tailwind start` para compilar automáticamente los estilos.

## Contribución

1. Crea un fork del repositorio.
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`).
3. Haz un commit de tus cambios (`git commit -m 'Agrega nueva funcionalidad'`).
4. Haz un push a la rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.