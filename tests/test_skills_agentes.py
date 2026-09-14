import io

import pytest

from conftest import import_module_from_path

m = import_module_from_path('skills_agentes', 'scripts/bulk_skills_agentes/skills_agentes.py')


def test_validar_filas_rechaza_accion_no_permitida():
    with pytest.raises(ValueError, match='no permitida'):
        m.validar_filas([{'email_usuario': 'a@x.com', 'skill': 'Inglés', 'accion': 'mover'}])


def test_aplicar_fila_agregar_usa_proficiency_por_defecto(requests_mock):
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1', 'email': 'a@x.com'}]},
    )
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/skills',
        json={'entities': [{'id': 's1', 'name': 'Inglés'}]},
    )
    patch_mock = requests_mock.patch('https://api.mypurecloud.com/api/v2/users/u1/routingskills/bulk', json={})

    m.aplicar_fila('token', 'api.mypurecloud.com', {'email_usuario': 'a@x.com', 'skill': 'Inglés', 'accion': 'agregar'})

    assert patch_mock.last_request.json() == [{'id': 's1', 'proficiency': 1.0}]


def test_aplicar_fila_agregar_usa_proficiency_del_csv(requests_mock):
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1', 'email': 'a@x.com'}]},
    )
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/skills',
        json={'entities': [{'id': 's1', 'name': 'Inglés'}]},
    )
    patch_mock = requests_mock.patch('https://api.mypurecloud.com/api/v2/users/u1/routingskills/bulk', json={})

    m.aplicar_fila('token', 'api.mypurecloud.com', {
        'email_usuario': 'a@x.com', 'skill': 'Inglés', 'accion': 'agregar', 'proficiency': '3.5',
    })

    assert patch_mock.last_request.json() == [{'id': 's1', 'proficiency': 3.5}]


def test_aplicar_fila_quitar(requests_mock):
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1', 'email': 'a@x.com'}]},
    )
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/routing/skills',
        json={'entities': [{'id': 's1', 'name': 'Inglés'}]},
    )
    delete_mock = requests_mock.delete('https://api.mypurecloud.com/api/v2/users/u1/routingskills/s1')

    m.aplicar_fila('token', 'api.mypurecloud.com', {'email_usuario': 'a@x.com', 'skill': 'Inglés', 'accion': 'quitar'})

    assert delete_mock.called_once


def test_aplicar_fila_skill_no_encontrada(requests_mock):
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1'}]},
    )
    requests_mock.get('https://api.mypurecloud.com/api/v2/routing/skills', json={'entities': []})

    with pytest.raises(ValueError, match='skill'):
        m.aplicar_fila('token', 'api.mypurecloud.com', {'email_usuario': 'a@x.com', 'skill': 'No Existe', 'accion': 'agregar'})


def test_main_sin_confirm_no_escribe_nada(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("email_usuario,skill,accion\na@x.com,Inglés,agregar\n", encoding='utf-8')

    monkeypatch.setenv('BULK_ARCHIVO_CSV', str(csv_path))
    monkeypatch.delenv('BULK_CONFIRM', raising=False)
    monkeypatch.setenv('GENESYS_REGION', '1')
    monkeypatch.setenv('GENESYS_CLIENT_ID', 'id')
    monkeypatch.setenv('GENESYS_CLIENT_SECRET', 'secret')

    requests_mock.post('https://login.mypurecloud.com/oauth/token', json={'access_token': 'tok'})
    requests_mock.post('https://api.mypurecloud.com/api/v2/users/search', json={'results': [{'id': 'u1'}]})
    requests_mock.get('https://api.mypurecloud.com/api/v2/routing/skills', json={'entities': [{'id': 's1', 'name': 'Inglés'}]})
    patch_mock = requests_mock.patch('https://api.mypurecloud.com/api/v2/users/u1/routingskills/bulk', json={})

    m.main()

    assert patch_mock.called is False


def test_main_con_confirm_escribe(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("email_usuario,skill,accion\na@x.com,Inglés,agregar\n", encoding='utf-8')

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
    requests_mock.get('https://api.mypurecloud.com/api/v2/routing/skills', json={'entities': [{'id': 's1', 'name': 'Inglés'}]})
    requests_mock.get('https://api.mypurecloud.com/api/v2/users/u1/routingskills', json={'entities': []})
    patch_mock = requests_mock.patch('https://api.mypurecloud.com/api/v2/users/u1/routingskills/bulk', json={})

    m.main()

    assert patch_mock.last_request.json() == [{'id': 's1', 'proficiency': 1.0}]
