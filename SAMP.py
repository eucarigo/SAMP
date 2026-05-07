"""samp: spotify_ad_muter_panel"""

# --- Imports ---
import asyncio, psutil
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
    QHBoxLayout, QSlider, QLabel
)
from PyQt6.QtCore import (
    Qt, QTimer, QSize, QRectF,
    QSizeF, QPointF, pyqtSlot
)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QIcon


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

def svgtp(svg_bytes: bytes, size: QSize = QSize(24, 24), color: str = None) -> QPixmap:
    """svgtp: svg_to_pixmap"""
    if color:
        svg_bytes = svg_bytes.replace(b"currentColor", color.encode())
    dpr = QApplication.primaryScreen().devicePixelRatio() if QApplication.instance() else 1.0
    renderer = QSvgRenderer(svg_bytes)
    physical_size = size * dpr
    pixmap = QPixmap(physical_size)
    pixmap.fill(Qt.GlobalColor.transparent)
    pixmap.setDevicePixelRatio(dpr)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter, QRectF(QPointF(0, 0), QSizeF(size)))
    painter.end()
    return pixmap


# --- Volumen del sistema ---
def gv():
    """gv: get_volume (sys vol)"""
    try:
        speakers = AudioUtilities.GetSpeakers()
        # Usamos la propiedad EndpointVolume (no un método)
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


# --- Volumen de Spotify ---
def gsv():
    """gsv: get_spotify_volume"""
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        try:
            if session.Process and session.Process.name() == "Spotify.exe":
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                return volume.GetMasterVolume()
        except (NoSuchProcess, ProcessLookupError, AttributeError):
            continue
    return None

def ssv(value: float):
    """ssv: set_spotify_volume"""
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        try:
            if session.Process and session.Process.name() == "Spotify.exe":
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                volume.SetMasterVolume(value, None)
                state.expected_volume = value
                break
        except (NoSuchProcess, ProcessLookupError, AttributeError):
            continue


# --- StateManager, SSBD, MSV ---
class StateManager:
    song_vol = 1.0
    ad_vol = 1.0
    current_state = None
    expected_volume = None   # Spotify
    expected_sys_volume = None  # sistema

state = StateManager()

async def ssbd():
    """ssbd: spotify_skip_button_detection"""
    manager = await GSMTCM.request_async()
    last_state = None
    while True:
        sys_vol = gsv()
        if sys_vol is None:
            await asyncio.sleep(0.5)
            continue
        if state.expected_volume is None:
            state.expected_volume = sys_vol
        external_change = abs(sys_vol - state.expected_volume) > 0.001

        session = manager.get_current_session()
        current = None
        if session and "Spotify" in (session.source_app_user_model_id or ""):
            playback = session.get_playback_info()
            if playback and playback.playback_status == 4:
                controls = playback.controls
                is_next_enabled = controls.is_next_enabled if controls else False
                current = "song" if is_next_enabled else "ad"

        if current is None:
            await asyncio.sleep(0.5)
            continue

        state.current_state = current
        state_changed = (current != last_state)

        if external_change and not state_changed:
            if current == "song":
                if not window.song_dragging:
                    window.song_slider.slider.blockSignals(True)
                    window.song_slider.setValue(int(sys_vol * 100))
                    window.song_slider.percent.setText(f"{int(sys_vol * 100)}%")
                    window.song_slider.slider.blockSignals(False)
            else:
                if not window.ad_dragging:
                    window.ad_slider.slider.blockSignals(True)
                    window.ad_slider.setValue(int(sys_vol * 100))
                    window.ad_slider.percent.setText(f"{int(sys_vol * 100)}%")
                    window.ad_slider.slider.blockSignals(False)
            state.expected_volume = sys_vol
        elif state_changed:
            if external_change:
                if current == "song":
                    if not window.song_dragging:
                        window.song_slider.slider.blockSignals(True)
                        window.song_slider.setValue(int(sys_vol * 100))
                        window.song_slider.percent.setText(f"{int(sys_vol * 100)}%")
                        window.song_slider.slider.blockSignals(False)
                else:
                    if not window.ad_dragging:
                        window.ad_slider.slider.blockSignals(True)
                        window.ad_slider.setValue(int(sys_vol * 100))
                        window.ad_slider.percent.setText(f"{int(sys_vol * 100)}%")
                        window.ad_slider.slider.blockSignals(False)
                state.expected_volume = sys_vol
            else:
                desired = state.song_vol if current == "song" else state.ad_vol
                if abs(desired - sys_vol) > 0.001:
                    ssv(desired)
                    if current == "song":
                        window.song_slider.setValue(int(desired * 100))
                    else:
                        window.ad_slider.setValue(int(desired * 100))
            last_state = current

        await asyncio.sleep(0.5)

async def msv():
    """msv: monitor_sys_volume"""
    sys_vol = gv()
    state.expected_sys_volume = sys_vol
    window.sys_slider.setValue(int(sys_vol * 100))
    # El callback se encarga del resto, esta tarea puede dormir para siempre
    while True:
        await asyncio.sleep(10)


# --- Callback ---
class SystemVolumeCallback(COMObject):
    _com_interfaces_ = [IAudioEndpointVolumeCallback]
    
    def __init__(self, window):
        super().__init__()
        self.window = window

    def OnNotify(self, pNotify):
        from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
        QMetaObject.invokeMethod(
            self.window,
            "sync_sys_slider_now",
            Qt.ConnectionType.QueuedConnection
        )


# --- GUI ---
class VolumeSlider(QWidget):
    def __init__(self, icon_svg: bytes, label_text: str, initial=100, icon_color: str = None):
        super().__init__()
        layout = QHBoxLayout()
        layout.setSpacing(6)

        # Icono
        self.icon_label = QLabel()
        pixmap = svgtp(icon_svg, QSize(28, 28), icon_color)
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setFixedSize(28, 28)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("margin-top: -3px; margin-bottom: 2px;")

        # Texto principal
        self.label = QLabel(label_text)
        self.label.setFixedWidth(70)
        self.label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(initial)
        self.slider.setStyleSheet("margin-top: 3px;")

        # Porcentaje
        self.percent = QLabel(f"{initial}%")
        self.percent.setFixedWidth(40)
        self.percent.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.percent)

        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.setLayout(layout)

        self.slider.valueChanged.connect(self._update_percent)

    def _update_percent(self, val):
        self.percent.setText(f"{val}%")

    def value(self):
        return self.slider.value() / 100.0

    def setValue(self, percent):
        self.slider.setValue(percent)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        pixmap = svgtp(SAMP_SVG, QSize(512, 512), color="#CC7722")
        self.setWindowIcon(QIcon(pixmap))
        self.setWindowTitle("SAMP")
        self.setFixedSize(360, 160)
        self.setStyleSheet("""
            QMainWindow {
                background: #0D1B2A;
                color: #E0E1DD;
            }
            QWidget {
                background: #1B263B;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #415A77;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #778DA9;
                border: 2px solid #E0E1DD;
                width: 10px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #778DA9;
                border-radius: 3px;
            }
            QLabel {
                font-family: 'Segoe UI Variable', 'Segoe UI';
                font-size: 11pt;
                color: #E0E1DD;
            }
        """)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(12)
        
        self.sys_slider = VolumeSlider(SYS_SVG, "Sistema", icon_color="#4a8cc7")
        self.song_slider = VolumeSlider(SP_SVG, "Canción", icon_color="#1DB954")
        self.ad_slider = VolumeSlider(AD_SVG, "Anuncios", icon_color="#AB000B")
        
        # Banderas de arrastre
        self.sys_dragging = False
        self.song_dragging = False
        self.ad_dragging = False

        # Conectar eventos de presión/liberación
        self.sys_slider.slider.sliderPressed.connect(lambda: setattr(self, 'sys_dragging', True))
        self.sys_slider.slider.sliderReleased.connect(lambda: setattr(self, 'sys_dragging', False))
        self.song_slider.slider.sliderPressed.connect(lambda: setattr(self, 'song_dragging', True))
        self.song_slider.slider.sliderReleased.connect(lambda: setattr(self, 'song_dragging', False))
        self.ad_slider.slider.sliderPressed.connect(lambda: setattr(self, 'ad_dragging', True))
        self.ad_slider.slider.sliderReleased.connect(lambda: setattr(self, 'ad_dragging', False))

        layout.addWidget(self.sys_slider)
        layout.addWidget(self.song_slider)
        layout.addWidget(self.ad_slider)
        
        self.sys_slider.slider.valueChanged.connect(self.on_sys_vol_changed)
        self.song_slider.slider.valueChanged.connect(self.on_song_vol_changed)
        self.ad_slider.slider.valueChanged.connect(self.on_ad_vol_changed)
        
        QTimer.singleShot(0, self.sync_from_system)

        self.endpoint_vol = None
        self.sys_vol_callback = None
        self.init_system_volume_callback()

    def closeEvent(self, event):
        # Limpiar callback al cerrar
        if self.endpoint_vol and self.sys_vol_callback:
            try:
                self.endpoint_vol.UnregisterControlChangeNotify(self.sys_vol_callback)
            except:
                pass
        super().closeEvent(event)

    def init_system_volume_callback(self):
        try:
            speakers = AudioUtilities.GetSpeakers()
            self.endpoint_vol = speakers.EndpointVolume
            self.sys_vol_callback = SystemVolumeCallback(self)
            self.endpoint_vol.RegisterControlChangeNotify(self.sys_vol_callback)
        except Exception as e:
            print(f"No se pudo registrar callback de sistema: {e}")

    @pyqtSlot()
    def sync_sys_slider_now(self):
        if self.sys_dragging:
            return
        vol = gv()
        if state.expected_sys_volume is None or abs(vol - state.expected_sys_volume) > 0.001:
            state.expected_sys_volume = vol
            # Bloquear señales para no disparar on_sys_vol_changed
            self.sys_slider.slider.blockSignals(True)
            self.sys_slider.setValue(int(vol * 100))
            self.sys_slider.percent.setText(f"{int(vol * 100)}%")
            self.sys_slider.slider.blockSignals(False)

    def sync_from_system(self):
        current = gsv()
        if current is not None:
            percent = int(current * 100)
            self.song_slider.setValue(percent)
            self.ad_slider.setValue(percent)
            state.song_vol = current
            state.ad_vol = current
            state.expected_volume = current
        else:
            pass
        
        sys_vol = gv()
        state.expected_sys_volume = sys_vol
        self.sys_slider.setValue(int(sys_vol * 100))
    
    def on_sys_vol_changed(self):
        val = self.sys_slider.value()   # Ya devuelve 0..1
        sv(val)
    
    def on_song_vol_changed(self):
        val = self.song_slider.value()  # 0..1
        state.song_vol = val
        if state.current_state == "song":
            ssv(val)
    
    def on_ad_vol_changed(self):
        val = self.ad_slider.value()    # 0..1
        state.ad_vol = val
        if state.current_state == "ad":
            ssv(val)


# --- Main ---
if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon(svgtp(SAMP_SVG, QSize(512, 512), color="#CC7722")))

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = MainWindow()
    window.setWindowIcon(QIcon(svgtp(SAMP_SVG, QSize(512, 512), color="#CC7722")))
    window.show()

    loop.create_task(ssbd())
    loop.create_task(msv())
    
    with loop:
        loop.run_forever()
