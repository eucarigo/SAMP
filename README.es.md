<h1 style="display: flex; align-items: baseline; gap: 12px;">
  <img src="samp.svg" alt="SAMP logo" style="height: 0.9em;">
  SAMP
</h1>

**SAMP** (acrónimo en inglés de *Spotify Ad Muter Panel*, en español *Panel para silenciar anuncios de Spotify*) es una aplicación para Windows que controla automáticamente el volumen de Spotify en función de si se está reproduciendo una canción o un anuncio.
**Versión actual**: 1.3.0

## ✨ Características

* 🎛️ **Controles independientes**: Ajusta los niveles de volumen de canciones y anuncios por separado.
* 🔊 **Volumen del sistema**: Gestiona el volumen maestro de Windows directamente desde la ventana principal.
* 🔄 **Detección automática del estado**: Detecta el estado de reproducción de Spotify (canción frente a anuncio) mediante la API de control de medios de Windows (GSMTC/SMTC).
* ⚡ **Cambio instantáneo de volumen**: Ajusta el volumen de la sesión de audio de Spotify a través de WASAPI (`pycaw`) inmediatamente tras la transición de estado.
* 🖥️ **Interfaz ligera**: Interfaz gráfica moderna construida con PyQt6 e integrada con `qasync`.
* 🎨 **Iconos vectoriales personalizados**: Iconos SVG integrados para los controles y estados de reproducción.
* 🌍 **Soporte multilingüe**: Inglés, español, alemán y francés — conmutable en tiempo de ejecución.
* 🎨 **Múltiples temas visuales**: Temas Oscuro, Claro y Bosque — conmutables en tiempo de ejecución.
* ⏱️ **Intervalo de comprobación configurable**: Ajusta con precisión la frecuencia de muestreo del estado (en décimas de segundo).
* 🔁 **Iniciar con Spotify**: Un observador en segundo plano inicia SAMP automáticamente cada vez que se abre Spotify durante la sesión.
* 🔒 **Control de instancia única**: Utiliza `QLocalServer`/`QLocalSocket` para traer la instancia existente al frente en lugar de lanzar duplicados.
* ℹ️ **Documentación integrada**: Diálogo "Acerca de" integrado que cubre tutoriales de uso, notas de arquitectura y detalles legales.

## 📋 Requisitos

* **Sistema operativo:** Windows 10 / 11 (64 bits, compilación 17763 o superior).
* **CPU:** 1 GHz o superior (arquitectura x86_64).
* **RAM:** 512 MB mínimo, 1 GB recomendado.
* **Espacio libre:** 52 MB mínimo, 60 MB recomendado.
* **Spotify:** Aplicación de escritorio instalada y en ejecución.
* **Python:** 3.8+ (3.12 recomendado) — solo necesario al ejecutar desde el código fuente.

## 🚀 Instalación

### 💿 Instalador ejecutable (Recomendado)

Descarga y ejecuta `SAMP_Setup_1.3.0.exe` compilado con Inno Setup. El asistente de instalación permite elegir entre instalaciones Rápida y Personalizada, creación de accesos directos en el escritorio/menú Inicio y la configuración opcional de la tarea en segundo plano *Iniciar con Spotify*.

### 📦 Versión portable (ZIP)

1. Descarga `SAMP-1.3.0-portable.zip` desde el último *release*.
2. Extrae el contenido del archivo ZIP en cualquier carpeta o unidad portable.
3. Ejecuta `SAMP.exe` directamente — sin necesidad de instalación ni permisos de administrador.

### 🛠️ Ejecución desde el código fuente

1. Clona el repositorio.
2. Instala las dependencias:

```bash
pip install PyQt6 qasync winsdk pycaw psutil comtypes

```

3. Ejecuta la aplicación:

```bash
python main.py

```

## 🕹️ Uso

1. Inicia Spotify y SAMP (o deja que se inicie automáticamente).
2. Ajusta los deslizadores:

* **Sistema**: Volumen maestro de Windows.
* **Canción**: Nivel de volumen para la reproducción de música.
* **Anuncios**: Nivel de volumen para los anuncios de audio (fíjalo en 0% para silenciarlos por completo).

3. Los ajustes manuales de los deslizadores durante cualquier estado guardan automáticamente el nuevo volumen para dicho estado.

### ⚙️ Ajustes (`Ctrl+,`)

* Cambiar el idioma de la aplicación (inglés, español, alemán, francés).
* Cambiar el tema visual (Oscuro, Claro, Bosque).
* Ajustar el intervalo de comprobación (por defecto: 0,5 segundos).
* Activar o desactivar la integración de **Iniciar con Spotify**.

### 🔁 Iniciar con Spotify - Detalles

* Registra o elimina la tarea `SAMP_StartWithSpotify` en el Programador de tareas de Windows.
* Un script de PowerShell en segundo plano escucha los eventos de inicio de `Spotify.exe` y activa SAMP tras un margen de 2 segundos.
* La elevación síncrona de UAC verifica la aprobación del Administrador y notifica el estado real de ejecución.
* La tarea programada se ejecuta con privilegios de usuario normales sin requerir derechos elevados para el funcionamiento diario.
* Se recomienda reiniciar la sesión actual de Windows tras activar o desactivar la opción para que los cambios surtan pleno efecto.

## ⚙️ Cómo funciona

* Consulta los controles de transporte multimedia de Spotify mediante `winsdk` (`GSMTCM`).
* Utiliza la heurística de disponibilidad del botón de medios "Siguiente pista" para diferenciar canciones de anuncios no omitibles.
* Ajusta el volumen de salida de la sesión de audio de Spotify a través de `pycaw` (WASAPI).
* Ejecuta un bucle de muestreo asíncrono (`qasync` + `asyncio`) para monitorizar los cambios de estado y sincronizar los deslizadores de la interfaz gráfica.
* Emplea un servidor IPC (`QLocalServer` denominado `SAMP_SingleInstance`) para garantizar el funcionamiento en una sola instancia.

## 🔒 Resumen de aviso legal

El uso de SAMP es bajo tu propia responsabilidad. Lee el [aviso legal completo](DISCLAIMER) para conocer los términos sobre conformidad con los **Términos de Servicio de Spotify**, limitación de responsabilidad y licencia.

En resumen:

- SAMP no bloquea los anuncios, solo baja su volumen.
- No modifica el cliente de Spotify ni interactúa con sus servidores.
- El desarrollador no se hace responsable de posibles suspensiones de la cuenta de Spotify según la interpretación que haga la empresa del uso de esta herramienta.

### IMPORTANTE

> El texto anterior **no invalida, ni sustituye** al [aviso legal completo](DISCLAIMER); sólo lo resume facilitando la comprensión del aviso oficial a los lectores no especializados.


## 📄 Licencia

Este proyecto se distribuye bajo la GNU General Public License v3.0 (GPLv3), sin garantías. Consulta el archivo `LICENSE` para más detalles o entra en la [página oficial de la GPLv3](https://www.gnu.org/licenses/gpl-3.0.html).


## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o un pull request para proponer cambios o mejoras.


## 🙏 Agradecimientos

Los iconos empleados en SAMP son dibujados mediante SVG. 

- El icono principal (silencio de negra enmarcado, coloreado con #CC7722) está basado en el icono [Quarter Rest de SVG Repo](https://www.svgrepo.com/svg/480283/quarter-rest), utilizado bajo los términos de la [licencia SVGRepo](https://www.svgrepo.com/page/licensing/). La composición final y el coloreado son trabajo original del desarrollador.

- El resto de iconos (altavoz, icono de Spotify e icono de anuncio) están sacados del repositorio [tabler-icons](https://github.com/tabler/tabler-icons/) ([licencia MIT](https://opensource.org/licenses/MIT)). 

> Acuérdate de apoyar también estos proyectos entrando en los enlaces indicados. 

## 📧 Contacto

Desarrollador: contact@eucarigo.com

Aviso legal: `DISCLAIMER`

---

⭐ Si te es útil, considera **darle una estrella** al repositorio.

*Programa gratis, sin anuncios, sin registro, de código abierto y licencia libre.*
