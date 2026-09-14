import io

import pytest

from conftest import import_module_from_path

m = import_module_from_path('actualizar_script_cola', 'scripts/bulk_actualizar_script_cola/actualizar_script_cola.py')


def test_aplicar_fila_hace_read_modify_write_sobre_la_cola(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/queues',
        json={'entities': [{'id': 'q1', 'name': 'Soporte'}]},
    )
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/scripts',
        json={'entities': [{'id': 's1', 'name': 'Bienvenida'}]},
    )
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/queues/q1',
        json={
            'id': 'q1',
            'name': 'Soporte',
            'mediaSettings': {'call': {'alertingTimeoutSeconds': 30}},
            'defaultScripts': {'outboundNoAnswer': {'id': 'otro'}},
        },
    )
    put_mock = requests_mock.put('https://api.mypurecloud.com/api/v2/routing/queues/q1', json={'id': 'q1'})

    m.aplicar_fila('token', 'api.mypurecloud.com', {
        'cola': 'Soporte', 'tipo_script': 'inQueue', 'nombre_script': 'Bienvenida',
    })

    enviado = put_mock.last_request.json()
    # No debe perder configuración que no tiene que ver con los scripts:
    assert enviado['mediaSettings'] == {'call': {'alertingTimeoutSeconds': 30}}
    # Conserva el script de otro tipo que ya estaba asignado:
    assert enviado['defaultScripts']['outboundNoAnswer'] == {'id': 'otro'}
    # Agrega/actualiza el tipo pedido:
    assert enviado['defaultScripts']['inQueue'] == {'id': 's1'}


def test_aplicar_fila_cola_no_encontrada(requests_mock):
    requests_mock.get('https://api.mypurecloud.com/api/v2/routing/queues', json={'entities': []})

    with pytest.raises(ValueError, match='cola'):
        m.aplicar_fila('token', 'api.mypurecloud.com', {
            'cola': 'No Existe', 'tipo_script': 'inQueue', 'nombre_script': 'Bienvenida',
        })


def test_aplicar_fila_script_no_encontrado(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/queues',
        json={'entities': [{'id': 'q1', 'name': 'Soporte'}]},
    )
    requests_mock.get('https://api.mypurecloud.com/api/v2/scripts', json={'entities': []})

    with pytest.raises(ValueError, match='script'):
        m.aplicar_fila('token', 'api.mypurecloud.com', {
            'cola': 'Soporte', 'tipo_script': 'inQueue', 'nombre_script': 'No Existe',
        })


def test_main_sin_confirm_no_escribe_nada(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("cola,tipo_script,nombre_script\nSoporte,inQueue,Bienvenida\n", encoding='utf-8')

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
    requests_mock.get('https://api.mypurecloud.com/api/v2/scripts', json={'entities': [{'id': 's1', 'name': 'Bienvenida'}]})
    put_mock = requests_mock.put('https://api.mypurecloud.com/api/v2/routing/queues/q1', json={'id': 'q1'})

    m.main()

    assert put_mock.called is False


def test_main_con_confirm_escribe(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("cola,tipo_script,nombre_script\nSoporte,inQueue,Bienvenida\n", encoding='utf-8')

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
    requests_mock.get('https://api.mypurecloud.com/api/v2/scripts', json={'entities': [{'id': 's1', 'name': 'Bienvenida'}]})
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/queues/q1',
        json={'id': 'q1', 'defaultScripts': {}},
    )
    put_mock = requests_mock.put('https://api.mypurecloud.com/api/v2/routing/queues/q1', json={'id': 'q1'})

    m.main()

    assert put_mock.last_request.json()['defaultScripts']['inQueue'] == {'id': 's1'}
