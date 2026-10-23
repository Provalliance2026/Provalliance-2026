// ── Tablas: ordenar pulsando la cabecera y descargar a Excel ──
// Se incrusta en cada dashboard generado. Funciona sobre cualquier <table> cuya primera fila sea la
// cabecera: no hay que tocar el código que la pinta, y el orden elegido se mantiene al filtrar.
// Las filas .total y las de "sin resultados" quedan siempre al final. Las tablas con filas .grupo
// (subtotales) no se ordenan, para no romper los grupos, pero sí se pueden descargar.
const valorCelda = texto => {
  const s = texto.trim();
  if (!s || s === '—') return null;
  const n = s.replace(/k€|[€%\s]/g, '').replace(/\./g, '').replace(',', '.');  // «1.234 €», «62 %», «1.048 k€»
  return /^-?\d+(\.\d+)?$/.test(n) ? +n : null;
};

function mejorarTabla(tabla, nombreArchivo) {
  const estado = { col: null, asc: false };
  let ocupado = false, animar = false;
  function aplicar() {
    if (ocupado) return;
    ocupado = true;
    const filas = [...tabla.rows], cabecera = filas[0];
    const agrupada = !!tabla.querySelector('tr.grupo');
    if (cabecera) [...cabecera.cells].forEach((th, i) => {
      th.classList.toggle('ordenable', !agrupada);
      th.dataset.orden = estado.col === i ? (estado.asc ? 'asc' : 'desc') : '';
      th.title = agrupada ? '' : 'Ordenar por esta columna';
      th.onclick = agrupada ? null : () => {
        const esTexto = i === 0 || th.classList.contains('txt');
        estado.asc = estado.col === i ? !estado.asc : esTexto;  // texto A→Z; números de mayor a menor
        estado.col = i;
        animar = true;
        aplicar();
      };
    });
    if (cabecera && !agrupada && estado.col !== null) {
      const fijas = r => r.classList.contains('total') || r.querySelector('td.vacio');
      const cuerpo = filas.slice(1).filter(r => !fijas(r)), final = filas.slice(1).filter(fijas);
      cuerpo.sort((a, b) => {
        const x = a.cells[estado.col]?.textContent ?? '', y = b.cells[estado.col]?.textContent ?? '';
        const nx = valorCelda(x), ny = valorCelda(y);
        const c = nx !== null && ny !== null ? nx - ny : x.localeCompare(y, 'es', { numeric: true });
        return estado.asc ? c : -c;
      });
      [...cuerpo, ...final].forEach(r => r.parentNode.appendChild(r));
      if (animar) {  // fundido de las filas al reordenar (efx-reordenada, en efectos.css)
        tabla.classList.remove('efx-reordenada');
        void tabla.offsetWidth;
        tabla.classList.add('efx-reordenada');
        clearTimeout(tabla.efxFin);
        tabla.efxFin = setTimeout(() => tabla.classList.remove('efx-reordenada'), 400);
      }
    }
    animar = false;
    ocupado = false;
  }
  // Cada vez que el dashboard vuelve a pintar la tabla (filtros, búsqueda), se reaplica el orden
  new MutationObserver(aplicar).observe(tabla, { childList: true });
  aplicar();

  const boton = document.createElement('button');
  boton.type = 'button';
  boton.className = 'descargar';
  boton.textContent = '↓ Descargar Excel';
  boton.title = 'Descarga la tabla tal como se ve ahora (con filtros y orden)';
  boton.onclick = () => descargarTabla(tabla, nombreArchivo);
  const contenedor = tabla.closest('.tabla') || tabla;
  contenedor.parentNode.insertBefore(boton, contenedor);
}

// CSV con «;» y BOM: Excel en español lo abre directamente, con acentos y decimales correctos
function descargarTabla(tabla, nombreArchivo) {
  const celda = td => {
    const n = valorCelda(td.textContent);
    if (n !== null) return String(n).replace('.', ',');
    const t = td.textContent.trim().replace(/\s+/g, ' ');
    return /[";\n]/.test(t) ? `"${t.replace(/"/g, '""')}"` : t;
  };
  const csv = [...tabla.rows].map(r => [...r.cells].map(celda).join(';')).join('\r\n');
  const url = URL.createObjectURL(new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' }));
  const a = Object.assign(document.createElement('a'), { href: url, download: nombreArchivo + '.csv' });
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
