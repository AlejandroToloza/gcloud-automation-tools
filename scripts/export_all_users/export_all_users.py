import requests
from openpyxl import Workbook
import os
import time
from datetime import datetime
from getpass import getpass

# Lista de regiones con login y API correctos
REGIONES = {
    '1': ('mypurecloud.com', 'Estados Unidos (Este)', 'login.mypurecloud.com', 'api.mypurecloud.com'),
    '2': ('usw2.pure.cloud', 'Estados Unidos (Oeste)', 'login.usw2.pure.cloud', 'api.usw2.pure.cloud'),
    '3': ('cac1.pure.cloud', 'Américas (Canadá)', 'login.cac1.pure.cloud', 'api.cac1.pure.cloud'),
    '4': ('sae1.pure.cloud', 'América (Sao Paulo)', 'login.sae1.pure.cloud', 'api.sae1.pure.cloud'),
    '5': ('mypurecloud.ie', 'EMEA (Dublín)-Irlanda', 'login.mypurecloud.ie', 'api.mypurecloud.ie'),
    '6': ('mypurecloud.de', 'EMEA (Fráncfort)-Frankfurt', 'login.mypurecloud.de', 'api.mypurecloud.de'),
    '7': ('mypurecloud.jp', 'Asia Pacífico (Tokio)-Tokio', 'login.mypurecloud.jp', 'api.mypurecloud.jp'),
    '8': ('mypurecloud.com.au', 'Asia Pacífico (Sydney)5Sydney', 'login.mypurecloud.com.au', 'api.mypurecloud.com.au')
}

def seleccionar_region():
    print("Seleccione la región de Genesys Cloud donde se encuentra su organización:\n")
    for key, (_, descripcion, _, _) in REGIONES.items():
        print(f"  {key}. {descripcion}")

    while True:
        opcion = input("\nIngrese el número de la región (ej: 1): ").strip()
        if opcion in REGIONES:
            _, desc, login_domain, api_domain = REGIONES[opcion]
            print(f"\n✔ Región seleccionada: {desc}\n")
            return login_domain, api_domain
        else:
            print("[!] Opción inválida. Intente nuevamente.")

def get_token(client_id, client_secret, login_domain):
    auth_url = f'https://{login_domain}/oauth/token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(auth_url, data=payload)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"[!] Error al obtener token: {response.status_code} - {response.text}")
        return None

def get_users(token, state, api_domain):
    users_list = []
    page_size = 500
    page_number = 1
    base_url = f'https://{api_domain}/api/v2/users'

    while True:
        params = {
            'pageSize': page_size,
            'pageNumber': page_number,
            'state': state
        }
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(base_url, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            for user in data.get('entities', []):
                users_list.append({
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email'],
                    'title': user.get('title', ''),
                    'state': 'Activo' if state == 'active' else 'Inactivo',
                    'department': user.get('department', ''),
                    'division': user.get('division', {}).get('name', '')
                })
            if page_number >= data.get('pageCount', 1):
                break
            page_number += 1
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 5))
            print(f"[!] Límite alcanzado. Reintentando en {retry_after} segundos...")
            time.sleep(retry_after)
        else:
            print(f"[!] Error al consultar usuarios: {response.status_code} - {response.text}")
            break

    return users_list

def export_to_excel(users, output_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Usuarios Genesys"
    ws.append(['ID', 'Nombre', 'Email', 'Título', 'Estado', 'Departamento', 'División'])

    for user in users:
        ws.append([
            user['id'], user['name'], user['email'], user['title'],
            user['state'], user['department'], user['division']
        ])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    print(f"[✔] Archivo generado: {output_path}")

def main():
    print("==== Exportador de Usuarios de Genesys Cloud ====\n")

    login_domain, api_domain = seleccionar_region()
    client_id = input("Ingrese el CLIENT ID: ").strip()

    print("🔐 NOTA: Al escribir el CLIENT SECRET no verás nada en pantalla (por seguridad).")
    client_secret = getpass("Ingrese el CLIENT SECRET (oculto): ").strip()

    token = get_token(client_id, client_secret, login_domain)
    if not token:
        return

    print("[*] Obteniendo usuarios activos...")
    usuarios_activos = get_users(token, 'active', api_domain)
    print(f"[+] {len(usuarios_activos)} usuarios activos encontrados.")

    print("[*] Obteniendo usuarios inactivos...")
    usuarios_inactivos = get_users(token, 'inactive', api_domain)
    print(f"[+] {len(usuarios_inactivos)} usuarios inactivos encontrados.")

    usuarios_totales = usuarios_activos + usuarios_inactivos

    archivo_nombre = f"usuarios_genesys_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    ruta_salida = os.path.join(os.path.expanduser('~'), 'Desktop', 'PYTHON', 'EXPORTS', archivo_nombre)

    export_to_excel(usuarios_totales, ruta_salida)

if __name__ == "__main__":
    main()
