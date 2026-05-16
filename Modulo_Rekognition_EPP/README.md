# Modulo Rekognition EPP

Sistema de reconocimiento facial para detectar a trabajadores en imágenes de incidencias de seguridad (falta de Equipo de Protección Personal - EPP), utilizando **AWS Rekognition**.

Este módulo monitorea de forma automática la aparición de nuevas incidencias, identifica a la persona que aparece y registra la hora oficial, los detalles del incumplimiento y genera reportes.

## Requisitos Previos

- **Sistema Operativo**: Windows
- **Python**: Versión 3.10 o superior (y debe estar agregado al PATH)
- **Credenciales AWS**: Access Key, Secret Key con permisos de Amazon Rekognition
- **Cámara Local** (opcional): Necesaria si se desea registrar a los trabajadores tomando fotos desde la computadora.

## Estructura de Carpetas e Imágenes

El sistema basa su lógica en dos carpetas principales, las cuales tienen propósitos totalmente distintos:

1. `imagenes_registro/`
   - **Propósito:** Almacenar las fotos de los rostros de los trabajadores para el sistema.
   - **Uso:** Aquí se guardan las fotos capturadas con la cámara o las imágenes que se copian cuando se registra un trabajador manualmente. El sistema **no** monitorea esta carpeta.

2. `imagenes_incidentes/`
   - **Propósito:** Recibir las imágenes de los incidentes de EPP.
   - **Uso:** El monitor automático revisará constantemente esta carpeta en búsqueda de archivos nuevos (jpg, jpeg o png).
   - **Nota importante:** Cada archivo debe tener en su nombre el tipo de incidencia (Ej. `incidencia_Sin_casco_001.jpg` o `incidencia_Sin_chaleco_Sin_guantes_002.jpg`).

### Formatos de Nombres de Imagen de Incidencia

El sistema detectará qué equipo de protección personal falta leyendo el nombre del archivo. Además, es capaz de detectar múltiples fallas a la vez.

Ejemplos válidos:
- `incidencia_Sin_casco_001.jpg`
- `incidencia_Sin_chaleco_Sin_mascarilla_Sin_guantes_002.jpg`
- `incidencia_Sin_casco_Sin_chaleco_Sin_guantes_20260515_024747.jpg`

> [!NOTE]
> La fecha y hora presentes en el nombre de la imagen **NO** serán utilizadas como la fecha y hora oficial. El sistema registrará la fecha y la hora del **momento exacto** en que procesa la imagen dentro de la carpeta monitoreada.

---

## Guía de Instalación Paso a Paso

1. **Descargar el proyecto**: Extraer todo el contenido en una carpeta local (Solo se hace una vez).
2. **Instalar Dependencias**: Haz doble clic en el archivo `instalar_todo.bat`. Esto se encargará de crear el entorno virtual de forma automática y de instalar todas las dependencias necesarias (Solo se hace una vez).
3. **Configurar AWS**: Haz doble clic en el archivo `configurar_aws.bat`. Pega allí tu `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` según se te solicite. Esto creará un archivo `.env` para la seguridad de tus claves (Solo se hace una vez).
   > [!WARNING]
   > El archivo `.env` nunca debe publicarse, compartirse o subirse a un repositorio como GitHub.
4. **Verificar Configuración**: Ejecuta `verificar_configuracion.bat` haciendo doble clic. Este script verificará si hay errores y si el entorno local puede comunicarse de forma exitosa con AWS (Solo se hace si se cambia de proveedor de AWS, si da algun error al iniciar el programa o si se reinstala, de esta menera su buscara la solucion adecuada de ser necesario).
5. **Iniciar el Sistema**: Finalmente, haz doble clic en `iniciar_sistema.bat`. Te abrirá el menú principal de la aplicación en consola.

---

## Cómo Registrar un Trabajador

Una vez que abra el menú con `iniciar_sistema.bat`:

1. Elige la opción **2. Registrar trabajador**
2. Se abrirá un submenú con dos modos:
   - **Registrar trabajador con cámara local**: Se activará la cámara para que te tomes una foto. Cuando te veas bien, presiona `ESPACIO`.
   - **Registrar trabajador desde imagen existente**: Ingresa la ruta completa (ej. `C:\Users\fotos\mifoto.jpg`) de una foto donde salgas.
3. Ingresa los datos como el Código de Trabajador (Ej. `TRA001`), el nombre completo, el área y el puesto.
4. El sistema subirá el rostro a la colección de AWS Rekognition para su entrenamiento, y guardará los datos.

## Cómo Usar el Monitor de Incidencias

1. Abre el menú usando `iniciar_sistema.bat` (si no lo tiene abierto ya).
2. Elige la opción **4. Iniciar monitor de carpeta imagenes_incidentes**.
3. Se abrirá una nueva consola (ventana negra) que se quedará esperando y monitoreando.
4. Cuando alguien copie y pegue una foto de un incidente (Ej. `incidencia_Sin_casco_001.jpg`) dentro de la carpeta `imagenes_incidentes/`, el monitor la detectará al instante.
5. Verás en pantalla que buscará al responsable de la imagen en AWS Rekognition y la registrará en el sistema.

## Explicación de los Archivos JSON

- `trabajadores.json`: Relaciona la imagen y FaceId de AWS con un registro sencillo para búsquedas rápidas.
- `datos_trabajadores.json`: Contiene toda la información corporativa en extenso, como área, puesto, fecha de alta, y rutas.
- `incidencias.json`: Cada que el monitor detecta a alguien sin EPP, guarda un historial detallado en este archivo.
- `alertas_pendientes.json`: Actúa como una "bandeja de entrada" de los incidentes que aún no han sido procesados o revisados por la administración.

## Solución de Problemas Frecuentes

- **Error: "Python no está instalado o en el PATH"**
  Debes instalar Python (3.10+) desde `python.org` y asegurarte de que la casilla "Add Python to PATH" esté marcada.
- **Error: "El entorno virtual venv no existe"**
  Asegúrate de haber ejecutado `instalar_todo.bat` antes que los demás scripts.
- **Error: "Falla al conectar con AWS Rekognition"**
  Verifica que las claves sean válidas o ejecuta nuevamente `configurar_aws.bat` para sobrescribirlas.
- **La cámara web no enciende o da error:**
  Comprueba que ninguna otra aplicación como Zoom o Teams esté usando la cámara.

## Comandos Manuales de Rescate
Si por alguna razón los `.bat` no funcionan:
- Para crear entorno virtual manual: `python -m venv venv`
- Para usar el entorno e instalar dependencias: `venv\Scripts\pip install -r requirements.txt`
- Para correr el menú: `venv\Scripts\python.exe menu_principal.py`
