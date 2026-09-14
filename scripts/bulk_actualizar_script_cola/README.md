# ✍️ Actualizar Script/IVR por Defecto de Colas en Bulk – Genesys Cloud

> ⚠️ **Este script ESCRIBE en tu organización** y cambia el flujo/IVR que se ejecuta cuando entra una interacción a la cola. Por defecto siempre corre en modo **vista previa (dry-run)**. Leé toda esta página antes de usar `--confirm`/`BULK_CONFIRM`.

Cambia el script (IVR) asignado por defecto a una cola, por tipo de interacción, en bulk. Es el complemento de escritura del reporte de solo lectura [colas_tipo_y_script](../colas_tipo_y_script/README.md).

## ⚠️ Detalle técnico importante

La API de colas de Genesys Cloud **no tiene PATCH, solo PUT** (reemplazo completo del recurso). Para no perder el resto de la configuración de la cola (routing rules, media settings, etc.), este script:

1. Trae la cola **completa** (`GET`).
2. Modifica solo el campo `defaultScripts` del tipo que le pediste, conservando los demás tipos de script ya asignados.
3. Reenvía la cola **completa** con ese único cambio (`PUT`).

---

## 🛠️ ¿Cómo usarlo?

CSV con estas columnas (`tipo_script` es el mismo identificador que ves en el reporte de `colas_tipo_y_script`, ej. `inQueue`, `outboundNoAnswer`):

```csv
cola,tipo_script,nombre_script
Soporte VIP,inQueue,Bienvenida VIP
Ventas,inQueue,Bienvenida Ventas
```

```bash
gcloud-tools update-queue-script --archivo cambios.csv --region 1            # vista previa
gcloud-tools update-queue-script --archivo cambios.csv --region 1 --confirm  # aplica de verdad
```

O directamente:

```bash
python scripts/bulk_actualizar_script_cola/actualizar_script_cola.py
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
