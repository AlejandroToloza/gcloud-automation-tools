"""Punto de entrada único (`gcloud-tools`) para todas las automatizaciones
del repositorio. Cada subcomando ejecuta el mismo main() que su script
equivalente en scripts/, sin duplicar lógica."""
import argparse
import importlib.util
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# comando -> (nombre de módulo, ruta relativa al script, descripción para --help)
COMANDOS = {
    'export-users': (
        'export_all_users',
        'scripts/export_all_users/export_all_users.py',
        'Exporta todos los usuarios activos e inactivos a Excel.',
    ),
    'queue-scripts': (
        'All_queues_with_scripts',
        'scripts/colas_tipo_y_script/All_queues_with_scripts.py',
        'Exporta las colas de la organización junto a sus scripts asignados.',
    ),
    'queue-members': (
        'miembros_por_cola',
        'scripts/miembros_por_cola/miembros_por_cola.py',
        'Exporta las colas de la organización junto a sus miembros.',
    ),
    'external-contacts': (
        'all_conact_externa',
        'scripts/total_contacts_externals/all_conact_externa.py',
        'Exporta el total de contactos externos de la organización.',
    ),
    'roles': (
        'agentes_por_roles',
        'scripts/agentes_por_roles/agentes_por_roles.py',
        'Exporta los agentes agrupados por rol de autorización.',
    ),
    'update-users': (
        'actualizar_usuarios',
        'scripts/bulk_actualizar_usuarios/actualizar_usuarios.py',
        'Actualiza department/title de usuarios en bulk desde un CSV (vista previa por defecto).',
    ),
    'set-user-state': (
        'activar_desactivar',
        'scripts/bulk_activar_desactivar/activar_desactivar.py',
        'Activa o desactiva usuarios en bulk desde un CSV (vista previa por defecto).',
    ),
    'update-division': (
        'reasignar_division',
        'scripts/bulk_reasignar_division/reasignar_division.py',
        'Reasigna la división de usuarios en bulk desde un CSV (vista previa por defecto).',
    ),
    'reset-password': (
        'reset_password',
        'scripts/bulk_reset_password/reset_password.py',
        'Fija una contraseña temporal nueva a usuarios en bulk desde un CSV (vista previa por defecto).',
    ),
    'update-queue-script': (
        'actualizar_script_cola',
        'scripts/bulk_actualizar_script_cola/actualizar_script_cola.py',
        'Actualiza el script/IVR por defecto de colas en bulk desde un CSV (vista previa por defecto).',
    ),
    'update-queue-wrapupcodes': (
        'wrapupcodes_cola',
        'scripts/bulk_wrapupcodes_cola/wrapupcodes_cola.py',
        'Agrega/quita wrap-up codes de colas en bulk desde un CSV (vista previa por defecto).',
    ),
    'migrate-role': (
        'migrar_rol',
        'scripts/bulk_migrar_rol/migrar_rol.py',
        'Migra usuarios de un rol de autorización a otro en bulk (vista previa por defecto).',
    ),
    'update-group-members': (
        'grupos_membership',
        'scripts/bulk_grupos_membership/grupos_membership.py',
        'Agrega/quita usuarios de un Group en bulk desde un CSV (vista previa por defecto).',
    ),
}

# Subcomandos que ESCRIBEN en la organización (no son de solo lectura) y por
# lo tanto aceptan --archivo/--confirm además de --region.
COMANDOS_BULK = {
    'update-users', 'set-user-state', 'update-division', 'reset-password',
    'update-queue-script', 'update-queue-wrapupcodes',
    'migrate-role', 'update-group-members',
}


def _cargar_main(nombre_modulo, ruta_relativa):
    """Carga el main() de un script a partir de su ruta, igual a como
    se comporta al ejecutarlo directamente con `python scripts/.../archivo.py`."""
    ruta = os.path.join(REPO_ROOT, ruta_relativa)
    spec = importlib.util.spec_from_file_location(nombre_modulo, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo.main


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='gcloud-tools',
        description='Automatizaciones de Genesys Cloud (gcloud-automation-tools).',
    )
    subparsers = parser.add_subparsers(dest='comando', required=True)
    for nombre, (_, _, descripcion) in COMANDOS.items():
        subparser = subparsers.add_parser(nombre, help=descripcion)
        subparser.add_argument(
            '--region',
            metavar='N',
            help='Número de región de Genesys Cloud (ver el menú interactivo para la lista). '
                 'Si se pasa, evita el menú y equivale a definir GENESYS_REGION.',
        )
        if nombre in COMANDOS_BULK:
            subparser.add_argument(
                '--archivo',
                metavar='CSV',
                help='Ruta al CSV con los cambios a aplicar.',
            )
            subparser.add_argument(
                '--confirm',
                action='store_true',
                help='Aplica los cambios de verdad. Sin esta bandera, solo muestra una vista previa (dry-run).',
            )

    args = parser.parse_args(argv)
    if args.region:
        os.environ['GENESYS_REGION'] = args.region
    if args.comando in COMANDOS_BULK:
        if args.archivo:
            os.environ['BULK_ARCHIVO_CSV'] = args.archivo
        if args.confirm:
            os.environ['BULK_CONFIRM'] = '1'

    nombre_modulo, ruta_relativa, _ = COMANDOS[args.comando]
    funcion_main = _cargar_main(nombre_modulo, ruta_relativa)
    funcion_main()


if __name__ == '__main__':
    main()
