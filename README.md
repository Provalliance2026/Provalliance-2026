# Provalliance 2026 · Dashboards del equipo

Repositorio común donde el equipo sube sus **Excel** y Claude genera a partir de ellos
**dashboards en HTML**. Todos los dashboards se publican en un portal web único.

## Cómo funciona

```
 Tú subes el Excel  ──►  Claude genera el HTML  ──►  Se revisa (Pull Request)  ──►  Aparece en el portal
 dashboards/x/datos/      dashboards/x/index.html     aprobación del responsable      GitHub Pages
```

## Estructura

```
dashboards/
├── _plantilla/              ← copia esta carpeta para empezar uno nuevo
└── ventas-salones/          ← una carpeta por dashboard (minúsculas y guiones)
    ├── ficha.json           ← título, descripción, responsable, área
    ├── datos/               ← los Excel de origen (NO se publican en la web)
    │   └── ventas-2026.xlsx
    └── index.html           ← el dashboard generado por Claude
```

## Subir un dashboard nuevo (desde la web de GitHub, sin instalar nada)

1. Entra en el repositorio → **Add file → Upload files**.
2. Arrastra tu Excel. Antes de confirmar, en el nombre del fichero escribe la ruta delante,
   por ejemplo `dashboards/ventas-salones/datos/` (GitHub crea las carpetas solo).
3. Abajo elige **"Create a new branch for this commit and start a pull request"** → *Propose changes*.
4. Pide a Claude (claude.ai/code, sobre este repositorio y esa rama):
   > Genera el dashboard de `dashboards/ventas-salones` a partir de su Excel. Quiero ver …
   Claude crea la `ficha.json` y el `index.html` siguiendo las reglas de [`CLAUDE.md`](CLAUDE.md).
5. Revisa el resultado y el responsable aprueba el Pull Request. Al fusionarlo en `main`,
   el dashboard aparece en el portal en un par de minutos.

## Actualizar un dashboard existente

Sube el Excel nuevo a la carpeta `datos/` del dashboard (puedes sustituir el anterior) y pide a
Claude: *"Actualiza el dashboard de `dashboards/ventas-salones` con el Excel nuevo"*.

## Reglas importantes

- **Nada de datos personales** (nombres de clientes o empleados, DNI, teléfonos, emails, nóminas
  individuales). Si el Excel los tiene, anonimízalos o agrégalos antes de subirlo (RGPD).
- Los Excel quedan en el repositorio (privado) pero **no se publican**: el HTML solo lleva
  los datos agregados que muestra.
- Tamaño máximo por fichero subido desde la web: 25 MB.
- Nunca subas contraseñas ni cadenas de conexión.

## Dónde se publica

Este repositorio es **privado** (aquí están los Excel). Al fusionar en `main`, el workflow
[`publicar-portal.yml`](.github/workflows/publicar-portal.yml) construye el portal **sin los Excel**
y lo copia al repositorio **público** [`Provalliance2026/dashboards`](https://github.com/Provalliance2026/dashboards),
que lo sirve en **https://provalliance2026.github.io/dashboards/**.

> El portal es público: cualquiera con el enlace puede ver los dashboards (solo datos agregados).

## Configuración inicial (solo administrador, una vez)

1. **Crear el repositorio público** `Provalliance2026/dashboards` (vacío o con README).
2. **Clave de despliegue** (en tu ordenador): `ssh-keygen -t ed25519 -N "" -f portal -C portal`
   - `portal.pub` → repositorio **dashboards** → *Settings → Deploy keys → Add* → marcar **Allow write access**.
   - `portal` (privada) → repositorio **Provalliance-2026** → *Settings → Secrets and variables → Actions*
     → *New repository secret* con nombre `PORTAL_DEPLOY_KEY`. Después borra ambos ficheros.
3. En **Provalliance-2026** → *Actions* → *Publicar portal de dashboards* → **Run workflow**.
4. En **dashboards** → *Settings → Pages* → *Deploy from a branch* → `main` / `(root)`.
5. En **Provalliance-2026**: *Settings → General* → rama por defecto `main`, y
   *Settings → Branches* → proteger `main` exigiendo Pull Request con 1 aprobación.
6. **Organización → Teams**: crear el equipo (p. ej. `analistas`) con permiso *Write* en
   Provalliance-2026 y descomentar la línea de [`.github/CODEOWNERS`](.github/CODEOWNERS).
