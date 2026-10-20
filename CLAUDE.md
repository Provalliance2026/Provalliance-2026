# Instrucciones para Claude

Repositorio de dashboards HTML generados a partir de Excel, organizado en cuatro unidades:
`unidades/salones` (SALONES), `unidades/franquicias` (FRANQUICIAS), `unidades/producto` (PRODUCTO)
y `unidades/hq` (HQ).
Responde y escribe todo (textos de los dashboards incluidos) en **español**.

**El repositorio es público.** Si un Excel contiene datos personales (nombres, DNI, teléfonos,
emails, importes individuales de personas), avisa antes de seguir y no los lleves al HTML.

## Al generar o actualizar un dashboard

1. Lee los Excel de `unidades/<unidad>/datos/` con Python (`pandas` + `openpyxl`). Revisa hojas,
   columnas, tipos, vacíos y totales antes de diseñar. Si algo es ambiguo, pregunta.
2. **Actualizar** un dashboard existente: conserva su estructura, gráficos y textos; cambia solo los
   datos (y lo que pidan). Comprueba que los totales cuadran con el Excel nuevo.
3. **Crear** uno nuevo: `unidades/<unidad>/<nombre>.html` (minúsculas y guiones).
   Si es una web de varias páginas, va en `unidades/<unidad>/<nombre>/` con un `index.html` de portada;
   el portal enlaza esa portada (enlace "← Portal" a `../../../`). Ej.: `unidades/producto/dist-wholesale/`.
4. Cada dashboard es **un único HTML autocontenido**:
   - En `<head>`: `<title>`, `<meta name="description">` (una frase) y
     `<meta name="actualizado" content="aaaa-mm-dd">` con la fecha de los datos. El portal los usa.
   - Datos **agregados** incrustados como JSON en un `<script>`; nunca el Excel completo.
   - Gráficos con Chart.js desde `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js`
     (versión fija). Sin otras dependencias externas salvo Google Fonts.
   - Cabecera con el nombre de la unidad, título, fecha de los datos y enlace "← Portal" a `../../`;
     fila de KPIs; gráficos; tabla de detalle si aporta.
     Si la unidad tiene varios dashboards (como HQ), añade también "← Menú <UNIDAD>" a `./`.
   - Responsive (usable en móvil) y modo claro/oscuro con variables CSS en `:root`.
   - Formato español: `1.234,56 €`, fechas `dd/mm/aaaa` (`Intl.NumberFormat('es-ES')`).
   - Tablas ordenables y con botón «Descargar Excel»: incrusta `scripts/comun/tablas.css` y `tablas.js`
     (marcadores `/*__TABLAS_CSS__*/` y `/*__TABLAS_JS__*/`, ver los `generar.py`) y llama a
     `mejorarTabla(tabla, nombreArchivo)` en cada tabla.
5. Ejecuta `python3 scripts/generar_portal.py` para comprobar que el portal se construye sin errores.
6. Haz commit en la rama de trabajo (no en `main`) con un mensaje descriptivo.

## Dashboards con generador propio

- **HQ · Viajes** (`unidades/hq/viajes.html`): cuando pasen el Excel `TEMPLATE_TRAVELPERK-TICKLEIA`,
  ejecuta `python3 scripts/viajes/generar.py <excel>`; no subas el Excel. Actualiza en
  `scripts/viajes/plantilla.html` el mes de los datos (`actualizado`, texto "enero–septiembre",
  `N_MESES`) y comprueba que los totales cuadran con el Excel. El responsable ha pedido expresamente
  que este dashboard muestre el detalle por empleado.
- **HQ · Marketing Q4** (`unidades/hq/marketing.html`): con el Excel `Marketing_Q4`, ejecuta
  `python3 scripts/marketing/generar.py <excel> <aaaa-mm-dd de los datos>`; no subas el Excel. Usa solo
  las pestañas en rojo `MK HQ`, `MKDIST` y `MKBSTORES` (tablas dinámicas por proveedor). El Excel es
  muy pesado: ábrelo siempre con `read_only=True`.

## Estilo visual común

El mismo que la portada del portal y DIST-WHOLESALE: fondo `#f2ede3`, texto `#1c1a14`, gris `#7a7260`,
bordes `#ddd8cc`, acento dorado `#b8860b`; títulos en EB Garamond y textos en Inter; tarjetas blancas
con radio 4px.

## No hacer

- No tocar dashboards de otras unidades salvo que se pida.
- No borrar ni reescribir los Excel de `datos/`.
