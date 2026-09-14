import importlib.util
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def import_module_from_path(name, relative_path):
    """Carga un módulo (script o el módulo común) directamente desde su ruta
    en el repo, igual a como lo ejecuta un usuario con `python scripts/.../archivo.py`."""
    path = os.path.join(REPO_ROOT, relative_path)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
