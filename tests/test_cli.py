import pytest

from conftest import import_module_from_path

cli = import_module_from_path('cli', 'gcloud_tools/cli.py')


def test_dispatch_carga_y_llama_al_main_del_comando(monkeypatch):
    llamados = []

    def fake_cargar_main(nombre_modulo, ruta_relativa):
        def fake_main():
            llamados.append(nombre_modulo)
        return fake_main

    monkeypatch.setattr(cli, '_cargar_main', fake_cargar_main)

    cli.main(['export-users'])

    assert llamados == ['export_all_users']


def test_cada_comando_dispatchea_su_propio_modulo(monkeypatch):
    llamados = []

    def fake_cargar_main(nombre_modulo, ruta_relativa):
        return lambda: llamados.append(nombre_modulo)

    monkeypatch.setattr(cli, '_cargar_main', fake_cargar_main)

    for comando, (nombre_modulo, _, _) in cli.COMANDOS.items():
        cli.main([comando])

    assert llamados == [nombre_modulo for nombre_modulo, _, _ in cli.COMANDOS.values()]


def test_comando_desconocido_termina_con_error():
    with pytest.raises(SystemExit):
        cli.main(['no-existe'])


def test_sin_comando_termina_con_error():
    with pytest.raises(SystemExit):
        cli.main([])


def test_cargar_main_carga_el_script_real():
    funcion_main = cli._cargar_main('export_all_users', 'scripts/export_all_users/export_all_users.py')
    assert callable(funcion_main)


def test_flag_region_define_genesys_region_antes_de_llamar(monkeypatch):
    monkeypatch.delenv('GENESYS_REGION', raising=False)
    valor_visto = {}

    def fake_cargar_main(nombre_modulo, ruta_relativa):
        def fake_main():
            valor_visto['region'] = cli.os.environ.get('GENESYS_REGION')
        return fake_main

    monkeypatch.setattr(cli, '_cargar_main', fake_cargar_main)

    cli.main(['export-users', '--region', '3'])

    assert valor_visto['region'] == '3'


def test_sin_flag_region_no_toca_la_variable_de_entorno(monkeypatch):
    monkeypatch.delenv('GENESYS_REGION', raising=False)
    llamado = []

    def fake_cargar_main(nombre_modulo, ruta_relativa):
        return lambda: llamado.append(cli.os.environ.get('GENESYS_REGION'))

    monkeypatch.setattr(cli, '_cargar_main', fake_cargar_main)

    cli.main(['export-users'])

    assert llamado == [None]


def test_comando_de_solo_lectura_no_acepta_archivo_ni_confirm():
    with pytest.raises(SystemExit):
        cli.main(['export-users', '--archivo', 'x.csv'])


def test_comando_bulk_define_archivo_y_confirm_antes_de_llamar(monkeypatch):
    monkeypatch.delenv('BULK_ARCHIVO_CSV', raising=False)
    monkeypatch.delenv('BULK_CONFIRM', raising=False)
    valor_visto = {}

    def fake_cargar_main(nombre_modulo, ruta_relativa):
        def fake_main():
            valor_visto['archivo'] = cli.os.environ.get('BULK_ARCHIVO_CSV')
            valor_visto['confirm'] = cli.os.environ.get('BULK_CONFIRM')
        return fake_main

    monkeypatch.setattr(cli, '_cargar_main', fake_cargar_main)

    cli.main(['update-users', '--archivo', 'cambios.csv', '--confirm'])

    assert valor_visto == {'archivo': 'cambios.csv', 'confirm': '1'}


def test_comando_bulk_sin_confirm_no_define_bulk_confirm(monkeypatch):
    monkeypatch.delenv('BULK_ARCHIVO_CSV', raising=False)
    monkeypatch.delenv('BULK_CONFIRM', raising=False)
    valor_visto = {}

    def fake_cargar_main(nombre_modulo, ruta_relativa):
        def fake_main():
            valor_visto['confirm'] = cli.os.environ.get('BULK_CONFIRM')
        return fake_main

    monkeypatch.setattr(cli, '_cargar_main', fake_cargar_main)

    cli.main(['update-users', '--archivo', 'cambios.csv'])

    assert valor_visto == {'confirm': None}
