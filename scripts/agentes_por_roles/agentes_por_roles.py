import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from genesys_client import seleccionar_region, solicitar_credenciales, obtener_token, solicitar_api, guardar_excel

MAX_WORKERS = 8


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


def obtener_detalles_usuarios(token, api_domain, usuario_ids):
    """Consulta nombre y email de una lista de IDs de usuario, en lotes de 100."""
    detalles = {}
    lote_tamano = 100
    ids_unicos = list(dict.fromkeys(usuario_ids))

    for i in range(0, len(ids_unicos), lote_tamano):
        lote = ids_unicos[i:i + lote_tamano]
        try:
            data = solicitar_api(token, api_domain, '/api/v2/users', params={
                'id': ','.join(lote),
                'pageSize': lote_tamano,
            })
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al obtener datos de usuarios: {e}")
            continue

        for user in data.get('entities', []):
            detalles[user['id']] = {
                'nombre': user.get('name', ''),
                'email': user.get('email', ''),
            }

    return detalles


def procesar_rol(token, api_domain, rol):
    """Devuelve las asignaciones (role_id, role_name, user_id) de un rol."""
    role_id = rol.get('id')
    role_name = rol.get('name')
    if not role_id:
        return []

    return [
        (role_id, role_name, user_id)
        for user_id in obtener_usuarios_de_rol(token, api_domain, role_id)
    ]


def main():
    print("==== Agentes por Roles - Genesys Cloud ====\n")

    login_domain, api_domain, region_nombre = seleccionar_region()
    client_id, client_secret = solicitar_credenciales()

    print("\n🔄 Solicitando token de autenticación...")
    token = obtener_token(client_id, client_secret, login_domain)
    if not token:
        print("🚫 No se pudo autenticar. Terminando.")
        return

    print("\n📥 Obteniendo listado de roles...")
    roles = obtener_roles(token, api_domain)
    print(f"[+] {len(roles)} roles encontrados.")

    print(f"\n👥 Consultando usuarios asignados a cada rol (hasta {MAX_WORKERS} en paralelo)...")
    asignaciones = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futuros = [executor.submit(procesar_rol, token, api_domain, rol) for rol in roles]
        for futuro in as_completed(futuros):
            asignaciones.extend(futuro.result())

    if not asignaciones:
        print("⚠️ No se encontraron agentes asignados a roles.")
        return

    print("\n🔎 Obteniendo nombre y email de los usuarios...")
    todos_los_ids = [user_id for _, _, user_id in asignaciones]
    detalles_usuarios = obtener_detalles_usuarios(token, api_domain, todos_los_ids)

    datos = []
    for role_id, role_name, user_id in asignaciones:
        detalle = detalles_usuarios.get(user_id, {})
        datos.append({
            'ID de Rol': role_id,
            'Nombre de Rol': role_name,
            'ID de Usuario': user_id,
            'Nombre de Usuario': detalle.get('nombre', ''),
            'Email': detalle.get('email', ''),
        })

    df = pd.DataFrame(datos).sort_values(['Nombre de Rol', 'Nombre de Usuario']).reset_index(drop=True)
    guardar_excel(df, 'agentes_por_roles', region_nombre)


if __name__ == "__main__":
    main()
