"""Genera unidades/hq/viajes.html a partir del Excel de viajes (TEMPLATE_TRAVELPERK-TICKLEIA).

Uso: python3 scripts/viajes/generar.py <ruta-al-excel.xlsx>
El Excel no se guarda en el repositorio: solo se leen Seguimiento, TARJETA y TOTAL2026.
"""
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI.parent.parent / "unidades" / "hq" / "viajes.html"

datos = subprocess.run([sys.executable, "-I", str(AQUI / "extraer.py"), sys.argv[1]],
                       check=True, capture_output=True, text=True).stdout
plantilla = (AQUI / "plantilla.html").read_text(encoding="utf-8")
# Código común de tablas (ordenar y descargar), compartido por todos los dashboards
COMUN = AQUI.parent / "comun"
plantilla = (plantilla.replace("/*__TABLAS_CSS__*/", (COMUN / "tablas.css").read_text(encoding="utf-8"))
             .replace("/*__TABLAS_JS__*/", (COMUN / "tablas.js").read_text(encoding="utf-8")))
SALIDA.write_text(plantilla.replace("__DATOS__", datos.replace("</", "<\\/")), encoding="utf-8")
print(f"Generado {SALIDA}")
