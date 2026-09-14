import io

import pytest

from conftest import import_module_from_path

m = import_module_from_path('actualizar_usuarios', 'scripts/bulk_actualizar_usuarios/actualizar_usuarios.py')


def test_validar_filas_acepta_campos_permitidos():
    m.validar_filas([
        {'email_usuario': 'a@x.com', 'campo': 'department', 'valor_nuevo': 'Ventas'},
        {'email_usuario': 'b@x.com', 'campo': 'title', 'valor_nuevo': 'Supervisor'},
    ])  # no debe lanzar


def test_validar_filas_rechaza_campo_no_permitido():
    with pytest.raises(ValueError, match='no permitido'):
        m.validar_filas([{'email_usuario': 'a@x.com', 'campo': 'email', 'valor_nuevo': 'x@x.com'}])


def test_aplicar_fila_resuelve_email_y_hace_patch(requests_mock):
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1', 'email': 'a@x.com', 'department': 'Soporte'}]},
    )
    patch_mock = requests_mock.patch('https://api.mypurecloud.com/api/v2/users/u1', json={'id': 'u1'})

    m.aplicar_fila('token', 'api.mypurecloud.com', {
        'email_usuario': 'a@x.com', 'campo': 'department', 'valor_nuevo': 'Ventas',
    })

    assert patch_mock.called_once
    assert patch_mock.last_request.json() == {'department': 'Ventas'}


def test_aplicar_fila_usuario_no_encontrado(requests_mock):
    requests_mock.post('https://api.mypurecloud.com/api/v2/users/search', json={'results': []})

    with pytest.raises(ValueError, match='No se encontró'):
        m.aplicar_fila('token', 'api.mypurecloud.com', {
            'email_usuario': 'nadie@x.com', 'campo': 'department', 'valor_nuevo': 'Ventas',
        })


def test_obtener_estado_actual_trae_valor_previo(requests_mock):
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1', 'department': 'Soporte'}]},
    )

    estado = m.obtener_estado_actual('token', 'api.mypurecloud.com', [
        {'email_usuario': 'a@x.com', 'campo': 'department', 'valor_nuevo': 'Ventas'},
    ])

    assert estado == [{
        'email_usuario': 'a@x.com',
        'campo': 'department',
        'valor_actual': 'Soporte',
        'valor_nuevo_propuesto': 'Ventas',
    }]


def test_main_sin_confirm_no_escribe_nada(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("email_usuario,campo,valor_nuevo\na@x.com,department,Ventas\n", encoding='utf-8')

    monkeypatch.setenv('BULK_ARCHIVO_CSV', str(csv_path))
    monkeypatch.delenv('BULK_CONFIRM', raising=False)
    monkeypatch.setenv('GENESYS_REGION', '1')
    monkeypatch.setenv('GENESYS_CLIENT_ID', 'id')
    monkeypatch.setenv('GENESYS_CLIENT_SECRET', 'secret')

    requests_mock.post('https://login.mypurecloud.com/oauth/token', json={'access_token': 'tok'})
    patch_mock = requests_mock.patch('https://api.mypurecloud.com/api/v2/users/u1', json={'id': 'u1'})
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1', 'department': 'Soporte'}]},
    )

    m.main()

    assert patch_mock.called is False


def test_main_con_confirm_escribe(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("email_usuario,campo,valor_nuevo\na@x.com,department,Ventas\n", encoding='utf-8')

    monkeypatch.setenv('BULK_ARCHIVO_CSV', str(csv_path))
    monkeypatch.setenv('BULK_CONFIRM', '1')
    monkeypatch.setenv('GENESYS_REGION', '1')
    monkeypatch.setenv('GENESYS_CLIENT_ID', 'id')
    monkeypatch.setenv('GENESYS_CLIENT_SECRET', 'secret')
    monkeypatch.setattr(m.sys, 'stdin', io.StringIO())

    expanduser_real = m.os.path.expanduser
    monkeypatch.setattr(m.os.path, 'expanduser', lambda p: str(tmp_path) if p == '~' else expanduser_real(p))

    requests_mock.post('https://login.mypurecloud.com/oauth/token', json={'access_token': 'tok'})
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1', 'department': 'Soporte'}]},
    )
    patch_mock = requests_mock.patch('https://api.mypurecloud.com/api/v2/users/u1', json={'id': 'u1'})

    m.main()

    assert patch_mock.called_once
    assert patch_mock.last_request.json() == {'department': 'Ventas'}
