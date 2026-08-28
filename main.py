"""
samp: spotify_ad_muter_panel
"""

version = "1.3.0"

# --- Imports ---
import asyncio, sys, os
from pathlib import Path
from psutil import NoSuchProcess
from ctypes import POINTER, cast

from qasync import QEventLoop
from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as GSMTCM
)
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, IAudioEndpointVolume, IAudioEndpointVolumeCallback
from comtypes import CLSCTX_ALL, COMObject

# PyQt6
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QSlider, QLabel, QDialog, QComboBox,
    QPushButton, QCheckBox, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QTimer, QSize, QRectF,
    QSizeF, QPointF, pyqtSlot
)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QIcon, QFont
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

# sws
from sws import (
    register_sws_task, unregister_sws_task,
    sws_task_exists, handle_elevated_cli,
    SWSError, SWSElevationCancelled, SWSElevationTimeout,
)


SAMP_SERVER = "SAMP_SingleInstance"


# --- Icons ---
SAMP_SVG = b"""
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" 
stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M7 3a2 2 0 0 0 -2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-14a2 2 0 0 0 -2 -2h-10" />
    <path fill="currentColor" stroke="none" transform="translate(12, 12) scale(0.022) translate(-256, -256)" 
    d="M349.091,371.859c-14.588-11.448-44.397-43.31-65.554-102.28c-20.802-57.964,25.648-94.268,50.571-113.841c6.486-5.102,7.92-11.556-0.692-20.531C324.82,126.241,219.343,9.028,219.343,9.028c-13.03-17.143-30.816-7.13-20.604,7.302c120.65,170.544-35.068,196.638-35.068,196.638s16.854,43.837,97.392,115.062c-84.28-21.915-138.6,40.178-97.392,104.108c41.2,63.923,120.798,77.62,127.358,79.45c7.261,2.02,17.794-3.659,6.561-10.953c-25.566-16.623-78.667-60.732-53.381-92.24c33.716-42.008,83.348-23.744,96.452-17.358C363.44,402.147,371.574,389.52,349.091,371.859z"/>
</svg>
"""

SYS_SVG = b"""
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M5 5a2 2 0 0 1 2 -2h10a2 2 0 0 1 2 2v14a2 2 0 0 1 -2 2h-10a2 2 0 0 1 -2 -2l0 -14" />
    <path d="M9 14a3 3 0 1 0 6 0a3 3 0 1 0 -6 0" />
    <path d="M12 7l0 .01" />
</svg>
"""

SP_SVG = b"""
<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M12.001 2C17.551 2 22.001 6.5 22.001 12C22.001 17.5 17.501 22 
    12.001 22C6.50098 22 2.00098 17.5 2.00098 12C2.00098 6.5 6.50098 2 12.001 
    2ZM12.001 4C7.60555 4 4.00098 7.60457 4.00098 12C4.00098 16.3954 7.60555 
    20 12.001 20C16.3964 20 20.001 16.3954 20.001 12C20.001 7.58572 16.4276 
    4 12.001 4ZM15.751 16.65C13.401 15.2 10.451 14.8992 6.95014 15.6992C6.60181 
    15.8008 6.30098 15.55 6.20098 15.25C6.10098 14.8992 6.35098 14.6 6.65098 
    14.5C10.451 13.6492 13.751 14 16.351 15.6C16.701 15.75 16.7501 16.1492 
    16.6018 16.45C16.4018 16.7492 16.0518 16.85 15.751 16.65ZM16.7501 13.95C14.051 
    12.3 9.95098 11.8 6.80098 12.8C6.40181 12.9 5.95098 12.7 5.85098 12.3C5.75098 
    11.9 5.95098 11.4492 6.35098 11.3492C10.001 10.25 14.501 10.8008 17.601 
    12.7C17.9018 12.8508 18.051 13.35 17.8018 13.7C17.551 14.05 17.101 14.2 
    16.7501 13.95ZM6.30098 9.75083C5.80098 9.9 5.30098 9.6 5.15098 9.15C5.00098 
    8.64917 5.30098 8.15 5.75098 7.99917C9.30098 6.94917 15.151 7.14917 18.8518 
    9.35C19.301 9.6 19.451 10.2 19.201 10.65C18.9518 11.0008 18.351 11.1492 
    17.9018 10.9C14.701 9 9.35098 8.8 6.30098 9.75083Z"/>
</svg>
"""

AD_SVG = b"""
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" 
stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M3 7a2 2 0 0 1 2 -2h14a2 2 0 0 1 2 2v10a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-10" />
    <path d="M7 15v-4a2 2 0 0 1 4 0v4" />
    <path d="M7 13l4 0" />
    <path d="M17 9v6h-1.5a1.5 1.5 0 1 1 1.5 -1.5" />
</svg>
"""

# --- Caché de pixmaps: evita recrear SVG en cada llamada ---
_pixmap_cache: dict[tuple, QPixmap] = {}

def svgtp(svg_bytes: bytes, size: QSize = QSize(24, 24), color: str = None) -> QPixmap:
    """svgtp: svg_to_pixmap — con caché por (svg_bytes, size, color)."""
    key = (id(svg_bytes), size.width(), size.height(), color)
    cached = _pixmap_cache.get(key)
    if cached is not None:
        return cached
    if color:
        svg_bytes = svg_bytes.replace(b"currentColor", color.encode())
    dpr = QApplication.primaryScreen().devicePixelRatio() if QApplication.instance() else 1.0
    renderer = QSvgRenderer(svg_bytes)
    physical_size = QSize(int(size.width() * dpr), int(size.height() * dpr))
    pixmap = QPixmap(physical_size)
    pixmap.fill(Qt.GlobalColor.transparent)
    pixmap.setDevicePixelRatio(dpr)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter, QRectF(QPointF(0, 0), QSizeF(size)))
    painter.end()
    _pixmap_cache[key] = pixmap
    return pixmap


# --- Ajustes ---
current_language = "es"
current_theme = "dark"

LANG_STRINGS = {
    "es": {
        "system": "Sistema",
        "song": "Canción",
        "ad": "Anuncios",
        "settings": "Ajustes",
        "theme_dark": "oscuro",
        "theme_light": "claro",
        "theme_forest": "bosque",
        "language_label": "Idioma:",
        "theme_label": "Tema:",
        "subtitle": "Panel para silenciar anuncios de Spotify",
        "check_interval_label": "Tiempo de comprobación",
        "apply": "Aplicar",
        "cancel": "Cancelar",
        "sws": "Iniciar con Spotify",
        "more": "Más...",
        "about": "sobre SAMP",
        "close": "Cerrar",
        "about_tutorial_title": "Cómo usar SAMP",
        "about_sws_title": "Iniciar con Spotify",
        "about_files_title": "Documentación",
        "about_how_title": "Cómo funciona",
        "about_how_items": [
            ("🎵", "SAMP monitoriza constantemente Spotify usando la API de control de medios de Windows (GSMTC) y la API de audio del sistema (WASAPI a través de pycaw)."),
            ("🔍", "Para distinguir entre una canción y un anuncio, SAMP comprueba si el botón «Siguiente» está disponible en la sesión de Spotify: durante un anuncio, avanzar de pista no está permitido."),
            ("🔊", "Al detectar un cambio de estado (canción → anuncio o viceversa), SAMP ajusta automáticamente el volumen de la aplicación Spotify al nivel que hayas configurado para cada tipo de contenido, sin tocar el volumen del sistema."),
        ],
        "about_tutorial_items": [
            ("🖱️", "Deslizador Sistema — controla el volumen maestro de Windows. Equivale a subir o bajar el volumen desde la barra de tareas."),
            ("🎵", "Deslizador Canción — establece el volumen al que sonará Spotify cuando reproduzca música. Ajústalo a tu gusto personal."),
            ("🔇", "Deslizador Anuncios — establece el volumen para los anuncios. Ponlo a 0% para silenciarlos por completo, o a un valor bajo si prefieres escucharlos a menor volumen."),
            ("⚙️", "Pulsa Ctrl+, en cualquier momento para abrir los Ajustes y cambiar el idioma, el tema visual o el intervalo de comprobación."),
            ("⏱️", "Intervalo de comprobación — define cada cuánto tiempo (en décimas de segundo) SAMP consulta el estado de Spotify. Un valor más bajo es más reactivo pero consume algo más de CPU; el valor por defecto (0.5 s) es ideal para la mayoría de equipos."),
        ],
        "about_sws_items": [
            ("📋", "Al activar «Iniciar con Spotify», SAMP crea una tarea programada en el Programador de tareas de Windows con el nombre SAMP_StartWithSpotify."),
            ("👁️", "La tarea lanza un script de PowerShell en segundo plano que espera a que aparezca el proceso Spotify.exe. Cuando Spotify arranca, el script espera 2 segundos adicionales para que Spotify registre su sesión de audio, y entonces inicia SAMP automáticamente."),
            ("🔒", "El proceso de registro requiere permisos de administrador; Windows mostrará el diálogo UAC para confirmar la operación. La tarea en sí corre con los privilegios normales del usuario, por lo que SAMP no necesita elevación para funcionar a diario."),
            ("🗑️", "Si desactivas la opción y pulsas Aplicar, la tarea se elimina del Programador de tareas y SAMP dejará de iniciarse automáticamente. Puedes volver a activarla en cualquier momento."),
            ("⚠️", "Si cancelas el diálogo UAC durante el registro o eliminación, la operación se cancela sin cambios; SAMP lo notificará sin bloquearse. Además, para que funcione una vez aplicado, es necesario reiniciar la sesión actual de Windows."),
        ],
        "about_files_items": [
            ("📄", "README — guía completa de instalación, requisitos del sistema, configuración avanzada y preguntas frecuentes."),
            ("⚖️", "DISCLAIMER.md — aviso legal sobre el uso de SAMP, limitaciones de responsabilidad y relación con Spotify AB."),
            ("📁", "Ambos archivos se encuentran en la misma carpeta que el ejecutable de SAMP (samp.exe)."),
        ],
    },
    "en": {
        "system": "System",
        "song": "Song",
        "ad": "Ads",
        "settings": "Settings",
        "theme_dark": "dark",
        "theme_light": "light",
        "theme_forest": "forest",
        "language_label": "Language:",
        "theme_label": "Theme:",
        "subtitle": "Spotify Ad Muter Panel",
        "check_interval_label": "Check interval",
        "apply": "Apply",
        "cancel": "Cancel",
        "sws": "Start with Spotify",
        "more": "More...",
        "about": "about SAMP",
        "close": "Close",

        "about_tutorial_title": "How to use SAMP",
        "about_sws_title": "Start with Spotify",
        "about_files_title": "Documentation",
        "about_how_title": "How it works",

        "about_how_items": [
            ("🎵", "SAMP continuously monitors Spotify using the Windows Global System Media Transport Controls (GSMTC) API and the system audio API (WASAPI via pycaw)."),
            ("🔍", "To distinguish between a song and an ad, SAMP checks whether the Next button is available in the Spotify session: during an ad, skipping tracks is not allowed."),
            ("🔊", "When a state change is detected (song → ad or vice versa), SAMP automatically adjusts the Spotify application volume to the level you configured for each content type, without touching the system volume."),
        ],
        "about_tutorial_items": [
            ("🖱️", "System slider — controls the Windows master volume. Equivalent to adjusting the volume from the taskbar."),
            ("🎵", "Song slider — sets the volume at which Spotify will play music. Adjust it to your personal preference."),
            ("🔇", "Ads slider — sets the volume for adverts. Set it to 0% to mute them entirely, or to a low value if you prefer to hear them more quietly."),
            ("⚙️", "Press Ctrl+, at any time to open Settings and change the language, visual theme, or check interval."),
            ("⏱️", "Check interval — defines how often (in tenths of a second) SAMP queries Spotify's state. A lower value is more responsive but uses slightly more CPU; the default (0.5 s) is ideal for most machines."),
        ],
        "about_sws_items": [
            ("📋", "Enabling «Start with Spotify» makes SAMP create a scheduled task in Windows Task Scheduler named SAMP_StartWithSpotify."),
            ("👁️", "The task runs a background PowerShell script that waits for the Spotify.exe process to appear. When Spotify starts, the script waits an additional 2 seconds for Spotify to register its audio session, then launches SAMP automatically."),
            ("🔒", "Registering the task requires administrator privileges; Windows will show a UAC dialog to confirm. The task itself runs with normal user privileges, so SAMP does not need elevation for day-to-day use."),
            ("🗑️", "If you uncheck the option and click Apply, the task is removed from Task Scheduler and SAMP will no longer start automatically. You can re-enable it at any time."),
            ("⚠️", "If you cancel the UAC dialog during registration or removal, the operation is cancelled without changes; SAMP will notify you without crashing. In addition, for the changes to take effect after you apply them, you need to restart your current Windows session."),
        ],
        "about_files_items": [
            ("📄", "README — full installation guide, system requirements, advanced configuration, and FAQ."),
            ("⚖️", "DISCLAIMER.md — legal notice about SAMP usage, liability limitations, and relationship with Spotify AB."),
            ("📁", "Both files are located in the same folder as the SAMP executable (samp.exe)."),
        ],
    },
    "de": {
        "system": "System",
        "song": "Lied",
        "ad": "Werbung",
        "settings": "Einstellungen",
        "theme_dark": "dunkel",
        "theme_light": "hell",
        "theme_forest": "Wald",
        "language_label": "Sprache:",
        "theme_label": "Thema:",
        "subtitle": "Spotify-Werbe-Stummschaltpanel",
        "check_interval_label": "Prüfintervall",
        "apply": "Übernehmen",
        "cancel": "Abbrechen",
        "sws": "Mit Spotify starten",
        "more": "Mehr...",
        "about": "über SAMP",
        "close": "Schließen",

        "about_tutorial_title": "So verwenden Sie SAMP",
        "about_sws_title": "Mit Spotify starten",
        "about_files_title": "Dokumentation",
        "about_how_title": "Funktionsweise",

        "about_how_items": [
            ("🎵", "SAMP überwacht Spotify kontinuierlich über die Windows-GSMTC-API und die System-Audio-API (WASAPI über pycaw)."),
            ("🔍", "Um zwischen einem Lied und einer Werbung zu unterscheiden, prüft SAMP, ob die Schaltfläche „Weiter“ in der Spotify-Sitzung verfügbar ist: Während einer Werbung ist das Überspringen nicht erlaubt."),
            ("🔊", "Bei einer Zustandsänderung (Lied → Werbung oder umgekehrt) passt SAMP das Spotify-Anwendungsvolumen automatisch auf den konfigurierten Wert an, ohne die Systemlautstärke zu ändern."),
        ],
        "about_tutorial_items": [
            ("🖱️", "System-Regler — steuert die Windows-Masterlautstärke, entspricht dem Anpassen über die Taskleiste."),
            ("🎵", "Lied-Regler — legt die Lautstärke für Musik in Spotify fest. Nach persönlichem Geschmack einstellen."),
            ("🔇", "Werbe-Regler — legt die Lautstärke für Werbung fest. Auf 0% setzen, um sie vollständig stummzuschalten."),
            ("⚙️", "Drücken Sie Strg+,, um jederzeit die Einstellungen zu öffnen (Sprache, Thema, Prüfintervall)."),
            ("⏱️", "Prüfintervall — legt fest, wie oft (in Zehntelsekunden) SAMP den Spotify-Status abfragt. Standardwert 0,5 s ist für die meisten Geräte ideal."),
        ],
        "about_sws_items": [
            ("📋", "Bei Aktivierung von „Mit Spotify starten“ erstellt SAMP eine geplante Aufgabe im Windows-Aufgabenplaner namens SAMP_StartWithSpotify."),
            ("👁️", "Die Aufgabe führt ein PowerShell-Skript im Hintergrund aus, das auf den Spotify.exe-Prozess wartet. Nach dem Start von Spotify wartet das Skript 2 Sekunden und startet SAMP dann automatisch."),
            ("🔒", "Das Registrieren der Aufgabe erfordert Administratorrechte; Windows zeigt einen UAC-Dialog zur Bestätigung. Die Aufgabe selbst läuft mit normalen Benutzerrechten."),
            ("🗑️", "Wird die Option deaktiviert und „Übernehmen“ geklickt, wird die Aufgabe entfernt. Sie können sie jederzeit erneut aktivieren."),
            ("⚠️", "Wird der UAC-Dialog abgebrochen, wird der Vorgang ohne Änderungen abgebrochen; SAMP gibt eine entsprechende Meldung aus. Außerdem muss die aktuelle Windows-Sitzung neu gestartet werden, damit die Änderung nach der Anwendung wirksam wird."),
        ],
        "about_files_items": [
            ("📄", "README — vollständige Installationsanleitung, Systemanforderungen, erweiterte Konfiguration und FAQ."),
            ("⚖️", "DISCLAIMER.md — rechtlicher Hinweis zur Nutzung von SAMP und Beziehung zu Spotify AB."),
            ("📁", "Beide Dateien befinden sich im selben Ordner wie die SAMP-EXE (samp.exe)."),
        ],
    },
    "fr": {
        "system": "Système",
        "song": "Chanson",
        "ad": "Publicités",
        "settings": "Paramètres",
        "theme_dark": "sombre",
        "theme_light": "clair",
        "theme_forest": "forêt",
        "language_label": "Langue :",
        "theme_label": "Thème :",
        "subtitle": "Panneau Sourdine Publicités Spotify",
        "check_interval_label": "Intervalle de vérification",
        "apply": "Appliquer",
        "cancel": "Annuler",
        "sws": "Démarrer avec Spotify",
        "more": "Plus...",
        "about": "à propos de SAMP",
        "close": "Fermer",

        "about_tutorial_title": "Comment utiliser SAMP",
        "about_sws_title": "Démarrer avec Spotify",
        "about_files_title": "Documentation",
        "about_how_title": "Fonctionnement",

        "about_how_items": [
            ("🎵", "SAMP surveille continuellement Spotify via l'API Windows GSMTC et l'API audio système (WASAPI via pycaw)."),
            ("🔍", "Pour distinguer une chanson d'une publicité, SAMP vérifie si le bouton Suivant est disponible dans la session Spotify : pendant une pub, passer à la piste suivante n'est pas autorisé."),
            ("🔊", "Lors d'un changement d'état (chanson → pub ou inversement), SAMP ajuste automatiquement le volume de l'application Spotify au niveau configuré, sans toucher au volume système."),
        ],
        "about_tutorial_items": [
            ("🖱️", "Curseur Système — contrôle le volume maître de Windows, équivalent au réglage depuis la barre des tâches."),
            ("🎵", "Curseur Chanson — définit le volume auquel Spotify jouera de la musique. À ajuster selon vos préférences."),
            ("🔇", "Curseur Publicités — définit le volume pour les publicités. Mettez-le à 0% pour les couper complètement."),
            ("⚙️", "Appuyez sur Ctrl+, à tout moment pour ouvrir les Paramètres (langue, thème, intervalle)."),
            ("⏱️", "Intervalle de vérification — définit la fréquence (en dixièmes de seconde) à laquelle SAMP interroge l'état de Spotify. La valeur par défaut (0,5 s) est idéale pour la plupart des machines."),
        ],
        "about_sws_items": [
            ("📋", "En activant « Démarrer avec Spotify », SAMP crée une tâche planifiée dans le Planificateur de tâches Windows nommée SAMP_StartWithSpotify."),
            ("👁️", "La tâche exécute un script PowerShell en arrière-plan qui attend l'apparition du processus Spotify.exe. Une fois Spotify lancé, le script attend 2 secondes supplémentaires puis démarre SAMP automatiquement."),
            ("🔒", "L'enregistrement de la tâche nécessite des droits administrateur ; Windows affichera une boîte de dialogue UAC pour confirmation. La tâche elle-même s'exécute avec les privilèges normaux de l'utilisateur."),
            ("🗑️", "Si vous désactivez l'option et cliquez sur Appliquer, la tâche est supprimée. Vous pouvez la réactiver à tout moment."),
            ("⚠️", "Si vous annulez la boîte de dialogue UAC, l'opération est annulée sans modification ; SAMP vous en informera. De plus, pour que les modifications prennent effet, il faut redémarrer la session Windows en cours."),
        ],
        "about_files_items": [
            ("📄", "README — guide d'installation complet, configuration avancée et FAQ."),
            ("⚖️", "DISCLAIMER.md — avis légal sur l'utilisation de SAMP et relation avec Spotify AB."),
            ("📁", "Ces fichiers se trouvent dans le même dossier que l'exécutable SAMP (samp.exe)."),
        ],
    },
    "pt": {
        "system": "Sistema",
        "song": "Música",
        "ad": "Anúncios",
        "settings": "Configurações",
        "theme_dark": "escuro",
        "theme_light": "claro",
        "theme_forest": "floresta",
        "language_label": "Idioma:",
        "theme_label": "Tema:",
        "subtitle": "Painel Silenciador de Anúncios do Spotify",
        "check_interval_label": "Intervalo de verificação",
        "apply": "Aplicar",
        "cancel": "Cancelar",
        "sws": "Iniciar com Spotify",
        "more": "Mais...",
        "about": "sobre SAMP",
        "close": "Fechar",

        "about_tutorial_title": "Como usar o SAMP",
        "about_sws_title": "Iniciar com Spotify",
        "about_files_title": "Documentação",
        "about_how_title": "Como funciona",

        "about_how_items": [
            ("🎵", "O SAMP monitoriza continuamente o Spotify usando a API GSMTC do Windows e a API de áudio do sistema (WASAPI via pycaw)."),
            ("🔍", "Para distinguir uma música de um anúncio, o SAMP verifica se o botão Seguinte está disponível na sessão do Spotify: durante um anúncio, avançar não é permitido."),
            ("🔊", "Ao detetar uma mudança de estado (música → anúncio ou vice-versa), o SAMP ajusta automaticamente o volume da aplicação Spotify para o nível configurado, sem alterar o volume do sistema."),
        ],
        "about_tutorial_items": [
            ("🖱️", "Controlo Sistema — controla o volume mestre do Windows, equivalente ao ajuste na barra de tarefas."),
            ("🎵", "Controlo Música — define o volume com que o Spotify reproduz música. Ajuste conforme preferir."),
            ("🔇", "Controlo Anúncios — define o volume para os anúncios. Coloque em 0% para os silenciar completamente."),
            ("⚙️", "Prima Ctrl+, a qualquer momento para abrir as Configurações (idioma, tema, intervalo)."),
            ("⏱️", "Intervalo de verificação — define com que frequência (em décimos de segundo) o SAMP consulta o estado do Spotify. O valor padrão (0,5 s) é ideal para a maioria dos computadores."),
        ],
        "about_sws_items": [
            ("📋", "Ao ativar «Iniciar com Spotify», o SAMP cria uma tarefa agendada no Agendador de Tarefas do Windows com o nome SAMP_StartWithSpotify."),
            ("👁️", "A tarefa executa um script PowerShell em segundo plano que aguarda o aparecimento do processo Spotify.exe. Quando o Spotify arranca, o script aguarda mais 2 segundos e depois inicia o SAMP automaticamente."),
            ("🔒", "O registo da tarefa requer privilégios de administrador; o Windows mostrará o diálogo UAC para confirmação. A tarefa em si corre com os privilégios normais do utilizador."),
            ("🗑️", "Se desativar a opção e clicar em Aplicar, a tarefa é removida. Pode reativá-la a qualquer momento."),
            ("⚠️", "Se cancelar o diálogo UAC, a operação é cancelada sem alterações; o SAMP notificá-lo-á sem bloquear. Além disso, para que as alterações tenham efeito após a aplicação, é necessário reiniciar a sessão atual do Windows."),
        ],
        "about_files_items": [
            ("📄", "README — guia completo de instalação, configuração avançada e FAQ."),
            ("⚖️", "DISCLAIMER.md — aviso legal sobre o uso do SAMP e relação com a Spotify AB."),
            ("📁", "Ambos os ficheiros encontram-se na mesma pasta que o executável do SAMP (samp.exe)."),
        ],
    },
    "ru": {
        "system": "Система",
        "song": "Песня",
        "ad": "Реклама",
        "settings": "Настройки",
        "theme_dark": "тёмная",
        "theme_light": "cветлая",
        "theme_forest": "лесная",
        "language_label": "Язык:",
        "theme_label": "Тема:",
        "subtitle": "Панель приглушения рекламы Spotify",
        "check_interval_label": "Интервал проверки",
        "apply": "Применить",
        "cancel": "Отмена",
        "sws": "Запускать со Spotify",
        "more": "Ещё...",
        "about": "О SAMP",
        "close": "Закрыть",

        "about_tutorial_title": "Как пользоваться SAMP",
        "about_sws_title": "Запуск вместе со Spotify",
        "about_files_title": "Документация",
        "about_how_title": "Принцип работы",

        "about_how_items": [
            ("🎵", "SAMP непрерывно отслеживает Spotify через Windows GSMTC API и системный аудио API (WASAPI через pycaw)."),
            ("🔍", "Для различения музыки и рекламы SAMP проверяет доступность кнопки «Следующий» в сессии Spotify: во время рекламы переключение треков недоступно."),
            ("🔊", "При обнаружении смены состояния (музыка → реклама или наоборот) SAMP автоматически регулирует громкость приложения Spotify до настроенного уровня, не затрагивая системную громкость."),
        ],
        "about_tutorial_items": [
            ("🖱️", "Ползунок «Система» — управляет мастер-громкостью Windows, аналогично регулировке из панели задач."),
            ("🎵", "Ползунок «Песня» — задаёт громкость, с которой Spotify будет воспроизводить музыку. Настройте по своему вкусу."),
            ("🔇", "Ползунок «Реклама» — задаёт громкость для рекламы. Установите 0%, чтобы полностью заглушить её."),
            ("⚙️", "Нажмите Ctrl+, в любой момент, чтобы открыть настройки (язык, тема, интервал проверки)."),
            ("⏱️", "Интервал проверки — определяет, как часто (в десятых долях секунды) SAMP опрашивает состояние Spotify. Значение по умолчанию 0,5 с оптимально для большинства устройств."),
        ],
        "about_sws_items": [
            ("📋", "При включении «Запускать со Spotify» SAMP создаёт задание в Планировщике задач Windows с именем SAMP_StartWithSpotify."),
            ("👁️", "Задание запускает фоновый скрипт PowerShell, который ожидает появления процесса Spotify.exe. Когда Spotify запустится, скрипт ждёт ещё 2 секунды для регистрации аудиосессии, затем автоматически запускает SAMP."),
            ("🔒", "Регистрация задания требует прав администратора; Windows покажет диалог UAC. Само задание выполняется с обычными правами пользователя."),
            ("🗑️", "Если отключить опцию и нажать «Применить», задание будет удалено. Вы можете повторно включить его в любое время."),
            ("⚠️", "Если отменить диалог UAC, операция прерывается без изменений; SAMP уведомит вас об этом. Кроме того, чтобы он заработал после установки, необходимо перезапустить текущую сессию Windows."),
        ],
        "about_files_items": [
            ("📄", "README — полное руководство по установке, расширенная настройка и FAQ."),
            ("⚖️", "DISCLAIMER.md — юридическое уведомление об использовании SAMP и отношениях со Spotify AB."),
            ("📁", "Оба файла находятся в той же папке, что и исполняемый файл SAMP (samp.exe)."),
        ],
    },
    "it": {
        "system": "Sistema",
        "song": "Canzone",
        "ad": "Annunci",
        "settings": "Impostazioni",
        "theme_dark": "scuro",
        "theme_light": "chiaro",
        "theme_forest": "foresta",
        "language_label": "Lingua:",
        "theme_label": "Tema:",
        "subtitle": "Pannello Silenziatore Annunci Spotify",
        "check_interval_label": "Intervallo di controllo",
        "apply": "Applica",
        "cancel": "Annulla",
        "sws": "Avvia con Spotify",
        "more": "Altro...",
        "about": "informazioni su SAMP",
        "close": "Chiudi",

        "about_tutorial_title": "Come usare SAMP",
        "about_sws_title": "Avvia con Spotify",
        "about_files_title": "Documentazione",
        "about_how_title": "Come funziona",

        "about_how_items": [
            ("🎵", "SAMP monitora continuamente Spotify tramite l'API Windows GSMTC e l'API audio di sistema (WASAPI tramite pycaw)."),
            ("🔍", "Per distinguere una canzone da un annuncio, SAMP verifica se il pulsante Avanti è disponibile nella sessione Spotify: durante un annuncio, saltare la traccia non è consentito."),
            ("🔊", "Quando viene rilevato un cambio di stato (canzone → annuncio o viceversa), SAMP regola automaticamente il volume dell'applicazione Spotify al livello configurato, senza modificare il volume di sistema."),
        ],
        "about_tutorial_items": [
            ("🖱️", "Cursore Sistema — controlla il volume principale di Windows, equivalente alla regolazione dalla barra delle applicazioni."),
            ("🎵", "Cursore Canzone — imposta il volume con cui Spotify riprodurrà la musica. Regolalo secondo le tue preferenze."),
            ("🔇", "Cursore Annunci — imposta il volume per gli annunci. Mettilo a 0% per silenziare completamente la pubblicità."),
            ("⚙️", "Premi Ctrl+, in qualsiasi momento per aprire le Impostazioni (lingua, tema, intervallo di controllo)."),
            ("⏱️", "Intervallo di controllo — definisce ogni quanto (in decimi di secondo) SAMP interroga lo stato di Spotify. Il valore predefinito (0,5 s) è ideale per la maggior parte dei computer."),
        ],
        "about_sws_items": [
            ("📋", "Attivando «Avvia con Spotify», SAMP crea un'attività pianificata nell'Utilità di pianificazione di Windows denominata SAMP_StartWithSpotify."),
            ("👁️", "L'attività esegue uno script PowerShell in background che attende la comparsa del processo Spotify.exe. Quando Spotify si avvia, lo script attende altri 2 secondi e poi avvia SAMP automaticamente."),
            ("🔒", "La registrazione dell'attività richiede privilegi di amministratore; Windows mostrerà la finestra di dialogo UAC per la conferma. L'attività stessa viene eseguita con i normali privilegi utente."),
            ("🗑️", "Se si disattiva l'opzione e si fa clic su Applica, l'attività viene rimossa. Puoi riattivarla in qualsiasi momento."),
            ("⚠️", "Se si annulla il dialogo UAC, l'operazione viene interrotta senza modifiche; SAMP ti notificherà senza bloccarsi. Inoltre, affinché funzioni una volta applicato, è necessario riavviare la sessione corrente di Windows."),
        ],
        "about_files_items": [
            ("📄", "README — guida completa all'installazione, configurazione avanzata e FAQ."),
            ("⚖️", "DISCLAIMER.md — avviso legale sull'utilizzo di SAMP e relazione con Spotify AB."),
            ("📁", "Entrambi i file si trovano nella stessa cartella dell'eseguibile SAMP (samp.exe)."),
        ],
    }
}

# --- THEME_EXTRAS ---
THEME_ABOUT_COLORS = {
    "dark": {
        "header_bg":     "#0D1B2A",
        "header_fg":     "#E0E1DD",
        "header_sub":    "#778DA9",
        "section_fg":    "#778DA9",
        "card_bg":       "#243347",
        "card_border":   "#2e4460",
        "emoji_bg":      "#1B263B",
        "body_fg":       "#C8CBD0",
        "version_fg":    "#415A77",
        "close_bg":      "#415A77",
        "close_fg":      "#E0E1DD",
        "close_hover":   "#4e6d8c",
        "dialog_bg":     "#1B263B",
    },
    "light": {
        "header_bg":     "#EAF4FB",
        "header_fg":     "#1A5E80",
        "header_sub":    "#2C7DA0",
        "section_fg":    "#2C7DA0",
        "card_bg":       "#F0F8FF",
        "card_border":   "#A9D6E5",
        "emoji_bg":      "#D1E8F2",
        "body_fg":       "#2C4A5A",
        "version_fg":    "#5A9CB8",
        "close_bg":      "#2C7DA0",
        "close_fg":      "#FFFFFF",
        "close_hover":   "#1A5E80",
        "dialog_bg":     "#FFFFFF",
    },
    "forest": {
        "header_bg":     "#293237",
        "header_fg":     "#b7c6c9",
        "header_sub":    "#647c5f",
        "section_fg":    "#8aab80",
        "card_bg":       "#3a4f4b",
        "card_border":   "#3d524e",
        "emoji_bg":      "#293237",
        "body_fg":       "#a3b8b5",
        "version_fg":    "#647c5f",
        "close_bg":      "#647c5f",
        "close_fg":      "#060807",
        "close_hover":   "#4a5c47",
        "dialog_bg":     "#4d6561",
    },
}


def apply_theme(theme: str):
    shared = """
        QLabel[section="true"] {
            font-size: 8pt;
            letter-spacing: 1px;
            text-transform: uppercase;
            border: none;
            background: transparent;
            padding: 0;
        }
        QFrame[role="separator"] {
            border: none;
            max-height: 1px;
            min-height: 1px;
        }
        QPushButton[role="primary"] {
            font-weight: 600;
            padding: 5px 18px;
        }
    """
    match theme:
        case "light":
            style = """
                QMainWindow { background: #E8F4F8; color: #2C7DA0; }
                QMainWindow > QWidget { background: #FFFFFF; }
                QDialog { background: #FFFFFF; color: #2C7DA0; }
                QSlider::groove:horizontal { height: 6px; background: #A9D6E5; border-radius: 3px; }
                QSlider::handle:horizontal { background: #FFFFFF; border: 2px solid #2C7DA0; width: 10px; height: 14px; margin: -4px 0; border-radius: 7px; }
                QSlider::sub-page:horizontal { background: #2C7DA0; border-radius: 3px; }
                QLabel { font-family: 'Segoe UI Variable', 'Segoe UI'; font-size: 11pt; color: #2C7DA0; }
                QLabel[key="true"] { background-color: #D1E8E2; color: #2C7DA0; border: 1px solid #A9D6E5; border-radius: 6px; padding: 3px 3px; font-family: 'Consolas', 'Courier New', monospace; font-size: 9pt; }
                QLabel[section="true"] { color: #2C7DA0; }
                QPushButton { background: #D1E8E2; color: #2C7DA0; border: 1px solid #A9D6E5; border-radius: 5px; padding: 4px 12px; }
                QPushButton:hover { background: #A9D6E5; }
                QPushButton:pressed { background: #2C7DA0; color: #FFFFFF; border-color: #2C7DA0; }
                QPushButton[role="primary"] { background: #2C7DA0; color: #FFFFFF; border-color: #2C7DA0; }
                QPushButton[role="primary"]:hover { background: #A9D6E5; color: #2C7DA0; }
                QComboBox { background: #D1E8E2; color: #2C7DA0; border: 1px solid #A9D6E5; border-radius: 5px; padding: 2px 6px; }
                QComboBox::drop-down { border: none; }
                QComboBox QAbstractItemView { background: #FFFFFF; color: #2C7DA0; selection-background-color: #2C7DA0; selection-color: #FFFFFF; }
                QFrame[role="separator"] { background: #A9D6E5; }
            """
        case "forest":
            style = """
                QMainWindow { background: #293237; color: #b7c6c9; }
                QMainWindow > QWidget { background: #4d6561; }
                QDialog { background: #4d6561; color: #b7c6c9; }
                QSlider::groove:horizontal { height: 6px; background: #293237; border-radius: 3px; }
                QSlider::handle:horizontal { background: #b7c6c9; border: 2px solid #060807; width: 10px; height: 14px; margin: -4px 0; border-radius: 7px; }
                QSlider::sub-page:horizontal { background: #647c5f; border-radius: 3px; }
                QLabel { font-family: 'Segoe UI Variable', 'Segoe UI'; font-size: 11pt; color: #b7c6c9; }
                QLabel[key="true"] { background-color: #293237; color: #b7c6c9; border: 1px solid #647c5f; border-radius: 6px; padding: 3px 3px; font-family: 'Consolas', 'Courier New', monospace; font-size: 9pt; }
                QLabel[section="true"] { color: #FFFFFF; }
                QPushButton { background: #293237; color: #b7c6c9; border: 1px solid #647c5f; border-radius: 5px; padding: 4px 12px; }
                QPushButton:hover { background: #647c5f; color: #060807; }
                QPushButton:pressed { background: #060807; color: #b7c6c9; border-color: #b7c6c9; }
                QPushButton[role="primary"] { background: #647c5f; color: #060807; border-color: #4a5c47; }
                QPushButton[role="primary"]:hover { background: #4a5c47; color: #b7c6c9; }
                QComboBox { background: #293237; color: #b7c6c9; border: 1px solid #647c5f; border-radius: 5px; padding: 2px 6px; }
                QComboBox::drop-down { border: none; }
                QComboBox QAbstractItemView { background: #4d6561; color: #b7c6c9; selection-background-color: #647c5f; selection-color: #060807; }
                QFrame[role="separator"] { background: #3d524e; }
            """
        case "dark" | _:
            style = """
                QMainWindow { background: #0D1B2A; color: #E0E1DD; }
                QMainWindow > QWidget { background: #1B263B; }
                QDialog { background: #1B263B; color: #E0E1DD; }
                QSlider::groove:horizontal { height: 6px; background: #415A77; border-radius: 3px; }
                QSlider::handle:horizontal { background: #778DA9; border: 2px solid #E0E1DD; width: 10px; height: 14px; margin: -4px 0; border-radius: 7px; }
                QSlider::sub-page:horizontal { background: #778DA9; border-radius: 3px; }
                QLabel { font-family: 'Segoe UI Variable', 'Segoe UI'; font-size: 11pt; color: #E0E1DD; }
                QLabel[key="true"] { background-color: #E0E0E0; color: #E0E1DD; border: 1px solid #aaa; border-radius: 6px; padding: 3px 3px; font-family: 'Consolas', 'Courier New', monospace; font-size: 9pt; }
                QLabel[section="true"] { color: #4e6480; }
                QPushButton { background: #415A77; color: #E0E1DD; border: 1px solid #2e4460; border-radius: 5px; padding: 4px 12px; }
                QPushButton:hover { background: #4e6d8c; }
                QPushButton:pressed { background: #778DA9; color: #0D1B2A; }
                QPushButton[role="primary"] { background: #778DA9; color: #0D1B2A; border-color: #5a7a96; }
                QPushButton[role="primary"]:hover { background: #8fa3b8; }
                QComboBox { background: #415A77; color: #E0E1DD; border: 1px solid #2e4460; border-radius: 5px; padding: 2px 6px; }
                QComboBox::drop-down { border: none; }
                QComboBox QAbstractItemView { background: #1B263B; color: #E0E1DD; selection-background-color: #415A77; selection-color: #E0E1DD; }
                QFrame[role="separator"] { background: #2e4460; }
            """
    QApplication.instance().setStyleSheet(style + shared)


# --- Volumen del sistema ---
def gv():
    """gv: get_volume (sys vol)"""
    try:
        speakers = AudioUtilities.GetSpeakers()
        volume = speakers.EndpointVolume
        return volume.GetMasterVolumeLevelScalar()
    except Exception as e:
        print(f"Error al obtener volumen del sistema: {e}")
        return 1.0

def sv(value: float):
    """sv: set_volume (sys vol)"""
    try:
        speakers = AudioUtilities.GetSpeakers()
        volume = speakers.EndpointVolume
        volume.SetMasterVolumeLevelScalar(value, None)
        state.expected_sys_volume = value
    except Exception as e:
        print(f"Error al establecer volumen del sistema: {e}")


# --- Caché de sesión de Spotify ---
_spotify_vol_cache: ISimpleAudioVolume | None = None
_spotify_pid_cache: int | None = None

def _get_spotify_volume_ctl() -> ISimpleAudioVolume | None:
    """Devuelve el control de volumen de Spotify, usando caché."""
    global _spotify_vol_cache, _spotify_pid_cache
    if _spotify_vol_cache is not None and _spotify_pid_cache is not None:
        try:
            import psutil
            psutil.Process(_spotify_pid_cache)
            return _spotify_vol_cache
        except (NoSuchProcess, Exception):
            _spotify_vol_cache = None
            _spotify_pid_cache = None

    for session in AudioUtilities.GetAllSessions():
        try:
            proc = session.Process
            if proc and proc.name() == "Spotify.exe":
                ctl = session._ctl.QueryInterface(ISimpleAudioVolume)
                _spotify_vol_cache = ctl
                _spotify_pid_cache = proc.pid
                return ctl
        except (NoSuchProcess, ProcessLookupError, AttributeError):
            continue
    return None

def gsv() -> float | None:
    """gsv: get_spotify_volume"""
    ctl = _get_spotify_volume_ctl()
    if ctl is None:
        return None
    try:
        return ctl.GetMasterVolume()
    except Exception:
        global _spotify_vol_cache, _spotify_pid_cache
        _spotify_vol_cache = None
        _spotify_pid_cache = None
        return None

def ssv(value: float):
    """ssv: set_spotify_volume"""
    ctl = _get_spotify_volume_ctl()
    if ctl is None:
        return
    try:
        ctl.SetMasterVolume(value, None)
        state.expected_volume = value
    except Exception:
        global _spotify_vol_cache, _spotify_pid_cache
        _spotify_vol_cache = None
        _spotify_pid_cache = None


# --- StateManager ---
class StateManager:
    song_vol = 1.0
    ad_vol = 1.0
    current_state: str | None = None
    expected_volume: float | None = None
    expected_sys_volume: float | None = None
    check_interval = 0.5
    sws = False

state = StateManager()


# --- ssbd ---
async def ssbd():
    """ssbd: spotify_skip_button_detection"""
    manager = await GSMTCM.request_async()
    last_state: str | None = None

    while True:
        await asyncio.sleep(state.check_interval)

        sys_vol = gsv()
        if sys_vol is None:
            continue

        if state.expected_volume is None:
            state.expected_volume = sys_vol

        external_change = abs(sys_vol - state.expected_volume) > 0.001

        session = manager.get_current_session()
        current: str | None = None
        if session and "Spotify" in (session.source_app_user_model_id or ""):
            # Heurística "fail-safe": por defecto tratamos la sesión como
            # anuncio salvo que podamos CONFIRMAR positivamente que es una
            # canción (is_next_enabled == True). Antes, cualquier sesión con
            # datos incompletos (playback_status distinto de 4, controls
            # ausentes, is_next_enabled no disponible —como ocurre con
            # anuncios tipo "Ad in progress" u otros anuncios "atípicos"—)
            # dejaba `current` en None y el ciclo se saltaba sin tocar el
            # volumen ni el estado. Eso provocaba que, si ese anuncio era el
            # primero detectado, sonara al volumen de canción (sin silenciar)
            # y que, si aparecía tras un anuncio normal, el silenciamiento
            # anterior se mantuviera solo por inercia, no por detección real.
            playback = session.get_playback_info()
            is_playing = bool(playback) and playback.playback_status == 4
            controls = playback.controls if playback else None
            is_confirmed_song = bool(
                is_playing and controls and controls.is_next_enabled
            )
            current = "song" if is_confirmed_song else "ad"

        if current is None:
            continue

        state.current_state = current
        state_changed = current != last_state

        s_slider = window.song_slider
        a_slider = window.ad_slider

        def _sync_slider_to_vol(slider, vol: float) -> None:
            pct = int(vol * 100)
            slider.slider.blockSignals(True)
            slider.setValue(pct)
            slider.percent.setText(f"{pct}%")
            slider.slider.blockSignals(False)

        if external_change and not state_changed:
            is_song = current == "song"
            if is_song and not window.song_dragging:
                _sync_slider_to_vol(s_slider, sys_vol)
            elif not is_song and not window.ad_dragging:
                _sync_slider_to_vol(a_slider, sys_vol)
            state.expected_volume = sys_vol

        elif state_changed:
            if external_change:
                is_song = current == "song"
                if is_song and not window.song_dragging:
                    _sync_slider_to_vol(s_slider, sys_vol)
                elif not is_song and not window.ad_dragging:
                    _sync_slider_to_vol(a_slider, sys_vol)
                state.expected_volume = sys_vol
            else:
                desired = state.song_vol if current == "song" else state.ad_vol
                if abs(desired - sys_vol) > 0.001:
                    ssv(desired)
                    target_slider = s_slider if current == "song" else a_slider
                    target_slider.setValue(int(desired * 100))
            last_state = current


# --- Callback de volumen del sistema ---
class SystemVolumeCallback(COMObject):
    _com_interfaces_ = [IAudioEndpointVolumeCallback]

    def __init__(self, window):
        super().__init__()
        self.window = window

    def OnNotify(self, pNotify):
        from PyQt6.QtCore import QMetaObject, Qt
        QMetaObject.invokeMethod(
            self.window,
            "sync_sys_slider_now",
            Qt.ConnectionType.QueuedConnection
        )


# --- GUI helpers ---
def _make_separator() -> QFrame:
    sep = QFrame()
    sep.setProperty("role", "separator")
    sep.setFrameShape(QFrame.Shape.HLine)
    sep.setFrameShadow(QFrame.Shadow.Plain)
    return sep


class VolumeSlider(QWidget):
    def __init__(self, icon_svg: bytes, label_text: str, initial=100, icon_color: str = None):
        super().__init__()
        self._svg_bytes  = icon_svg
        self._icon_color = icon_color

        self.setFixedHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.icon_label = QLabel()
        pixmap = svgtp(icon_svg, QSize(24, 24), icon_color)
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setFixedSize(24, 24)

        self.label = QLabel(label_text)
        self.label.setFixedWidth(70)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(initial)
        self.slider.setFixedHeight(40)

        self.percent = QLabel(f"{initial}%")
        self.percent.setFixedWidth(40)
        self.percent.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self.icon_label, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.label,      0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.slider,     0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.percent,    0, Qt.AlignmentFlag.AlignVCenter)

        self.slider.valueChanged.connect(self._update_percent)

    def _update_percent(self, val):
        self.percent.setText(f"{val}%")

    def value(self):
        return self.slider.value() / 100.0

    def setValue(self, percent):
        self.slider.setValue(percent)

    def set_label(self, text: str):
        self.label.setText(text)


# --- Sobre SAMP ---
class AboutDialog(QDialog):
    def __init__(self, parent: QDialog, lang: str, theme: str = None):
        super().__init__(parent)
        self._lang = lang
        strings = LANG_STRINGS[lang]
        _theme = theme if theme is not None else current_theme
        c = THEME_ABOUT_COLORS.get(_theme, THEME_ABOUT_COLORS["dark"])

        self.setWindowTitle(f"SAMP  –  {strings['about']}  (v{version})")
        pixmap = svgtp(SAMP_SVG, QSize(512, 512), color="#CC7722")
        self.setWindowIcon(QIcon(pixmap))
        self.setFixedSize(520, 620)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        # Raíz
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Cabecera
        header = QWidget()
        header.setFixedHeight(72)
        header.setStyleSheet(f"""background: {c['header_bg']}; border-bottom: 1px solid {c['card_border']};""")
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(20, 0, 20, 0)
        hlay.setSpacing(14)

        logo_lbl = QLabel()
        logo_px = svgtp(SAMP_SVG, QSize(36, 36), color="#CC7722")
        logo_lbl.setPixmap(logo_px)
        logo_lbl.setFixedSize(36, 36)
        logo_lbl.setStyleSheet("background: transparent; border: none;")

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        title_lbl = QLabel("SAMP")
        title_lbl.setStyleSheet(f"color: {c['header_fg']}; font-size: 15pt; font-weight: 700; background: transparent; border: none;")
        sub_lbl = QLabel(strings["subtitle"])
        sub_lbl.setStyleSheet(f"color: {c['header_sub']}; font-size: 8pt; background: transparent; border: none;")
        title_col.addWidget(title_lbl)
        title_col.addWidget(sub_lbl)

        ver_lbl = QLabel(f"v{version}")
        ver_lbl.setStyleSheet(f"color: {c['version_fg']}; font-size: 8pt; font-weight: 600; background: transparent; border: none;")
        ver_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        hlay.addWidget(logo_lbl, 0, Qt.AlignmentFlag.AlignVCenter)
        hlay.addLayout(title_col, 1)
        hlay.addWidget(ver_lbl, 0, Qt.AlignmentFlag.AlignVCenter)
        root.addWidget(header)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"background: {c['dialog_bg']}; border: none;")

        content_widget = QWidget()
        content_widget.setStyleSheet(f"background: {c['dialog_bg']};")
        content_lay = QVBoxLayout(content_widget)
        content_lay.setContentsMargins(16, 16, 16, 8)
        content_lay.setSpacing(12)

        # Secciones
        sections = [
            (strings["about_how_title"],      strings["about_how_items"]),
            (strings["about_tutorial_title"], strings["about_tutorial_items"]),
            (strings["about_sws_title"],      strings["about_sws_items"]),
            (strings["about_files_title"],    strings["about_files_items"]),
        ]

        for title, items in sections:
            content_lay.addWidget(self._make_section(title, items, c))

        content_lay.addStretch()
        scroll.setWidget(content_widget)
        root.addWidget(scroll, 1)

        # Footer
        footer = QWidget()
        footer.setFixedHeight(52)
        footer.setStyleSheet(
            f"background: {c['header_bg']}; "
            f"border-top: 1px solid {c['card_border']};"
        )
        flay = QHBoxLayout(footer)
        flay.setContentsMargins(16, 0, 16, 0)

        close_btn = QPushButton(strings["close"])
        close_btn.setFixedSize(100, 32)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['close_bg']};
                color: {c['close_fg']};
                border: none;
                border-radius: 5px;
                font-weight: 600;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background: {c['close_hover']};
            }}
            QPushButton:pressed {{
                opacity: 0.8;
            }}
        """)
        close_btn.clicked.connect(self.accept)

        flay.addStretch()
        flay.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        root.addWidget(footer)

    # Helpers

    def _make_section(self, title: str, items: list[tuple[str, str]], c: dict) -> QWidget:
        """Crea un bloque con encabezado de sección y tarjetas de ítems."""
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        # Encabezado de sección
        sec_lbl = QLabel(title.upper())
        sec_lbl.setStyleSheet(
            f"color: {c['section_fg']}; font-size: 7pt; font-weight: 700; "
            "letter-spacing: 1.5px; background: transparent; border: none; "
            "padding-left: 2px;"
        )
        lay.addWidget(sec_lbl)

        # Tarjeta contenedora de ítems
        card = QWidget()
        card.setStyleSheet(f"background: {c['card_bg']}; border: 1px solid {c['card_border']}; border-radius: 8px;")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(12, 10, 12, 10)
        card_lay.setSpacing(0)

        for i, (emoji, text) in enumerate(items):
            card_lay.addWidget(self._make_item(emoji, text, c))
            if i < len(items) - 1:
                div = QFrame()
                div.setFrameShape(QFrame.Shape.HLine)
                div.setStyleSheet(
                    f"color: {c['card_border']}; "
                    f"background: {c['card_border']}; "
                    "border: none; max-height: 1px; min-height: 1px; "
                    "margin: 2px 0px;"
                )
                card_lay.addWidget(div)

        lay.addWidget(card)
        return container

    def _make_item(self, emoji: str, text: str, c: dict) -> QWidget:
        """Crea una fila con emoji a la izquierda y texto a la derecha."""
        row = QWidget()
        row.setStyleSheet(f"background: {c['card_bg']}; border: none;")
        rlay = QHBoxLayout(row)
        rlay.setContentsMargins(0, 6, 0, 6)
        rlay.setSpacing(10)

        emoji_lbl = QLabel(emoji)
        emoji_lbl.setFixedSize(28, 28)
        emoji_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        emoji_lbl.setStyleSheet(
            f"background: {c['emoji_bg']}; border-radius: 6px; "
            "font-size: 13pt; border: none;"
        )

        text_lbl = QLabel(text)
        text_lbl.setWordWrap(True)
        text_lbl.setStyleSheet(
            f"color: {c['body_fg']}; font-size: 9pt; "
            "background: transparent; border: none;"
        )
        text_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        rlay.addWidget(emoji_lbl, 0, Qt.AlignmentFlag.AlignTop)
        rlay.addWidget(text_lbl, 1)
        return row


# --- Ajustes ---
class SettingsWindow(QDialog):
    def __init__(self, parent: "MainWindow"):
        super().__init__(parent)
        self._main_win = parent

        self.setFixedSize(400, 290)
        pixmap = svgtp(SAMP_SVG, QSize(512, 512), color="#CC7722")
        self.setWindowIcon(QIcon(pixmap))

        self._original_lang = current_language
        self._original_theme = current_theme
        self._original_interval = state.check_interval

        self._selected_lang = current_language
        self._selected_theme = current_theme
        self._selected_interval = state.check_interval
        self._selected_sws = False

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(0)

        self.section_appearance = QLabel()
        self.section_appearance.setProperty("section", True)
        root.addWidget(self.section_appearance)
        root.addSpacing(6)

        appearance_row = QHBoxLayout()
        appearance_row.setSpacing(10)

        lang_col = QVBoxLayout()
        lang_col.setSpacing(3)
        self.lang_label = QLabel()
        lang_col.addWidget(self.lang_label)
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Deutsch  (🇩🇪)", "de")
        self.lang_combo.addItem("English  (🇬🇧)", "en")
        self.lang_combo.addItem("español  (🇪🇸)", "es")
        self.lang_combo.addItem("français  (🇫🇷)", "fr")
        self.lang_combo.addItem("italiano  (🇮🇹)", "it")
        self.lang_combo.addItem("português  (🇵🇹)", "pt")
        self.lang_combo.addItem("русский  (🇷🇺)", "ru")
        self.lang_combo.setCurrentIndex(self.lang_combo.findData(self._selected_lang))
        lang_col.addWidget(self.lang_combo)

        theme_col = QVBoxLayout()
        theme_col.setSpacing(3)
        self.theme_label = QLabel()
        theme_col.addWidget(self.theme_label)
        self.theme_combo = QComboBox()
        self.update_theme_combo_items()
        theme_col.addWidget(self.theme_combo)

        appearance_row.addLayout(lang_col, 3)
        appearance_row.addLayout(theme_col, 2)
        root.addLayout(appearance_row)

        root.addSpacing(14)
        root.addWidget(_make_separator())
        root.addSpacing(12)

        self.section_behavior = QLabel()
        self.section_behavior.setProperty("section", True)
        root.addWidget(self.section_behavior)
        root.addSpacing(8)

        sws_row = QHBoxLayout()
        sws_row.setSpacing(8)
        self.spotify_check_label = QLabel()
        self.spotify_check = QCheckBox()
        self.spotify_check.setChecked(False)
        self.spotify_check.setEnabled(False)
        self.spotify_check.toggled.connect(lambda checked: setattr(self, '_selected_sws', checked))
        sws_row.addWidget(self.spotify_check_label)
        sws_row.addStretch()
        sws_row.addWidget(self.spotify_check)
        root.addLayout(sws_row)

        root.addSpacing(12)

        self.check_interval_label = QLabel()
        root.addWidget(self.check_interval_label)
        root.addSpacing(4)

        slider_row = QHBoxLayout()
        slider_row.setSpacing(8)
        self.check_slider = QSlider(Qt.Orientation.Horizontal)
        self.check_slider.setRange(1, 50)
        self.check_slider.setValue(int(self._selected_interval * 10))
        self.check_slider.valueChanged.connect(self.on_check_interval_changed)
        self.check_value_label = QLabel()
        self.check_value_label.setFixedWidth(36)
        self.check_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.check_value_label.setText(f"{self._selected_interval:.1f}s")
        slider_row.addWidget(self.check_slider, 1)
        slider_row.addWidget(self.check_value_label)
        root.addLayout(slider_row)

        root.addSpacing(14)
        root.addWidget(_make_separator())
        root.addSpacing(10)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        self.cancel_button = QPushButton()
        self.apply_button  = QPushButton()
        self.apply_button.setProperty("role", "primary")
        self.apply_button.setDefault(True)
        self.more_button = QPushButton()
        button_row.addWidget(self.more_button)
        button_row.addStretch()
        button_row.addWidget(self.cancel_button)
        button_row.addWidget(self.apply_button)
        root.addLayout(button_row)

        self.update_settings_texts()

        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.apply_changes)
        self.more_button.clicked.connect(self.open_more_dialog)

        QTimer.singleShot(0, lambda: asyncio.ensure_future(self._init_sws_state_async()))

    def open_more_dialog(self):
        AboutDialog(self, self._selected_lang, self._selected_theme).exec()

    async def _init_sws_state_async(self):
        loop = asyncio.get_event_loop()
        try:
            exists = await loop.run_in_executor(None, sws_task_exists)
        except Exception:
            exists = False
        self._selected_sws = exists
        state.sws = exists
        self.spotify_check.setChecked(exists)
        self.spotify_check.setEnabled(True)

    def on_check_interval_changed(self, val: int) -> None:
        self._selected_interval = val / 10.0
        self.check_value_label.setText(f"{self._selected_interval:.1f}s")

    def on_language_changed(self) -> None:
        new_lang = self.lang_combo.currentData()
        if new_lang != self._selected_lang:
            self._selected_lang = new_lang
            self.update_settings_texts()

    def on_theme_changed(self) -> None:
        new_theme = self.theme_combo.currentData()
        if new_theme != self._selected_theme:
            self._selected_theme = new_theme
            apply_theme(self._selected_theme)

    def update_theme_combo_items(self) -> None:
        strings = LANG_STRINGS[self._selected_lang]
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        self.theme_combo.addItem(strings["theme_dark"],   "dark")
        self.theme_combo.addItem(strings["theme_light"],  "light")
        self.theme_combo.addItem(strings["theme_forest"], "forest")
        idx = self.theme_combo.findData(self._selected_theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        self.theme_combo.blockSignals(False)

    def update_settings_texts(self) -> None:
        lang = self._selected_lang
        strings = LANG_STRINGS[lang]
        self.setWindowTitle("SAMP  –  " + strings["settings"])
        self.lang_label.setText(strings["language_label"])
        self.theme_label.setText(strings["theme_label"])
        self.check_interval_label.setText(strings["check_interval_label"])
        self.spotify_check_label.setText(strings["sws"])
        self.cancel_button.setText(strings["cancel"])
        self.apply_button.setText(strings["apply"])
        self.more_button.setText(strings["more"])
        section_labels = {
            "es": ("Apariencia", "Comportamiento"),
            "en": ("Appearance", "Behavior"),
            "de": ("Erscheinungsbild", "Verhalten"),
            "fr": ("Apparence", "Comportement"),
            "pt": ("Aparência", "Comportamento"),
            "ru": ("Внешний вид", "Поведение"),
            "it": ("Aspetto", "Comportamento"),
        }
        app_label, beh_label = section_labels.get(lang, ("Appearance", "Behavior"))
        self.section_appearance.setText(app_label.upper())
        self.section_behavior.setText(beh_label.upper())
        self.update_theme_combo_items()

    def apply_changes(self) -> None:
        global current_language, current_theme
        current_language = self._selected_lang
        current_theme    = self._selected_theme
        state.check_interval = self._selected_interval

        apply_theme(current_theme)
        self._main_win.update_texts()

        # Cierra el diálogo YA; la parte de sws se resuelve en segundo plano
        self.accept()
        asyncio.ensure_future(self._apply_sws_async())

    def reject(self) -> None:
        if self._selected_theme != self._original_theme:
            apply_theme(self._original_theme)
        super().reject()

    async def _apply_sws_async(self) -> None:
        loop = asyncio.get_event_loop()
        samp_exe = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(sys.argv[0])

        try:
            currently_exists = await loop.run_in_executor(None, sws_task_exists)

            if self._selected_sws and not currently_exists:
                await loop.run_in_executor(None, register_sws_task, samp_exe)
            elif not self._selected_sws and currently_exists:
                await loop.run_in_executor(None, unregister_sws_task)
        except (SWSElevationCancelled, SWSElevationTimeout) as e:
            # UAC cancelado o sin respuesta: no asumimos nada, abajo se
            # reconcilia state.sws con la realidad del Task Scheduler.
            print(f"Start with Spotify: elevación no completada ({e})")
        except SWSError as e:
            print(f"Start with Spotify: error al aplicar el cambio ({e})")
        except Exception as e:
            print(f"Start with Spotify: error inesperado ({e})")
        finally:
            # Pase lo que pase arriba, state.sws SIEMPRE refleja la tarea
            # programada real, nunca lo que "debería" haber pasado. Esto
            # evita que la UI quede desincronizada del sistema.
            try:
                state.sws = await loop.run_in_executor(None, sws_task_exists)
            except Exception:
                pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        pixmap = svgtp(SAMP_SVG, QSize(512, 512), color="#CC7722")
        self.setWindowIcon(QIcon(pixmap))
        self.setWindowTitle("SAMP")
        self.setFixedSize(400, 180)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        self.sys_slider  = VolumeSlider(SYS_SVG, "Sistema",  icon_color="#4a8cc7")
        self.song_slider = VolumeSlider(SP_SVG,  "Canción",  icon_color="#1DB954")
        self.ad_slider   = VolumeSlider(AD_SVG,  "Anuncios", icon_color="#AB000B")

        self.sys_dragging  = False
        self.song_dragging = False
        self.ad_dragging   = False

        self.sys_slider.slider.sliderPressed.connect(lambda: setattr(self, 'sys_dragging', True))
        self.sys_slider.slider.sliderReleased.connect(lambda: setattr(self, 'sys_dragging', False))
        self.song_slider.slider.sliderPressed.connect(lambda: setattr(self, 'song_dragging', True))
        self.song_slider.slider.sliderReleased.connect(lambda: setattr(self, 'song_dragging', False))
        self.ad_slider.slider.sliderPressed.connect(lambda: setattr(self, 'ad_dragging', True))
        self.ad_slider.slider.sliderReleased.connect(lambda: setattr(self, 'ad_dragging', False))

        layout.addWidget(self.sys_slider)
        layout.addWidget(self.song_slider)
        layout.addWidget(self.ad_slider)

        footer_widget = QWidget()
        footer_widget.setStyleSheet("background: transparent;")
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 4, 0, 0)
        footer_layout.setSpacing(6)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        key_ctrl      = QLabel("Ctrl")
        key_ctrl.setProperty("key", True)
        separator_lbl = QLabel("+")
        key_comma     = QLabel(",")
        key_comma.setProperty("key", True)
        self.arrow_label = QLabel()

        footer_layout.addWidget(key_ctrl)
        footer_layout.addWidget(separator_lbl)
        footer_layout.addWidget(key_comma)
        footer_layout.addWidget(self.arrow_label)
        layout.addWidget(footer_widget)

        self.sys_slider.slider.valueChanged.connect(self.on_sys_vol_changed)
        self.song_slider.slider.valueChanged.connect(self.on_song_vol_changed)
        self.ad_slider.slider.valueChanged.connect(self.on_ad_vol_changed)

        QTimer.singleShot(0, self.sync_from_system)

        self.endpoint_vol     = None
        self.sys_vol_callback = None
        self.init_system_volume_callback()

        self.update_texts()

    def update_texts(self) -> None:
        strings = LANG_STRINGS[current_language]
        self.sys_slider.set_label(strings["system"])
        self.song_slider.set_label(strings["song"])
        self.ad_slider.set_label(strings["ad"])
        self.arrow_label.setText("→ " + strings["settings"])
        self.setWindowTitle(f"SAMP  –  Spotify Ad Muter Panel  (v{version})")

    def closeEvent(self, event) -> None:
        if self.endpoint_vol and self.sys_vol_callback:
            try:
                self.endpoint_vol.UnregisterControlChangeNotify(self.sys_vol_callback)
            except Exception:
                pass
        super().closeEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Comma and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.open_settings()
        else:
            super().keyPressEvent(event)

    def open_settings(self) -> None:
        SettingsWindow(self).exec()

    def init_system_volume_callback(self) -> None:
        try:
            speakers = AudioUtilities.GetSpeakers()
            self.endpoint_vol = speakers.EndpointVolume
            self.sys_vol_callback = SystemVolumeCallback(self)
            self.endpoint_vol.RegisterControlChangeNotify(self.sys_vol_callback)
        except Exception as e:
            print(f"No se pudo registrar callback de sistema: {e}")

    @pyqtSlot()
    def sync_sys_slider_now(self) -> None:
        if self.sys_dragging:
            return
        vol = gv()
        if state.expected_sys_volume is None or abs(vol - state.expected_sys_volume) > 0.001:
            state.expected_sys_volume = vol
            self.sys_slider.slider.blockSignals(True)
            self.sys_slider.setValue(int(vol * 100))
            self.sys_slider.percent.setText(f"{int(vol * 100)}%")
            self.sys_slider.slider.blockSignals(False)

    def sync_from_system(self) -> None:
        current = gsv()
        if current is not None:
            percent = int(current * 100)
            self.song_slider.setValue(percent)
            self.ad_slider.setValue(percent)
            state.song_vol        = current
            state.ad_vol          = current
            state.expected_volume = current
        sys_vol = gv()
        state.expected_sys_volume = sys_vol
        self.sys_slider.setValue(int(sys_vol * 100))

    def on_sys_vol_changed(self) -> None:
        sv(self.sys_slider.value())

    def on_song_vol_changed(self) -> None:
        val = self.song_slider.value()
        state.song_vol = val
        if state.current_state == "song":
            ssv(val)

    def on_ad_vol_changed(self) -> None:
        val = self.ad_slider.value()
        state.ad_vol = val
        if state.current_state == "ad":
            ssv(val)

    def bring_to_front(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()


# --- Main ---
if __name__ == "__main__":
    # handle_elevated_cli() devuelve None si esta no es una invocación
    # relanzada por UAC (arranque normal de la app), o un código de salida
    # real (0 = éxito, != 0 = fallo) si sí lo es. Antes se ignoraba el
    # resultado y siempre se salía con 0, por lo que el proceso padre no
    # podía saber si el registro/eliminación de la tarea había funcionado.
    _elevated_exit_code = handle_elevated_cli()
    if _elevated_exit_code is not None:
        sys.exit(_elevated_exit_code)

    app = QApplication([])
    app.setWindowIcon(QIcon(svgtp(SAMP_SVG, QSize(512, 512), color="#CC7722")))

    font = QFont()
    font.setPointSizeF(11.0)
    app.setFont(font)

    socket = QLocalSocket()
    socket.connectToServer(SAMP_SERVER)
    if socket.waitForConnected(500):
        socket.write(b"activate")
        socket.flush()
        socket.disconnectFromServer()
        socket.close()
        sys.exit(0)

    server = QLocalServer()
    if not server.listen(SAMP_SERVER):
        sys.exit(1)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = MainWindow()
    apply_theme(current_theme)
    window.show()

    def on_new_connection():
        client_connection = server.nextPendingConnection()
        if client_connection:
            client_connection.disconnectFromServer()
            client_connection.close()
        window.bring_to_front()

    server.newConnection.connect(on_new_connection)

    loop.create_task(ssbd())

    with loop:
        loop.run_forever()
