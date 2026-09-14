import io

import pytest

from conftest import import_module_from_path

m = import_module_from_path('reasignar_division', 'scripts/bulk_reasignar_division/reasignar_division.py')


def test_aplicar_fila_resuelve_usuario_y_division(requests_mock):
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1', 'email': 'a@x.com'}]},
    )
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/authorization/divisions',
        json={'entities': [{'id': 'd1', 'name': 'Ventas'}], 'pageCount': 1},
    )
    patch_mock = requests_mock.patch('https://api.mypurecloud.com/api/v2/users/u1', json={'id': 'u1'})

    m.aplicar_fila('token', 'api.mypurecloud.com', {'email_usuario': 'a@x.com', 'division_nueva': 'Ventas'})

    assert patch_mock.last_request.json() == {'division': {'id': 'd1'}}


def test_aplicar_fila_usuario_no_encontrado(requests_mock):
    requests_mock.post('https://api.mypurecloud.com/api/v2/users/search', json={'results': []})

    with pytest.raises(ValueError, match='No se encontró un usuario'):
        m.aplicar_fila('token', 'api.mypurecloud.com', {'email_usuario': 'nadie@x.com', 'division_nueva': 'Ventas'})


def test_aplicar_fila_division_no_encontrada(requests_mock):
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1'}]},
    )
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/authorization/divisions',
        json={'entities': [{'id': 'd1', 'name': 'Ventas'}], 'pageCount': 1},
    )

    with pytest.raises(ValueError, match='división'):
        m.aplicar_fila('token', 'api.mypurecloud.com', {'email_usuario': 'a@x.com', 'division_nueva': 'No Existe'})


def test_main_sin_confirm_no_escribe_nada(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("email_usuario,division_nueva\na@x.com,Ventas\n", encoding='utf-8')

    monkeypatch.setenv('BULK_ARCHIVO_CSV', str(csv_path))
    monkeypatch.delenv('BULK_CONFIRM', raising=False)
    monkeypatch.setenv('GENESYS_REGION', '1')
    monkeypatch.setenv('GENESYS_CLIENT_ID', 'id')
    monkeypatch.setenv('GENESYS_CLIENT_SECRET', 'secret')

    requests_mock.post('https://login.mypurecloud.com/oauth/token', json={'access_token': 'tok'})
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1'}]},
    )
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/authorization/divisions',
        json={'entities': [{'id': 'd1', 'name': 'Ventas'}], 'pageCount': 1},
    )
    patch_mock = requests_mock.patch('https://api.mypurecloud.com/api/v2/users/u1', json={'id': 'u1'})

    m.main()

    assert patch_mock.called is False


def test_main_con_confirm_escribe(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("email_usuario,division_nueva\na@x.com,Ventas\n", encoding='utf-8')

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
        json={'results': [{'id': 'u1'}]},
    )
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/authorization/divisions',
        json={'entities': [{'id': 'd1', 'name': 'Ventas'}], 'pageCount': 1},
    )
    patch_mock = requests_mock.patch('https://api.mypurecloud.com/api/v2/users/u1', json={'id': 'u1'})

    m.main()

    assert patch_mock.last_request.json() == {'division': {'id': 'd1'}}
