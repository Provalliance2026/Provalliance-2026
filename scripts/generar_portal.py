"""Construye el portal en _site/: una portada con los dashboards de cada unidad.

Las carpetas datos/ (los Excel) no se copian al portal.
"""
import html
import json
import shutil
from html.parser import HTMLParser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
UNIDADES = RAIZ / "unidades"
SALIDA = RAIZ / "_site"
EXTENSIONES_DATOS = {".xlsx", ".xlsm", ".xls", ".csv"}


class LectorCabecera(HTMLParser):
    """Extrae <title> y las etiquetas <meta name="..."> de un dashboard."""

    def __init__(self):
        super().__init__()
        self.meta, self._en_titulo = {}, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._en_titulo = True
        elif tag == "meta" and a.get("name") in ("description", "actualizado"):
            self.meta[a["name"]] = a.get("content", "")

    def handle_endtag(self, tag):
        if tag == "title":
            self._en_titulo = False

    def handle_data(self, data):
        if self._en_titulo:
            self.meta["titulo"] = self.meta.get("titulo", "") + data.strip()


def leer_dashboard(ruta: Path) -> dict:
    lector = LectorCabecera()
    lector.feed(ruta.read_text(encoding="utf-8"))
    archivo = ruta.relative_to(ruta.parent.parent) if ruta.name == "index.html" else Path(ruta.name)
    return {"archivo": archivo.as_posix(), "titulo": lector.meta.get("titulo") or ruta.stem, **lector.meta}


def leer_unidades() -> list[dict]:
    unidades = []
    for carpeta in UNIDADES.iterdir():
        if not (carpeta / "unidad.json").exists():
            continue
        unidad = json.loads((carpeta / "unidad.json").read_text(encoding="utf-8"))
        unidad["carpeta"] = carpeta.name
        # Dashboards sueltos (*.html) y webs de varias páginas (<subcarpeta>/index.html)
        paginas = [*carpeta.glob("*.html"),
                   *(p for p in carpeta.glob("*/index.html") if p.parent.name != "datos")]
        unidad["dashboards"] = sorted((leer_dashboard(p) for p in paginas), key=lambda d: d["titulo"])
        unidades.append(unidad)
    return sorted(unidades, key=lambda u: (u.get("orden", 99), u["nombre"]))


def copiar_publico(origen: Path, destino: Path) -> None:
    for ruta in origen.rglob("*"):
        relativa = ruta.relative_to(origen)
        if ruta.is_dir() or relativa.parts[0] == "datos" or ruta.suffix.lower() in EXTENSIONES_DATOS:
            continue
        (destino / relativa).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ruta, destino / relativa)


def seccion(u: dict, ruta: str) -> str:
    """ruta: prefijo de los enlaces desde la página donde se pinta la sección."""
    e = html.escape
    if u["dashboards"]:
        tarjetas = "".join(f"""
        <a class="tarjeta" href="{ruta}{e(d['archivo'])}">
          <h3>{e(d['titulo'])}</h3>
          <p>{e(d.get('description', ''))}</p>
          <small>{'Datos a ' + e(d['actualizado']) if d.get('actualizado') else ''}</small>
        </a>""" for d in u["dashboards"])
    else:
        tarjetas = '\n        <p class="vacio">Todavía no hay dashboards.</p>'
    return f"""
  <section>
    <h2>{e(u['nombre'])}</h2>
    <div class="rejilla">{tarjetas}
    </div>
  </section>"""


PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root {{ --fondo:#f6f7f9; --tarjeta:#fff; --texto:#1b1f24; --suave:#5b6470; --borde:#e2e5ea; --principal:#1f3a5f; --acento:#c8102e; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --fondo:#111418; --tarjeta:#1a1f26; --texto:#e8ebef; --suave:#9aa3ae; --borde:#2a313a; --principal:#8fb3e0; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family:Inter, system-ui, sans-serif; background:var(--fondo); color:var(--texto); }}
  header, section {{ max-width:1100px; margin:auto; padding:0 16px; }}
  header {{ padding-top:32px; }}
  h1 {{ margin:0; color:var(--principal); font-size:1.6rem; }}
  h2 {{ margin:32px 0 12px; font-size:.85rem; letter-spacing:.08em; color:var(--acento); border-bottom:1px solid var(--borde); padding-bottom:8px; }}
  .rejilla {{ display:grid; gap:16px; grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); }}
  .tarjeta {{ display:block; background:var(--tarjeta); border:1px solid var(--borde); border-radius:12px; padding:20px; color:inherit; text-decoration:none; transition:border-color .15s; }}
  .tarjeta:hover {{ border-color:var(--principal); }}
  .tarjeta h3 {{ font-size:1.05rem; margin:0 0 8px; }}
  .tarjeta p {{ color:var(--suave); margin:0 0 12px; }}
  .tarjeta small, .vacio {{ color:var(--suave); }}
  footer {{ height:32px; }}
  .volver {{ display:inline-block; margin-bottom:8px; color:var(--suave); text-decoration:none; font-size:.85rem; }}
</style>
</head>
<body>
<header>{volver}<h1>{titulo}</h1></header>{secciones}
<footer></footer>
</body>
</html>
"""


def main() -> None:
    unidades = leer_unidades()
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir()
    for u in unidades:
        copiar_publico(UNIDADES / u["carpeta"], SALIDA / "unidades" / u["carpeta"])
    secciones = "".join(seccion(u, f"unidades/{u['carpeta']}/") for u in unidades)
    (SALIDA / "index.html").write_text(
        PLANTILLA.format(titulo="Dashboards Provalliance", volver="", secciones=secciones), encoding="utf-8")
    # Una página por unidad, para que /unidades/<unidad>/ no dé 404
    for u in unidades:
        (SALIDA / "unidades" / u["carpeta"] / "index.html").write_text(PLANTILLA.format(
            titulo=f"Dashboards Provalliance · {html.escape(u['nombre'])}",
            volver='<a class="volver" href="../../index.html">← Portal</a><br>',
            secciones=seccion(u, "")), encoding="utf-8")
    total = sum(len(u["dashboards"]) for u in unidades)
    print(f"Portal generado en {SALIDA}: {len(unidades)} unidades, {total} dashboards.")


if __name__ == "__main__":
    main()
