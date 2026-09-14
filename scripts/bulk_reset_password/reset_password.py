import os
import secrets
import string
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from genesys_client import (
    seleccionar_region,
    solicitar_credenciales,
    obtener_token,
    solicitar_api_post,
    buscar_usuario_por_email,
)
from bulk_ops import (
    leer_filas_csv,
    mostrar_resumen,
    confirmar_ejecucion,
    ejecutar_bulk,
    guardar_log_auditoria,
)

COLUMNAS_REQUERIDAS = ['email_usuario']


def generar_password_temporal(longitud=16):
    """Genera una contraseña temporal aleatoria (mayúscula, minúscula, dígito
    y símbolo garantizados), usando el generador criptográfico `secrets`."""
    mayusculas = string.ascii_uppercase
    minusculas = string.ascii_lowercase
    digitos = string.digits
    simbolos = '!@#$%^&*-_=+'

    obligatorios = [
        secrets.choice(mayusculas),
        secrets.choice(minusculas),
        secrets.choice(digitos),
        secrets.choice(simbolos),
    ]
    resto = [
        secrets.choice(mayusculas + minusculas + digitos + simbolos)
        for _ in range(longitud - len(obligatorios))
    ]
    caracteres = obligatorios + resto
    secrets.SystemRandom().shuffle(caracteres)
    return ''.join(caracteres)


def formatear_fila(fila):
    return f"{fila['email_usuario']}: se le asignará una contraseña temporal nueva"


def aplicar_fila(token, api_domain, fila):
    """Resuelve el email a un usuario real y le fija una contraseña temporal
    nueva. La contraseña se imprime SOLO en consola, nunca se guarda en el
    log de auditoría ni en ningún archivo."""
    usuario = buscar_usuario_por_email(token, api_domain, fila['email_usuario'])
    if usuario is None:
        raise ValueError(f"No se encontró un usuario con email {fila['email_usuario']!r}")

    password_nueva = generar_password_temporal()
    solicitar_api_post(token, api_domain, f"/api/v2/users/{usuario['id']}/password", {
        'newPassword': password_nueva,
    })
    print(f"   🔑 {fila['email_usuario']}: {password_nueva}")


def main():
    print("==== Reset de Contraseña en Bulk - Genesys Cloud ====\n")
    print("⚠️  Este script ESCRIBE en tu organización (no es de solo lectura).\n")
    print("⚠️  Genesys Cloud no tiene un endpoint de 'enviar email de reset': este script")
    print("   genera una contraseña temporal nueva y la fija directamente. Comunicásela")
    print("   vos al usuario por un canal seguro — no queda guardada en ningún archivo.\n")

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

    guardar_log_auditoria('reset_password', resultados, region_nombre)


if __name__ == "__main__":
    main()
