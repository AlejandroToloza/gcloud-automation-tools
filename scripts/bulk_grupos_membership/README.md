# ✍️ Membership de Grupos en Bulk – Genesys Cloud

> ⚠️ **Este script ESCRIBE en tu organización.** Por defecto siempre corre en modo **vista previa (dry-run)**. Leé toda esta página antes de usar `--confirm`/`BULK_CONFIRM`.

Agrega o quita usuarios de un **Group** de Genesys Cloud (distinto de las colas — se usa para permisos y distribución de notificaciones), en bulk.

---

## 🛠️ ¿Cómo usarlo?

CSV con estas columnas:

```csv
email_usuario,grupo,accion
juan.perez@empresa.com,Supervisores,agregar
maria.gomez@empresa.com,Piloto Nueva Campaña,quitar
```

`accion` solo acepta `agregar` o `quitar`.

```bash
gcloud-tools update-group-members --archivo cambios.csv --region 1            # vista previa
gcloud-tools update-group-members --archivo cambios.csv --region 1 --confirm  # aplica de verdad
```

O directamente:

```bash
python scripts/bulk_grupos_membership/grupos_membership.py
```
(usando `BULK_ARCHIVO_CSV`/`BULK_CONFIRM` del `.env`, ver [.env.example](../../.env.example))

Si alguien más modificó el grupo justo antes de que se aplique tu cambio, esa fila queda registrada como error en el log (control de concurrencia de Genesys) en vez de aplicarse sobre datos desactualizados — volvé a correr el script para reintentarla.

---

## 🙋‍♂️ Autor

**Arley Alejandro Toloza Martínez**  
🔗 [LinkedIn](https://www.linkedin.com/in/alejandro-toloza/) · 🔗 [GitHub](https://github.com/AlejandroToloza)

Licencia MIT.
