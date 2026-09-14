# ✍️ Activar/Desactivar Usuarios en Bulk – Genesys Cloud

> ⚠️ **Este script ESCRIBE en tu organización** y desactivar un usuario le quita el acceso de inmediato. Por defecto siempre corre en modo **vista previa (dry-run)**. Leé toda esta página antes de usar `--confirm`/`BULK_CONFIRM`.

Activa o desactiva cuentas de usuario en **Genesys Cloud** en bulk, a partir de un CSV. Sigue el mismo modelo de seguridad que [actualizar usuarios](../bulk_actualizar_usuarios/README.md): vista previa por defecto, backup del estado previo, log de auditoría fila por fila.

Ideal para:
- Offboarding masivo (baja de una campaña/BPO completa)
- Reactivar cuentas tras una licencia/ausencia

---

## 🛠️ ¿Cómo usarlo?

CSV con estas columnas exactas:

```csv
email_usuario,accion
juan.perez@empresa.com,desactivar
maria.gomez@empresa.com,activar
```

`accion` solo acepta `activar` o `desactivar`.

```bash
gcloud-tools set-user-state --archivo cambios.csv --region 1            # vista previa
gcloud-tools set-user-state --archivo cambios.csv --region 1 --confirm  # aplica de verdad
```

O directamente:

```bash
python scripts/bulk_activar_desactivar/activar_desactivar.py
```
(usando `BULK_ARCHIVO_CSV`/`BULK_CONFIRM` del `.env`, ver [.env.example](../../.env.example))

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

**Arley Alejandro Toloza Martínez**  
🔗 [LinkedIn](https://www.linkedin.com/in/alejandro-toloza/) · 🔗 [GitHub](https://github.com/AlejandroToloza)

Licencia MIT.
