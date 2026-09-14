import os
import sys

import pandas as pd
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from genesys_client import seleccionar_region, solicitar_credenciales, obtener_token, solicitar_api, guardar_excel


def obtener_contactos(token, api_domain):
    """Obtiene todos los contactos externos disponibles usando paginación."""
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


def main():
    print("📤 Exportador de Contactos Externos - Genesys Cloud\n")

    login_domain, api_domain, region_nombre = seleccionar_region()
    client_id, client_secret = solicitar_credenciales()

    print("\n🔄 Solicitando token de autenticación...")
    token = obtener_token(client_id, client_secret, login_domain)
    if not token:
        print("🚫 No se pudo autenticar. Terminando.")
        sys.exit(1)

    print("\n📥 Obteniendo contactos externos...")
    contactos = obtener_contactos(token, api_domain)

    if not contactos:
        print("⚠️ No se encontraron contactos externos.")
        return

    df = pd.json_normalize(contactos)
    guardar_excel(df, 'contactos_externos', region_nombre)


if __name__ == "__main__":
    main()
