# Music Murcia

Aplicación de escritorio para gestionar el inventario de una tienda de vinilos,
desarrollada con Python, PySide6 y MySQL.

## Requisitos

- Python 3.10 o superior
- Servidor MySQL disponible en `127.0.0.1:3306`
- Usuario MySQL `root` con permisos para crear la base de datos `Music_Murcia`

## Instalación en Windows

Desde la carpeta del proyecto, crea y activa un entorno virtual e instala las
dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configura la contraseña de MySQL en la sesión actual de PowerShell y ejecuta la
aplicación:

```powershell
$env:MYSQL_PASSWORD = "<contraseña de MySQL>"
python Main.py
```

La aplicación crea la base de datos y la tabla `Discos` si todavía no existen.
No guardes contraseñas ni bases de datos locales en el repositorio.
