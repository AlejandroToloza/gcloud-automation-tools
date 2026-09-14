import os

import pandas as pd
import pytest
import requests

from conftest import import_module_from_path

genesys_client = import_module_from_path('genesys_client', 'scripts/common/genesys_client.py')


def test_obtener_token_exitoso(requests_mock):
    requests_mock.post(
        'https://login.mypurecloud.com/oauth/token',
        json={'access_token': 'abc123'},
        status_code=200,
    )
    token = genesys_client.obtener_token('id', 'secret', 'login.mypurecloud.com')
    assert token == 'abc123'


def test_obtener_token_credenciales_invalidas(requests_mock):
    requests_mock.post(
        'https://login.mypurecloud.com/oauth/token',
        status_code=401,
        json={'message': 'invalid_client'},
    )
    token = genesys_client.obtener_token('id', 'secret', 'login.mypurecloud.com')
    assert token is None


def test_solicitar_api_reintenta_en_rate_limit(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/queues',
        [
            {'status_code': 429, 'headers': {'Retry-After': '0'}},
            {'json': {'entities': [{'id': '1'}]}, 'status_code': 200},
        ],
    )
    data = genesys_client.solicitar_api('token', 'api.mypurecloud.com', '/api/v2/routing/queues')
    assert data == {'entities': [{'id': '1'}]}
    assert requests_mock.call_count == 2


def test_obtener_divisiones_pagina_hasta_pagecount(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/authorization/divisions',
        [
            {'json': {'entities': [{'id': 'd1', 'name': 'Home'}], 'pageCount': 2}, 'status_code': 200},
            {'json': {'entities': [{'id': 'd2', 'name': 'Ventas'}], 'pageCount': 2}, 'status_code': 200},
        ],
    )

    divisiones = genesys_client.obtener_divisiones('token', 'api.mypurecloud.com')

    assert [d['id'] for d in divisiones] == ['d1', 'd2']


def test_buscar_division_por_nombre_encuentra_sin_distinguir_mayusculas(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/authorization/divisions',
        json={'entities': [{'id': 'd1', 'name': 'Ventas'}], 'pageCount': 1},
    )

    division = genesys_client.buscar_division_por_nombre('token', 'api.mypurecloud.com', 'ventas')

    assert division == {'id': 'd1', 'name': 'Ventas'}


def test_buscar_division_por_nombre_sin_coincidencia(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/authorization/divisions',
        json={'entities': [{'id': 'd1', 'name': 'Ventas'}], 'pageCount': 1},
    )

    division = genesys_client.buscar_division_por_nombre('token', 'api.mypurecloud.com', 'No Existe')

    assert division is None


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

    colas = genesys_client.obtener_colas('token', 'api.mypurecloud.com')

    assert [c['id'] for c in colas] == ['1', '2']
    assert requests_mock.call_count == 2


def test_obtener_colas_detiene_en_error(requests_mock):
    requests_mock.get('https://api.mypurecloud.com/api/v2/routing/queues', status_code=500)

    colas = genesys_client.obtener_colas('token', 'api.mypurecloud.com')

    assert colas == []


def test_solicitar_api_propaga_error_http(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/users/x',
        status_code=404,
        json={'message': 'not found'},
    )
    with pytest.raises(requests.exceptions.HTTPError):
        genesys_client.solicitar_api('token', 'api.mypurecloud.com', '/api/v2/users/x')


def test_guardar_excel_usa_region_y_prefijo(tmp_path, monkeypatch):
    expanduser_real = genesys_client.os.path.expanduser
    monkeypatch.setattr(
        genesys_client.os.path,
        'expanduser',
        lambda p: str(tmp_path) if p == '~' else expanduser_real(p),
    )
    df = pd.DataFrame([{'a': 1}])

    ruta = genesys_client.guardar_excel(df, 'prefijo', 'Estados Unidos (Este)')

    assert ruta.startswith(str(tmp_path))
    nombre_archivo = os.path.basename(ruta)
    assert nombre_archivo.startswith('prefijo_estados_unidos_este_')
    assert nombre_archivo.endswith('.xlsx')
    assert os.path.isfile(ruta)


def test_solicitar_credenciales_desde_variables_de_entorno(monkeypatch):
    monkeypatch.setenv('GENESYS_CLIENT_ID', 'env-id')
    monkeypatch.setenv('GENESYS_CLIENT_SECRET', 'env-secret')

    client_id, client_secret = genesys_client.solicitar_credenciales()

    assert (client_id, client_secret) == ('env-id', 'env-secret')


def test_solicitar_credenciales_pide_por_consola_si_no_hay_env(monkeypatch):
    monkeypatch.delenv('GENESYS_CLIENT_ID', raising=False)
    monkeypatch.delenv('GENESYS_CLIENT_SECRET', raising=False)
    monkeypatch.setattr('builtins.input', lambda _: 'typed-id')
    monkeypatch.setattr(genesys_client, 'getpass', lambda _: 'typed-secret')

    client_id, client_secret = genesys_client.solicitar_credenciales()

    assert (client_id, client_secret) == ('typed-id', 'typed-secret')


def test_seleccionar_region_desde_variable_de_entorno(monkeypatch):
    monkeypatch.setenv('GENESYS_REGION', '2')

    def input_no_debe_llamarse(_):
        raise AssertionError('no debería pedir input cuando GENESYS_REGION es válida')

    monkeypatch.setattr('builtins.input', input_no_debe_llamarse)

    login_domain, api_domain, descripcion = genesys_client.seleccionar_region()

    assert (login_domain, api_domain) == ('login.usw2.pure.cloud', 'api.usw2.pure.cloud')
    assert descripcion == 'Estados Unidos (Oeste)'


def test_seleccionar_region_invalida_cae_a_consola(monkeypatch):
    monkeypatch.setenv('GENESYS_REGION', '99')
    monkeypatch.setattr('builtins.input', lambda _: '3')

    login_domain, api_domain, descripcion = genesys_client.seleccionar_region()

    assert descripcion == 'Américas (Canadá)'
    assert (login_domain, api_domain) == ('login.cac1.pure.cloud', 'api.cac1.pure.cloud')


def test_seleccionar_region_pide_por_consola_si_no_hay_env(monkeypatch):
    monkeypatch.delenv('GENESYS_REGION', raising=False)
    monkeypatch.setattr('builtins.input', lambda _: '1')

    login_domain, api_domain, descripcion = genesys_client.seleccionar_region()

    assert descripcion == 'Estados Unidos (Este)'
    assert (login_domain, api_domain) == ('login.mypurecloud.com', 'api.mypurecloud.com')
