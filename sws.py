"""
sws: start_with_spotify
"""

import base64, ctypes, getpass, os, subprocess, sys, tempfile, textwrap
from __future__ import annotations
from ctypes import wintypes

_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
TASK_NAME = "SAMP_StartWithSpotify"

_ELEVATION_TIMEOUT_MS = 120_000

_WAIT_TIMEOUT = 0x00000102
_SEE_MASK_NOCLOSEPROCESS = 0x00000040
_SW_SHOWNORMAL = 1


# --- Errores propios -------------------------------------------------------
class SWSError(Exception):
    """Error genérico al gestionar la tarea de Start with Spotify."""


class SWSElevationCancelled(SWSError):
    """El usuario canceló el diálogo UAC (o ShellExecute no pudo elevar)."""


class SWSElevationTimeout(SWSError):
    """El proceso elevado no terminó dentro del tiempo esperado."""


class SWSElevationFailed(SWSError):
    """El proceso elevado terminó con un código de error."""


# --- Estructura para ShellExecuteExW (necesaria para poder esperar) -------
class _SHELLEXECUTEINFOW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("fMask", ctypes.c_ulong),
        ("hwnd", wintypes.HWND),
        ("lpVerb", wintypes.LPCWSTR),
        ("lpFile", wintypes.LPCWSTR),
        ("lpParameters", wintypes.LPCWSTR),
        ("lpDirectory", wintypes.LPCWSTR),
        ("nShow", ctypes.c_int),
        ("hInstApp", wintypes.HINSTANCE),
        ("lpIDList", ctypes.c_void_p),
        ("lpClass", wintypes.LPCWSTR),
        ("hKeyClass", wintypes.HKEY),
        ("dwHotKey", wintypes.DWORD),
        ("hIconOrMonitor", wintypes.HANDLE),
        ("hProcess", wintypes.HANDLE),
    ]


# --- Helpers de elevación UAC ----------------------------------------------
def _is_elevated() -> bool:
    """True si el proceso actual tiene privilegios de administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def _relaunch_elevated_and_wait(action: str, samp_path: str = "") -> int:
    """
    Relanza el propio ejecutable / script con ShellExecuteExW "runas" (UAC)
    y ESPERA a que termine, devolviendo su código de salida real.

    A diferencia de ShellExecuteW (usado anteriormente), ShellExecuteExW con
    SEE_MASK_NOCLOSEPROCESS nos entrega un handle al proceso elevado que
    podemos usar con WaitForSingleObject + GetExitCodeProcess. Sin esto no
    hay forma fiable de saber si el registro/eliminación de la tarea
    realmente tuvo éxito.

    Lanza SWSElevationCancelled si el usuario cancela el UAC,
    SWSElevationTimeout si el proceso no responde a tiempo.
    """
    if getattr(sys, "frozen", False):
        exe = sys.executable
        args = f"--sws-action {action}"
    else:
        exe = sys.executable  # python.exe
        script = os.path.abspath(__file__)
        args = f'"{script}" --sws-action {action}'

    if samp_path:
        args += f' --samp-path "{samp_path}"'

    sei = _SHELLEXECUTEINFOW()
    sei.cbSize = ctypes.sizeof(sei)
    sei.fMask = _SEE_MASK_NOCLOSEPROCESS
    sei.hwnd = None
    sei.lpVerb = "runas"
    sei.lpFile = exe
    sei.lpParameters = args
    sei.lpDirectory = None
    sei.nShow = _SW_SHOWNORMAL
    sei.hInstApp = None

    ok = ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(sei))
    if not ok:
        # El usuario canceló el UAC o el sistema rechazó la elevación.
        raise SWSElevationCancelled(
            "El usuario canceló el diálogo UAC o la elevación falló."
        )

    if not sei.hProcess:
        # No deberíamos llegar aquí con SEE_MASK_NOCLOSEPROCESS y ok=True,
        # pero por seguridad no bloqueamos indefinidamente.
        return 0

    try:
        result = ctypes.windll.kernel32.WaitForSingleObject(
            sei.hProcess, _ELEVATION_TIMEOUT_MS
        )
        if result == _WAIT_TIMEOUT:
            raise SWSElevationTimeout(
                "El proceso elevado no respondió a tiempo."
            )

        exit_code = wintypes.DWORD()
        ctypes.windll.kernel32.GetExitCodeProcess(
            sei.hProcess, ctypes.byref(exit_code)
        )
        return int(exit_code.value)
    finally:
        ctypes.windll.kernel32.CloseHandle(sei.hProcess)


# --- Script de vigilancia (PowerShell) --------------------------------------
def _watchdog_ps_script(samp_path: str) -> str:
    """
    Construye el script PowerShell que vigila Spotify durante toda la
    sesión de Windows y relanza SAMP cada vez que Spotify pasa de "cerrado"
    a "abierto" (flanco de subida), en lugar de una sola vez.

    - Sondea cada 1 s (barato en CPU).
    - Al detectar el flanco, espera 2 s extra para que Spotify registre su
      sesión de audio (si no, pycaw no la encontraría todavía) y entonces
      lanza SAMP sin bloquear (Start-Process, sin -Wait).
    - SAMP se encarga de no duplicarse: si ya hay una instancia abierta,
      el nuevo lanzamiento simplemente trae la ventana existente al frente
      y termina (ver QLocalServer/QLocalSocket en main.py).
    - -WindowStyle Hidden evita que aparezca una consola visible.
    """
    samp_escaped = samp_path.replace("'", "''")  # escapa comillas simples en PS
    return textwrap.dedent(f"""\
        $wasRunning = $false
        while ($true) {{
            $isRunning = [bool](Get-Process -Name Spotify -ErrorAction SilentlyContinue)
            if ($isRunning -and -not $wasRunning) {{
                Start-Sleep -Seconds 2
                Start-Process -FilePath '{samp_escaped}'
            }}
            $wasRunning = $isRunning
            Start-Sleep -Seconds 1
        }}
    """).strip()


def _encode_ps_command(ps_script: str) -> str:
    """Codifica un script PowerShell en UTF-16LE + Base64 para -EncodedCommand."""
    return base64.b64encode(ps_script.encode("utf-16-le")).decode("ascii")


# --- Operaciones sobre el Task Scheduler (schtasks.exe) ---------------------
def _create_task_xml(samp_path: str) -> str:
    """
    Genera el XML de definición de tarea en el formato que acepta
    `schtasks /Create /XML`.

    Trigger: inicio de sesión del usuario actual (ONLOGON).
    Acción:  powershell.exe con el watchdog codificado en Base64, que vive
             durante toda la sesión (ver _watchdog_ps_script).
    La tarea NO requiere privilegios elevados para ejecutarse; corre en el
    contexto del usuario normal (solo su REGISTRO/ELIMINACIÓN requiere UAC).
    """
    encoded = _encode_ps_command(_watchdog_ps_script(samp_path))
    username = getpass.getuser()

    return f"""\
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Lanza SAMP (Spotify Ad Muter Panel) cada vez que se abre Spotify en esta sesion.</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <UserId>{username}</UserId>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{username}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-NonInteractive -WindowStyle Hidden -EncodedCommand {encoded}</Arguments>
    </Exec>
  </Actions>
</Task>"""


def _run_schtasks_create(samp_path: str) -> None:
    """Escribe el XML en un archivo temporal y registra la tarea.

    Lanza SWSError si `schtasks` devuelve un código de error, incluyendo
    la salida de error del propio comando para facilitar el diagnóstico.
    """
    xml_content = _create_task_xml(samp_path)
    # schtasks /Create /XML requiere el archivo en UTF-16
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".xml", encoding="utf-16", delete=False
    ) as f:
        f.write(xml_content)
        tmp_path = f.name

    try:
        proc = subprocess.run(
            ["schtasks", "/Create", "/TN", TASK_NAME, "/XML", tmp_path, "/F"],
            capture_output=True,
            creationflags=_NO_WINDOW,
        )
        if proc.returncode != 0:
            stderr = proc.stderr.decode(errors="replace").strip()
            raise SWSError(f"schtasks /Create falló ({proc.returncode}): {stderr}")
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def _run_schtasks_delete() -> None:
    proc = subprocess.run(
        ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
        capture_output=True,
        creationflags=_NO_WINDOW,
    )
    if proc.returncode != 0:
        stderr = proc.stderr.decode(errors="replace").strip()
        raise SWSError(f"schtasks /Delete falló ({proc.returncode}): {stderr}")


# --- API pública -------------------------------------------------------------
def sws_task_exists() -> bool:
    """Devuelve True si la tarea SAMP_StartWithSpotify existe.

    Esta es la ÚNICA fuente de verdad sobre si "Start with Spotify" está
    activo; el llamador debe usarla para reconciliar el estado de la UI
    tras cualquier intento de registro/eliminación, en lugar de asumir
    que la operación solicitada tuvo éxito.
    """
    result = subprocess.run(
        ["schtasks", "/Query", "/TN", TASK_NAME],
        capture_output=True,
        creationflags=_NO_WINDOW,
    )
    return result.returncode == 0


def register_sws_task(samp_path: str) -> None:
    """Registra la tarea programada.

    Si el proceso actual no está elevado, relanza un proceso elevado que
    hace únicamente el registro y sale, ESPERANDO su resultado real.
    Lanza SWSElevationCancelled / SWSElevationTimeout / SWSElevationFailed
    / SWSError si algo falla; el llamador debe capturarlas y, en cualquier
    caso, volver a consultar `sws_task_exists()` para saber el estado real.
    """
    if not _is_elevated():
        exit_code = _relaunch_elevated_and_wait("register", samp_path)
        if exit_code != 0:
            raise SWSElevationFailed(
                f"El registro elevado de la tarea falló (código {exit_code})."
            )
        return
    _run_schtasks_create(samp_path)


def unregister_sws_task() -> None:
    """Elimina la tarea programada. Eleva si es necesario, esperando su
    resultado real (ver `register_sws_task`).

    Es seguro llamarla aunque la tarea no exista.
    """
    if not _is_elevated():
        exit_code = _relaunch_elevated_and_wait("unregister")
        if exit_code != 0:
            raise SWSElevationFailed(
                f"La eliminación elevada de la tarea falló (código {exit_code})."
            )
        return
    _run_schtasks_delete()


# --- Punto de entrada cuando se relanza elevado ------------------------------
def handle_elevated_cli() -> int | None:
    """
    Procesa los argumentos --sws-action si están presentes.

    Devuelve:
      - None si esta invocación NO es una relanzada para gestionar SWS
        (el llamador debe continuar con el arranque normal de la app).
      - Un int (código de salida real: 0 = éxito, != 0 = fallo) si esta
        invocación SÍ era para registrar/eliminar la tarea; el llamador
        debe hacer sys.exit(ese_codigo) inmediatamente, sin construir la
        QApplication.

    A diferencia de versiones anteriores, este código de salida se
    propaga de verdad hasta el proceso padre (ver _relaunch_elevated_and_wait),
    así que un fallo de `schtasks` ya no se pierde en silencio.
    """
    args = sys.argv[1:]
    if "--sws-action" not in args:
        return None

    idx = args.index("--sws-action")
    action = args[idx + 1] if idx + 1 < len(args) else ""

    try:
        if action == "register":
            path_idx = args.index("--samp-path") if "--samp-path" in args else -1
            samp_path = args[path_idx + 1] if path_idx >= 0 else sys.executable
            _run_schtasks_create(samp_path)
        elif action == "unregister":
            if sws_task_exists():
                _run_schtasks_delete()
        else:
            return 1
        return 0
    except Exception:
        return 1
