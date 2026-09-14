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

    args = parser.parse_args(argv)
    if args.region:
        os.environ['GENESYS_REGION'] = args.region

    nombre_modulo, ruta_relativa, _ = COMANDOS[args.comando]
    funcion_main = _cargar_main(nombre_modulo, ruta_relativa)
    funcion_main()


if __name__ == '__main__':
    main()
