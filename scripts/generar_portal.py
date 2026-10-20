"""Construye el portal en _site/: una portada con todos los dashboards y sus HTML.

Los Excel de cada carpeta datos/ no se copian, para que nunca se publiquen.
"""
import html
import json
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DASHBOARDS = RAIZ / "dashboards"
SALIDA = RAIZ / "_site"
EXCLUIR = {"datos", "__pycache__"}
EXTENSIONES_DATOS = {".xlsx", ".xlsm", ".xls", ".csv"}


def copiar_publico(origen: Path, destino: Path) -> None:
    for ruta in origen.rglob("*"):
        relativa = ruta.relative_to(origen)
        if ruta.is_dir() or EXCLUIR & set(relativa.parts) or ruta.suffix.lower() in EXTENSIONES_DATOS:
            continue
        (destino / relativa).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ruta, destino / relativa)


def leer_dashboards() -> list[dict]:
    fichas, errores = [], []
    for carpeta in sorted(DASHBOARDS.iterdir()):
        if not carpeta.is_dir() or carpeta.name.startswith("_"):
            continue
        if not (carpeta / "index.html").exists():
            continue  # todavía sin generar
        try:
            ficha = json.loads((carpeta / "ficha.json").read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            errores.append(f"{carpeta.name}: ficha.json ausente o inválida ({e})")
            continue
        ficha["carpeta"] = carpeta.name
        fichas.append(ficha)
    if errores:
        sys.exit("Errores:\n  " + "\n  ".join(errores))
    return fichas


def tarjeta(f: dict) -> str:
    e = lambda clave: html.escape(str(f.get(clave, "")))
    return f"""
      <a class="tarjeta" href="dashboards/{e('carpeta')}/index.html">
        <span class="area">{e('area')}</span>
        <h2>{e('titulo')}</h2>
        <p>{e('descripcion')}</p>
        <small>{e('responsable')} · datos a {e('actualizado')}</small>
      </a>"""


PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboards Provalliance</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root {{ --fondo:#f6f7f9; --tarjeta:#fff; --texto:#1b1f24; --suave:#5b6470; --borde:#e2e5ea; --principal:#1f3a5f; --acento:#c8102e; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --fondo:#111418; --tarjeta:#1a1f26; --texto:#e8ebef; --suave:#9aa3ae; --borde:#2a313a; --principal:#8fb3e0; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family:Inter, system-ui, sans-serif; background:var(--fondo); color:var(--texto); }}
  header {{ padding:32px 16px 8px; max-width:1100px; margin:auto; }}
  h1 {{ margin:0; color:var(--principal); font-size:1.6rem; }}
  header p {{ color:var(--suave); margin:4px 0 0; }}
  main {{ display:grid; gap:16px; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); padding:16px; max-width:1100px; margin:auto; }}
  .tarjeta {{ display:block; background:var(--tarjeta); border:1px solid var(--borde); border-radius:12px; padding:20px; color:inherit; text-decoration:none; transition:border-color .15s; }}
  .tarjeta:hover {{ border-color:var(--principal); }}
  .tarjeta h2 {{ font-size:1.1rem; margin:8px 0; }}
  .tarjeta p {{ color:var(--suave); margin:0 0 12px; }}
  .tarjeta small {{ color:var(--suave); }}
  .area {{ font-size:.75rem; font-weight:600; text-transform:uppercase; color:var(--acento); }}
  .vacio {{ color:var(--suave); }}
</style>
</head>
<body>
<header>
  <h1>Dashboards Provalliance</h1>
  <p>{total} dashboards publicados</p>
</header>
<main>{tarjetas}
</main>
</body>
</html>
"""


def main() -> None:
    fichas = leer_dashboards()
    fichas.sort(key=lambda f: (str(f.get("area", "")), str(f.get("titulo", ""))))
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir()
    for f in fichas:
        copiar_publico(DASHBOARDS / f["carpeta"], SALIDA / "dashboards" / f["carpeta"])
    tarjetas = "".join(tarjeta(f) for f in fichas) or '\n  <p class="vacio">Todavía no hay dashboards.</p>'
    (SALIDA / "index.html").write_text(PLANTILLA.format(total=len(fichas), tarjetas=tarjetas), encoding="utf-8")
    print(f"Portal generado en {SALIDA} con {len(fichas)} dashboards.")


if __name__ == "__main__":
    main()
