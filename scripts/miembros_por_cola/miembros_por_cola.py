import os
import sys

import pandas as pd
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from genesys_client import (
    seleccionar_region,
    solicitar_credenciales,
    obtener_token,
    solicitar_api,
    obtener_colas,
    guardar_excel,
)


def obtener_miembros_de_cola(token, api_domain, queue_id):
    """Obtiene todos los miembros (agentes) de una cola específica."""
    miembros = []
    page_number = 1

    while True:
        try:
            data = solicitar_api(token, api_domain, f'/api/v2/routing/queues/{queue_id}/members', params={
                'pageSize': 100,
                'pageNumber': page_number,
            })
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al obtener miembros de la cola {queue_id}: {e}")
            break

        entidades = data.get('entities', [])
        if not entidades:
            break
        miembros.extend(entidades)

        if page_number >= data.get('pageCount', 1):
            break
        page_number += 1

    return miembros


def main():
    print("==== Miembros por Cola - Genesys Cloud ====\n")

    login_domain, api_domain, region_nombre = seleccionar_region()
    client_id, client_secret = solicitar_credenciales()

    print("\n🔄 Solicitando token de autenticación...")
    token = obtener_token(client_id, client_secret, login_domain)
    if not token:
        print("🚫 No se pudo autenticar. Terminando.")
        return

    print("\n📥 Obteniendo listado de colas...")
    colas = obtener_colas(token, api_domain)
    print(f"[+] {len(colas)} colas encontradas.")

    print("\n👥 Consultando miembros de cada cola...")
    datos = []
    for cola in colas:
        queue_id = cola.get('id')
        queue_name = cola.get('name')
        if not queue_id:
            continue

        for miembro in obtener_miembros_de_cola(token, api_domain, queue_id):
            usuario = miembro.get('user') or {}
            datos.append({
                'ID de Cola': queue_id,
                'Nombre de Cola': queue_name,
                'ID de Usuario': usuario.get('id', ''),
                'Nombre de Usuario': usuario.get('name', ''),
                'Unido a la Cola': miembro.get('joined', ''),
                'Ring Number': miembro.get('ringNumber', ''),
            })

    if not datos:
        print("⚠️ No se encontraron miembros en ninguna cola.")
        return

    df = pd.DataFrame(datos)
    guardar_excel(df, 'miembros_por_cola', region_nombre)


if __name__ == "__main__":
    main()
