# Correcciones para que el proyecto compile

Este paquete contiene **solo los archivos nuevos o modificados**. Se copian
sobre el repositorio ya clonado, respetando la estructura de carpetas.

No reemplaza el repositorio: se integra en él y se confirma con un commit
normal en tu rama.

## Cómo aplicarlo

Desde la raíz del repositorio (donde está `docker-compose.yml`):

```bash
cp -r /ruta/a/este/paquete/* .
```

En Windows, copia las carpetas `apps` y `scripts` y los archivos sueltos
sobre la raíz del repo, aceptando reemplazar.

## Antes de copiar: recupera la página del QR

`RegistroPage.tsx` fue sobrescrito por error con la tabla administrativa.
Recupéralo desde el historial **antes** de copiar este paquete:

```bash
git checkout HEAD -- apps/web/src/pages/RegistroPage.tsx
```

La tabla administrativa viene en este paquete como `RegistrosEntradaPage.tsx`.

## Verificación

```bash
cd apps/web
npm install
npm run build     # debe terminar sin errores
```

## Archivos incluidos

### Infraestructura que faltaba (nueva)
- `apps/web/src/components/ui/` — componentes e iconos
- `apps/web/src/components/charts/` — gráficas en SVG
- `apps/web/src/components/layout/` — Sidebar, Topbar y AdminLayout
- `apps/web/src/context/` — DataProvider y ToastProvider
- `apps/web/src/data/initial.ts` — estado inicial vacío
- `apps/web/src/hooks/`, `apps/web/src/lib/format.ts`, `apps/web/src/types/admin.ts`
- `apps/web/src/styles/` — tokens, layout, components, pages
- `apps/web/src/assets/images/` — logo y decoraciones

### Páginas
- Nueve páginas con sus rutas de importación corregidas
- Cinco páginas nuevas: Catálogos, Parámetros, Seguridad,
  Registro de trabajadores y Registros de entrada

### Integración
- `App.tsx` — rutas bajo `/panel` con redirecciones desde las rutas antiguas
- `main.tsx` — providers y hojas de estilo
- `contexts/AuthContext.tsx` — corrige el bug de `atob` y añade la sede activa
- `services/adminApi.ts` — cliente de los 38 endpoints de la API

### Backend
- `docker-compose.yml` — corrige la línea corrupta de POSTGRES_PASSWORD
- `pyproject.toml` — añade la dependencia `pydantic[email]`
- `scripts/crear_admin.py` — crea el primer usuario administrador
