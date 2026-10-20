# Provalliance 2026 · Dashboards

El equipo sube sus **Excel** por unidad y Claude genera o actualiza los **dashboards en HTML**.
Todos se publican en un portal común: **https://provalliance2026.github.io/Provalliance-2026/**

## Unidades

| Unidad | Carpeta |
|---|---|
| SALONES | [`unidades/salones/`](unidades/salones) |
| FRANQUICIAS | [`unidades/franquicias/`](unidades/franquicias) |
| PRODUCTO | [`unidades/producto/`](unidades/producto) |

Cada unidad tiene la misma estructura:

```
unidades/salones/
├── unidad.json          ← nombre y responsable de la unidad
├── datos/               ← aquí se suben los Excel
│   └── ventas-2026-09.xlsx
└── ventas.html          ← dashboards generados por Claude (uno o varios)
```

## Subir un Excel (desde la web de GitHub, sin instalar nada)

1. Entra en la carpeta `datos/` de tu unidad (p. ej. `unidades/salones/datos/`).
2. **Add file → Upload files** y arrastra el Excel.
3. Abajo elige **"Create a new branch for this commit and start a pull request"** → *Propose changes*.
4. Pide a Claude (claude.ai/code, sobre este repositorio y esa rama), por ejemplo:
   > Actualiza el dashboard de ventas de SALONES con el Excel nuevo.
   > Crea un dashboard nuevo en FRANQUICIAS a partir de `aperturas.xlsx` que muestre …
5. Revisa el resultado; al aprobar y fusionar el Pull Request en `main`, el portal se actualiza
   en un par de minutos.

## ⚠️ Este repositorio es público

Cualquiera puede ver lo que se sube aquí, **incluidos los Excel y su historial** (aunque luego
se borren). Por eso:

- **Nada de datos personales**: nombres de clientes o empleados, DNI, teléfonos, emails, nóminas.
- **Nada confidencial**: si un dato no debe verse fuera de la empresa, no lo subas.
- Mejor subir Excel ya **agregados** (por salón, mes, familia de producto…) que el detalle.
- Nunca contraseñas ni cadenas de conexión.

## Configuración inicial (solo administrador, una vez)

1. *Settings → General* → rama por defecto **`main`**.
2. *Settings → Pages* → *Source*: **GitHub Actions**.
3. *Settings → Branches* → proteger `main` exigiendo Pull Request con 1 aprobación.
4. *Organización → Teams* → crear el equipo y darle permiso *Write* en este repositorio.
