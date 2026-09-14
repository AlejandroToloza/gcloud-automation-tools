import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from genesys_client import (
    seleccionar_region,
    solicitar_credenciales,
    obtener_token,
    solicitar_api,
    solicitar_api_put,
    buscar_cola_por_nombre,
    buscar_script_por_nombre,
)
from bulk_ops import (
    leer_filas_csv,
    mostrar_resumen,
    confirmar_ejecucion,
    ejecutar_bulk,
    guardar_log_auditoria,
    hacer_backup_previo,
)

COLUMNAS_REQUERIDAS = ['cola', 'tipo_script', 'nombre_script']


def formatear_fila(fila):
    return f"Cola {fila['cola']!r}: script {fila['tipo_script']} -> {fila['nombre_script']!r}"


def aplicar_fila(token, api_domain, fila):
    """Resuelve cola y script, y actualiza defaultScripts sin tocar el resto de
    la configuración de la cola. La API de colas no tiene PATCH, solo PUT (que
    reemplaza el recurso entero) — por eso se trae la cola completa, se
    modifica solo defaultScripts, y se reenvía entera."""
    cola = buscar_cola_por_nombre(token, api_domain, fila['cola'])
    if cola is None:
        raise ValueError(f"No se encontró una cola llamada {fila['cola']!r}")

    script = buscar_script_por_nombre(token, api_domain, fila['nombre_script'])
    if script is None:
        raise ValueError(f"No se encontró un script llamado {fila['nombre_script']!r}")

    cola_completa = solicitar_api(token, api_domain, f"/api/v2/routing/queues/{cola['id']}")
    default_scripts = dict(cola_completa.get('defaultScripts') or {})
    default_scripts[fila['tipo_script']] = {'id': script['id']}
    cola_completa['defaultScripts'] = default_scripts

    solicitar_api_put(token, api_domain, f"/api/v2/routing/queues/{cola['id']}", cola_completa)


def obtener_estado_actual(token, api_domain, filas):
    """Trae el script actualmente asignado a cada (cola, tipo_script), para el backup previo."""
    estado = []
    for fila in filas:
        cola = buscar_cola_por_nombre(token, api_domain, fila['cola'])
        script_actual_id = ''
        if cola is not None:
            cola_completa = solicitar_api(token, api_domain, f"/api/v2/routing/queues/{cola['id']}")
            default_scripts = cola_completa.get('defaultScripts') or {}
            script_actual_id = (default_scripts.get(fila['tipo_script']) or {}).get('id', '')
        estado.append({
            'cola': fila['cola'],
            'tipo_script': fila['tipo_script'],
            'script_id_actual': script_actual_id,
            'script_nuevo_propuesto': fila['nombre_script'],
        })
    return estado


def main():
    print("==== Actualizar Script/IVR por Defecto de Colas en Bulk - Genesys Cloud ====\n")
    print("⚠️  Este script ESCRIBE en tu organización (no es de solo lectura).\n")
    print("⚠️  Cambia el flujo/IVR que se ejecuta cuando entra una interacción a la cola.\n")

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
        'actualizar_script_cola',
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

    guardar_log_auditoria('actualizar_script_cola', resultados, region_nombre)


if __name__ == "__main__":
    main()
