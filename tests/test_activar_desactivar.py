import io

import pytest

from conftest import import_module_from_path

m = import_module_from_path('activar_desactivar', 'scripts/bulk_activar_desactivar/activar_desactivar.py')


def test_validar_filas_acepta_acciones_permitidas():
    m.validar_filas([
        {'email_usuario': 'a@x.com', 'accion': 'activar'},
        {'email_usuario': 'b@x.com', 'accion': 'desactivar'},
    ])  # no debe lanzar


def test_validar_filas_rechaza_accion_no_permitida():
    with pytest.raises(ValueError, match='no permitida'):
        m.validar_filas([{'email_usuario': 'a@x.com', 'accion': 'suspender'}])


def test_aplicar_fila_desactivar(requests_mock):
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1', 'state': 'active'}]},
    )
    patch_mock = requests_mock.patch('https://api.mypurecloud.com/api/v2/users/u1', json={'id': 'u1'})

    m.aplicar_fila('token', 'api.mypurecloud.com', {'email_usuario': 'a@x.com', 'accion': 'desactivar'})

    assert patch_mock.last_request.json() == {'state': 'inactive'}


def test_aplicar_fila_activar(requests_mock):
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1', 'state': 'inactive'}]},
    )
    patch_mock = requests_mock.patch('https://api.mypurecloud.com/api/v2/users/u1', json={'id': 'u1'})

    m.aplicar_fila('token', 'api.mypurecloud.com', {'email_usuario': 'a@x.com', 'accion': 'activar'})

    assert patch_mock.last_request.json() == {'state': 'active'}


def test_aplicar_fila_usuario_no_encontrado(requests_mock):
    requests_mock.post('https://api.mypurecloud.com/api/v2/users/search', json={'results': []})

    with pytest.raises(ValueError, match='No se encontró'):
        m.aplicar_fila('token', 'api.mypurecloud.com', {'email_usuario': 'nadie@x.com', 'accion': 'activar'})


def test_main_sin_confirm_no_escribe_nada(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("email_usuario,accion\na@x.com,desactivar\n", encoding='utf-8')

    monkeypatch.setenv('BULK_ARCHIVO_CSV', str(csv_path))
    monkeypatch.delenv('BULK_CONFIRM', raising=False)
    monkeypatch.setenv('GENESYS_REGION', '1')
    monkeypatch.setenv('GENESYS_CLIENT_ID', 'id')
    monkeypatch.setenv('GENESYS_CLIENT_SECRET', 'secret')

    requests_mock.post('https://login.mypurecloud.com/oauth/token', json={'access_token': 'tok'})
    patch_mock = requests_mock.patch('https://api.mypurecloud.com/api/v2/users/u1', json={'id': 'u1'})
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1', 'state': 'active'}]},
    )

    m.main()

    assert patch_mock.called is False


def test_main_con_confirm_escribe(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("email_usuario,accion\na@x.com,desactivar\n", encoding='utf-8')

    monkeypatch.setenv('BULK_ARCHIVO_CSV', str(csv_path))
    monkeypatch.setenv('BULK_CONFIRM', '1')
    monkeypatch.setenv('GENESYS_REGION', '1')
    monkeypatch.setenv('GENESYS_CLIENT_ID', 'id')
    monkeypatch.setenv('GENESYS_CLIENT_SECRET', 'secret')
    monkeypatch.setattr(m.sys, 'stdin', io.StringIO())

    expanduser_real = m.os.path.expanduser
    monkeypatch.setattr(m.os.path, 'expanduser', lambda p: str(tmp_path) if p == '~' else expanduser_real(p))

    requests_mock.post('https://login.mypurecloud.com/oauth/token', json={'access_token': 'tok'})
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1', 'state': 'active'}]},
    )
    patch_mock = requests_mock.patch('https://api.mypurecloud.com/api/v2/users/u1', json={'id': 'u1'})

    m.main()

    assert patch_mock.last_request.json() == {'state': 'inactive'}
