import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from genesys_client import (
    seleccionar_region,
    solicitar_credenciales,
    obtener_token,
    solicitar_api,
    solicitar_api_post,
    solicitar_api_delete,
    buscar_cola_por_nombre,
    buscar_wrapupcode_por_nombre,
)
from bulk_ops import (
    leer_filas_csv,
    mostrar_resumen,
    confirmar_ejecucion,
    ejecutar_bulk,
    guardar_log_auditoria,
    hacer_backup_previo,
)

COLUMNAS_REQUERIDAS = ['cola', 'wrapup_code', 'accion']
ACCIONES_PERMITIDAS = {'agregar', 'quitar'}


def validar_filas(filas):
    """Valida que la columna 'accion' use únicamente valores permitidos."""
    invalidas = [f for f in filas if f.get('accion') not in ACCIONES_PERMITIDAS]
    if invalidas:
        raise ValueError(
            f"{len(invalidas)} fila(s) usan una 'accion' no permitida. "
            f"Acciones permitidas: {sorted(ACCIONES_PERMITIDAS)}"
        )


def formatear_fila(fila):
    return f"Cola {fila['cola']!r}: {fila['accion']} wrap-up code {fila['wrapup_code']!r}"


def aplicar_fila(token, api_domain, fila):
    """Resuelve cola y wrap-up code, y agrega/quita el código de esa cola."""
    cola = buscar_cola_por_nombre(token, api_domain, fila['cola'])
    if cola is None:
        raise ValueError(f"No se encontró una cola llamada {fila['cola']!r}")

    code = buscar_wrapupcode_por_nombre(token, api_domain, fila['wrapup_code'])
    if code is None:
        raise ValueError(f"No se encontró un wrap-up code llamado {fila['wrapup_code']!r}")

    if fila['accion'] == 'agregar':
        solicitar_api_post(
            token, api_domain, f"/api/v2/routing/queues/{cola['id']}/wrapupcodes", [{'id': code['id']}],
        )
    else:
        solicitar_api_delete(token, api_domain, f"/api/v2/routing/queues/{cola['id']}/wrapupcodes/{code['id']}")


def obtener_estado_actual(token, api_domain, filas):
    """Trae los wrap-up codes actualmente asignados a cada cola involucrada, para el backup previo."""
    estado = []
    cache_colas = {}
    for fila in filas:
        nombre_cola = fila['cola']
        if nombre_cola not in cache_colas:
            codigos_actuales = []
            cola = buscar_cola_por_nombre(token, api_domain, nombre_cola)
            if cola is not None:
                data = solicitar_api(token, api_domain, f"/api/v2/routing/queues/{cola['id']}/wrapupcodes")
                codigos_actuales = [c.get('name', '') for c in data.get('entities', [])]
            cache_colas[nombre_cola] = codigos_actuales

        estado.append({
            'cola': nombre_cola,
            'wrapup_codes_actuales': ', '.join(cache_colas[nombre_cola]),
            'wrapup_code_propuesto': fila['wrapup_code'],
            'accion_propuesta': fila['accion'],
        })
    return estado


def main():
    print("==== Actualizar Wrap-Up Codes de Colas en Bulk - Genesys Cloud ====\n")
    print("⚠️  Este script ESCRIBE en tu organización (no es de solo lectura).\n")

    archivo = os.environ.get('BULK_ARCHIVO_CSV', '').strip()
    if not archivo:
        print("❌ Falta indicar el CSV. Definí BULK_ARCHIVO_CSV (o usá --archivo con gcloud-tools).")
        return

    try:
        filas = leer_filas_csv(archivo, COLUMNAS_REQUERIDAS)
        validar_filas(filas)
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
        'wrapupcodes_cola',
        lambda: obtener_estado_actual(token, api_domain, filas),
        region_nombre,
    )

    if not confirmar_ejecucion(len(filas), auto_confirmar=not sys.stdin.isatty()):
        print("🚫 Cancelado: no se escribió nada.")
        return

    print(f"\n✍️  Aplicando {len(filas)} cambio(s)...")
    resultados = ejecutar_bulk(filas, lambda fila: aplicar_fila(token, api_domain, fila))

    exitosos = sum(1 for r in resultados if r['estado'] == 'ok')
    fallidos = len(resultados) - exitosos
    if fallidos:
        print(f"\n✅ {exitosos} cambio(s) aplicados. ❌ {fallidos} con error (ver log de auditoría).")
    else:
        print(f"\n✅ {exitosos} cambio(s) aplicados correctamente.")

    guardar_log_auditoria('wrapupcodes_cola', resultados, region_nombre)


if __name__ == "__main__":
    main()
