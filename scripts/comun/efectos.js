// ── Efectos visuales comunes (ver efectos.css) ──
// Se incrusta al final del <body> del portal y de cada dashboard, después de su propio código.
// Nada de esto cambia los datos: si el navegador pide reducir animaciones, no se anima nada.
(() => {
  const quieto = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const enPantalla = el => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.bottom > 0 && r.top < innerHeight;
  };

  // ── Salida: al pinchar un panel se desvanece y la página se funde antes de navegar ──
  const PANELES = 'a.unidad, a.tarjeta, a.nav-card, .novedades a';
  document.addEventListener('click', ev => {
    const a = ev.target.closest(PANELES);
    if (!a || quieto || ev.defaultPrevented || ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
    ev.preventDefault();
    a.classList.add('efx-desvanece');
    setTimeout(() => document.body.classList.add('efx-saliendo'), 120);
    setTimeout(() => { location.href = a.href; }, 420);
  });
  // Al volver con «Atrás» (caché del navegador) la página reaparece
  addEventListener('pageshow', () => {
    document.body.classList.remove('efx-saliendo');
    document.querySelectorAll('.efx-desvanece').forEach(el => el.classList.remove('efx-desvanece'));
  });
  // En iOS, :active solo se aplica si hay algún escuchador táctil
  document.addEventListener('touchstart', () => {}, { passive: true });
  if (quieto) return;

  // ── 1. Entrada escalonada de las tarjetas de KPI que se ven al abrir ──
  document.querySelectorAll('.kpi, .kpi-card').forEach((k, i) => {
    if (!enPantalla(k)) return;
    k.style.animationDelay = Math.min(i, 6) * 0.06 + 's';
    k.classList.add('efx-entra');
    k.addEventListener('animationend', () => { k.classList.remove('efx-entra'); k.style.animationDelay = ''; }, { once: true });
  });

  // ── 2. Las cifras de los KPI cuentan desde 0 la primera vez que se ven ──
  // Cada posición de KPI se anima una sola vez: si el dashboard la repinta al filtrar, ya no.
  const CIFRAS = '.kpi .v, .kpi .kv, .kpi .val, .kpi-value';
  const NUMERO = /-?\d{1,3}(?:\.\d{3})+(?:,\d+)?|-?\d+(?:,\d+)?/g;
  const vistos = new WeakMap();
  const yaContado = el => {
    const caja = el.closest('.kpis') || el.parentElement;
    const clave = el.id || [...caja.querySelectorAll(CIFRAS)].indexOf(el);
    if (!vistos.has(caja)) vistos.set(caja, new Set());
    const s = vistos.get(caja);
    if (s.has(clave)) return true;
    s.add(clave);
    return false;
  };
  function contar(el) {
    const final = el.textContent;
    const nums = final.match(NUMERO);
    if (!nums || nums.length !== 1 || /[/:]/.test(final)) return false;  // solo una cifra; nada de fechas
    if (yaContado(el)) return true;
    const txt = nums[0], decimales = (txt.split(',')[1] || '').length;
    const objetivo = +txt.replace(/\./g, '').replace(',', '.');
    if (!objetivo) return true;
    const f = new Intl.NumberFormat('es-ES', { minimumFractionDigits: decimales, maximumFractionDigits: decimales,
                                              useGrouping: txt.includes('.') ? 'always' : false });
    const [antes, despues] = [final.slice(0, final.indexOf(txt)), final.slice(final.indexOf(txt) + txt.length)];
    const inicio = performance.now(), dura = 1000;
    let escrito = final;
    const paso = t => {
      if (el.textContent !== escrito) return;  // el dashboard lo ha repintado: se deja su valor
      const p = Math.min((t - inicio) / dura, 1), e = 1 - Math.pow(1 - p, 3);
      escrito = p < 1 ? antes + f.format(objetivo * e) + despues : final;
      el.textContent = escrito;
      if (p < 1) requestAnimationFrame(paso);
    };
    requestAnimationFrame(paso);
    return true;
  }
  // Se espera a que la cifra esté visible (pestañas ocultas, scroll) y tenga un número
  const pendientes = new Set();
  const alVer = new IntersectionObserver(entradas => entradas.forEach(en => {
    if (en.isIntersecting && contar(en.target)) { alVer.unobserve(en.target); pendientes.delete(en.target); }
  }), { threshold: 0.6 });
  const buscarCifras = () => document.querySelectorAll(CIFRAS).forEach(el => {
    if (!pendientes.has(el)) { pendientes.add(el); alVer.observe(el); }
  });
  buscarCifras();
  // Cifras que el dashboard pinta más tarde (datos asíncronos, filtros, pestañas)
  let programado = false;
  new MutationObserver(() => {
    if (programado) return;
    programado = true;
    requestAnimationFrame(() => {
      programado = false;
      buscarCifras();
      pendientes.forEach(el => {  // ya visible pero aún sin número cuando se observó
        if (!el.isConnected) { alVer.unobserve(el); pendientes.delete(el); }
        else if (enPantalla(el) && contar(el)) { alVer.unobserve(el); pendientes.delete(el); }
      });
    });
  }).observe(document.body, { childList: true, subtree: true, characterData: true });

  // ── 3. Los gráficos se dibujan cuando aparecen en pantalla, no al cargar ──
  if (window.Chart) {
    const graficos = new IntersectionObserver(entradas => entradas.forEach(en => {
      if (!en.isIntersecting) return;
      graficos.unobserve(en.target);
      const g = Chart.getChart(en.target);
      if (g) { g.reset(); g.update(); }
    }), { threshold: 0.3 });
    const vigilar = g => { if (!enPantalla(g.canvas)) graficos.observe(g.canvas); };
    Object.values(Chart.instances).forEach(vigilar);
    Chart.register({ id: 'efxAlVer', afterInit: vigilar });
  }
})();
