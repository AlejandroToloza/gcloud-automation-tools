import os
import sys

import pandas as pd
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from genesys_client import seleccionar_region, solicitar_credenciales, obtener_token, solicitar_api, guardar_excel


def obtener_usuarios(token, api_domain, estado):
    """Obtiene todos los usuarios de un estado ('active' o 'inactive') usando paginación."""
    usuarios = []
    page_number = 1

    while True:
        try:
            data = solicitar_api(token, api_domain, '/api/v2/users', params={
                'pageSize': 500,
                'pageNumber': page_number,
                'state': estado,
            })
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al consultar usuarios: {e}")
            break

        for user in data.get('entities', []):
            usuarios.append({
                'ID': user['id'],
                'Nombre': user['name'],
                'Email': user.get('email', ''),
                'Título': user.get('title', ''),
                'Estado': 'Activo' if estado == 'active' else 'Inactivo',
                'Departamento': user.get('department', ''),
                'División': user.get('division', {}).get('name', ''),
            })

        if page_number >= data.get('pageCount', 1):
            break
        page_number += 1

    return usuarios


def main():
    print("==== Exportador de Usuarios de Genesys Cloud ====\n")

    login_domain, api_domain, region_nombre = seleccionar_region()
    client_id, client_secret = solicitar_credenciales()

    print("\n🔄 Solicitando token de autenticación...")
    token = obtener_token(client_id, client_secret, login_domain)
    if not token:
        print("🚫 No se pudo autenticar. Terminando.")
        return

    print("[*] Obteniendo usuarios activos...")
    usuarios_activos = obtener_usuarios(token, api_domain, 'active')
    print(f"[+] {len(usuarios_activos)} usuarios activos encontrados.")

    print("[*] Obteniendo usuarios inactivos...")
    usuarios_inactivos = obtener_usuarios(token, api_domain, 'inactive')
    print(f"[+] {len(usuarios_inactivos)} usuarios inactivos encontrados.")

    usuarios_totales = usuarios_activos + usuarios_inactivos
    if not usuarios_totales:
        print("⚠️ No se encontraron usuarios.")
        return

    df = pd.DataFrame(usuarios_totales)
    guardar_excel(df, 'usuarios_genesys', region_nombre)


if __name__ == "__main__":
    main()
