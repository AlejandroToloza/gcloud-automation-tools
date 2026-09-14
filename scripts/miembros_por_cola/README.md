# 👥 Miembros por Cola – Genesys Cloud

Este script automatiza la extracción de todas las colas de una organización en **Genesys Cloud** junto con sus respectivos miembros (agentes), consolidando la información en un archivo Excel (.xlsx).

Es ideal para tareas de:
- Auditoría de asignación de agentes a colas
- Balanceo de carga y capacidad por cola
- Documentación interna
- Limpieza de agentes que ya no deberían estar en ciertas colas

---

## ⚙️ ¿Qué hace este script?

✅ Lista todas las colas de la organización  
✅ Obtiene los miembros de cada cola (ID, nombre, si está unido a la cola)  
✅ Compatible con múltiples regiones de Genesys Cloud  
✅ Entrada segura del `Client ID` y `Client Secret`  
✅ Exportación a Excel con columnas organizadas  
✅ Controla errores de límite de peticiones (Rate Limits)

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
python scripts/miembros_por_cola/miembros_por_cola.py
```
---

## Ingresa los siguientes datos cuando se te solicite:

🔸 Número de región (selección de lista)

🔸 Client ID

🔸 Client Secret (entrada segura oculta)

---

## El archivo se guardará automáticamente en tu escritorio, en la ruta:

**Escritorio/PYTHON/EXPORTS/miembros_por_cola_{region}_YYYYMMDD_HHMMSS.xlsx**

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
| ID de Cola | Nombre de Cola | ID de Usuario | Nombre de Usuario | Unido a la Cola | Ring Number |

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
