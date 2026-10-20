"""Genera unidades/hq/marketing.html a partir del Excel Marketing Q4 (pestañas MK HQ, MKDIST y MKBSTORES).

Uso: python3 scripts/marketing/generar.py <ruta-al-excel.xlsx> <fecha-datos aaaa-mm-dd>
El Excel no se guarda en el repositorio.
"""
import subprocess
import sys
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI.parent.parent / "unidades" / "hq" / "marketing.html"

fecha = date.fromisoformat(sys.argv[2])
datos = subprocess.run([sys.executable, "-I", str(AQUI / "extraer.py"), sys.argv[1]],
                       check=True, capture_output=True, text=True).stdout
html = (AQUI / "plantilla.html").read_text(encoding="utf-8")
html = (html.replace("__DATOS__", datos.replace("</", "<\\/"))
            .replace("__ACTUALIZADO__", fecha.isoformat()).replace("__FECHA__", fecha.strftime("%d/%m/%Y")))
SALIDA.write_text(html, encoding="utf-8")
print(f"Generado {SALIDA}")
