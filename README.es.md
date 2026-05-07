<h1 style="display: flex; align-items: baseline; gap: 12px;">
  <img src="samp.svg" alt="SAMP logo" style="height: 0.9em;">
  SAMP
</h1>

**SAMP** (acrónimo en inglés de *Spotify Ad Muter Panel*, en español *Panel para silenciar anuncios de Spotify*) es una aplicación para Windows que controla automáticamente el volumen de Spotify en función de si está reproduciendo una canción o un anuncio. 

Permite ajustar por separado el nivel de volumen para canciones y para anuncios, además de integrarse con el volumen del sistema.

**Versión actual**: 1.0


## ✨ Características

- 🎛️ **Controles independientes** para volumen de canciones y anuncios.
- 🔊 **Volumen del sistema** también ajustable desde la misma ventana.
- 🔄 **Detección automática** del estado de Spotify (canción / anuncio) usando la API de control multimedia de Windows (SMTC).
- ⚡ **Cambio instantáneo** de volumen cuando Spotify pasa de canción a anuncio o viceversa.
- 🖥️ **Interfaz ligera** con PyQt6 y estilo oscuro.
- 🎨 **Iconos personalizados** para cada modo.


## 📋 Requisitos

- **Sistema operativo:** Windows 10 / 11 (64 bits)
- **CPU:** 1 GHz o superior (cualquier procesador x86_64 de los últimos 10 años)
- **RAM:** 512 MB mínimo, 1 GB o más recomendado
- **Espacio libre:** al menos 65 MB (100 MB recomendado)
- **Spotify:** aplicación de escritorio instalada y ejecutándose
- **Python:** no es necesario si usas el ejecutable (aún no implementado), pero para desarrollo necesitas Python 3.8+ (3.12 recomendado)

### Dependencias (sólo para ejecutar desde código)

```bash
pip install pyqt6 qasync pycaw psutil winsdk comtypes
```


## 🚀 Instalación

> Próximamente se publicarán ejecutables precompilados. Mientras tanto, puedes ejecutar desde código fuente.


## 🕹️ Uso

1. Inicia Spotify y reproduce una canción o un anuncio.

2. Ajusta los deslizadores:

- `Sistema`: controla el volumen maestro de Windows.
- `Canción`: se aplicará automáticamente cuando Spotify reproduzca una canción.
- `Anuncios`: volumen que se aplicará durante los anuncios de audio.

3. SAMP detecta automáticamente el estado de reproducción y cambia el volumen de la sesión de Spotify al valor que hayas elegido para ese estado.

> 💡 Nota: Si cambias manualmente el volumen de Spotify desde el control deslizante de una canción o anuncio mientras estás en ese estado, el cambio se aplica al momento y se guarda como nuevo valor preferido para ese estado.


## ⚙️ ¿Cómo funciona?

- Utiliza la API `GlobalSystemMediaTransportControlsSessionManager` de Windows (winsdk) para obtener la sesión multimedia de Spotify.

- Detecta si el botón de "siguiente" está habilitado: en Spotify, durante las canciones el botón de siguiente está activo; durante los anuncios está desactivado. Esa es la heurística empleada.

- Mediante `pycaw`, obtiene el control de volumen de la sesión del proceso `Spotify.exe` y lo ajusta según el estado actual.

- Un hilo asíncrono monitoriza periódicamente el estado y los cambios externos de volumen (por ejemplo, si el usuario cambia el volumen desde la mezcladora de Windows) y sincroniza los deslizadores.


## ⚠️ Resumen de aviso legal

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
