import os

import pandas as pd
import pytest

from conftest import import_module_from_path

bulk_ops = import_module_from_path('bulk_ops', 'scripts/common/bulk_ops.py')


def escribir_csv(tmp_path, contenido):
    ruta = tmp_path / 'datos.csv'
    ruta.write_text(contenido, encoding='utf-8')
    return str(ruta)


def test_leer_filas_csv_ok(tmp_path):
    ruta = escribir_csv(tmp_path, "email_usuario,campo,valor_nuevo\na@x.com,department,Ventas\n")

    filas = bulk_ops.leer_filas_csv(ruta, ['email_usuario', 'campo', 'valor_nuevo'])

    assert filas == [{'email_usuario': 'a@x.com', 'campo': 'department', 'valor_nuevo': 'Ventas'}]


def test_leer_filas_csv_columnas_faltantes(tmp_path):
    ruta = escribir_csv(tmp_path, "email_usuario,campo\na@x.com,department\n")

    with pytest.raises(ValueError, match='valor_nuevo'):
        bulk_ops.leer_filas_csv(ruta, ['email_usuario', 'campo', 'valor_nuevo'])


def test_leer_filas_csv_sin_filas(tmp_path):
    ruta = escribir_csv(tmp_path, "email_usuario,campo,valor_nuevo\n")

    with pytest.raises(ValueError, match='no tiene filas'):
        bulk_ops.leer_filas_csv(ruta, ['email_usuario', 'campo', 'valor_nuevo'])


def test_leer_filas_csv_archivo_inexistente():
    with pytest.raises(FileNotFoundError):
        bulk_ops.leer_filas_csv('no/existe.csv', ['email_usuario'])


def test_confirmar_ejecucion_auto_confirmar_no_pregunta(monkeypatch):
    def input_no_debe_llamarse(_):
        raise AssertionError('no debería pedir input con auto_confirmar=True')

    monkeypatch.setattr('builtins.input', input_no_debe_llamarse)

    assert bulk_ops.confirmar_ejecucion(5, auto_confirmar=True) is True


def test_confirmar_ejecucion_acepta_solo_si_exacto(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'si')  # minúscula: no cuenta
    assert bulk_ops.confirmar_ejecucion(3, auto_confirmar=False) is False

    monkeypatch.setattr('builtins.input', lambda _: 'SI')
    assert bulk_ops.confirmar_ejecucion(3, auto_confirmar=False) is True


def test_ejecutar_bulk_un_error_no_aborta_el_lote():
    filas = [{'id': 1}, {'id': 2}, {'id': 3}]

    def funcion(fila):
        if fila['id'] == 2:
            raise ValueError('boom')

    resultados = bulk_ops.ejecutar_bulk(filas, funcion)

    assert [r['estado'] for r in resultados] == ['ok', 'error', 'ok']
    assert resultados[1]['detalle'] == 'boom'


def test_guardar_log_auditoria_incluye_estado_y_detalle(tmp_path, monkeypatch):
    expanduser_real = bulk_ops.os.path.expanduser
    monkeypatch.setattr(
        bulk_ops.os.path,
        'expanduser',
        lambda p: str(tmp_path) if p == '~' else expanduser_real(p),
    )
    resultados = [
        {'fila': {'email_usuario': 'a@x.com'}, 'estado': 'ok', 'detalle': ''},
        {'fila': {'email_usuario': 'b@x.com'}, 'estado': 'error', 'detalle': 'no encontrado'},
    ]

    ruta = bulk_ops.guardar_log_auditoria('actualizar_usuarios', resultados, 'Estados Unidos (Este)')

    df = pd.read_excel(ruta)
    assert list(df['_estado']) == ['ok', 'error']
    assert list(df['_detalle'].fillna('')) == ['', 'no encontrado']


def test_hacer_backup_previo_guarda_lo_que_devuelve_fetch(tmp_path, monkeypatch):
    expanduser_real = bulk_ops.os.path.expanduser
    monkeypatch.setattr(
        bulk_ops.os.path,
        'expanduser',
        lambda p: str(tmp_path) if p == '~' else expanduser_real(p),
    )

    ruta = bulk_ops.hacer_backup_previo(
        'actualizar_usuarios',
        lambda: [{'email_usuario': 'a@x.com', 'valor_actual': 'Ventas'}],
        'Estados Unidos (Este)',
    )

    df = pd.read_excel(ruta)
    assert df.iloc[0]['valor_actual'] == 'Ventas'
