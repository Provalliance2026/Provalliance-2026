# Instrucciones para Claude

Este repositorio contiene dashboards HTML generados a partir de Excel que sube el equipo.
Responde y escribe todo (textos de los dashboards incluidos) en **español**.

## Al generar o actualizar un dashboard

1. Trabaja dentro de `dashboards/<nombre>/`. Si la carpeta no tiene `ficha.json`, créala copiando
   `dashboards/_plantilla/ficha.json` y rellénala (pregunta lo que no puedas deducir).
2. Lee los Excel de `datos/` con Python (`pandas` + `openpyxl`). Revisa hojas, columnas, tipos,
   vacíos y totales antes de diseñar. Si algo es ambiguo, pregunta.
3. Genera **un único `index.html` autocontenido**:
   - Datos **agregados** incrustados como JSON en una etiqueta `<script>`; nunca filas con datos
     personales (nombres, DNI, teléfonos, emails, importes individuales de personas).
   - Gráficos con Chart.js desde `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js`
     (versión fija). Sin otras dependencias externas salvo Google Fonts.
   - Estructura: cabecera (título, fecha de los datos, enlace "← Portal" a `../../index.html`),
     fila de KPIs, gráficos, y tabla de detalle si aporta.
   - Responsive (usable en móvil), modo claro/oscuro con variables CSS en `:root`.
   - Formato español: `1.234,56 €`, fechas `dd/mm/aaaa` (`Intl.NumberFormat('es-ES')`).
4. Actualiza `actualizado` en `ficha.json` con la fecha de los datos.
5. Ejecuta `python3 scripts/generar_portal.py` para comprobar que el portal se construye sin errores.
6. Haz commit en la rama de trabajo (no en `main`) con un mensaje descriptivo.

## Estilo visual común

- Fuente: Inter. Color principal `#1f3a5f`, acento `#c8102e`, fondo claro `#f6f7f9`.
- Tarjetas con borde suave y radio 12px. Mismo aspecto en todos los dashboards.

## No hacer

- No modificar dashboards de otras carpetas salvo que se pida.
- No borrar ni reescribir los Excel de `datos/`.
- No publicar datos sin agregar ni subir credenciales.
