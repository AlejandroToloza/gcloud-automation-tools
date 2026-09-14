import os
import sys

import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from genesys_client import seleccionar_region, solicitar_credenciales, obtener_token, obtener_contactos, guardar_excel


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
