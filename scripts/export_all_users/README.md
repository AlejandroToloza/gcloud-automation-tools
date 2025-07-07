# 📤 Exportador de Usuarios – Genesys Cloud

Este script automatiza la extracción de todos los usuarios activos e inactivos de una organización en **Genesys Cloud**, consolidando la información en un archivo Excel (.xlsx).

Es ideal para tareas de:
- Auditoría de usuarios
- Control de accesos
- Documentación interna
- Limpieza de cuentas inactivas

---

## ⚙️ ¿Qué hace este script?

✅ Exporta todos los usuarios (activos e inactivos)  
✅ Compatible con múltiples regiones de Genesys Cloud  
✅ Entrada segura del `Client ID` y `Client Secret`  
✅ Exportación a Excel con columnas organizadas  
✅ Controla errores de límite de peticiones (Rate Limits)

---

## 🛠️ ¿Cómo usarlo?

1. **Clona** o **descarga** el repositorio:

```bash
git clone https://github.com/AlejandroToloza/gcloud-automation-tools.git

    Instala los requisitos (si no lo has hecho):

pip install -r requirements.txt

    Ejecuta el script desde consola:

python scripts/export_all_users/export_all_users.py

    Ingresa los siguientes datos cuando se te solicite:

    🔸 Número de región (selección de lista)

    🔸 Client ID

    🔸 Client Secret (entrada segura oculta)

    El archivo se guardará automáticamente en tu escritorio, en la ruta:

Escritorio/PYTHON/EXPORTS/usuarios_genesys_YYYYMMDD_HHMMSS.xlsx

🌍 Regiones disponibles
Número	Región	Dominio de API
1	🇺🇸 Estados Unidos (Este)	api.mypurecloud.com
2	🇺🇸 Estados Unidos (Oeste)	api.usw2.pure.cloud
3	🇨🇦 Canadá	api.cac1.pure.cloud
4	🇧🇷 Brasil (São Paulo)	api.sae1.pure.cloud
5	🇮🇪 Irlanda (Dublín)	api.mypurecloud.ie
6	🇩🇪 Alemania (Fráncfort)	api.mypurecloud.de
7	🇯🇵 Japón (Tokio)	api.mypurecloud.jp
8	🇦🇺 Australia (Sydney)	api.mypurecloud.com.au

🔗 Consulta oficial:
Genesys Cloud Domain Names
📦 Estructura del archivo Excel generado
ID	Nombre	Email	Título	Estado	Departamento	División

    Los datos se exportan limpios y organizados para facilitar análisis posteriores.

🧑‍💻 Autor

Arley Alejandro Toloza Martínez
Ingeniero de Sistemas especializado en automatización con Python y Genesys Cloud.
🔗 [LinkedIn](https://www.linkedin.com/in/alejandrotoloza)  
🔗 [GitHub](https://github.com/AlejandroToloza)
🤝 ¿Quieres contribuir?

¡Bienvenido! Puedes proponer mejoras, reportar errores o crear un pull request.
⚖️ Licencia

Este proyecto está bajo licencia MIT.
Puedes usarlo, modificarlo y distribuirlo libremente, siempre dando el debido crédito.

🎯 ¿Te fue útil?
Dale una ⭐ al repositorio y comparte con tu equipo o red. ¡Automatizar es avanzar!