import io

import pytest

from conftest import import_module_from_path

m = import_module_from_path('migrar_rol', 'scripts/bulk_migrar_rol/migrar_rol.py')


def test_expandir_migraciones_una_fila_por_usuario_afectado(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/authorization/roles',
        json={'entities': [
            {'id': 'r_old', 'name': 'Agente Junior'},
            {'id': 'r_new', 'name': 'Agente Senior'},
        ], 'pageCount': 1},
    )
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/authorization/roles/r_old/users',
        json={'entities': [{'id': 'u1'}, {'id': 'u2'}], 'pageCount': 1},
    )
    requests_mock.get('https://api.mypurecloud.com/api/v2/users/u1', json={'id': 'u1', 'email': 'a@x.com'})
    requests_mock.get('https://api.mypurecloud.com/api/v2/users/u2', json={'id': 'u2', 'email': 'b@x.com'})

    filas = m.expandir_migraciones('token', 'api.mypurecloud.com', [
        {'rol_origen': 'Agente Junior', 'rol_destino': 'Agente Senior'},
    ])

    assert [f['email_usuario'] for f in filas] == ['a@x.com', 'b@x.com']
    assert all(f['rol_origen_id'] == 'r_old' and f['rol_destino_id'] == 'r_new' for f in filas)


def test_expandir_migraciones_rol_origen_no_encontrado(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/authorization/roles',
        json={'entities': [], 'pageCount': 1},
    )

    with pytest.raises(ValueError, match='rol'):
        m.expandir_migraciones('token', 'api.mypurecloud.com', [
            {'rol_origen': 'No Existe', 'rol_destino': 'Agente Senior'},
        ])


def test_aplicar_fila_agrega_nuevo_antes_de_quitar_viejo(requests_mock):
    add_mock = requests_mock.put('https://api.mypurecloud.com/api/v2/authorization/roles/r_new/users/add', json=['u1'])
    remove_mock = requests_mock.put(
        'https://api.mypurecloud.com/api/v2/authorization/roles/r_old/users/remove', json=['u1'],
    )

    m.aplicar_fila('token', 'api.mypurecloud.com', {
        'user_id': 'u1', 'rol_origen_id': 'r_old', 'rol_destino_id': 'r_new',
    })

    assert add_mock.called_once
    assert remove_mock.called_once
    assert add_mock.last_request.json() == ['u1']
    assert remove_mock.last_request.json() == ['u1']


def test_main_sin_confirm_no_escribe_nada(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("rol_origen,rol_destino\nAgente Junior,Agente Senior\n", encoding='utf-8')

    monkeypatch.setenv('BULK_ARCHIVO_CSV', str(csv_path))
    monkeypatch.delenv('BULK_CONFIRM', raising=False)
    monkeypatch.setenv('GENESYS_REGION', '1')
    monkeypatch.setenv('GENESYS_CLIENT_ID', 'id')
    monkeypatch.setenv('GENESYS_CLIENT_SECRET', 'secret')

    requests_mock.post('https://login.mypurecloud.com/oauth/token', json={'access_token': 'tok'})
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/authorization/roles',
        json={'entities': [
            {'id': 'r_old', 'name': 'Agente Junior'},
            {'id': 'r_new', 'name': 'Agente Senior'},
        ], 'pageCount': 1},
    )
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/authorization/roles/r_old/users',
        json={'entities': [{'id': 'u1'}], 'pageCount': 1},
    )
    requests_mock.get('https://api.mypurecloud.com/api/v2/users/u1', json={'id': 'u1', 'email': 'a@x.com'})
    add_mock = requests_mock.put('https://api.mypurecloud.com/api/v2/authorization/roles/r_new/users/add', json=['u1'])

    m.main()

    assert add_mock.called is False


def test_main_con_confirm_escribe(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("rol_origen,rol_destino\nAgente Junior,Agente Senior\n", encoding='utf-8')

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
        'https://api.mypurecloud.com/api/v2/authorization/roles',
        json={'entities': [
            {'id': 'r_old', 'name': 'Agente Junior'},
            {'id': 'r_new', 'name': 'Agente Senior'},
        ], 'pageCount': 1},
    )
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/authorization/roles/r_old/users',
        json={'entities': [{'id': 'u1'}], 'pageCount': 1},
    )
    requests_mock.get('https://api.mypurecloud.com/api/v2/users/u1', json={'id': 'u1', 'email': 'a@x.com'})
    add_mock = requests_mock.put('https://api.mypurecloud.com/api/v2/authorization/roles/r_new/users/add', json=['u1'])
    remove_mock = requests_mock.put(
        'https://api.mypurecloud.com/api/v2/authorization/roles/r_old/users/remove', json=['u1'],
    )

    m.main()

    assert add_mock.called_once
    assert remove_mock.called_once
