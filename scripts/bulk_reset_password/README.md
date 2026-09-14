# ✍️ Reset de Contraseña en Bulk – Genesys Cloud

> ⚠️ **Este script ESCRIBE en tu organización** y es el más sensible del repositorio: fija contraseñas nuevas de verdad. Por defecto siempre corre en modo **vista previa (dry-run)**. Leé toda esta página antes de usar `--confirm`/`BULK_CONFIRM`.

Fija una contraseña temporal nueva (generada aleatoriamente) a una lista de usuarios en **Genesys Cloud**, en bulk.

## ⚠️ Diferencia importante con lo que probablemente esperás

Genesys Cloud **no tiene** un endpoint de "enviar email de reset" — el admin fija la contraseña directamente (`POST /api/v2/users/{userId}/password`). Este script:

1. Genera una contraseña temporal aleatoria y segura por usuario (16 caracteres, con mayúscula/minúscula/dígito/símbolo garantizados, usando el generador criptográfico de Python).
2. La aplica de verdad contra la API.
3. La **imprime una única vez en tu consola** — tenés que comunicársela vos al usuario por un canal seguro.
4. **Nunca la guarda en ningún archivo** (ni en el log de auditoría, ni en el backup): quedaría en texto plano en un Excel sin cifrar, lo cual es un riesgo de seguridad real. El log solo registra si la operación funcionó o no para cada usuario, nunca la contraseña.

Por eso este script tampoco hace backup previo (no hay una "contraseña anterior" legible para respaldar).

---

## 🛠️ ¿Cómo usarlo?

CSV con una sola columna:

```csv
email_usuario
juan.perez@empresa.com
maria.gomez@empresa.com
```

```bash
gcloud-tools reset-password --archivo cambios.csv --region 1            # vista previa
gcloud-tools reset-password --archivo cambios.csv --region 1 --confirm  # aplica de verdad
```

O directamente:

```bash
python scripts/bulk_reset_password/reset_password.py
```
(usando `BULK_ARCHIVO_CSV`/`BULK_CONFIRM` del `.env`, ver [.env.example](../../.env.example))

**Corré esto en una consola que puedas copiar de forma segura** — las contraseñas nuevas se muestran ahí, una vez, y no quedan guardadas en ningún otro lado.

---

## 🙋‍♂️ Autor

**Arley Alejandro Toloza Martínez**  
🔗 [LinkedIn](https://www.linkedin.com/in/alejandro-toloza/) · 🔗 [GitHub](https://github.com/AlejandroToloza)

Licencia MIT.
