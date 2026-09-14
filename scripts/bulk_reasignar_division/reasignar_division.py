import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from genesys_client import (
    seleccionar_region,
    solicitar_credenciales,
    obtener_token,
    solicitar_api_patch,
    buscar_usuario_por_email,
    buscar_division_por_nombre,
)
from bulk_ops import (
    leer_filas_csv,
    mostrar_resumen,
    confirmar_ejecucion,
    ejecutar_bulk,
    guardar_log_auditoria,
    hacer_backup_previo,
)

COLUMNAS_REQUERIDAS = ['email_usuario', 'division_nueva']


def formatear_fila(fila):
    return f"{fila['email_usuario']}: -> división {fila['division_nueva']!r}"


def aplicar_fila(token, api_domain, fila):
    """Resuelve el email y el nombre de división a IDs reales, y aplica el cambio."""
    usuario = buscar_usuario_por_email(token, api_domain, fila['email_usuario'])
    if usuario is None:
        raise ValueError(f"No se encontró un usuario con email {fila['email_usuario']!r}")

    division = buscar_division_por_nombre(token, api_domain, fila['division_nueva'])
    if division is None:
        raise ValueError(f"No se encontró una división llamada {fila['division_nueva']!r}")

    solicitar_api_patch(token, api_domain, f"/api/v2/users/{usuario['id']}", {
        'division': {'id': division['id']},
    })


def obtener_estado_actual(token, api_domain, filas):
    """Trae la división actual de cada usuario, para el backup previo."""
    estado = []
    for fila in filas:
        usuario = buscar_usuario_por_email(token, api_domain, fila['email_usuario']) or {}
        division_actual = (usuario.get('division') or {}).get('name', '')
        estado.append({
            'email_usuario': fila['email_usuario'],
            'division_actual': division_actual,
            'division_nueva_propuesta': fila['division_nueva'],
        })
    return estado


def main():
    print("==== Reasignar División de Usuarios en Bulk - Genesys Cloud ====\n")
    print("⚠️  Este script ESCRIBE en tu organización (no es de solo lectura).\n")
    print("⚠️  Cambiar la división afecta qué objetos/datos puede ver y gestionar el usuario.\n")

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
        'reasignar_division',
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

    guardar_log_auditoria('reasignar_division', resultados, region_nombre)


if __name__ == "__main__":
    main()
