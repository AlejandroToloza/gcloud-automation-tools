# ✍️ Limpieza de Contactos Externos en Bulk – Genesys Cloud

> ⚠️ **Este script ESCRIBE en tu organización y BORRA datos de forma permanente.** Es la única operación de todo el repositorio que elimina información en vez de solo cambiar un estado. Por defecto siempre corre en modo **vista previa (dry-run)**. Leé toda esta página antes de usar `--confirm`/`BULK_CONFIRM`.

Elimina contactos externos de **Genesys Cloud** en bulk, a partir de un CSV de IDs.

## ⚠️ Por qué el CSV pide IDs y no "borra los que parezcan duplicados"

A propósito, este script **no decide por su cuenta** qué contactos son duplicados o viejos — vos tenés que listar exactamente los IDs a borrar. Es la misma filosofía que el resto del repositorio: el CSV es la fuente de verdad explícita, nunca un algoritmo adivinando.

Para encontrar candidatos a limpiar, corré primero el reporte de solo lectura [total_contacts_externals](../total_contacts_externals/README.md) (exporta todos los contactos a Excel), revisalo ahí, y armá el CSV de IDs a partir de eso.

Como es la única operación que borra información permanentemente, antes de aplicar guarda un backup con el **contenido completo** de cada contacto (no solo su ID), por si hay que reconstruir alguno a mano después.

---

## 🛠️ ¿Cómo usarlo?

CSV con estas columnas (`motivo` es opcional, solo para que el log de auditoría sea más legible):

```csv
contacto_id,motivo
a1b2c3d4-...,duplicado de otro contacto
e5f6g7h8-...,sin actividad hace más de 2 años
```

```bash
gcloud-tools delete-contacts --archivo cambios.csv --region 1            # vista previa
gcloud-tools delete-contacts --archivo cambios.csv --region 1 --confirm  # borra de verdad
```

O directamente:

```bash
python scripts/bulk_limpieza_contactos/limpieza_contactos.py
```
(usando `BULK_ARCHIVO_CSV`/`BULK_CONFIRM` del `.env`, ver [.env.example](../../.env.example))

---

## 🙋‍♂️ Autor

**Arley Alejandro Toloza Martínez**  
🔗 [LinkedIn](https://www.linkedin.com/in/alejandro-toloza/) · 🔗 [GitHub](https://github.com/AlejandroToloza)

Licencia MIT.
