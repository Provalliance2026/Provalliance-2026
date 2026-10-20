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
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{ --fondo:#f2ede3; --tarjeta:#fff; --texto:#1c1a14; --suave:#7a7260; --borde:#ddd8cc; --principal:#1c1a14; --acento:#b8860b; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --fondo:#16140f; --tarjeta:#201d17; --texto:#efe9dc; --suave:#a39c8c; --borde:#3a352b; --principal:#efe9dc; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family:Inter, system-ui, sans-serif; background:var(--fondo); color:var(--texto); }}
  header, section {{ max-width:1100px; margin:auto; padding:0 16px; }}
  header {{ padding-top:32px; }}
  h1 {{ margin:0; color:var(--principal); font-family:'EB Garamond', Georgia, serif; font-weight:500; font-size:2.2rem; }}
  h2 {{ margin:32px 0 12px; font-size:.85rem; letter-spacing:.08em; color:var(--acento); border-bottom:1px solid var(--borde); padding-bottom:8px; }}
  section {{ margin-top:24px; }}
  .rejilla {{ display:grid; gap:16px; grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); }}
  .tarjeta {{ display:block; background:var(--tarjeta); border:1px solid var(--borde); border-radius:4px; padding:20px; color:inherit; text-decoration:none; transition:border-color .15s; }}
  .tarjeta:hover {{ border-color:var(--acento); }}
  .tarjeta h3 {{ font-family:'EB Garamond', Georgia, serif; font-weight:500; font-size:1.35rem; margin:0 0 8px; }}
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


PORTADA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Provalliance · Cuadros de Mando</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=Inter:wght@500;600&display=swap" rel="stylesheet">
<style>
  :root {{ --fondo:#f2ede3; --tarjeta:#fff; --texto:#1c1a14; --cuerpo:#3a3628; --suave:#7a7260; --borde:#ddd8cc; --acento:#b8860b; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --fondo:#16140f; --tarjeta:#201d17; --texto:#efe9dc; --cuerpo:#d6cfbf; --suave:#a39c8c; --borde:#3a352b; }}
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:'EB Garamond', Georgia, serif; background:var(--fondo); color:var(--texto);
         min-height:100vh; display:flex; flex-direction:column; }}
  .barra {{ display:flex; justify-content:space-between; gap:16px; padding:32px 60px 0; border-top:2px solid var(--texto); }}
  .etiqueta {{ font-family:Inter, sans-serif; font-size:10px; font-weight:600; letter-spacing:2.5px; text-transform:uppercase; color:var(--suave); }}
  .centro {{ flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:40px 24px; }}
  .antetitulo {{ font-style:italic; font-size:20px; color:var(--suave); margin-bottom:16px; }}
  h1 {{ font-weight:400; font-size:clamp(40px, 9vw, 130px); letter-spacing:-1px; line-height:.95; margin-bottom:28px; }}
  .separador {{ width:64px; height:2px; background:var(--acento); margin:0 auto 32px; }}
  .texto {{ font-size:19px; color:var(--cuerpo); margin-bottom:52px; }}
  .unidades {{ display:flex; gap:20px; justify-content:center; flex-wrap:wrap; }}
  .unidad {{ display:flex; flex-direction:column; align-items:flex-start; gap:10px; width:260px; padding:28px; text-align:left;
            background:var(--tarjeta); border:1px solid var(--borde); border-radius:4px; color:inherit; text-decoration:none;
            transition:border-color .18s, box-shadow .18s, transform .18s; }}
  .unidad:hover {{ border-color:var(--acento); box-shadow:0 6px 28px rgba(0,0,0,.08); transform:translateY(-2px); }}
  .unidad h2 {{ font-weight:500; font-size:28px; letter-spacing:1px; }}
  .unidad p {{ font-size:15px; color:var(--suave); flex:1; }}
  .flecha {{ font-family:Inter, sans-serif; font-size:10px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:var(--suave); }}
  .unidad:hover .flecha {{ color:var(--acento); }}
  .pie {{ padding:0 60px 32px; border-bottom:1px solid var(--borde); font-style:italic; font-size:14px; color:var(--suave); }}
  @media (max-width:600px) {{
    .barra {{ padding:20px 16px 0; }} .pie {{ padding:0 16px 24px; }}
    .unidad {{ width:100%; max-width:340px; }}
  }}
</style>
</head>
<body>
<div class="barra">
  <span class="etiqueta">Cuadros de Mando</span>
  <span class="etiqueta">Ejercicio 2026</span>
</div>
<div class="centro">
  <div class="antetitulo">Selecciona una unidad</div>
  <h1>PROVALLIANCE</h1>
  <div class="separador"></div>
  <div class="texto">Informes y dashboards de cada unidad de negocio.</div>
  <div class="unidades">{tarjetas}
  </div>
</div>
<div class="pie">Cifras en euros</div>
</body>
</html>
"""


def tarjeta_unidad(u: dict) -> str:
    n = len(u["dashboards"])
    destino = "index.html"
    if n == 0:
        cuenta = "Todavía sin dashboards"
    elif n == 1:  # sin página intermedia: directo al único dashboard
        cuenta = u["dashboards"][0]["titulo"].split(" · ")[0]
        destino = u["dashboards"][0]["archivo"]
    else:
        cuenta = f"{n} dashboards"
    return f"""
    <a class="unidad" href="unidades/{html.escape(u['carpeta'])}/{html.escape(destino)}">
      <h2>{html.escape(u['nombre'])}</h2>
      <p>{cuenta}</p>
      <span class="flecha">Entrar →</span>
    </a>"""


def main() -> None:
    unidades = leer_unidades()
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir()
    for u in unidades:
        copiar_publico(UNIDADES / u["carpeta"], SALIDA / "unidades" / u["carpeta"])
    tarjetas = "".join(tarjeta_unidad(u) for u in unidades)
    (SALIDA / "index.html").write_text(PORTADA.format(tarjetas=tarjetas), encoding="utf-8")
    # Una página por unidad con sus dashboards
    for u in unidades:
        (SALIDA / "unidades" / u["carpeta"] / "index.html").write_text(PLANTILLA.format(
            titulo=html.escape(u['nombre']),
            volver='<a class="volver" href="../../index.html">← Portal</a><br>',
            secciones=seccion(u, "")), encoding="utf-8")
    total = sum(len(u["dashboards"]) for u in unidades)
    print(f"Portal generado en {SALIDA}: {len(unidades)} unidades, {total} dashboards.")


if __name__ == "__main__":
    main()
