import requests
import pandas as pd
import os
import sys
from datetime import datetime
from getpass import getpass

# =================== REGIONES DISPONIBLES ===================
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
    """Muestra un menú para seleccionar la región"""
    print("🌍 Selecciona la región de tu organización:\n")
    for k, v in REGIONES.items():
        print(f"{k}. {v[1]}  →  {v[0]}")
    opcion = input("\n🔸 Ingresa el número de la región: ").strip()

    if opcion not in REGIONES:
        print("❌ Opción inválida. Terminando ejecución.")
        sys.exit(1)

    return REGIONES[opcion][2], REGIONES[opcion][3], REGIONES[opcion][1]

def obtener_token(client_id, client_secret, dominio_login):
    """Solicita un token de autenticación OAuth2 Client Credentials"""
    url = f'https://{dominio_login}/oauth/token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"❌ Error al obtener token: {e}")
        return None

def obtener_colas(token, dominio_api):
    """Obtiene todas las colas usando paginación"""
    headers = {'Authorization': f'Bearer {token}'}
    endpoint = f'https://{dominio_api}/api/v2/routing/queues?pageSize=100'
    todas_las_colas = []

    while endpoint:
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            data = response.json()
            todas_las_colas.extend(data.get('entities', []))

            next_uri = data.get('nextUri')
            endpoint = f"https://{dominio_api}{next_uri}" if next_uri else None
        except Exception as e:
            print(f"❌ Error al obtener colas: {e}")
            break

    return todas_las_colas

def obtener_nombre_script(token, dominio_api, script_id):
    """Obtiene el nombre del script a partir del ID"""
    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://{dominio_api}/api/v2/scripts/{script_id}'

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            return 'Script no encontrado'
        response.raise_for_status()
        return response.json().get('name', 'Nombre no disponible')
    except Exception as e:
        print(f"⚠️ Error al obtener nombre de script {script_id}: {e}")
        return 'Error'

def obtener_scripts_de_cola(token, dominio_api, queue_id):
    """Consulta los scripts asignados a una cola específica"""
    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://{dominio_api}/api/v2/routing/queues/{queue_id}'

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        default_scripts = data.get('defaultScripts', {})
        scripts_info = []

        for tipo_script, script_info in default_scripts.items():
            script_id = script_info.get('id')
            script_nombre = obtener_nombre_script(token, dominio_api, script_id) if script_id else 'No asignado'
            scripts_info.append({
                'Tipo de Script': tipo_script,
                'ID de Script': script_id or 'No asignado',
                'Nombre del Script': script_nombre
            })

        return scripts_info

    except Exception as e:
        print(f"❌ Error al obtener scripts de cola {queue_id}: {e}")
        return [{
            'Tipo de Script': 'Error',
            'ID de Script': 'Error',
            'Nombre del Script': 'Error'
        }]

def guardar_excel(dataframe, nombre_region):
    """Guarda los resultados en un archivo Excel en Escritorio/PYTHON/EXPORTS/"""
    try:
        carpeta_export = os.path.join(os.path.expanduser("~"), "Desktop", "PYTHON", "EXPORTS")
        os.makedirs(carpeta_export, exist_ok=True)

        nombre_limpio = nombre_region.lower().replace(" ", "_").replace("(", "").replace(")", "")
        nombre_archivo = f"queues_and_scripts_{nombre_limpio}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        ruta = os.path.join(carpeta_export, nombre_archivo)

        dataframe.to_excel(ruta, index=False)
        print(f"\n✅ Archivo Excel generado correctamente en:\n{ruta}")
    except Exception as e:
        print(f"❌ Error al guardar el archivo Excel: {e}")

def main():
    print("==== Exportador de Usuarios de Genesys Cloud ====\n")

    login_domain, api_domain, region_name = seleccionar_region()
    client_id = input("Ingrese el CLIENT ID: ").strip()

    print("🔐 NOTA: Al escribir el CLIENT SECRET no verás nada en pantalla (por seguridad).")
    client_secret = getpass("Ingrese el CLIENT SECRET (oculto): ").strip()

    print("\n🔄 Obteniendo token...")
    token = obtener_token(client_id, client_secret, login_domain)
    if not token:
        print("No se pudo obtener el token. Saliendo.")
        return

    print("\n📥 Obteniendo listado de colas...")
    colas = obtener_colas(token, api_domain)

    print("\n🔗 Consultando scripts asignados a cada cola...")
    datos = []
    for cola in colas:
        queue_id = cola.get('id')
        queue_name = cola.get('name')
        if not queue_id:
            continue
        scripts = obtener_scripts_de_cola(token, api_domain, queue_id)
        for script in scripts:
            datos.append({
                'ID de Cola': queue_id,
                'Nombre de Cola': queue_name,
                'Tipo de Script': script['Tipo de Script'],
                'ID de Script': script['ID de Script'],
                'Nombre del Script': script['Nombre del Script']
            })

    df = pd.DataFrame(datos)
    guardar_excel(df, region_name)

if __name__ == "__main__":
    main()
5