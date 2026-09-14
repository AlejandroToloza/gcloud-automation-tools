"""Utilidades compartidas por los scripts de escritura en bulk (bulk-write)
sobre Genesys Cloud: lectura/validación de CSV, vista previa (dry-run),
confirmación explícita antes de escribir, ejecución fila por fila sin
abortar el lote ante un error, backup del estado previo, y log de
auditoría de lo que se aplicó."""
import csv
import os
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from genesys_client import guardar_excel


def leer_filas_csv(ruta, columnas_requeridas):
    """Lee un CSV como lista de dicts y valida que tenga las columnas requeridas."""
    if not os.path.isfile(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    with open(ruta, newline='', encoding='utf-8-sig') as f:
        lector = csv.DictReader(f)
        columnas_presentes = set(lector.fieldnames or [])
        faltantes = set(columnas_requeridas) - columnas_presentes
        if faltantes:
            raise ValueError(
                f"Al CSV le faltan columnas requeridas: {sorted(faltantes)}. "
                f"Columnas encontradas: {sorted(columnas_presentes)}"
            )
        filas = list(lector)

    if not filas:
        raise ValueError("El CSV no tiene filas de datos.")

    return filas


def mostrar_resumen(filas, formatear_fila):
    """Imprime una vista previa numerada de los cambios que se aplicarían."""
    print(f"\n📋 Vista previa: {len(filas)} cambio(s) a aplicar\n")
    for i, fila in enumerate(filas, start=1):
        print(f"  {i}. {formatear_fila(fila)}")
    print()


def confirmar_ejecucion(cantidad, auto_confirmar=False):
    """Pide confirmación explícita antes de escribir de verdad.
    auto_confirmar (--confirm / BULK_CONFIRM=1) salta el prompt interactivo,
    pensado para tareas programadas."""
    if auto_confirmar:
        print(f"🔓 Confirmación automática recibida: se aplicarán {cantidad} cambio(s).")
        return True

    respuesta = input(f"\n⚠️  Escriba SI para aplicar {cantidad} cambio(s) reales: ").strip()
    return respuesta == 'SI'


def ejecutar_bulk(filas, funcion_por_fila):
    """Aplica funcion_por_fila(fila) a cada fila. Si una fila falla, se
    registra el error y se sigue con las demás: un error no aborta el lote."""
    resultados = []
    for fila in filas:
        try:
            funcion_por_fila(fila)
            resultados.append({'fila': fila, 'estado': 'ok', 'detalle': ''})
        except Exception as e:
            resultados.append({'fila': fila, 'estado': 'error', 'detalle': str(e)})
    return resultados


def guardar_log_auditoria(nombre_operacion, resultados, region_nombre):
    """Guarda un Excel con el resultado fila por fila de una operación bulk
    (qué se intentó, si funcionó o no, y el detalle del error si lo hubo)."""
    filas_log = []
    for r in resultados:
        fila_log = dict(r['fila'])
        fila_log['_estado'] = r['estado']
        fila_log['_detalle'] = r['detalle']
        filas_log.append(fila_log)

    df = pd.DataFrame(filas_log)
    print(f"\n📝 Guardando log de auditoría ({len(resultados)} fila(s))...")
    return guardar_excel(df, f'log_{nombre_operacion}', region_nombre)


def hacer_backup_previo(nombre_operacion, funcion_fetch, region_nombre):
    """Guarda el estado 'antes' (lo que devuelva funcion_fetch, una lista de
    dicts) en un Excel, antes de aplicar ningún cambio real."""
    datos = funcion_fetch()
    df = pd.DataFrame(datos)
    print("\n💾 Guardando backup del estado actual antes de escribir...")
    return guardar_excel(df, f'backup_{nombre_operacion}', region_nombre)
