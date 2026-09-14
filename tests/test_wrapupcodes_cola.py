import io

import pytest

from conftest import import_module_from_path

m = import_module_from_path('wrapupcodes_cola', 'scripts/bulk_wrapupcodes_cola/wrapupcodes_cola.py')


def test_validar_filas_rechaza_accion_no_permitida():
    with pytest.raises(ValueError, match='no permitida'):
        m.validar_filas([{'cola': 'Soporte', 'wrapup_code': 'Resuelto', 'accion': 'borrar'}])


def test_aplicar_fila_agregar(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/queues',
        json={'entities': [{'id': 'q1', 'name': 'Soporte'}]},
    )
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/wrapupcodes',
        json={'entities': [{'id': 'w1', 'name': 'Resuelto'}]},
    )
    post_mock = requests_mock.post(
        'https://api.mypurecloud.com/api/v2/routing/queues/q1/wrapupcodes',
        json=[{'id': 'w1'}],
    )

    m.aplicar_fila('token', 'api.mypurecloud.com', {'cola': 'Soporte', 'wrapup_code': 'Resuelto', 'accion': 'agregar'})

    assert post_mock.last_request.json() == [{'id': 'w1'}]


def test_aplicar_fila_quitar(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/queues',
        json={'entities': [{'id': 'q1', 'name': 'Soporte'}]},
    )
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/wrapupcodes',
        json={'entities': [{'id': 'w1', 'name': 'Resuelto'}]},
    )
    delete_mock = requests_mock.delete('https://api.mypurecloud.com/api/v2/routing/queues/q1/wrapupcodes/w1')

    m.aplicar_fila('token', 'api.mypurecloud.com', {'cola': 'Soporte', 'wrapup_code': 'Resuelto', 'accion': 'quitar'})

    assert delete_mock.called_once


def test_aplicar_fila_wrapupcode_no_encontrado(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/queues',
        json={'entities': [{'id': 'q1', 'name': 'Soporte'}]},
    )
    requests_mock.get('https://api.mypurecloud.com/api/v2/routing/wrapupcodes', json={'entities': []})

    with pytest.raises(ValueError, match='wrap-up code'):
        m.aplicar_fila('token', 'api.mypurecloud.com', {'cola': 'Soporte', 'wrapup_code': 'No Existe', 'accion': 'agregar'})


def test_main_sin_confirm_no_escribe_nada(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("cola,wrapup_code,accion\nSoporte,Resuelto,agregar\n", encoding='utf-8')

    monkeypatch.setenv('BULK_ARCHIVO_CSV', str(csv_path))
    monkeypatch.delenv('BULK_CONFIRM', raising=False)
    monkeypatch.setenv('GENESYS_REGION', '1')
    monkeypatch.setenv('GENESYS_CLIENT_ID', 'id')
    monkeypatch.setenv('GENESYS_CLIENT_SECRET', 'secret')

    requests_mock.post('https://login.mypurecloud.com/oauth/token', json={'access_token': 'tok'})
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/queues',
        json={'entities': [{'id': 'q1', 'name': 'Soporte'}]},
    )
    requests_mock.get('https://api.mypurecloud.com/api/v2/routing/wrapupcodes', json={'entities': [{'id': 'w1', 'name': 'Resuelto'}]})
    post_mock = requests_mock.post('https://api.mypurecloud.com/api/v2/routing/queues/q1/wrapupcodes', json=[])

    m.main()

    assert post_mock.called is False


def test_main_con_confirm_escribe(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("cola,wrapup_code,accion\nSoporte,Resuelto,agregar\n", encoding='utf-8')

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
        'https://api.mypurecloud.com/api/v2/routing/queues',
        json={'entities': [{'id': 'q1', 'name': 'Soporte'}]},
    )
    requests_mock.get('https://api.mypurecloud.com/api/v2/routing/wrapupcodes', json={'entities': [{'id': 'w1', 'name': 'Resuelto'}]})
    requests_mock.get('https://api.mypurecloud.com/api/v2/routing/queues/q1/wrapupcodes', json={'entities': []})
    post_mock = requests_mock.post('https://api.mypurecloud.com/api/v2/routing/queues/q1/wrapupcodes', json=[])

    m.main()

    assert post_mock.last_request.json() == [{'id': 'w1'}]
