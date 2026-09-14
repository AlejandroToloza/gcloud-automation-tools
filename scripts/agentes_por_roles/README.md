# 🧩 Agentes por Roles – Genesys Cloud

Este script automatiza la extracción de todos los roles de autorización de una organización en **Genesys Cloud** junto con los agentes asignados a cada uno, consolidando la información en un archivo Excel (.xlsx).

Es ideal para tareas de:
- Auditoría de permisos y accesos
- Revisión de cumplimiento (compliance)
- Documentación interna
- Detección de agentes con roles innecesarios

---

## ⚙️ ¿Qué hace este script?

✅ Lista todos los roles de autorización de la organización  
✅ Obtiene los agentes asignados a cada rol (ID, nombre, email)  
✅ Consulta los roles en paralelo (hasta 8 a la vez) para acelerar organizaciones grandes  
✅ Compatible con múltiples regiones de Genesys Cloud  
✅ Entrada segura del `Client ID` y `Client Secret`  
✅ Exportación a Excel con columnas organizadas  
✅ Controla errores de límite de peticiones (Rate Limits)

> ℹ️ El script reporta las asignaciones directas de rol devueltas por la API (`/api/v2/authorization/roles/{roleId}/users`). Los roles otorgados únicamente a nivel de división podrían no aparecer aquí.

---

## 🛠️ ¿Cómo usarlo?

1. **Clona** o **descarga** el repositorio:

```bash
git clone https://github.com/AlejandroToloza/gcloud-automation-tools.git
```

Instala los requisitos (si no lo has hecho):

```bash
pip install -r requirements.txt
```

Ejecuta el script desde consola:

```bash
python scripts/agentes_por_roles/agentes_por_roles.py
```
---

## Ingresa los siguientes datos cuando se te solicite:

🔸 Número de región (selección de lista)

🔸 Client ID

🔸 Client Secret (entrada segura oculta)

---

## El archivo se guardará automáticamente en tu escritorio, en la ruta:

**Escritorio/PYTHON/EXPORTS/agentes_por_roles_{region}_YYYYMMDD_HHMMSS.xlsx**

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

## 🔗 Consulta oficial:
**Genesys Cloud Domain Names**
https://es-help.mypurecloud.com/articles/change-the-region-of-your-genesys-cloud-organization/#tab2

---

## 📦 Estructura del archivo Excel generado
| ID de Rol | Nombre de Rol | ID de Usuario | Nombre de Usuario | Email |

> Los datos se exportan limpios y organizados para facilitar análisis posteriores.

---

## 🙋‍♂️ Autor

Este proyecto fue desarrollado por:

**Arley Alejandro Toloza Martínez**  
Ingeniero de Sistemas | Especialista en Genesys Cloud | Apasionado por la automatización con Python  
🔗 [LinkedIn](https://www.linkedin.com/in/alejandro-toloza/)  
🔗 [GitHub](https://github.com/AlejandroToloza)

---

## 🤝 ¿Quieres contribuir?

¡Bienvenido! Puedes proponer mejoras, reportar errores o crear un pull request.

---

## ⚖️ Licencia

Este proyecto está bajo licencia MIT.
Puedes usarlo, modificarlo y distribuirlo libremente, siempre dando el debido crédito.

---

## 🎯 ¿Te fue útil?
Dale una ⭐ al repositorio y comparte con tu equipo o red. ¡Automatizar es avanzar!

---
