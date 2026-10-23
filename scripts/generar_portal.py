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


# Al pinchar un panel: el panel se desvanece y la página se funde antes de navegar
DESVANECER = """<style>
  body { transition:opacity .35s ease; }
  body.saliendo { opacity:0; }
  .desvanecer { transition:opacity .35s ease, transform .35s ease, filter .35s ease !important;
                opacity:0 !important; transform:scale(.96) !important; filter:blur(2px); }
  @media (prefers-reduced-motion: reduce) { body, .desvanecer { transition:none !important; } }
</style>
<script>
document.addEventListener("click", ev => {
  const a = ev.target.closest("a.unidad, a.tarjeta, .novedades a");
  if (!a || ev.defaultPrevented || ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  ev.preventDefault();
  a.classList.add("desvanecer");
  setTimeout(() => document.body.classList.add("saliendo"), 120);
  setTimeout(() => { location.href = a.href; }, 420);
});
// Al volver con «Atrás» (caché del navegador) la página reaparece
addEventListener("pageshow", () => {
  document.body.classList.remove("saliendo");
  document.querySelectorAll(".desvanecer").forEach(el => el.classList.remove("desvanecer"));
});
</script>"""


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


# Icono (trazo SVG) según palabras del título; el color rota por posición, como en DIST-WHOLESALE
ICONOS = [
    (("viaje", "travel"), '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>'),
    (("marketing", "publicidad"), '<path d="M3 11v2a1 1 0 0 0 1 1h2l5 4V6L6 10H4a1 1 0 0 0-1 1z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M18.5 5.5a9 9 0 0 1 0 13"/>'),
    (("stock", "inventario"), '<path d="M21 8l-9-5-9 5 9 5 9-5z"/><path d="M3 8v8l9 5 9-5V8"/><line x1="12" y1="13" x2="12" y2="21"/>'),
    (("venta", "margen", "wholesale", "comercial"), '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>'),
]
ICONO_DEFECTO = '<line x1="3" y1="21" x2="21" y2="21"/><path d="M3 21V9"/><path d="M9 21V13"/><path d="M15 21V6"/><path d="M21 21V3"/>'
COLORES = [("#e4f0e8", "#2d5a3d"), ("#faeeda", "#ba7517"), ("#e8eaf5", "#1e3a5f"), ("#f3e6ec", "#8a2f56"), ("#f5e8e0", "#8b4a20")]


def icono(titulo: str) -> str:
    t = titulo.lower()
    return next((svg for claves, svg in ICONOS if any(k in t for k in claves)), ICONO_DEFECTO)


def fecha_es(iso: str) -> str:
    partes = iso.split("-")
    return "/".join(reversed(partes)) if len(partes) == 3 else iso


def tarjeta_dashboard(d: dict, i: int) -> str:
    e = html.escape
    fondo, trazo = COLORES[i % len(COLORES)]
    titulo, _, subtitulo = d["titulo"].partition(" · ")
    fecha = f"Datos a {fecha_es(d['actualizado'])}" if d.get("actualizado") else ""
    return f"""
    <a class="tarjeta" href="{e(d['archivo'])}" style="--icono-fondo:{fondo}; --icono-trazo:{trazo}">
      <span class="icono"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{icono(d['titulo'])}</svg></span>
      <h2>{e(titulo)}</h2>
      <p>{e(d.get('description', ''))}</p>
      <div class="pie-tarjeta"><span>{e(fecha)}</span><span class="flecha">Abrir →</span></div>
    </a>"""


UNIDAD = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{nombre} · Provalliance</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{ --fondo:#f2ede3; --tarjeta:#fff; --texto:#1c1a14; --cuerpo:#3a3628; --suave:#7a7260; --borde:#ddd8cc; --acento:#b8860b; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --fondo:#16140f; --tarjeta:#201d17; --texto:#efe9dc; --cuerpo:#d6cfbf; --suave:#a39c8c; --borde:#3a352b; }}
    .icono {{ filter:brightness(.85) saturate(1.2); }}
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:'EB Garamond', Georgia, serif; background:var(--fondo); color:var(--texto);
         min-height:100vh; display:flex; flex-direction:column; }}
  .barra {{ display:flex; justify-content:space-between; gap:16px; padding:32px 60px 0; border-top:2px solid var(--texto); }}
  .etiqueta {{ font-family:Inter, sans-serif; font-size:10px; font-weight:600; letter-spacing:2.5px; text-transform:uppercase; color:var(--suave); text-decoration:none; white-space:nowrap; }}
  a.etiqueta:hover {{ color:var(--acento); }}
  .centro {{ flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:48px 24px; }}
  .antetitulo {{ font-style:italic; font-size:20px; color:var(--suave); margin-bottom:12px; }}
  h1 {{ font-weight:400; font-size:clamp(64px, 11vw, 150px); letter-spacing:-1px; line-height:.95; margin-bottom:28px; }}
  .separador {{ width:64px; height:2px; background:var(--acento); margin:0 auto 28px; }}
  .texto {{ font-size:19px; color:var(--cuerpo); margin-bottom:48px; }}
  .tarjetas {{ display:flex; gap:24px; justify-content:center; flex-wrap:wrap; }}
  .tarjeta {{ display:flex; flex-direction:column; align-items:flex-start; gap:12px; width:340px; min-height:270px; padding:32px; text-align:left;
             background:var(--tarjeta); border:1px solid var(--borde); border-top:3px solid var(--icono-trazo); border-radius:4px;
             color:inherit; text-decoration:none; transition:border-color .18s, box-shadow .18s, transform .18s; }}
  .tarjeta:hover {{ border-color:var(--acento); border-top-color:var(--acento); box-shadow:0 10px 32px rgba(0,0,0,.09); transform:translateY(-3px); }}
  .icono {{ width:52px; height:52px; border-radius:12px; display:flex; align-items:center; justify-content:center; background:var(--icono-fondo); margin-bottom:6px; }}
  .icono svg {{ width:26px; height:26px; stroke:var(--icono-trazo); }}
  .tarjeta h2 {{ font-weight:500; font-size:32px; line-height:1.05; }}
  .tarjeta p {{ font-family:Inter, sans-serif; font-size:14px; line-height:1.55; color:var(--suave); flex:1; }}
  .pie-tarjeta {{ width:100%; display:flex; justify-content:space-between; align-items:center; padding-top:14px; border-top:1px solid var(--borde);
                 font-family:Inter, sans-serif; font-size:12px; color:var(--suave); }}
  .flecha {{ font-size:10px; font-weight:600; letter-spacing:2px; text-transform:uppercase; transition:color .15s, letter-spacing .15s; }}
  .tarjeta:hover .flecha {{ color:var(--acento); letter-spacing:3px; }}
  .vacio {{ font-style:italic; color:var(--suave); font-size:18px; }}
  .pie {{ padding:0 60px 32px; border-bottom:1px solid var(--borde); font-style:italic; font-size:14px; color:var(--suave); }}
  @media (max-width:600px) {{
    .barra {{ padding:20px 16px 0; }} .pie {{ padding:0 16px 24px; }} .barra span.etiqueta {{ display:none; }}
    .tarjeta {{ width:100%; max-width:380px; min-height:0; padding:24px; }}
  }}
</style>
</head>
<body>
<div class="barra">
  <a class="etiqueta" href="../../">← Portal</a>
  <span class="etiqueta">Cuadros de Mando · Ejercicio 2026</span>
</div>
<div class="centro">
  <div class="antetitulo">Unidad de negocio</div>
  <h1>{nombre}</h1>
  <div class="separador"></div>
  <div class="texto">{texto}</div>
  <div class="tarjetas">{tarjetas}
  </div>
</div>
<div class="pie">Provalliance · Cifras en euros</div>
{desvanecer}
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
  .novedades {{ width:min(620px, 100%); margin-top:44px; text-align:left; }}
  .novedades h2 {{ font-family:Inter, sans-serif; font-size:10px; font-weight:600; letter-spacing:2.5px; text-transform:uppercase; color:var(--suave);
                  padding-bottom:6px; border-bottom:1px solid var(--texto); }}
  .novedades ul {{ list-style:none; }}
  .novedades a {{ display:grid; grid-template-columns:90px 1fr auto; gap:12px; align-items:baseline; padding:7px 4px;
                 border-bottom:1px solid var(--borde); color:inherit; text-decoration:none; transition:background .15s; }}
  .novedades a:hover {{ background:var(--tarjeta); }}
  .novedades a:hover .nov-nombre {{ color:var(--acento); }}
  .nov-unidad {{ font-family:Inter, sans-serif; font-size:9px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:var(--acento); }}
  .nov-nombre {{ font-size:16px; }}
  .nov-fecha {{ font-family:Inter, sans-serif; font-size:11px; color:var(--suave); white-space:nowrap; }}
  .pie {{ padding:0 60px 32px; border-bottom:1px solid var(--borde); font-style:italic; font-size:14px; color:var(--suave); }}
  @media (max-width:600px) {{
    .barra {{ padding:20px 16px 0; }} .pie {{ padding:0 16px 24px; }}
    .unidad {{ width:100%; max-width:340px; }}
    .novedades a {{ grid-template-columns:1fr auto; }} .nov-unidad {{ grid-column:1 / -1; }}
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
  <section class="novedades">
    <h2>Últimas actualizaciones</h2>
    <ul>{novedades}
    </ul>
  </section>
</div>
<div class="pie">Cifras en euros</div>
{desvanecer}
</body>
</html>
"""


REDIRECCION = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url={destino}">
<script>location.replace("{destino}")</script>
<title>Redirigiendo…</title>
</head>
<body><a href="{destino}">Abrir el dashboard</a></body>
</html>
"""

def novedades(unidades: list[dict], cuantas: int = 6) -> str:
    """Dashboards ordenados por fecha de datos (meta «actualizado»), los más recientes primero."""
    e = html.escape
    todos = [(d["actualizado"], u, d) for u in unidades for d in u["dashboards"] if d.get("actualizado")]
    todos.sort(key=lambda x: x[0], reverse=True)
    return "".join(f"""
      <li><a href="unidades/{e(u['carpeta'])}/{e(d['archivo'])}">
        <span class="nov-unidad">{e(u['nombre'])}</span>
        <span class="nov-nombre">{e(d['titulo'].split(' · ')[0])}</span>
        <span class="nov-fecha">Datos a {fecha_es(fecha)}</span>
      </a></li>""" for fecha, u, d in todos[:cuantas])


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
    (SALIDA / "index.html").write_text(PORTADA.format(tarjetas=tarjetas, novedades=novedades(unidades), desvanecer=DESVANECER), encoding="utf-8")
    # Una página por unidad con sus dashboards; si solo tiene uno, redirige a él
    for u in unidades:
        pagina = SALIDA / "unidades" / u["carpeta"] / "index.html"
        if len(u["dashboards"]) == 1:
            destino = html.escape(u["dashboards"][0]["archivo"])
            pagina.write_text(REDIRECCION.format(destino=destino), encoding="utf-8")
            continue
        n = len(u["dashboards"])
        pagina.write_text(UNIDAD.format(
            nombre=html.escape(u["nombre"]),
            texto="Selecciona el informe que quieres consultar." if n else "Todavía no hay dashboards en esta unidad.",
            tarjetas="".join(tarjeta_dashboard(d, i) for i, d in enumerate(u["dashboards"])),
            desvanecer=DESVANECER), encoding="utf-8")
    total = sum(len(u["dashboards"]) for u in unidades)
    print(f"Portal generado en {SALIDA}: {len(unidades)} unidades, {total} dashboards.")


if __name__ == "__main__":
    main()
