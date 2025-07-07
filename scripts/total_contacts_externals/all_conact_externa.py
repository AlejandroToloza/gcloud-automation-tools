import requests
import pandas as pd
import sys
import os
from datetime import datetime
from getpass import getpass

# === REGIONES DISPONIBLES ===
# Formato: ID : (Dominio base, Descripción, Login domain, API domain)
REGIONES = {
    '1': ('mypurecloud.com', 'Estados Unidos (Este)', 'login.mypurecloud.com', 'api.mypurecloud.com'),
    '2': ('usw2.pure.cloud', 'Estados Unidos (Oeste)', 'login.usw2.pure.cloud', 'api.usw2.pure.cloud'),
    '3': ('cac1.pure.cloud', 'Américas (Canadá)', 'login.cac1.pure.cloud', 'api.cac1.pure.cloud'),
    '4': ('sae1.pure.cloud', 'América (Sao Paulo)', 'login.sae1.pure.cloud', 'api.sae1.pure.cloud'),
    '5': ('mypurecloud.ie', 'EMEA (Dublín)-Irlanda', 'login.mypurecloud.ie', 'api.mypurecloud.ie'),
    '6': ('mypurecloud.de', 'EMEA (Fráncfort)-Frankfurt', 'login.mypurecloud.de', 'api.mypurecloud.de'),
    '7': ('mypurecloud.jp', 'Asia Pacífico (Tokio)-Tokio', 'login.mypurecloud.jp', 'api.mypurecloud.jp'),
    '8': ('mypurecloud.com.au', 'Asia Pacífico (Sydney)', 'login.mypurecloud.com.au', 'api.mypurecloud.com.au')
}

def seleccionar_region():
    """Muestra opciones y permite al usuario seleccionar región"""
    print("🌍 Seleccione la región de Genesys Cloud:\n")
    for key, (_, descripcion, _, _) in REGIONES.items():
        print(f"  {key}. {descripcion}")

    while True:
        opcion = input("\nIngrese el número de la región: ").strip()
        if opcion in REGIONES:
            _, desc, login_domain, api_domain = REGIONES[opcion]
            print(f"\n✔ Región seleccionada: {desc}")
            return login_domain, api_domain, desc
        else:
            print("[!] Opción inválida. Intente nuevamente.")

def obtener_token(client_id, client_secret, login_domain):
    """Solicita un token de acceso válido usando client_credentials"""
    url = f"https://{login_domain}/oauth/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener el token:\n{e}")
        return None

def obtener_contactos(token, api_domain):
    """Obtiene todos los contactos externos disponibles usando paginación"""
    headers = {'Authorization': f'Bearer {token}'}
    url = f"https://{api_domain}/api/v2/externalcontacts/contacts"

    page_size = 100
    page_number = 1
    contactos_total = []

    while True:
        params = {'pageSize': page_size, 'pageNumber': page_number}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
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

def guardar_en_excel(contactos, region_nombre):
    """Guarda los contactos obtenidos en un archivo Excel en una ruta fija"""
    try:
        df = pd.json_normalize(contactos)

        # Formato de nombre limpio para archivo
        region_limpia = region_nombre.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo = f"contactos_externos_{region_limpia}_{timestamp}.xlsx"

        # Ruta fija: Escritorio/PYTHON/EXPORTS/
        ruta_salida = os.path.join(os.path.expanduser("~"), "Desktop", "PYTHON", "EXPORTS")
        os.makedirs(ruta_salida, exist_ok=True)

        ruta_final = os.path.join(ruta_salida, archivo)
        df.to_excel(ruta_final, index=False)

        print(f"\n📁 Archivo guardado exitosamente en:\n{ruta_final}")
    except Exception as e:
        print(f"❌ Error al guardar Excel:\n{e}")

def main():
    print("📤 Exportador de Contactos Externos - Genesys Cloud\n")

    # 1. Seleccionar región
    login_domain, api_domain, region_nombre = seleccionar_region()

    # 2. Ingreso seguro de credenciales
    print("\n🔐 Ingrese las credenciales:")
    client_id = input("Client ID: ").strip()
    client_secret = getpass("Client Secret (oculto): ").strip()

    # 3. Obtener token
    print("\n🔄 Solicitando token de autenticación...")
    token = obtener_token(client_id, client_secret, login_domain)

    if not token:
        print("🚫 No se pudo autenticar. Terminando.")
        sys.exit(1)

    # 4. Obtener contactos
    print("\n📥 Obteniendo contactos externos...")
    contactos = obtener_contactos(token, api_domain)

    # 5. Exportar
    if contactos:
        guardar_en_excel(contactos, region_nombre)
    else:
        print("⚠️ No se encontraron contactos externos.")

if __name__ == "__main__":
    main()
