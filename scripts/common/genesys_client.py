"""Utilidades compartidas por los scripts de automatización de Genesys Cloud:
selección de región, autenticación OAuth2 y llamadas paginadas a la API,
y exportación de resultados a Excel."""
import os
import time
from datetime import datetime
from getpass import getpass

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

REGIONES = {
    '1': ('mypurecloud.com', 'Estados Unidos (Este)', 'login.mypurecloud.com', 'api.mypurecloud.com'),
    '2': ('usw2.pure.cloud', 'Estados Unidos (Oeste)', 'login.usw2.pure.cloud', 'api.usw2.pure.cloud'),
    '3': ('cac1.pure.cloud', 'Américas (Canadá)', 'login.cac1.pure.cloud', 'api.cac1.pure.cloud'),
    '4': ('sae1.pure.cloud', 'América (Sao Paulo)', 'login.sae1.pure.cloud', 'api.sae1.pure.cloud'),
    '5': ('mypurecloud.ie', 'EMEA (Dublín)-Irlanda', 'login.mypurecloud.ie', 'api.mypurecloud.ie'),
    '6': ('mypurecloud.de', 'EMEA (Fráncfort)-Frankfurt', 'login.mypurecloud.de', 'api.mypurecloud.de'),
    '7': ('mypurecloud.jp', 'Asia Pacífico (Tokio)-Tokio', 'login.mypurecloud.jp', 'api.mypurecloud.jp'),
    '8': ('mypurecloud.com.au', 'Asia Pacífico (Sydney)', 'login.mypurecloud.com.au', 'api.mypurecloud.com.au'),
}


def seleccionar_region():
    """Muestra el menú de regiones y devuelve (login_domain, api_domain, descripcion)."""
    print("🌍 Selecciona la región de tu organización:\n")
    for key, (_, descripcion, _, _) in REGIONES.items():
        print(f"  {key}. {descripcion}")

    while True:
        opcion = input("\nIngrese el número de la región: ").strip()
        if opcion in REGIONES:
            _, descripcion, login_domain, api_domain = REGIONES[opcion]
            print(f"\n✔ Región seleccionada: {descripcion}\n")
            return login_domain, api_domain, descripcion
        print("[!] Opción inválida. Intente nuevamente.")


def solicitar_credenciales():
    """Obtiene Client ID y Client Secret desde las variables de entorno
    GENESYS_CLIENT_ID / GENESYS_CLIENT_SECRET (o un archivo .env), y si no
    están definidas, las pide por consola (el secret no se muestra en pantalla)."""
    client_id = os.environ.get('GENESYS_CLIENT_ID', '').strip()
    client_secret = os.environ.get('GENESYS_CLIENT_SECRET', '').strip()
    if client_id and client_secret:
        print("🔐 Credenciales cargadas desde variables de entorno (GENESYS_CLIENT_ID / GENESYS_CLIENT_SECRET).")
        return client_id, client_secret

    client_id = input("Ingrese el CLIENT ID: ").strip()
    print("🔐 NOTA: Al escribir el CLIENT SECRET no verás nada en pantalla (por seguridad).")
    client_secret = getpass("Ingrese el CLIENT SECRET (oculto): ").strip()
    return client_id, client_secret


def obtener_token(client_id, client_secret, login_domain):
    """Solicita un token OAuth2 (client_credentials). Devuelve None si falla."""
    url = f'https://{login_domain}/oauth/token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener el token: {e}")
        return None


def solicitar_api(token, api_domain, path, params=None):
    """Hace un GET autenticado contra la API de Genesys Cloud, reintentando
    automáticamente si se alcanza el límite de peticiones (HTTP 429)."""
    url = f'https://{api_domain}{path}' if path.startswith('/') else f'https://{api_domain}/{path}'
    headers = {'Authorization': f'Bearer {token}'}

    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 5))
            print(f"[!] Límite de peticiones alcanzado. Reintentando en {retry_after} segundos...")
            time.sleep(retry_after)
            continue
        response.raise_for_status()
        return response.json()


def obtener_colas(token, api_domain):
    """Obtiene todas las colas de la organización, siguiendo la paginación por nextUri."""
    colas = []
    path = '/api/v2/routing/queues?pageSize=100'

    while path:
        try:
            data = solicitar_api(token, api_domain, path)
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al obtener colas: {e}")
            break
        colas.extend(data.get('entities', []))
        path = data.get('nextUri')

    return colas


def guardar_excel(dataframe, prefijo_archivo, region_nombre):
    """Guarda un DataFrame en Excel dentro de Escritorio/PYTHON/EXPORTS/ y devuelve la ruta generada."""
    carpeta_export = os.path.join(os.path.expanduser("~"), "Desktop", "PYTHON", "EXPORTS")
    os.makedirs(carpeta_export, exist_ok=True)

    region_limpia = region_nombre.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"{prefijo_archivo}_{region_limpia}_{timestamp}.xlsx"
    ruta = os.path.join(carpeta_export, nombre_archivo)

    dataframe.to_excel(ruta, index=False)
    print(f"\n✅ Archivo Excel generado correctamente en:\n{ruta}")
    return ruta
