from conftest import import_module_from_path

m = import_module_from_path('export_all_users', 'scripts/export_all_users/export_all_users.py')


def test_obtener_usuarios_pagina_hasta_pagecount(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/users',
        [
            {
                'json': {
                    'entities': [{'id': '1', 'name': 'Ana', 'email': 'ana@x.com'}],
                    'pageCount': 2,
                },
                'status_code': 200,
            },
            {
                'json': {
                    'entities': [{'id': '2', 'name': 'Bob', 'email': 'bob@x.com'}],
                    'pageCount': 2,
                },
                'status_code': 200,
            },
        ],
    )

    usuarios = m.obtener_usuarios('token', 'api.mypurecloud.com', 'active')

    assert [u['ID'] for u in usuarios] == ['1', '2']
    assert all(u['Estado'] == 'Activo' for u in usuarios)
    assert requests_mock.call_count == 2


def test_obtener_usuarios_inactivos_marca_estado(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/users',
        json={'entities': [{'id': '1', 'name': 'Ana', 'email': 'ana@x.com'}], 'pageCount': 1},
    )

    usuarios = m.obtener_usuarios('token', 'api.mypurecloud.com', 'inactive')

    assert usuarios[0]['Estado'] == 'Inactivo'


def test_obtener_usuarios_detiene_en_error(requests_mock):
    requests_mock.get('https://api.mypurecloud.com/api/v2/users', status_code=500)

    usuarios = m.obtener_usuarios('token', 'api.mypurecloud.com', 'active')

    assert usuarios == []
