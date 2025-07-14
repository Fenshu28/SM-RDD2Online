# RDR2 Session Manager

Una aplicación de escritorio moderna y fácil de usar para gestionar sesiones privadas en Red Dead Redemption 2 Online.

## Características

- 🎯 **Detección automática** de la instalación de RDR2 (Steam/Epic Games)
- 📝 **Gestión de sesiones** - Crear, activar y eliminar sesiones privadas
- 🔄 **Cambio rápido** entre modo público y privado
- 💾 **Persistencia** - Guarda tus sesiones para uso futuro
- 🎨 **Interfaz moderna** con tema oscuro
- ⚡ **Fácil de usar** - Sin configuración compleja

## Instalación

1. Asegúrate de tener Python 3.6 o superior instalado
2. Descarga el archivo `rdr2_session_manager.py`
3. Ejecuta el programa:
   ```bash
   python rdr2_session_manager.py
   ```

## Uso

### Primera configuración

1. **Detección automática**: El programa intentará detectar automáticamente la ruta de RDR2
   - Steam: `C:\Program Files (x86)\Steam\steamapps\common\Red Dead Redemption 2\x64\data`
   - Epic Games: `C:\Program Files\Epic Games\Red Dead Redemption 2\x64\data`

2. **Configuración manual**: Si no se detecta automáticamente, haz clic en "Buscar" para seleccionar manualmente la carpeta `x64\data` de tu instalación de RDR2

### Crear una sesión privada

1. Ingresa un **nombre** para tu sesión (ej: "Sesión con amigos")
2. Ingresa la **clave de sesión** proporcionada por el host
3. Haz clic en "Crear Sesión"

### Activar una sesión

1. Selecciona una sesión de la lista
2. Haz clic en "Activar Sesión"
3. El estado cambiará para mostrar que la sesión privada está activa

### Volver al modo público

1. Haz clic en "Modo Público"
2. Esto eliminará el archivo `startup.meta` del directorio del juego
3. El estado cambiará a "Modo Público Activo"

### Eliminar una sesión

1. Selecciona una sesión de la lista
2. Haz clic en "Eliminar Sesión"
3. Confirma la eliminación

## Estructura de archivos

- `rdr2_session_manager.py` - Aplicación principal
- `rdr2_sessions.json` - Archivo donde se guardan las sesiones (se crea automáticamente)
- `startup.meta` - Archivo que se genera en el directorio del juego para sesiones privadas

## Funcionamiento técnico

El programa funciona creando un archivo `startup.meta` en el directorio `x64\data` de RDR2. Este archivo contiene:
- La estructura XML base requerida por el juego
- La clave de sesión al final del archivo

Para el modo público, simplemente elimina este archivo del directorio del juego.

## Solución de problemas

### El programa no detecta RDR2
- Verifica que RDR2 esté instalado correctamente
- Usa el botón "Buscar" para seleccionar manualmente la carpeta `x64\data`

### No se puede activar la sesión
- Verifica que la ruta del juego sea correcta
- Asegúrate de que tengas permisos de escritura en el directorio
- Cierra RDR2 antes de cambiar de sesión

### La sesión no funciona en el juego
- Verifica que la clave de sesión sea correcta
- Asegúrate de que el host de la sesión esté en línea
- Reinicia RDR2 después de activar la sesión

## Compatibilidad

- ✅ Windows 10/11
- ✅ Steam
- ✅ Epic Games Store
- ✅ Python 3.6+

## Notas importantes

- ⚠️ Solo puede haber un archivo `startup.meta` a la vez
- ⚠️ Cierra RDR2 antes de cambiar entre sesiones
- ⚠️ Haz una copia de seguridad de tu carpeta de juego antes de usar (precaución)
- ⚠️ Este software es para uso educativo y personal únicamente

## Contribuciones

Si encuentras algún problema o tienes sugerencias, por favor:
1. Reporta el issue con detalles específicos
2. Incluye tu sistema operativo y versión de Python
3. Describe los pasos para reproducir el problema