# ✍️ Migrar Usuarios de Rol en Bulk – Genesys Cloud

> ⚠️ **Este script ESCRIBE en tu organización** y cambia permisos de acceso. Por defecto siempre corre en modo **vista previa (dry-run)**. Leé toda esta página antes de usar `--confirm`/`BULK_CONFIRM`.

Migra a **todos** los usuarios que hoy tienen un rol de autorización hacia otro rol, en bulk. Útil cuando un rol viejo queda obsoleto y hay que mover a todos sus usuarios a su reemplazo, sin hacerlo uno por uno.

## ⚠️ A diferencia de los demás scripts de bulk-write

El CSV no lista usuarios: lista **pares de roles** (origen → destino). El script:

1. Busca **todos** los usuarios que hoy tienen el rol de origen.
2. Te muestra esa lista completa en la vista previa (con email, no solo el nombre del rol) — así ves el alcance real antes de confirmar.
3. Al aplicar, agrega primero el rol nuevo y **recién después** quita el viejo por cada usuario — si algo falla a mitad de camino, el usuario queda con ambos roles en vez de con ninguno.

---

## 🛠️ ¿Cómo usarlo?

CSV con estas columnas (nombres de rol, no IDs):

```csv
rol_origen,rol_destino
Agente Junior,Agente Senior
```

```bash
gcloud-tools migrate-role --archivo cambios.csv --region 1            # vista previa
gcloud-tools migrate-role --archivo cambios.csv --region 1 --confirm  # aplica de verdad
```

O directamente:

```bash
python scripts/bulk_migrar_rol/migrar_rol.py
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
