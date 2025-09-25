# AppFacturas - Tapia & López Abogados

Aplicación web para la gestión integral de facturación del despacho **Tapia & López Abogados**. Permite administrar clientes, emitir facturas con conceptos detallados y mantener el control de cobros. Incluye autenticación de usuarios y herramientas de respaldo completo de la información.

## Características principales

- Autenticación de usuarios con contraseñas cifradas (Flask-Login).
- Panel principal con indicadores de clientes y facturas recientes.
- Gestión completa de clientes (alta, edición, eliminación y búsqueda).
- Creación y edición de facturas con múltiples conceptos, cálculo automático de impuestos y totales.
- Exportación de toda la base de datos a un archivo JSON (respaldo).
- Importación/restauración de datos desde un archivo JSON previamente exportado.
- Interfaz en español con diseño responsive basado en Bootstrap 5.

## Requisitos

- Python 3.10 o superior
- Entorno virtual recomendado

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows usar .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Inicializar la base de datos

```bash
flask --app run.py shell <<'PY'
from app import db, create_app
from app.models import User
app = create_app()
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", email="admin@tapia-lopez.com")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
PY
```

También puedes ejecutar `python` e introducir los mismos comandos para crear un usuario inicial.

## Ejecutar la aplicación

```bash
flask --app run.py run --debug
```

La aplicación estará disponible en `http://127.0.0.1:5000`.

## Respaldo e importación de datos

- **Exportar**: desde la barra de navegación selecciona `Respaldo → Descargar respaldo`. Se generará un archivo JSON con toda la información (usuarios, clientes, facturas y conceptos).
- **Importar**: desde `Respaldo → Restaurar datos` carga un archivo exportado previamente. **Advertencia:** esta acción eliminará los datos actuales antes de importar los del archivo.

## Estructura del proyecto

```
appfacturas/
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── backup.py
│   ├── clients.py
│   ├── dashboard.py
│   ├── invoices.py
│   ├── models.py
│   ├── static/
│   │   └── styles.css
│   └── templates/
│       ├── backup/
│       │   └── import.html
│       ├── clients/
│       │   ├── form.html
│       │   └── list.html
│       ├── invoices/
│       │   ├── detail.html
│       │   ├── form.html
│       │   └── list.html
│       ├── base.html
│       ├── dashboard.html
│       ├── login.html
│       └── register.html
├── requirements.txt
├── run.py
└── README.md
```

## Copias de seguridad manuales

El archivo de base de datos SQLite se almacena por defecto en `instance/appfacturas.db`. Para un respaldo adicional puedes copiar este archivo junto con los respaldos JSON exportados desde la aplicación.
