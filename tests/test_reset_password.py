import io
import string

import pytest

from conftest import import_module_from_path

m = import_module_from_path('reset_password', 'scripts/bulk_reset_password/reset_password.py')


def test_generar_password_temporal_cumple_complejidad():
    password = m.generar_password_temporal()

    assert len(password) == 16
    assert any(c in string.ascii_uppercase for c in password)
    assert any(c in string.ascii_lowercase for c in password)
    assert any(c in string.digits for c in password)
    assert any(c in '!@#$%^&*-_=+' for c in password)


def test_generar_password_temporal_no_se_repite():
    passwords = {m.generar_password_temporal() for _ in range(20)}
    assert len(passwords) == 20  # prácticamente imposible que choquen si es aleatorio real


def test_aplicar_fila_envia_password_nueva(requests_mock):
    requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/search',
        json={'results': [{'id': 'u1', 'email': 'a@x.com'}]},
    )
    password_mock = requests_mock.post(
        'https://api.mypurecloud.com/api/v2/users/u1/password',
        json={},
    )

    m.aplicar_fila('token', 'api.mypurecloud.com', {'email_usuario': 'a@x.com'})

    assert password_mock.called_once
    enviado = password_mock.last_request.json()
    assert set(enviado.keys()) == {'newPassword'}
    assert len(enviado['newPassword']) == 16


def test_aplicar_fila_usuario_no_encontrado(requests_mock):
    requests_mock.post('https://api.mypurecloud.com/api/v2/users/search', json={'results': []})

    with pytest.raises(ValueError, match='No se encontró'):
        m.aplicar_fila('token', 'api.mypurecloud.com', {'email_usuario': 'nadie@x.com'})


def test_main_con_confirm_no_guarda_password_en_el_log(tmp_path, monkeypatch, requests_mock):
    csv_path = tmp_path / 'cambios.csv'
    csv_path.write_text("email_usuario\na@x.com\n", encoding='utf-8')

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
        json={'results': [{'id': 'u1', 'email': 'a@x.com'}]},
    )
    password_mock = requests_mock.post('https://api.mypurecloud.com/api/v2/users/u1/password', json={})

    m.main()

    assert password_mock.called_once
    password_enviada = password_mock.last_request.json()['newPassword']

    import glob
    archivos_log = glob.glob(str(tmp_path / '**' / 'log_reset_password_*.xlsx'), recursive=True)
    assert len(archivos_log) == 1

    import pandas as pd
    df = pd.read_excel(archivos_log[0])
    contenido = df.to_csv(index=False)
    assert password_enviada not in contenido
    assert 'newPassword' not in contenido
