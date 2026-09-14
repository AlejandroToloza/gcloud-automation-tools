"""Utilidades compartidas por los scripts de automatización de Genesys Cloud:
selección de región, autenticación OAuth2 y llamadas paginadas a la API,
y exportación de resultados a Excel."""
import os
import sys
import time
from datetime import datetime
from getpass import getpass

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# En consolas con un codepage heredado (cp1252 y similares, típico en tareas
# programadas de Windows o consolas antiguas) los prints con emoji de estos
# scripts pueden lanzar UnicodeEncodeError y cortar la ejecución. Se fuerza
# UTF-8 en stdout/stderr, reemplazando lo que no se pueda mostrar.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except (AttributeError, ValueError):
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
    """Devuelve (login_domain, api_domain, descripcion) de la región a usar.

    Si la variable de entorno GENESYS_REGION está definida con un número de
    región válido (ver REGIONES), la usa directamente sin preguntar nada,
    para permitir ejecuciones no interactivas (tareas programadas, CLI con
    --region). Si no está definida o es inválida, muestra el menú interactivo."""
    region_env = os.environ.get('GENESYS_REGION', '').strip()
    if region_env:
        if region_env in REGIONES:
            _, descripcion, login_domain, api_domain = REGIONES[region_env]
            print(f"🌍 Región cargada desde GENESYS_REGION: {descripcion}\n")
            return login_domain, api_domain, descripcion
        print(f"[!] GENESYS_REGION={region_env!r} no es una región válida. Se pedirá por consola.\n")

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


def solicitar_api_post(token, api_domain, path, body):
    """Hace un POST autenticado (ej. endpoints de búsqueda) contra la API de
    Genesys Cloud, reintentando automáticamente en HTTP 429."""
    url = f'https://{api_domain}{path}' if path.startswith('/') else f'https://{api_domain}/{path}'
    headers = {'Authorization': f'Bearer {token}'}

    while True:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 5))
            print(f"[!] Límite de peticiones alcanzado. Reintentando en {retry_after} segundos...")
            time.sleep(retry_after)
            continue
        response.raise_for_status()
        return response.json()


def solicitar_api_patch(token, api_domain, path, body):
    """Hace un PATCH autenticado (escritura) contra la API de Genesys Cloud,
    reintentando automáticamente en HTTP 429."""
    url = f'https://{api_domain}{path}' if path.startswith('/') else f'https://{api_domain}/{path}'
    headers = {'Authorization': f'Bearer {token}'}

    while True:
        response = requests.patch(url, headers=headers, json=body)
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 5))
            print(f"[!] Límite de peticiones alcanzado. Reintentando en {retry_after} segundos...")
            time.sleep(retry_after)
            continue
        response.raise_for_status()
        return response.json()


def solicitar_api_put(token, api_domain, path, body):
    """Hace un PUT autenticado (reemplazo completo del recurso, o bulk-add/remove
    en los endpoints que lo usan así) contra la API de Genesys Cloud,
    reintentando automáticamente en HTTP 429."""
    url = f'https://{api_domain}{path}' if path.startswith('/') else f'https://{api_domain}/{path}'
    headers = {'Authorization': f'Bearer {token}'}

    while True:
        response = requests.put(url, headers=headers, json=body)
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 5))
            print(f"[!] Límite de peticiones alcanzado. Reintentando en {retry_after} segundos...")
            time.sleep(retry_after)
            continue
        response.raise_for_status()
        return response.json()


def solicitar_api_delete(token, api_domain, path, params=None):
    """Hace un DELETE autenticado contra la API de Genesys Cloud, reintentando
    automáticamente en HTTP 429."""
    url = f'https://{api_domain}{path}' if path.startswith('/') else f'https://{api_domain}/{path}'
    headers = {'Authorization': f'Bearer {token}'}

    while True:
        response = requests.delete(url, headers=headers, params=params)
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 5))
            print(f"[!] Límite de peticiones alcanzado. Reintentando en {retry_after} segundos...")
            time.sleep(retry_after)
            continue
        response.raise_for_status()
        return None if not response.content else response.json()


def buscar_usuario_por_email(token, api_domain, email):
    """Busca un usuario por email exacto vía POST /api/v2/users/search.
    Devuelve el dict del usuario encontrado, o None si no hay coincidencia."""
    body = {
        'query': [{'type': 'EXACT', 'fields': ['email'], 'value': email}],
        'pageSize': 1,
    }
    data = solicitar_api_post(token, api_domain, '/api/v2/users/search', body)
    resultados = data.get('results', [])
    return resultados[0] if resultados else None


def obtener_divisiones(token, api_domain):
    """Obtiene todas las divisiones de autorización de la organización."""
    divisiones = []
    page_number = 1

    while True:
        data = solicitar_api(token, api_domain, '/api/v2/authorization/divisions', params={
            'pageSize': 100,
            'pageNumber': page_number,
        })
        entidades = data.get('entities', [])
        if not entidades:
            break
        divisiones.extend(entidades)

        if page_number >= data.get('pageCount', 1):
            break
        page_number += 1

    return divisiones


def buscar_division_por_nombre(token, api_domain, nombre):
    """Busca una división por nombre exacto (sin distinguir mayúsculas/minúsculas).
    Devuelve el dict de la división, o None si no hay coincidencia."""
    nombre_normalizado = nombre.strip().lower()
    for division in obtener_divisiones(token, api_domain):
        if division.get('name', '').strip().lower() == nombre_normalizado:
            return division
    return None


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


def buscar_cola_por_nombre(token, api_domain, nombre):
    """Busca una cola por nombre exacto (sin distinguir mayúsculas/minúsculas).
    Devuelve el dict de la cola, o None si no hay coincidencia."""
    nombre_normalizado = nombre.strip().lower()
    for cola in obtener_colas(token, api_domain):
        if cola.get('name', '').strip().lower() == nombre_normalizado:
            return cola
    return None


def buscar_script_por_nombre(token, api_domain, nombre):
    """Busca un script por nombre exacto vía GET /api/v2/scripts?name=...
    Devuelve el dict del script, o None si no hay coincidencia."""
    data = solicitar_api(token, api_domain, '/api/v2/scripts', params={'name': nombre, 'pageSize': 25})
    nombre_normalizado = nombre.strip().lower()
    for script in data.get('entities', []):
        if script.get('name', '').strip().lower() == nombre_normalizado:
            return script
    return None


def buscar_wrapupcode_por_nombre(token, api_domain, nombre):
    """Busca un wrap-up code por nombre exacto vía GET /api/v2/routing/wrapupcodes?name=...
    Devuelve el dict del wrap-up code, o None si no hay coincidencia."""
    data = solicitar_api(token, api_domain, '/api/v2/routing/wrapupcodes', params={'name': nombre, 'pageSize': 25})
    nombre_normalizado = nombre.strip().lower()
    for code in data.get('entities', []):
        if code.get('name', '').strip().lower() == nombre_normalizado:
            return code
    return None


def buscar_grupo_por_nombre(token, api_domain, nombre):
    """Busca un grupo (Group) por nombre exacto vía POST /api/v2/groups/search.
    Devuelve el dict del grupo (incluye 'version', necesario para modificar
    su membership), o None si no hay coincidencia."""
    body = {
        'query': [{'type': 'EXACT', 'fields': ['name'], 'value': nombre}],
        'pageSize': 1,
    }
    data = solicitar_api_post(token, api_domain, '/api/v2/groups/search', body)
    resultados = data.get('results', [])
    return resultados[0] if resultados else None


def buscar_skill_por_nombre(token, api_domain, nombre):
    """Busca una skill de enrutamiento por nombre exacto vía GET /api/v2/routing/skills?name=...
    (el filtro del servidor es por prefijo, así que se valida el nombre exacto
    del lado del cliente). Devuelve el dict de la skill, o None si no hay coincidencia."""
    data = solicitar_api(token, api_domain, '/api/v2/routing/skills', params={'name': nombre, 'pageSize': 25})
    nombre_normalizado = nombre.strip().lower()
    for skill in data.get('entities', []):
        if skill.get('name', '').strip().lower() == nombre_normalizado:
            return skill
    return None


def obtener_roles(token, api_domain):
    """Obtiene todos los roles de autorización de la organización."""
    roles = []
    page_number = 1

    while True:
        try:
            data = solicitar_api(token, api_domain, '/api/v2/authorization/roles', params={
                'pageSize': 100,
                'pageNumber': page_number,
            })
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al obtener roles: {e}")
            break

        entidades = data.get('entities', [])
        if not entidades:
            break
        roles.extend(entidades)

        if page_number >= data.get('pageCount', 1):
            break
        page_number += 1

    return roles


def buscar_rol_por_nombre(token, api_domain, nombre):
    """Busca un rol de autorización por nombre exacto (sin distinguir
    mayúsculas/minúsculas). Devuelve el dict del rol, o None si no hay coincidencia."""
    nombre_normalizado = nombre.strip().lower()
    for rol in obtener_roles(token, api_domain):
        if rol.get('name', '').strip().lower() == nombre_normalizado:
            return rol
    return None


def obtener_usuarios_de_rol(token, api_domain, role_id):
    """Obtiene los IDs de los usuarios asignados directamente a un rol."""
    usuario_ids = []
    page_number = 1

    while True:
        try:
            data = solicitar_api(token, api_domain, f'/api/v2/authorization/roles/{role_id}/users', params={
                'pageSize': 100,
                'pageNumber': page_number,
            })
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al obtener usuarios del rol {role_id}: {e}")
            break

        entidades = data.get('entities', [])
        if not entidades:
            break
        usuario_ids.extend(u.get('id') for u in entidades if u.get('id'))

        if page_number >= data.get('pageCount', 1):
            break
        page_number += 1

    return usuario_ids


def obtener_contactos(token, api_domain):
    """Obtiene todos los contactos externos de la organización, usando paginación."""
    page_size = 100
    page_number = 1
    contactos_total = []

    while True:
        try:
            data = solicitar_api(token, api_domain, '/api/v2/externalcontacts/contacts', params={
                'pageSize': page_size,
                'pageNumber': page_number,
            })
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al obtener contactos:\n{e}")
            break

        contactos = data.get('entities', [])
        if not contactos:
            break
        contactos_total.extend(contactos)
        print(f"✅ Página {page_number} procesada: {len(contactos)} contactos")

        if page_number * page_size >= data.get('total', 0):
            break
        page_number += 1

    return contactos_total


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
