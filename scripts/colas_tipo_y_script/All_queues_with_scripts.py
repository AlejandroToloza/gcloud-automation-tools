import os
import sys

import pandas as pd
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from genesys_client import seleccionar_region, solicitar_credenciales, obtener_token, solicitar_api, guardar_excel


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


def obtener_nombre_script(token, api_domain, script_id):
    """Obtiene el nombre de un script a partir de su ID."""
    try:
        data = solicitar_api(token, api_domain, f'/api/v2/scripts/{script_id}')
        return data.get('name', 'Nombre no disponible')
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return 'Script no encontrado'
        print(f"⚠️ Error al obtener nombre de script {script_id}: {e}")
        return 'Error'
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error al obtener nombre de script {script_id}: {e}")
        return 'Error'


def obtener_scripts_de_cola(token, api_domain, queue_id):
    """Consulta los scripts asignados a una cola específica."""
    try:
        data = solicitar_api(token, api_domain, f'/api/v2/routing/queues/{queue_id}')
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener scripts de cola {queue_id}: {e}")
        return [{
            'Tipo de Script': 'Error',
            'ID de Script': 'Error',
            'Nombre del Script': 'Error',
        }]

    default_scripts = data.get('defaultScripts', {})
    scripts_info = []

    for tipo_script, script_info in default_scripts.items():
        script_id = script_info.get('id')
        script_nombre = obtener_nombre_script(token, api_domain, script_id) if script_id else 'No asignado'
        scripts_info.append({
            'Tipo de Script': tipo_script,
            'ID de Script': script_id or 'No asignado',
            'Nombre del Script': script_nombre,
        })

    return scripts_info


def main():
    print("==== Exportador de Colas y Scripts de Genesys Cloud ====\n")

    login_domain, api_domain, region_nombre = seleccionar_region()
    client_id, client_secret = solicitar_credenciales()

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
                'Nombre del Script': script['Nombre del Script'],
            })

    if not datos:
        print("⚠️ No se encontraron colas.")
        return

    df = pd.DataFrame(datos)
    guardar_excel(df, 'queues_and_scripts', region_nombre)


if __name__ == "__main__":
    main()
