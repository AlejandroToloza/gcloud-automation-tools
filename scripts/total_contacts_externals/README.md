# 📤 Exportador de Contactos Externos – Genesys Cloud

Este script automatiza la extracción de todos los **contactos externos** registrados en una organización de **Genesys Cloud**, consolidando los resultados en un archivo Excel (.xlsx) listo para análisis o integración.

Ideal para tareas como:

- 🔎 Auditoría de datos externos  
- 📊 Análisis de relaciones con terceros  
- 🔁 Integraciones con CRMs u otras plataformas  
- 📁 Documentación y control de datos de clientes/proveedores  

---

## ⚙️ ¿Qué hace este script?

- ✅ Extrae todos los contactos externos registrados en Genesys Cloud  
- ✅ Compatible con múltiples regiones oficiales  
- ✅ Entrada segura del `Client ID` y `Client Secret`  
- ✅ Exportación a Excel con columnas limpias y formato tabular  
- ✅ Manejo de paginación y errores de red  
- ✅ Ruta fija de exportación: `Escritorio/PYTHON/EXPORTS/`  

---

## 🛠️ ¿Cómo usarlo?

1. **Clona o descarga** el repositorio:

```bash
git clone https://github.com/AlejandroToloza/gcloud-automation-tools.git
```

2. **Instala los requisitos** (una sola vez):

```bash
pip install -r requirements.txt
```

3. **Ejecuta el script desde consola:**

```bash
python scripts/export_external_contacts/export_external_contacts.py
```
---

## 🧩 Flujo de ejecución

- Selección de región mediante menú interactivo  
- Ingreso del `Client ID` y `Client Secret` (entrada oculta por seguridad)  
- Autenticación con la API de Genesys Cloud  
- Descarga paginada de todos los contactos externos  
- Generación automática de archivo `.xlsx` en la carpeta de exportación  

---

## 💾 Ruta del archivo exportado

El archivo se guardará automáticamente en tu escritorio, en la ruta:

**Escritorio/PYTHON/EXPORTS/contactos_<region>_YYYYMMDD_HHMMSS.xlsx**

**Ejemplo de nombre generado:**  

**contactos_estados_unidos_este_20250707_094534.xlsx**

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

**Genesys Cloud Domain Names**  
https://es-help.mypurecloud.com/articles/change-the-region-of-your-genesys-cloud-organization/#tab2

---

## 📦 Estructura del archivo Excel generado

El archivo Excel contendrá columnas con información completa de cada contacto externo, tales como:

| ID | Nombre | Email | Organización | Identificadores externos | Teléfonos | Direcciones |
|----|--------|-------|---------------|---------------------------|-----------|-------------|

> ⚠️ Los datos exportados pueden variar según los campos disponibles en tu organización.

---

## 🙋‍♂️ Autor

Este proyecto fue desarrollado por:

**Arley Alejandro Toloza Martínez**  
Ingeniero de Sistemas | Especialista en Genesys Cloud | Apasionado por la automatización con Python  

🔗 [LinkedIn](https://www.linkedin.com/in/alejandrotoloza)  
🔗 [GitHub](https://github.com/AlejandroToloza)  

---

## 🤝 ¿Quieres contribuir?

¡Bienvenido! Puedes:

- 🛠️ Proponer mejoras  
- 🐞 Reportar errores  
- 🌱 Crear nuevos scripts en este mismo repositorio  

Abre un Pull Request o un Issue y comencemos a colaborar.

---

## ⚖️ Licencia

Este proyecto está licenciado bajo **MIT**.  
Puedes usarlo, modificarlo y distribuirlo libremente, siempre dando el debido crédito.

---

## ⭐ ¿Te fue útil?

Dale una ⭐ al repositorio y compártelo con tus colegas o tu equipo.  
¡Automatizar es avanzar! 🚀
