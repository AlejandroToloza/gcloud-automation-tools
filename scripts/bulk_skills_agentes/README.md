# ✍️ Skills de Enrutamiento en Bulk – Genesys Cloud

> ⚠️ **Este script ESCRIBE en tu organización.** Por defecto siempre corre en modo **vista previa (dry-run)**. Leé toda esta página antes de usar `--confirm`/`BULK_CONFIRM`.

Agrega o quita skills de enrutamiento (routing skills) de una lista de agentes, en bulk.

---

## 🛠️ ¿Cómo usarlo?

CSV con estas columnas (`proficiency` es opcional, de 0 a 5, solo se usa al agregar — si no la ponés, se usa `1.0`):

```csv
email_usuario,skill,accion,proficiency
juan.perez@empresa.com,Inglés,agregar,4
maria.gomez@empresa.com,Ventas B2B,agregar,
carlos.diaz@empresa.com,Soporte Nivel 1,quitar,
```

```bash
gcloud-tools update-skills --archivo cambios.csv --region 1            # vista previa
gcloud-tools update-skills --archivo cambios.csv --region 1 --confirm  # aplica de verdad
```

O directamente:

```bash
python scripts/bulk_skills_agentes/skills_agentes.py
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
