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
