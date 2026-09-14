# ✍️ Wrap-Up Codes de Colas en Bulk – Genesys Cloud

> ⚠️ **Este script ESCRIBE en tu organización.** Cambia qué códigos de cierre puede elegir un agente al terminar una interacción en la cola. Por defecto siempre corre en modo **vista previa (dry-run)**. Leé toda esta página antes de usar `--confirm`/`BULK_CONFIRM`.

Agrega o quita wrap-up codes de una cola, en bulk.

---

## 🛠️ ¿Cómo usarlo?

CSV con estas columnas:

```csv
cola,wrapup_code,accion
Soporte VIP,Resuelto en primer contacto,agregar
Ventas,Sin interés,quitar
```

`accion` solo acepta `agregar` o `quitar`.

```bash
gcloud-tools update-queue-wrapupcodes --archivo cambios.csv --region 1            # vista previa
gcloud-tools update-queue-wrapupcodes --archivo cambios.csv --region 1 --confirm  # aplica de verdad
```

O directamente:

```bash
python scripts/bulk_wrapupcodes_cola/wrapupcodes_cola.py
```
(usando `BULK_ARCHIVO_CSV`/`BULK_CONFIRM` del `.env`, ver [.env.example](../../.env.example))

---

## 🙋‍♂️ Autor

**Arley Alejandro Toloza Martínez**  
🔗 [LinkedIn](https://www.linkedin.com/in/alejandro-toloza/) · 🔗 [GitHub](https://github.com/AlejandroToloza)

Licencia MIT.
