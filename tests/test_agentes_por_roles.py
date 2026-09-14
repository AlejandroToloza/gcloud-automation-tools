from conftest import import_module_from_path

m = import_module_from_path('agentes_por_roles', 'scripts/agentes_por_roles/agentes_por_roles.py')


def test_obtener_roles_pagina_hasta_pagecount(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/authorization/roles',
        [
            {'json': {'entities': [{'id': 'r1', 'name': 'Admin'}], 'pageCount': 2}, 'status_code': 200},
            {'json': {'entities': [{'id': 'r2', 'name': 'Agente'}], 'pageCount': 2}, 'status_code': 200},
        ],
    )

    roles = m.obtener_roles('token', 'api.mypurecloud.com')

    assert [r['id'] for r in roles] == ['r1', 'r2']
    assert requests_mock.call_count == 2


def test_obtener_usuarios_de_rol(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/authorization/roles/r1/users',
        json={'entities': [{'id': 'u1'}, {'id': 'u2'}], 'pageCount': 1},
    )

    ids = m.obtener_usuarios_de_rol('token', 'api.mypurecloud.com', 'r1')

    assert ids == ['u1', 'u2']


def test_procesar_rol_arma_asignaciones(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/authorization/roles/r1/users',
        json={'entities': [{'id': 'u1'}, {'id': 'u2'}], 'pageCount': 1},
    )

    asignaciones = m.procesar_rol('token', 'api.mypurecloud.com', {'id': 'r1', 'name': 'Admin'})

    assert asignaciones == [('r1', 'Admin', 'u1'), ('r1', 'Admin', 'u2')]


def test_procesar_rol_sin_id_devuelve_vacio():
    assert m.procesar_rol('token', 'api.mypurecloud.com', {'name': 'Sin ID'}) == []


def test_obtener_detalles_usuarios_deduplica_y_agrupa_en_lotes(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/users',
        json={'entities': [
            {'id': 'u1', 'name': 'Ana', 'email': 'ana@x.com'},
            {'id': 'u2', 'name': 'Bob', 'email': 'bob@x.com'},
        ]},
    )

    detalles = m.obtener_detalles_usuarios('token', 'api.mypurecloud.com', ['u1', 'u2', 'u1'])

    assert detalles['u1']['nombre'] == 'Ana'
    assert detalles['u2']['email'] == 'bob@x.com'
    assert requests_mock.call_count == 1
