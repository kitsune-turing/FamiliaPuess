# Familia Puess — Sistema de Control de Asistencia

Sistema completo de control de asistencia con cuatro componentes:

| Componente | Dominio | Rama |
|---|---|---|
| API (FastAPI) | `process-api.familiapues.com` | `deploy/api` |
| Panel administrativo (React) | `panel.familiapues.com` | `deploy/web` |
| Registro de asistencia (React) | `imputar.familiapues.com` | `deploy/imputacion` |
| Kiosco Desktop (PySide6) | Aplicación local | `deploy/desktop` |

---

## Requisitos previos

- **Python 3.13+**
- **Node.js 18+** (para las aplicaciones web)
- **PostgreSQL 16+**
- **Git**
- **Inno Setup 6** (opcional, solo para generar el instalador .exe del Desktop)
  - Descargar: https://jrsoftware.org/isdl.php

---

## 1. Clonar el repositorio

```bash
git clone https://github.com/kitsune-turing/FamiliaPuess.git
cd FamiliaPuess
```

---

## 2. Configurar la base de datos (PostgreSQL)

### 2.1 Crear la base de datos

```sql
CREATE DATABASE familia_puess;
```

### 2.2 Ejecutar el esquema

```bash
git checkout deploy/api
psql -U postgres -d familia_puess -f apps/API/database/database.sql
```

Esto crea todas las tablas, catálogos base, configuración inicial y el usuario administrador por defecto.

---

## 3. API (FastAPI)

### 3.1 Cambiar a la rama

```bash
git checkout deploy/api
```

### 3.2 Instalar dependencias

```bash
pip install -e .
```

### 3.3 Variables de entorno

Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
APP_TIMEZONE=America/Bogota
DATABASE_URL=postgresql+asyncpg://usuario:contraseña@localhost:5432/familia_puess
CORS_ORIGINS=["https://panel.familiapues.com","https://imputar.familiapues.com","http://localhost:5173"]
JWT_SECRET_KEY=tu_clave_secreta_jwt_segura
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=1440
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
DESKTOP_API_KEY=tu_api_key_para_dispositivos_desktop
```

> **Importante:** `CORS_ORIGINS` debe incluir todos los dominios que consumen la API.

### 3.4 Ejecutar en desarrollo

```bash
uvicorn apps.API.main:app --reload --port 8000
```

### 3.5 Despliegue en Railway

La rama `deploy/api` incluye un `Dockerfile` que Railway usa automáticamente. Railway auto-despliega al hacer push a la rama.

```bash
git push origin deploy/api
```

Variables de entorno a configurar en Railway: las mismas del paso 3.3, con `DATABASE_URL` apuntando a la base de datos de producción.

---

## 4. Panel administrativo (React + Vite)

### 4.1 Cambiar a la rama

```bash
git checkout deploy/web
```

### 4.2 Instalar dependencias

```bash
npm install
```

### 4.3 Variables de entorno

Crear `.env` en la raíz:

```env
VITE_API_BASE_URL=https://process-api.familiapues.com
```

### 4.4 Ejecutar en desarrollo

```bash
npm run dev
```

Se abre en `http://localhost:5173`.

### 4.5 Despliegue

```bash
npm run build
git push origin deploy/web
```

Railway sirve el contenido estático generado en `dist/`.

---

## 5. Registro de asistencia / Imputación (React + Vite)

### 5.1 Cambiar a la rama

```bash
git checkout deploy/imputacion
```

### 5.2 Instalar y ejecutar

```bash
cd apps/web
npm install
npm run dev
```

### 5.3 Despliegue

```bash
npm run build
git push origin deploy/imputacion
```

---

## 6. Aplicación Desktop (Kiosco — PySide6)

La aplicación de escritorio funciona como kiosco de registro de asistencia. Muestra un código QR que los trabajadores escanean para registrar su entrada/salida.

### 6.1 Cambiar a la rama

```bash
git checkout deploy/desktop
```

### 6.2 Instalar dependencias

```bash
pip install -e ".[desktop]"
```

### 6.3 Ejecutar en desarrollo

```bash
python -m apps.Desktop.main
```

### 6.4 Generar el ejecutable (.exe)

#### Paso 1: Instalar PyInstaller y certifi

```bash
pip install pyinstaller certifi
```

#### Paso 2: Ejecutar el script de build

```bash
python apps/Desktop/build_installer.py --skip-inno
```

Esto genera `dist/FamiliaPuess.exe` (ejecutable portable ~60 MB).

#### Paso 3 (opcional): Generar el instalador de Windows

Requiere **Inno Setup 6** instalado en el sistema.

```bash
python apps/Desktop/build_installer.py
```

Esto genera `dist/installer/FamiliaPuess_Setup_1.0.0.exe`, un instalador que:
- Instala la aplicación en `Archivos de programa`
- Crea acceso directo en el menú Inicio
- Opcionalmente crea acceso directo en el Escritorio
- Pide la API Key durante la instalación
- Registra la aplicación en "Agregar o quitar programas" de Windows

### 6.5 Configuración de la API Key

La aplicación necesita una API Key para conectarse al servidor. Se puede configurar de tres formas:

**Opción A — Durante la instalación:**
El instalador (.exe de Inno Setup) solicita la API Key automáticamente.

**Opción B — Desde la aplicación:**
Si no hay API Key configurada, la aplicación muestra un diálogo al iniciar pidiendo la clave.

**Opción C — Por línea de comandos:**

```bash
FamiliaPuess.exe --set-api-key TU_API_KEY
```

**Opción D — Manualmente:**
Crear el archivo `%USERPROFILE%\.familia_puess\config.ini`:

```ini
[auth]
api_key = TU_API_KEY

[device]
id = NOMBRE_DISPOSITIVO
```

La API Key se genera desde el panel administrativo (`panel.familiapues.com`) en la configuración del sistema. Es la misma variable `DESKTOP_API_KEY` configurada en la API.

### 6.6 Archivos de configuración del Desktop

| Archivo | Ubicación | Propósito |
|---|---|---|
| `config.ini` | `%USERPROFILE%\.familia_puess\` | API Key y ID del dispositivo |
| `desktop.log` | `%USERPROFILE%\.familia_puess\` | Logs de la aplicación |

### 6.7 Variables de entorno opcionales del Desktop

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `DESKTOP_API_BASE_URL` | `https://process-api.familiapues.com` | URL de la API |
| `DESKTOP_REGISTRO_PUBLICO_URL` | `https://imputar.familiapues.com/registro` | URL de registro público |
| `DESKTOP_API_KEY` | — | API Key (alternativa al config.ini) |
| `DESKTOP_DISPOSITIVO_ID` | — | ID del dispositivo (alternativa al config.ini) |

---

## Estructura del proyecto

```
FamiliaPuess/
├── apps/
│   ├── API/                  # FastAPI — backend
│   │   ├── core/             # Configuración, timezone, seguridad
│   │   ├── database/         # SQL del esquema
│   │   ├── dependencies/     # Inyección de dependencias
│   │   ├── models/           # Modelos SQLAlchemy
│   │   ├── repositories/     # Acceso a datos
│   │   ├── routers/          # Endpoints
│   │   ├── schemas/          # Schemas Pydantic
│   │   ├── security/         # Autenticación JWT
│   │   ├── services/         # Lógica de negocio
│   │   └── main.py           # Entry point
│   ├── Desktop/              # PySide6 — kiosco
│   │   ├── api/              # Cliente HTTP
│   │   ├── assets/           # Íconos, imágenes, fuentes
│   │   ├── ui/               # Ventana principal
│   │   ├── utils/            # Configuración local
│   │   ├── workers/          # Rotación de tokens
│   │   ├── build_installer.py
│   │   ├── familia_puess.spec # PyInstaller config
│   │   ├── installer.iss     # Inno Setup config
│   │   └── main.py           # Entry point
│   └── web/                  # React + Vite — panel y registro
├── shared/                   # Constantes compartidas
├── tests/                    # Tests
└── pyproject.toml            # Dependencias Python
```

---

## Ramas de despliegue

| Rama | Servicio | Auto-deploy |
|---|---|---|
| `deploy/api` | API FastAPI | Railway (Docker) |
| `deploy/web` | Panel admin | Railway (static) |
| `deploy/imputacion` | Registro asistencia | Railway (static) |
| `deploy/desktop` | Kiosco Windows | Build manual local |
| `developer` | Desarrollo integrado | No despliega |

---

## Credenciales por defecto

El usuario administrador se crea con el esquema SQL. Cambiar la contraseña inmediatamente después del primer inicio de sesión desde el panel administrativo.

---

## Autor

Anderson Gomez Tobon
