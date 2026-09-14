import io

from conftest import import_module_from_path

m = import_module_from_path('limpieza_contactos', 'scripts/bulk_limpieza_contactos/limpieza_contactos.py')


def test_formatear_fila_incluye_motivo_si_esta():
    assert m.formatear_fila({'contacto_id': 'c1', 'motivo': 'duplicado'}) == "Eliminar contacto c1 (duplicado)"
    assert m.formatear_fila({'contacto_id': 'c1', 'motivo': ''}) == "Eliminar contacto c1"


def test_aplicar_fila_llama_delete(requests_mock):
    delete_mock = requests_mock.delete('https://api.mypurecloud.com/api/v2/externalcontacts/contacts/c1')

    m.aplicar_fila('token', 'api.mypurecloud.com', {'contacto_id': 'c1'})

    assert delete_mock.called_once


def test_obtener_estado_actual_guarda_el_contacto_completo(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/externalcontacts/contacts/c1',
        json={'id': 'c1', 'firstName': 'Juan', 'email': 'juan@x.com'},
    )

    estado = m.obtener_estado_actual('token', 'api.mypurecloud.com', [{'contacto_id': 'c1'}])

    assert estado == [{'id': 'c1', 'firstName': 'Juan', 'email': 'juan@x.com', 'contacto_id_solicitado': 'c1'}]


def test_obtener_estado_actual_contacto_ya_no_existe(requests_mock):
    requests_mock.get('https://api.mypurecloud.com/api/v2/externalcontacts/contacts/c1', status_code=404)

    estado = m.obtener_estado_actual('token', 'api.mypurecloud.com', [{'contacto_id': 'c1'}])

    assert estado == [{'contacto_id_solicitado': 'c1'}]


def test_main_sin_confirm_no_borra_nada(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("contacto_id\nc1\n", encoding='utf-8')

    monkeypatch.setenv('BULK_ARCHIVO_CSV', str(csv_path))
    monkeypatch.delenv('BULK_CONFIRM', raising=False)
    monkeypatch.setenv('GENESYS_REGION', '1')
    monkeypatch.setenv('GENESYS_CLIENT_ID', 'id')
    monkeypatch.setenv('GENESYS_CLIENT_SECRET', 'secret')

    requests_mock.post('https://login.mypurecloud.com/oauth/token', json={'access_token': 'tok'})
    delete_mock = requests_mock.delete('https://api.mypurecloud.com/api/v2/externalcontacts/contacts/c1')

    m.main()

    assert delete_mock.called is False


def test_main_con_confirm_borra(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("contacto_id\nc1\n", encoding='utf-8')

    monkeypatch.setenv('BULK_ARCHIVO_CSV', str(csv_path))
    monkeypatch.setenv('BULK_CONFIRM', '1')
    monkeypatch.setenv('GENESYS_REGION', '1')
    monkeypatch.setenv('GENESYS_CLIENT_ID', 'id')
    monkeypatch.setenv('GENESYS_CLIENT_SECRET', 'secret')
    monkeypatch.setattr(m.sys, 'stdin', io.StringIO())

    expanduser_real = m.os.path.expanduser
    monkeypatch.setattr(m.os.path, 'expanduser', lambda p: str(tmp_path) if p == '~' else expanduser_real(p))

    requests_mock.post('https://login.mypurecloud.com/oauth/token', json={'access_token': 'tok'})
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/externalcontacts/contacts/c1',
        json={'id': 'c1', 'firstName': 'Juan'},
    )
    delete_mock = requests_mock.delete('https://api.mypurecloud.com/api/v2/externalcontacts/contacts/c1')

    m.main()

    assert delete_mock.called_once
