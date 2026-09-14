from conftest import import_module_from_path

m = import_module_from_path('miembros_por_cola', 'scripts/miembros_por_cola/miembros_por_cola.py')


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
            {'json': {'entities': [{'id': '2', 'name': 'Cola B'}]}, 'status_code': 200},
        ],
    )

    colas = m.obtener_colas('token', 'api.mypurecloud.com')

    assert [c['id'] for c in colas] == ['1', '2']


def test_obtener_miembros_de_cola_pagina_hasta_pagecount(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/queues/q1/members',
        [
            {
                'json': {
                    'entities': [{'user': {'id': 'u1', 'name': 'Ana'}, 'joined': True, 'ringNumber': 1}],
                    'pageCount': 2,
                },
                'status_code': 200,
            },
            {
                'json': {
                    'entities': [{'user': {'id': 'u2', 'name': 'Bob'}, 'joined': False, 'ringNumber': 2}],
                    'pageCount': 2,
                },
                'status_code': 200,
            },
        ],
    )

    miembros = m.obtener_miembros_de_cola('token', 'api.mypurecloud.com', 'q1')

    assert [mi['user']['id'] for mi in miembros] == ['u1', 'u2']
    assert requests_mock.call_count == 2


def test_obtener_miembros_de_cola_sin_miembros(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/queues/q1/members',
        json={'entities': [], 'pageCount': 1},
    )

    miembros = m.obtener_miembros_de_cola('token', 'api.mypurecloud.com', 'q1')

    assert miembros == []
