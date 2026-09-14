# ✍️ Actualizar Usuarios en Bulk – Genesys Cloud

> ⚠️ **Este script ESCRIBE en tu organización.** No es un reporte de solo lectura como el resto del repositorio: modifica de verdad `department`/`title` de los usuarios que le indiques. Por defecto siempre corre en modo **vista previa (dry-run)** y no aplica nada — leé toda esta página antes de usar `--confirm`/`BULK_CONFIRM`.

Actualiza el `department` o el `title` de una lista de usuarios en **Genesys Cloud**, en bulk, a partir de un CSV. Es el primero de varios scripts de escritura planeados para este repositorio (bulk-write), y sienta la base de seguridad (vista previa, backup, log de auditoría) que reutilizarán los siguientes.

Ideal para tareas de:
- Reorganizaciones de equipo (cambiar el departamento de varios agentes a la vez)
- Corregir en bulk títulos/cargos cargados mal en un onboarding masivo

---

## 🛡️ Cómo funciona la seguridad (léelo antes de usarlo)

1. **Por defecto, SIEMPRE es una vista previa.** Corrés el script, te muestra fila por fila qué cambiaría, y termina ahí. No se toca la organización.
2. **Solo escribe si definís `BULK_CONFIRM=1`** (o pasás `--confirm` con `gcloud-tools`).
3. Antes de escribir, guarda automáticamente un **backup** del valor actual de cada usuario afectado (Excel, misma carpeta que los demás reportes).
4. Si corrés el script en una consola interactiva, te pide escribir `SI` una última vez antes de aplicar los cambios reales (en una tarea programada, sin consola interactiva, este paso se salta solo).
5. Al terminar, guarda un **log de auditoría** (Excel) con el resultado fila por fila: qué se intentó, si funcionó o no, y el detalle del error si lo hubo. Un error en una fila **no** cancela las demás.

---

## 🛠️ ¿Cómo usarlo?

Instala los requisitos (si no lo has hecho):

```bash
pip install -r requirements.txt
```

Preparás un CSV con estas columnas exactas:

```csv
email_usuario,campo,valor_nuevo
juan.perez@empresa.com,department,Ventas
maria.gomez@empresa.com,title,Supervisora
```

`campo` solo acepta `department` o `title` (a propósito: es la versión de menor riesgo de esta funcionalidad).

**Vista previa (no cambia nada):**

```bash
python scripts/bulk_actualizar_usuarios/actualizar_usuarios.py
```
(te va a pedir región, `Client ID` y `Client Secret`; para el CSV, definí `BULK_ARCHIVO_CSV` en tu `.env` o como variable de entorno — ver `.env.example`)

**Aplicar los cambios de verdad**, una vez que revisaste la vista previa:

```bash
BULK_CONFIRM=1 python scripts/bulk_actualizar_usuarios/actualizar_usuarios.py
```

O con el [CLI único](../../README.md#-cli-único-opcional):

```bash
gcloud-tools update-users --archivo cambios.csv --region 1          # vista previa
gcloud-tools update-users --archivo cambios.csv --region 1 --confirm # aplica de verdad
```

---

## El backup y el log se guardan junto a los demás reportes:

**Escritorio/PYTHON/EXPORTS/backup_actualizar_usuarios_{region}_YYYYMMDD_HHMMSS.xlsx**
**Escritorio/PYTHON/EXPORTS/log_actualizar_usuarios_{region}_YYYYMMDD_HHMMSS.xlsx**

---

## 🌍 Regiones disponibles

| Nº | Región                    | Dominio de API              |
|----|---------------------------|------------------------------|
| 1  | 🇺🇸 Estados Unidos (Este)  | `api.mypurecloud.com`        |
| 2  | 🇺🇸 Estados Unidos (Oeste) | `api.usw2.pure.cloud`        |
| 3  | 🇨🇦 Canadá                 | `api.cac1.pure.cloud`        |
| 4  | 🇧🇷 Brasil (São Paulo)     | `api.sae1.pure.cloud`        |
| 5  | 🇮🇪 Irlanda (Dublín)       | `api.mypurecloud.ie`         |
| 6  | 🇩🇪 Alemania (Fráncfort)   | `api.mypurecloud.de`         |
| 7  | 🇯🇵 Japón (Tokio)          | `api.mypurecloud.jp`         |
| 8  | 🇦🇺 Australia (Sydney)     | `api.mypurecloud.com.au`     |

---

## 🙋‍♂️ Autor

Este proyecto fue desarrollado por:

**Arley Alejandro Toloza Martínez**  
Ingeniero de Sistemas | Especialista en Genesys Cloud | Apasionado por la automatización con Python  
🔗 [LinkedIn](https://www.linkedin.com/in/alejandro-toloza/)  
🔗 [GitHub](https://github.com/AlejandroToloza)

---

## ⚖️ Licencia

Este proyecto está bajo licencia MIT.
Puedes usarlo, modificarlo y distribuirlo libremente, siempre dando el debido crédito.
