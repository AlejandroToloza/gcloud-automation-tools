# 📤 Exportador de Colas y Scripts – Genesys Cloud

Este script automatiza la exportación de todas las **colas (queues)** en una organización de **Genesys Cloud**, incluyendo los **scripts asignados** a cada una.  
Los resultados se consolidan en un archivo Excel (.xlsx), ideal para documentación, auditorías y mantenimiento de configuraciones.

Ideal para tareas como:

- 🧾 Auditoría de scripts asignados a colas  
- 🛠️ Verificación de configuración en flujos y campañas  
- 🧩 Integración con herramientas de gestión o monitoreo  
- 🧹 Limpieza o validación de scripts obsoletos  

---

## ⚙️ ¿Qué hace este script?

- ✅ Extrae todas las colas (queues) activas de tu organización  
- ✅ Obtiene los scripts por tipo asociados a cada cola  
- ✅ Compatible con múltiples regiones oficiales de Genesys Cloud  
- ✅ Entrada segura del `Client ID` y `Client Secret`  
- ✅ Manejo de paginación y errores de red  
- ✅ Exportación a Excel con columnas organizadas  
- ✅ Ruta fija de exportación: `Escritorio/PYTHON/EXPORTS/`  

---

## 🛠️ ¿Cómo usarlo?

Clona o descarga el repositorio:

```bash
git clone https://github.com/AlejandroToloza/gcloud-automation-tools.git
```

Instala los requisitos (una sola vez):

```bash
pip install -r requirements.txt
```

Ejecuta el script desde consola:

```bash
python scripts/export_queues_and_scripts/export_queues_and_scripts.py
```
---

## 🧩 Flujo de ejecución

- Selección de región mediante menú interactivo  
- Ingreso del `Client ID`  
- Ingreso seguro del `Client Secret` (oculto en consola)  
- Obtención del token de autenticación  
- Llamadas paginadas a la API de Genesys Cloud para obtener colas  
- Por cada cola, consulta de scripts asignados  
- Exportación del resultado en archivo Excel  

---

## 💾 Ruta del archivo exportado

El archivo se guardará automáticamente en tu escritorio, en la siguiente ruta:

**Escritorio/PYTHON/EXPORTS/queues_and_scripts_<region>_YYYYMMDD_HHMMSS.xlsx**

Ejemplo de nombre generado:  
**queues_and_scripts_estados_unidos_este_20250707_104801.xlsx**

---

## 🌍 Regiones disponibles

| Nº | Región                    | Dominio de API              |
|----|---------------------------|------------------------------|
| 1  | 🇺🇸 Estados Unidos (Este)  | api.mypurecloud.com         |
| 2  | 🇺🇸 Estados Unidos (Oeste) | api.usw2.pure.cloud         |
| 3  | 🇨🇦 Canadá                 | api.cac1.pure.cloud         |
| 4  | 🇧🇷 Brasil (São Paulo)     | api.sae1.pure.cloud         |
| 5  | 🇮🇪 Irlanda (Dublín)       | api.mypurecloud.ie          |
| 6  | 🇩🇪 Alemania (Fráncfort)   | api.mypurecloud.de          |
| 7  | 🇯🇵 Japón (Tokio)          | api.mypurecloud.jp          |
| 8  | 🇦🇺 Australia (Sydney)     | api.mypurecloud.com.au      |

---

## 🔗 Consulta oficial

**Genesys Cloud Domain Names:**  
https://es-help.mypurecloud.com/articles/change-the-region-of-your-genesys-cloud-organization/#tab2

---

## 📦 Estructura del archivo Excel generado

El archivo exportado contiene las siguientes columnas:

| Queue ID | Queue Name | Script Type | Script ID | Script Name |
|----------|------------|-------------|-----------|-------------|

> Cada fila representa un script asociado a una cola específica.  
> Si una cola tiene varios scripts asignados, se listarán en múltiples filas.

---

## 🙋‍♂️ Autor

Este proyecto fue desarrollado por:  
**Arley Alejandro Toloza Martínez**  
*Ingeniero de Sistemas | Especialista en Genesys Cloud | Apasionado por la automatización con Python*

🔗 [LinkedIn](https://www.linkedin.com/in/alejandrotoloza)  
🔗 [GitHub](https://github.com/AlejandroToloza)

---

## 🤝 ¿Quieres contribuir?

¡Bienvenido! Puedes:

- 🛠️ Proponer mejoras  
- 🐞 Reportar errores  
- 🌱 Crear nuevos scripts en este mismo repositorio  

Abre un Pull Request o Issue y comencemos a colaborar.

---

## ⚖️ Licencia

Este proyecto está licenciado bajo **MIT**.  
Puedes usarlo, modificarlo y distribuirlo libremente, siempre dando el debido crédito.

---

## ⭐ ¿Te fue útil?

Dale una ⭐ al repositorio y compártelo con tus colegas o equipo.  
**¡Automatizar es avanzar! 🚀**