# 🧩 Exportador de Usuarios de Genesys Cloud

Este script permite extraer todos los usuarios activos e inactivos de una organización en Genesys Cloud, y exportarlos a un archivo Excel (.xlsx). Está pensado para facilitar procesos de auditoría, depuración, control de accesos, y documentación interna.

## 🚀 Características principales

- ✅ Exportación completa de usuarios (activos e inactivos)
- ✅ Compatible con todas las regiones de Genesys Cloud
- ✅ Entrada segura del Client ID y Secret
- ✅ Manejo de paginación y control de rate limits (errores 429)
- ✅ Archivo Excel con columnas limpias y organizadas

## 🧪 Requisitos

- Python 3.8 o superior
- Librerías:

Antes de este comando asegurate que estas en la carpeta en donde esta el archivo requeirements.txt
```bash
pip install -r requirements.txt 
```


## ⚙️ Cómo usar

1. Clona o descarga este repositorio
2. Ejecuta el script desde consola:

```bash
python scripts/export_all_users.py
```

3. Ingresa los siguientes datos cuando se te solicite:

- 🔸 Región de Genesys Cloud (mediante selección numérica)
- 🔸 Client ID
- 🔸 Client Secret ´Por seguridad no se mostrara nada cuando ingreses los datos´

4. El archivo se guardará automáticamente en tu escritorio, dentro de la ruta:

```
Escritorio/PYTHON/EXPORTS/usuarios_genesys_YYYYMMDD_HHMMSS.xlsx
```

## 🌍 Ejemplos de regiones de Genesys

- `mypurecloud.com` (Estados Unidos)
- `us-east-1.pure.cloud` (USA Este)
- `eu-west-1.pure.cloud` (Europa Oeste)
- `sa-east-1.pure.cloud` (Sudamérica)

🔗 Puedes ver la lista completa aquí:  
[Genesys Cloud Domain Names](https://es-help.mypurecloud.com/articles/change-the-region-of-your-genesys-cloud-organization/#tab2)

## 📦 Estructura del archivo Excel

| ID | Nombre | Email | Título | Estado | Departamento | División |
|----|--------|-------|--------|--------|--------------|----------|

## 👨‍💻 Autor

Este proyecto fue desarrollado por:

**Arley Alejandro Toloza Martínez**  
Ingeniero de Sistemas, especialista en Genesys Cloud y automatización con Python.

🔗 [LinkedIn](https://www.linkedin.com/in/alejandro-toloza/)  
🔗 [GitHub](https://github.com/AlejandroToloza)

## 🤝 Contribuciones

¿Tienes ideas, mejoras o quieres adaptarlo a tus necesidades? ¡Bienvenido!  
Puedes abrir un [issue](https://github.com/AlejandroToloza/repo/issues) o un Pull Request.

## ⚖️ Licencia

Este proyecto está bajo la licencia MIT.
