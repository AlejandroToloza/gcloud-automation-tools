# 🛠️ Genesys Cloud Automation Tools

Bienvenido a `gcloud-automation-tools`, una colección de scripts y herramientas en Python para automatizar tareas comunes en Genesys Cloud.

🔍 Este repositorio está enfocado en aumentar la eficiencia de áreas como soporte, administración de usuarios, auditoría, y operaciones dentro del ecosistema Genesys Cloud, aprovechando sus APIs oficiales.

---

## ⚙️ Automatizaciones disponibles

| Automatización | Descripción breve | Estado |
|----------------|-------------------|--------|
| [Export all users](./scripts/export_all_users/README.md) | Exporta todos los usuarios activos e inactivos a un archivo Excel. | ✅ Disponible |
| [Colas tipo y script](./scripts/colas_tipo_y_script/README.md) | Extrae todas las colas de la organización, su tipo, nombre del script, ID de la cola y del script. | ✅ Disponible |
| [Miembros por cola](./scripts/miembros_por_cola/README.md) | Lista todas las colas existentes junto con sus respectivos miembros. | 🔜 En desarrollo |
| [Total contacts externals](./scripts/total_contacts_externals/README.md) | Devuelve el total de contactos externos creados en la organización. | ✅ Disponible |
| [Agentes por roles](./scripts/agentes_por_roles/README.md) | Muestra los agentes agrupados por rol, junto con el ID de cada rol. | 🔜 En desarrollo |

---

## 🧩 ¿Qué necesitas para usar estos scripts?

### ✅ Requisitos

- Python 3.8 o superior
- Instalar las dependencias necesarias con:

```bash
pip install -r requirements.txt
```

> 📌 Asegúrate de estar en la carpeta raíz del repositorio antes de ejecutar ese comando.

---

## 📂 Estructura del repositorio

```
gcloud-automation-tools/
├── scripts/
│   ├── common/                  # Módulo compartido (auth, regiones, export a Excel)
│   ├── export_all_users/
│   ├── agentes_por_roles/
│   ├── colas_tipo_y_script/
│   ├── miembros_por_cola/
│   └── total_contacts_externals/
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🙋‍♂️ Autor

Este proyecto fue desarrollado por:

**Arley Alejandro Toloza Martínez**  
Ingeniero de Sistemas | Especialista en Genesys Cloud | Apasionado por la automatización con Python  
🔗 [LinkedIn](https://www.linkedin.com/in/alejandro-toloza/)  
🔗 [GitHub](https://github.com/AlejandroToloza)

---

## 🤝 Contribuciones

¿Tienes ideas o mejoras? ¡Bienvenido!  
Puedes abrir un issue o un pull request.

---

## ⚖️ Licencia

Este proyecto está bajo la licencia MIT.  
Puedes usarlo, modificarlo y compartirlo libremente dando el debido crédito.
