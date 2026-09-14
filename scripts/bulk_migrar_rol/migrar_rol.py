import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from genesys_client import (
    seleccionar_region,
    solicitar_credenciales,
    obtener_token,
    solicitar_api,
    solicitar_api_put,
    buscar_rol_por_nombre,
    obtener_usuarios_de_rol,
)
from bulk_ops import (
    leer_filas_csv,
    mostrar_resumen,
    confirmar_ejecucion,
    ejecutar_bulk,
    guardar_log_auditoria,
    hacer_backup_previo,
)

COLUMNAS_REQUERIDAS = ['rol_origen', 'rol_destino']


def expandir_migraciones(token, api_domain, filas_csv):
    """Convierte cada fila (rol_origen, rol_destino) del CSV en una fila por
    cada usuario que hoy tiene el rol de origen: eso es lo que realmente se
    va a migrar. Se resuelve acá (antes de la vista previa) para que la vista
    previa muestre el alcance real, no solo los nombres de rol del CSV."""
    filas_efectivas = []

    for fila in filas_csv:
        rol_origen = buscar_rol_por_nombre(token, api_domain, fila['rol_origen'])
        if rol_origen is None:
            raise ValueError(f"No se encontró un rol llamado {fila['rol_origen']!r}")

        rol_destino = buscar_rol_por_nombre(token, api_domain, fila['rol_destino'])
        if rol_destino is None:
            raise ValueError(f"No se encontró un rol llamado {fila['rol_destino']!r}")

        for user_id in obtener_usuarios_de_rol(token, api_domain, rol_origen['id']):
            usuario = solicitar_api(token, api_domain, f'/api/v2/users/{user_id}')
            filas_efectivas.append({
                'email_usuario': usuario.get('email', user_id),
                'user_id': user_id,
                'rol_origen_id': rol_origen['id'],
                'rol_origen_nombre': rol_origen['name'],
                'rol_destino_id': rol_destino['id'],
                'rol_destino_nombre': rol_destino['name'],
            })

    return filas_efectivas


def formatear_fila(fila):
    return f"{fila['email_usuario']}: {fila['rol_origen_nombre']!r} -> {fila['rol_destino_nombre']!r}"


def aplicar_fila(token, api_domain, fila):
    """Agrega el rol nuevo primero y recién después quita el viejo: si algo
    falla a mitad de camino, el usuario queda con ambos roles en vez de con
    ninguno."""
    solicitar_api_put(
        token, api_domain, f"/api/v2/authorization/roles/{fila['rol_destino_id']}/users/add", [fila['user_id']],
    )
    solicitar_api_put(
        token, api_domain, f"/api/v2/authorization/roles/{fila['rol_origen_id']}/users/remove", [fila['user_id']],
    )


def obtener_estado_actual(filas):
    """El propio proceso de expansión ya deja registrado quién tenía el rol
    de origen antes de migrar — eso es el backup, sin llamadas extra."""
    return [
        {
            'email_usuario': fila['email_usuario'],
            'rol_origen': fila['rol_origen_nombre'],
            'rol_destino_propuesto': fila['rol_destino_nombre'],
        }
        for fila in filas
    ]


def main():
    print("==== Migrar Usuarios de Rol en Bulk - Genesys Cloud ====\n")
    print("⚠️  Este script ESCRIBE en tu organización (no es de solo lectura).\n")
    print("⚠️  Cambia los permisos de todos los usuarios que hoy tengan el rol de origen.\n")

    archivo = os.environ.get('BULK_ARCHIVO_CSV', '').strip()
    if not archivo:
        print("❌ Falta indicar el CSV. Definí BULK_ARCHIVO_CSV (o usá --archivo con gcloud-tools).")
        return

    try:
        filas_csv = leer_filas_csv(archivo, COLUMNAS_REQUERIDAS)
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

    print("\n🔎 Resolviendo roles y usuarios afectados...")
    try:
        filas = expandir_migraciones(token, api_domain, filas_csv)
    except ValueError as e:
        print(f"❌ {e}")
        return

    if not filas:
        print("⚠️ No hay usuarios con el rol de origen indicado. No hay nada para migrar.")
        return

    mostrar_resumen(filas, formatear_fila)

    modo_aplicar = os.environ.get('BULK_CONFIRM', '').strip().lower() in ('1', 'true', 'si', 'sí')
    if not modo_aplicar:
        print("👀 Esto fue solo una vista previa (dry-run). No se aplicó ningún cambio.")
        print("   Para aplicarlos de verdad, definí BULK_CONFIRM=1 (o --confirm con gcloud-tools) y volvé a correr.")
        return

    hacer_backup_previo('migrar_rol', lambda: obtener_estado_actual(filas), region_nombre)

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

    guardar_log_auditoria('migrar_rol', resultados, region_nombre)


if __name__ == "__main__":
    main()
