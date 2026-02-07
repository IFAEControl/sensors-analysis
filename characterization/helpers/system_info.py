import platform
import getpass
from pathlib import Path

def get_system_info():
    return {
        "username": getpass.getuser(),
        "cwd": str(Path.cwd()),
        "os": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "architecture": platform.architecture()[0],
        "python_version": platform.python_version(),
        "hostname": platform.node(),
    }
