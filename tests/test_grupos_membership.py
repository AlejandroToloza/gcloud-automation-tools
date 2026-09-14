import io

import pytest

from conftest import import_module_from_path

m = import_module_from_path('grupos_membership', 'scripts/bulk_grupos_membership/grupos_membership.py')


def test_validar_filas_rechaza_accion_no_permitida():
    with pytest.raises(ValueError, match='no permitida'):
        m.validar_filas([{'email_usuario': 'a@x.com', 'grupo': 'Ventas', 'accion': 'mover'}])


def test_aplicar_fila_agregar_usa_version_del_grupo(requests_mock):
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1', 'email': 'a@x.com'}]},
    )
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/groups/search',
        json={'results': [{'id': 'g1', 'name': 'Ventas', 'version': 4}]},
    )
    post_mock = requests_mock.post('https://api.mypurecloud.com/api/v2/groups/g1/members', json={})

    m.aplicar_fila('token', 'api.mypurecloud.com', {'email_usuario': 'a@x.com', 'grupo': 'Ventas', 'accion': 'agregar'})

    assert post_mock.last_request.json() == {'memberIds': ['u1'], 'version': 4}


def test_aplicar_fila_quitar(requests_mock):
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1', 'email': 'a@x.com'}]},
    )
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/groups/search',
        json={'results': [{'id': 'g1', 'name': 'Ventas', 'version': 4}]},
    )
    delete_mock = requests_mock.delete('https://api.mypurecloud.com/api/v2/groups/g1/members')

    m.aplicar_fila('token', 'api.mypurecloud.com', {'email_usuario': 'a@x.com', 'grupo': 'Ventas', 'accion': 'quitar'})

    assert delete_mock.called_once
    assert delete_mock.last_request.qs == {'ids': ['u1']}


def test_aplicar_fila_grupo_no_encontrado(requests_mock):
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1'}]},
    )
    requests_mock.post('https://api.mypurecloud.com/api/v2/groups/search', json={'results': []})

    with pytest.raises(ValueError, match='grupo'):
        m.aplicar_fila('token', 'api.mypurecloud.com', {'email_usuario': 'a@x.com', 'grupo': 'No Existe', 'accion': 'agregar'})


def test_main_sin_confirm_no_escribe_nada(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("email_usuario,grupo,accion\na@x.com,Ventas,agregar\n", encoding='utf-8')

    monkeypatch.setenv('BULK_ARCHIVO_CSV', str(csv_path))
    monkeypatch.delenv('BULK_CONFIRM', raising=False)
    monkeypatch.setenv('GENESYS_REGION', '1')
    monkeypatch.setenv('GENESYS_CLIENT_ID', 'id')
    monkeypatch.setenv('GENESYS_CLIENT_SECRET', 'secret')

    requests_mock.post('https://login.mypurecloud.com/oauth/token', json={'access_token': 'tok'})
    requests_mock.post('https://api.mypurecloud.com/api/v2/users/search', json={'results': [{'id': 'u1'}]})
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/groups/search',
        json={'results': [{'id': 'g1', 'name': 'Ventas', 'version': 1}]},
    )
    post_mock = requests_mock.post('https://api.mypurecloud.com/api/v2/groups/g1/members', json={})

    m.main()

    assert post_mock.called is False


def test_main_con_confirm_escribe(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("email_usuario,grupo,accion\na@x.com,Ventas,agregar\n", encoding='utf-8')

    monkeypatch.setenv('BULK_ARCHIVO_CSV', str(csv_path))
    monkeypatch.setenv('BULK_CONFIRM', '1')
    monkeypatch.setenv('GENESYS_REGION', '1')
    monkeypatch.setenv('GENESYS_CLIENT_ID', 'id')
    monkeypatch.setenv('GENESYS_CLIENT_SECRET', 'secret')
    monkeypatch.setattr(m.sys, 'stdin', io.StringIO())

    expanduser_real = m.os.path.expanduser
    monkeypatch.setattr(m.os.path, 'expanduser', lambda p: str(tmp_path) if p == '~' else expanduser_real(p))

    requests_mock.post('https://login.mypurecloud.com/oauth/token', json={'access_token': 'tok'})
    requests_mock.post('https://api.mypurecloud.com/api/v2/users/search', json={'results': [{'id': 'u1', 'email': 'a@x.com'}]})
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/groups/search',
        json={'results': [{'id': 'g1', 'name': 'Ventas', 'version': 1}]},
    )
    requests_mock.get('https://api.mypurecloud.com/api/v2/groups/g1/members', json={'entities': []})
    post_mock = requests_mock.post('https://api.mypurecloud.com/api/v2/groups/g1/members', json={})

    m.main()

    assert post_mock.last_request.json() == {'memberIds': ['u1'], 'version': 1}
