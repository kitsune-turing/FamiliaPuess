# Familia Puess — Sistema de Control de Asistencia

## Descargar Instalador

[**Descargar FamiliaPuess_Setup_1.1.0.exe**](installer_output/FamiliaPuess_Setup_1.1.0.exe)

## Instalador Desktop

El instalador se genera con Inno Setup desde el script `installer.iss`:

```bash
"C:\Program Files\Inno Setup 7\ISCC.exe" installer.iss
```

### Requisitos

- Windows 10/11 (64 bits)

### Instalación

1. Ejecuta `FamiliaPuess_Setup_1.1.0.exe`
2. Sigue el asistente de instalación (en español)
3. Al finalizar, la aplicación se inicia automáticamente
4. Ingresa la **API Key** cuando se solicite (solo la primera vez)

### Configuración

La configuración se almacena en `%USERPROFILE%\.familia_puess\config.ini`.

Para configurar la API key manualmente:

```bash
FamiliaPuess.exe --set-api-key TU_API_KEY
```
