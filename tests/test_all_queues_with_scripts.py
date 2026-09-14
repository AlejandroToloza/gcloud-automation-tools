from conftest import import_module_from_path

m = import_module_from_path('All_queues_with_scripts', 'scripts/colas_tipo_y_script/All_queues_with_scripts.py')


def test_obtener_colas_sigue_nexturi(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/queues',
        [
            {
                'json': {
                    'entities': [{'id': '1', 'name': 'Cola A'}],
                    'nextUri': '/api/v2/routing/queues?pageSize=100&pageNumber=2',
                },
                'status_code': 200,
            },
            {
                'json': {'entities': [{'id': '2', 'name': 'Cola B'}]},
                'status_code': 200,
            },
        ],
    )

    colas = m.obtener_colas('token', 'api.mypurecloud.com')

    assert [c['id'] for c in colas] == ['1', '2']
    assert requests_mock.call_count == 2


def test_obtener_nombre_script_no_encontrado(requests_mock):
    requests_mock.get('https://api.mypurecloud.com/api/v2/scripts/abc', status_code=404)

    nombre = m.obtener_nombre_script('token', 'api.mypurecloud.com', 'abc')

    assert nombre == 'Script no encontrado'


def test_obtener_nombre_script_exitoso(requests_mock):
    requests_mock.get('https://api.mypurecloud.com/api/v2/scripts/abc', json={'name': 'Bienvenida'})

    nombre = m.obtener_nombre_script('token', 'api.mypurecloud.com', 'abc')

    assert nombre == 'Bienvenida'


def test_obtener_scripts_de_cola(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/queues/q1',
        json={'defaultScripts': {'inQueue': {'id': 'scr1'}, 'outboundNoAnswer': {}}},
    )
    requests_mock.get('https://api.mypurecloud.com/api/v2/scripts/scr1', json={'name': 'Bienvenida'})

    scripts = m.obtener_scripts_de_cola('token', 'api.mypurecloud.com', 'q1')

    por_tipo = {s['Tipo de Script']: s for s in scripts}
    assert por_tipo['inQueue']['Nombre del Script'] == 'Bienvenida'
    assert por_tipo['outboundNoAnswer']['ID de Script'] == 'No asignado'
