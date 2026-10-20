# Instrucciones para Claude

Repositorio de dashboards HTML generados a partir de Excel, organizado en tres unidades:
`unidades/salones` (SALONES), `unidades/franquicias` (FRANQUICIAS) y `unidades/producto` (PRODUCTO).
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
   el portal enlaza esa portada (enlace "← Portal" a `../../../index.html`). Ej.: `unidades/producto/dist-wholesale/`.
4. Cada dashboard es **un único HTML autocontenido**:
   - En `<head>`: `<title>`, `<meta name="description">` (una frase) y
     `<meta name="actualizado" content="aaaa-mm-dd">` con la fecha de los datos. El portal los usa.
   - Datos **agregados** incrustados como JSON en un `<script>`; nunca el Excel completo.
   - Gráficos con Chart.js desde `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js`
     (versión fija). Sin otras dependencias externas salvo Google Fonts.
   - Cabecera con el nombre de la unidad, título, fecha de los datos y enlace "← Portal" a `../../index.html`;
     fila de KPIs; gráficos; tabla de detalle si aporta.
   - Responsive (usable en móvil) y modo claro/oscuro con variables CSS en `:root`.
   - Formato español: `1.234,56 €`, fechas `dd/mm/aaaa` (`Intl.NumberFormat('es-ES')`).
5. Ejecuta `python3 scripts/generar_portal.py` para comprobar que el portal se construye sin errores.
6. Haz commit en la rama de trabajo (no en `main`) con un mensaje descriptivo.

## Estilo visual común

- Fuente: Inter. Color principal `#1f3a5f`, acento `#c8102e`, fondo claro `#f6f7f9`.
- Tarjetas con borde suave y radio 12px. Mismo aspecto en todos los dashboards.

## No hacer

- No tocar dashboards de otras unidades salvo que se pida.
- No borrar ni reescribir los Excel de `datos/`.
