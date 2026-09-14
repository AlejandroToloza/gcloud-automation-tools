import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from genesys_client import (
    seleccionar_region,
    solicitar_credenciales,
    obtener_token,
    solicitar_api,
    solicitar_api_patch,
    solicitar_api_delete,
    buscar_usuario_por_email,
    buscar_skill_por_nombre,
)
from bulk_ops import (
    leer_filas_csv,
    mostrar_resumen,
    confirmar_ejecucion,
    ejecutar_bulk,
    guardar_log_auditoria,
    hacer_backup_previo,
)

COLUMNAS_REQUERIDAS = ['email_usuario', 'skill', 'accion']
ACCIONES_PERMITIDAS = {'agregar', 'quitar'}
PROFICIENCY_DEFECTO = 1.0


def validar_filas(filas):
    """Valida que la columna 'accion' use únicamente valores permitidos."""
    invalidas = [f for f in filas if f.get('accion') not in ACCIONES_PERMITIDAS]
    if invalidas:
        raise ValueError(
            f"{len(invalidas)} fila(s) usan una 'accion' no permitida. "
            f"Acciones permitidas: {sorted(ACCIONES_PERMITIDAS)}"
        )


def _proficiency_de_fila(fila):
    valor = (fila.get('proficiency') or '').strip()
    return float(valor) if valor else PROFICIENCY_DEFECTO


def formatear_fila(fila):
    if fila['accion'] == 'agregar':
        return f"{fila['email_usuario']}: agregar skill {fila['skill']!r} (proficiency {_proficiency_de_fila(fila)})"
    return f"{fila['email_usuario']}: quitar skill {fila['skill']!r}"


def aplicar_fila(token, api_domain, fila):
    """Resuelve usuario y skill, y la agrega (con proficiency) o la quita."""
    usuario = buscar_usuario_por_email(token, api_domain, fila['email_usuario'])
    if usuario is None:
        raise ValueError(f"No se encontró un usuario con email {fila['email_usuario']!r}")

    skill = buscar_skill_por_nombre(token, api_domain, fila['skill'])
    if skill is None:
        raise ValueError(f"No se encontró una skill de enrutamiento llamada {fila['skill']!r}")

    if fila['accion'] == 'agregar':
        solicitar_api_patch(token, api_domain, f"/api/v2/users/{usuario['id']}/routingskills/bulk", [{
            'id': skill['id'],
            'proficiency': _proficiency_de_fila(fila),
        }])
    else:
        solicitar_api_delete(token, api_domain, f"/api/v2/users/{usuario['id']}/routingskills/{skill['id']}")


def obtener_estado_actual(token, api_domain, filas):
    """Trae las skills actuales de cada usuario involucrado, para el backup previo."""
    estado = []
    cache_skills_usuario = {}

    for fila in filas:
        email = fila['email_usuario']
        if email not in cache_skills_usuario:
            skills_actuales = []
            usuario = buscar_usuario_por_email(token, api_domain, email)
            if usuario is not None:
                data = solicitar_api(token, api_domain, f"/api/v2/users/{usuario['id']}/routingskills")
                skills_actuales = [
                    f"{s.get('name', '')} ({s.get('proficiency', '')})" for s in data.get('entities', [])
                ]
            cache_skills_usuario[email] = skills_actuales

        estado.append({
            'email_usuario': email,
            'skills_actuales': ', '.join(cache_skills_usuario[email]),
            'skill_propuesta': fila['skill'],
            'accion_propuesta': fila['accion'],
        })

    return estado


def main():
    print("==== Skills de Enrutamiento en Bulk - Genesys Cloud ====\n")
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
        'skills_agentes',
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

    guardar_log_auditoria('skills_agentes', resultados, region_nombre)


if __name__ == "__main__":
    main()
