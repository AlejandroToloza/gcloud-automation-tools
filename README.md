# 🛠️ Genesys Cloud Automation Tools

[![Tests](https://github.com/AlejandroToloza/gcloud-automation-tools/actions/workflows/tests.yml/badge.svg)](https://github.com/AlejandroToloza/gcloud-automation-tools/actions/workflows/tests.yml)

Bienvenido a `gcloud-automation-tools`, una colección de scripts y herramientas en Python para automatizar tareas comunes en Genesys Cloud.

🔍 Este repositorio está enfocado en aumentar la eficiencia de áreas como soporte, administración de usuarios, auditoría, y operaciones dentro del ecosistema Genesys Cloud, aprovechando sus APIs oficiales.

---

## ⚙️ Automatizaciones disponibles

| Automatización | Descripción breve | Estado |
|----------------|-------------------|--------|
| [Export all users](./scripts/export_all_users/README.md) | Exporta todos los usuarios activos e inactivos a un archivo Excel. | ✅ Disponible |
| [Colas tipo y script](./scripts/colas_tipo_y_script/README.md) | Extrae todas las colas de la organización, su tipo, nombre del script, ID de la cola y del script. | ✅ Disponible |
| [Miembros por cola](./scripts/miembros_por_cola/README.md) | Lista todas las colas existentes junto con sus respectivos miembros. | ✅ Disponible |
| [Total contacts externals](./scripts/total_contacts_externals/README.md) | Devuelve el total de contactos externos creados en la organización. | ✅ Disponible |
| [Agentes por roles](./scripts/agentes_por_roles/README.md) | Muestra los agentes agrupados por rol, junto con el ID de cada rol. | ✅ Disponible |
| [Actualizar usuarios en bulk](./scripts/bulk_actualizar_usuarios/README.md) ✍️ | Actualiza department/title de usuarios en bulk desde un CSV (escribe en tu organización). | ✅ Disponible |
| [Activar/desactivar usuarios en bulk](./scripts/bulk_activar_desactivar/README.md) ✍️ | Activa o desactiva cuentas de usuario en bulk desde un CSV (escribe en tu organización). | ✅ Disponible |
| [Reasignar división en bulk](./scripts/bulk_reasignar_division/README.md) ✍️ | Cambia la división de usuarios en bulk desde un CSV (escribe en tu organización). | ✅ Disponible |
| [Reset de contraseña en bulk](./scripts/bulk_reset_password/README.md) ✍️ | Fija una contraseña temporal nueva a usuarios en bulk desde un CSV (escribe en tu organización). | ✅ Disponible |
| [Script/IVR de colas en bulk](./scripts/bulk_actualizar_script_cola/README.md) ✍️ | Actualiza el script por defecto de colas en bulk desde un CSV (escribe en tu organización). | ✅ Disponible |
| [Wrap-up codes de colas en bulk](./scripts/bulk_wrapupcodes_cola/README.md) ✍️ | Agrega/quita wrap-up codes de colas en bulk desde un CSV (escribe en tu organización). | ✅ Disponible |

---

## 🧩 ¿Qué necesitas para usar estos scripts?

### ✅ Requisitos

- Python 3.8 o superior
- Instalar las dependencias necesarias con:

```bash
pip install -r requirements.txt
```

> 📌 Asegúrate de estar en la carpeta raíz del repositorio antes de ejecutar ese comando.

### 🔐 Credenciales y región (opcional, necesario para automatizar sin intervención humana)

Por defecto, cada script te pide el `Client ID`, `Client Secret` **y la región** por consola. Para correr los scripts sin que nadie los atienda (tarea programada, cron), define las tres cosas como variables de entorno:

```bash
cp .env.example .env
# Edita .env y completa tus credenciales y GENESYS_REGION
```

Si el archivo `.env` existe, los scripts lo leen automáticamente y se saltan **ambas** preguntas (credenciales y región). `.env` está en `.gitignore`: nunca se sube al repositorio.

> ⚠️ Definir solo `GENESYS_CLIENT_ID`/`GENESYS_CLIENT_SECRET` sin `GENESYS_REGION` no alcanza para una ejecución 100% desatendida: el script igual se quedará esperando que elijas la región por consola.

### 🚀 CLI único (opcional)

En vez de recordar la ruta de cada script, puedes instalar el repositorio como herramienta y usar un solo comando:

```bash
pip install -e .
gcloud-tools --help
```

```bash
gcloud-tools export-users
gcloud-tools queue-scripts
gcloud-tools queue-members
gcloud-tools external-contacts
gcloud-tools roles
gcloud-tools update-users --archivo cambios.csv     # ✍️ escribe — ver más abajo
gcloud-tools set-user-state --archivo cambios.csv   # ✍️ escribe
gcloud-tools update-division --archivo cambios.csv  # ✍️ escribe
gcloud-tools reset-password --archivo cambios.csv   # ✍️ escribe
gcloud-tools update-queue-script --archivo cambios.csv       # ✍️ escribe
gcloud-tools update-queue-wrapupcodes --archivo cambios.csv  # ✍️ escribe
```

Cualquier subcomando acepta `--region` para saltar el menú interactivo (equivale a definir `GENESYS_REGION`):

```bash
gcloud-tools export-users --region 1
```

Cada subcomando ejecuta exactamente el mismo script que su equivalente en `scripts/`; es solo una forma más cómoda de invocarlos.

---

## ✍️ Operaciones de escritura (bulk)

A diferencia de las automatizaciones de arriba (todas de solo lectura/exportación), estos scripts **escriben** en tu organización de Genesys Cloud. Todos comparten el mismo modelo de seguridad:

- **Vista previa por defecto**: sin `--confirm` (o `BULK_CONFIRM=1`), el script solo muestra qué cambiaría y no toca nada.
- **Backup automático** del estado "antes", guardado como Excel antes de escribir (excepto reset de contraseña, que no tiene un "antes" legible para respaldar).
- **Un error en una fila no cancela el resto** del lote — se registra y se sigue.
- **Log de auditoría**: qué se aplicó, cuándo, con qué resultado, fila por fila.

| Comando | Qué hace | Detalle |
|---|---|---|
| `update-users` | Actualiza department/title | [README](./scripts/bulk_actualizar_usuarios/README.md) |
| `set-user-state` | Activa/desactiva usuarios | [README](./scripts/bulk_activar_desactivar/README.md) |
| `update-division` | Reasigna división | [README](./scripts/bulk_reasignar_division/README.md) |
| `reset-password` | Fija contraseña temporal nueva | [README](./scripts/bulk_reset_password/README.md) — leé la nota de seguridad antes de usarlo |
| `update-queue-script` | Script/IVR por defecto de colas | [README](./scripts/bulk_actualizar_script_cola/README.md) |
| `update-queue-wrapupcodes` | Wrap-up codes de colas | [README](./scripts/bulk_wrapupcodes_cola/README.md) |

---

## 📂 Estructura del repositorio

```
gcloud-automation-tools/
├── gcloud_tools/                # CLI único (gcloud-tools)
├── scripts/
│   ├── common/                  # Módulo compartido (auth, regiones, export a Excel, bulk-write)
│   ├── export_all_users/
│   ├── agentes_por_roles/
│   ├── colas_tipo_y_script/
│   ├── miembros_por_cola/
│   ├── total_contacts_externals/
│   ├── bulk_actualizar_usuarios/  # ✍️ Escribe en la organización (ver más abajo)
│   ├── bulk_activar_desactivar/   # ✍️
│   ├── bulk_reasignar_division/   # ✍️
│   ├── bulk_reset_password/       # ✍️
│   ├── bulk_actualizar_script_cola/  # ✍️
│   └── bulk_wrapupcodes_cola/        # ✍️
├── tests/                       # Tests automatizados (pytest)
├── .env.example
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── LICENSE
└── README.md
```

---

## ✅ Tests

Este proyecto usa `pytest` con `requests-mock` para probar la lógica de cada script (paginación, reintentos por límite de peticiones, autenticación) sin necesitar credenciales reales ni conexión a Genesys Cloud.

```bash
pip install -r requirements-dev.txt
pytest
```

---

## 🙋‍♂️ Autor

Este proyecto fue desarrollado por:

**Arley Alejandro Toloza Martínez**  
Ingeniero de Sistemas | Especialista en Genesys Cloud | Apasionado por la automatización con Python  
🔗 [LinkedIn](https://www.linkedin.com/in/alejandro-toloza/)  
🔗 [GitHub](https://github.com/AlejandroToloza)

---

## 🤝 Contribuciones

¿Tienes ideas o mejoras? ¡Bienvenido!  
Puedes abrir un issue o un pull request.

---

## ⚖️ Licencia

Este proyecto está bajo la licencia MIT.  
Puedes usarlo, modificarlo y compartirlo libremente dando el debido crédito.
