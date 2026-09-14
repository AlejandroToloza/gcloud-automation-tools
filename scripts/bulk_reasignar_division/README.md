# ✍️ Reasignar División de Usuarios en Bulk – Genesys Cloud

> ⚠️ **Este script ESCRIBE en tu organización.** Cambiar la división de un usuario afecta qué objetos y datos puede ver y gestionar. Por defecto siempre corre en modo **vista previa (dry-run)**. Leé toda esta página antes de usar `--confirm`/`BULK_CONFIRM`.

Reasigna la división de una lista de usuarios en **Genesys Cloud** en bulk, a partir de un CSV. Mismo modelo de seguridad que el resto de los scripts de bulk-write: vista previa por defecto, backup del estado previo, log de auditoría fila por fila.

Ideal para reorganizaciones de equipo o fusiones donde varios usuarios cambian de división a la vez.

---

## 🛠️ ¿Cómo usarlo?

CSV con estas columnas exactas (`division_nueva` es el **nombre** de la división, tal como aparece en Genesys Cloud):

```csv
email_usuario,division_nueva
juan.perez@empresa.com,Ventas
maria.gomez@empresa.com,Soporte
```

```bash
gcloud-tools update-division --archivo cambios.csv --region 1            # vista previa
gcloud-tools update-division --archivo cambios.csv --region 1 --confirm  # aplica de verdad
```

O directamente:

```bash
python scripts/bulk_reasignar_division/reasignar_division.py
```
(usando `BULK_ARCHIVO_CSV`/`BULK_CONFIRM` del `.env`, ver [.env.example](../../.env.example))

Si el nombre de la división no existe exactamente (no distingue mayúsculas/minúsculas), esa fila queda registrada como error en el log y el resto del lote se sigue aplicando igual.

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
