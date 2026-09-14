import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from genesys_client import (
    seleccionar_region,
    solicitar_credenciales,
    obtener_token,
    solicitar_api,
    solicitar_api_delete,
)
from bulk_ops import (
    leer_filas_csv,
    mostrar_resumen,
    confirmar_ejecucion,
    ejecutar_bulk,
    guardar_log_auditoria,
    hacer_backup_previo,
)

COLUMNAS_REQUERIDAS = ['contacto_id']


def formatear_fila(fila):
    motivo = fila.get('motivo', '').strip()
    return f"Eliminar contacto {fila['contacto_id']}" + (f" ({motivo})" if motivo else "")


def aplicar_fila(token, api_domain, fila):
    """Elimina el contacto externo. Es la única operación del repositorio que
    borra datos de forma permanente en vez de solo cambiar un estado — por
    eso el CSV nunca 'decide' qué borrar por sí mismo: cada contacto a
    eliminar tiene que estar explícitamente listado, y siempre queda un
    backup completo (no solo el ID) guardado antes de la ejecución."""
    solicitar_api_delete(token, api_domain, f"/api/v2/externalcontacts/contacts/{fila['contacto_id']}")


def obtener_estado_actual(token, api_domain, filas):
    """Trae el contenido completo de cada contacto antes de borrarlo, para el backup previo."""
    estado = []
    for fila in filas:
        try:
            contacto = solicitar_api(token, api_domain, f"/api/v2/externalcontacts/contacts/{fila['contacto_id']}")
        except Exception:
            contacto = {}
        fila_backup = dict(contacto)
        fila_backup['contacto_id_solicitado'] = fila['contacto_id']
        estado.append(fila_backup)
    return estado


def main():
    print("==== Limpieza de Contactos Externos en Bulk - Genesys Cloud ====\n")
    print("⚠️  Este script ESCRIBE en tu organización (no es de solo lectura).\n")
    print("⚠️  Esto BORRA contactos de forma permanente. No hay 'deshacer' más allá del backup.\n")
    print("   El CSV tiene que listar exactamente los IDs a borrar (este script no detecta")
    print("   duplicados por su cuenta — revisá vos qué contactos son candidatos antes de listarlos).\n")

    archivo = os.environ.get('BULK_ARCHIVO_CSV', '').strip()
    if not archivo:
        print("❌ Falta indicar el CSV. Definí BULK_ARCHIVO_CSV (o usá --archivo con gcloud-tools).")
        return

    try:
        filas = leer_filas_csv(archivo, COLUMNAS_REQUERIDAS)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ {e}")
        return

    login_domain, api_domain, region_nombre = seleccionar_region()
    client_id, client_secret = solicitar_credenciales()

    print("\n🔄 Solicitando token de autenticación...")
    token = obtener_token(client_id, client_secret, login_domain)
    if not token:
        print("🚫 No se pudo autenticar. Terminando.")
        return

    mostrar_resumen(filas, formatear_fila)

    modo_aplicar = os.environ.get('BULK_CONFIRM', '').strip().lower() in ('1', 'true', 'si', 'sí')
    if not modo_aplicar:
        print("👀 Esto fue solo una vista previa (dry-run). No se aplicó ningún cambio.")
        print("   Para aplicarlos de verdad, definí BULK_CONFIRM=1 (o --confirm con gcloud-tools) y volvé a correr.")
        return

    hacer_backup_previo(
        'limpieza_contactos',
        lambda: obtener_estado_actual(token, api_domain, filas),
        region_nombre,
    )

    if not confirmar_ejecucion(len(filas), auto_confirmar=not sys.stdin.isatty()):
        print("🚫 Cancelado: no se escribió nada.")
        return

    print(f"\n✍️  Eliminando {len(filas)} contacto(s)...")
    resultados = ejecutar_bulk(filas, lambda fila: aplicar_fila(token, api_domain, fila))

    exitosos = sum(1 for r in resultados if r['estado'] == 'ok')
    fallidos = len(resultados) - exitosos
    if fallidos:
        print(f"\n✅ {exitosos} contacto(s) eliminados. ❌ {fallidos} con error (ver log de auditoría).")
    else:
        print(f"\n✅ {exitosos} contacto(s) eliminados correctamente.")

    guardar_log_auditoria('limpieza_contactos', resultados, region_nombre)


if __name__ == "__main__":
    main()
