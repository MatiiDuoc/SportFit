# SportFit

## Descripción

SportFit es una plataforma de gestión deportiva desarrollada en Django, con estilos usando Tailwind CSS.

---

## Requisitos

- Python 3.10+
- Node.js y npm (para Tailwind CSS)
- Google Chrome (para Selenium)
- ChromeDriver (para Selenium)
- Oracle Client (si usas Oracle como base de datos)

---

## Instalación

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/tuusuario/sportfit.git
   cd sportfit
   ```

2. **Crea y activa un entorno virtual:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # En Windows
   ```

3. **Instala dependencias de Python:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Instala dependencias de Node (para Tailwind):**
   ```bash
   npm install
   ```

5. **Configura las variables de entorno:**
   - Crea un archivo `.env` en la raíz del proyecto basado en `.env.example`.
   - **Nunca subas tu archivo `.env` real al repositorio.**

6. **Configura la base de datos Oracle (si aplica):**
   - Asegúrate de tener el cliente Oracle instalado.
   - Completa los datos de conexión en tu `.env`.

7. **Instala ChromeDriver:**
   - Descarga la versión compatible con tu Google Chrome desde [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/).
   - Coloca `chromedriver.exe` en una carpeta incluida en tu PATH o especifica la ruta en tu código.

---

## Uso de Tailwind CSS

1. **Instalación de Tailwind CSS**
   ```bash
   python manage.py tailwind install
   ```

2. **Compilar Tailwind en modo desarrollo**
   ```bash
   python manage.py tailwind start
   ```

3. **Compilar Tailwind para producción**
   ```bash
   python manage.py tailwind build
   ```

---

## Migraciones y Base de Datos

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Ejecución del servidor

```bash
python manage.py runserver
```

---

## Pruebas

```bash
python manage.py test
```

---

## Buenas prácticas para colaborar

- Usa ramas para nuevas funcionalidades.
- Haz Pull Requests y revisa el código de tus compañeros.
- No subas archivos sensibles ni el archivo `.env`.
- Actualiza el `requirements.txt` si agregas nuevas dependencias.
- Comenta tu código y sigue la convención PEP8.

---

## Seguridad

- No subas archivos de configuración sensibles ni claves.
- Usa el archivo `.gitignore` para ignorar archivos temporales y secretos.

---

## Licencia

[MIT](LICENSE) (o la que corresponda)