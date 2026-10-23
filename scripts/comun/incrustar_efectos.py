"""Incrusta (o actualiza) efectos.css y efectos.js en dashboards HTML estáticos, sin generador propio.

Uso: python3 scripts/comun/incrustar_efectos.py <html> [<html> ...]
El CSS va antes de </head> y el JS antes de </body>, entre marcadores <!-- efectos --> ... <!-- /efectos -->,
así que se puede volver a ejecutar tras cambiar efectos.* sin duplicar nada.
"""
import re
import sys
from pathlib import Path

COMUN = Path(__file__).resolve().parent
CSS = f"<!-- efectos -->\n<style>\n{(COMUN / 'efectos.css').read_text(encoding='utf-8')}</style>\n<!-- /efectos -->\n"
JS = f"<!-- efectos -->\n<script>\n{(COMUN / 'efectos.js').read_text(encoding='utf-8')}</script>\n<!-- /efectos -->\n"

for ruta in map(Path, sys.argv[1:]):
    html = re.sub(r"<!-- efectos -->.*?<!-- /efectos -->\n", "", ruta.read_text(encoding="utf-8"), flags=re.S)
    if html.count("</head>") != 1 or html.count("</body>") != 1:
        sys.exit(f"{ruta}: se esperaba un único </head> y </body>")
    html = html.replace("</head>", CSS + "</head>").replace("</body>", JS + "</body>")
    ruta.write_text(html, encoding="utf-8")
    print(f"Efectos incrustados en {ruta}")
