"""
Exemple interactiu per a la reunió amb Comertia (eix 1: posició competitiva per format).

Pàgina HTML autocontinguda, sense cap dependència externa, per obrir en local al
portàtil. Porta dades de Comertia, o sigui que la sortida va a `data/raw/comertia/`
(ignorat pel git) i NO es publica enlloc.

Tres peces:
  1. La fitxa del mes: el requadre que acompanyaria cada Indicador Comertia.
  2. Contra qui es mesura: diferencial mensual i mitjana mòbil de 12 mesos contra
     cada format de distribució de l'INE.
  3. Tres setmanes abans que l'INE: dia de publicació de Comertia i de l'INE.

Llegeix `posicio_competitiva.csv` (sortida de comertia_posicio_competitiva.py) i
`indicador_comertia.csv` (comertia.build_serie). Cal executar abans aquells dos.

Ús: python analisi/comertia_demo_reunio.py
"""
import json
import os

import pandas as pd

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "comertia")
OUT = os.path.join(RAW, "exemple_interactiu_comertia.html")

SERIES = ["Comertia", "Grans cadenes", "Empreses unilocalitzades", "Petites cadenes",
          "Grans superfícies", "Catalunya, total"]

# Data en què l'INE va publicar l'ICM de cada mes, segons el dia que el motor de
# l'Observatori el va incorporar (historial de data/cache/icm.csv). Només els mesos
# que el motor ha vist sortir: abans del maig de 2026 no hi era.
INE_PUBLICACIO = {
    "2026-04": "2026-05-28",
    "2026-05": "2026-06-29",
    "2026-06": "2026-07-28",
    "2026-07": "2026-08-28",
    "2026-08": "2026-09-29",
}
# Comertia no penja les notes al web des del juny de 2026: data de la premsa o del PDF.
COMERTIA_PUBLICACIO_EXTRA = {
    "2026-04": "2026-05-08",  # nota de premsa (la xifra s'ha revisat després al PDF)
    "2026-05": "2026-06-05",  # nota de premsa (íd.)
    "2026-07": "2026-08-05",  # ViaEmpresa, El Nacional i Ràdio Balaguer, 5-8-2026
    "2026-08": "2026-09-07",  # Indicador_Comertia_Agost_2026.pdf
}


def carrega():
    pc = pd.read_csv(os.path.join(RAW, "posicio_competitiva.csv"))
    pc["mes"] = pc["mes"].str[:7]
    mesos = []
    for _, r in pc.iterrows():
        mesos.append({"mes": r["mes"], **{s: (None if pd.isna(r[s]) else round(float(r[s]), 1))
                                          for s in SERIES}})
    ic = pd.read_csv(os.path.join(RAW, "indicador_comertia.csv"))
    ic["mes"] = ic["data"].str[:7]
    pub = {m: d for m, d in zip(ic["mes"], ic["data_publicacio"]) if isinstance(d, str)}
    pub.update(COMERTIA_PUBLICACIO_EXTRA)
    calendari = []
    for mes, ine in INE_PUBLICACIO.items():
        com = pub.get(mes)
        dies = (pd.Timestamp(ine) - pd.Timestamp(com)).days if com else None
        calendari.append({"mes": mes, "comertia": com, "ine": ine, "dies": dies})
    return mesos, calendari


HTML = r"""<!doctype html>
<html lang="ca">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>L'Indicador Comertia, en context</title>
<style>
  :root {
    --navy: #003366; --ink: #1d2733; --muted: #6b7684; --line: #e3e7ec;
    --ocre: #bf8a2e; --teal: #2f7d72; --red: #c0392b; --bg: #f5f6f8; --card: #ffffff;
    --comertia: #bf8a2e;
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--ink);
         font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
  .wrap { max-width: 980px; margin: 0 auto; padding: 28px 20px 60px; }
  header .eyebrow { font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: var(--ocre); font-weight: 700; }
  header h1 { font-family: Georgia, "Times New Roman", serif; font-size: 34px; color: var(--navy); margin: 8px 0 6px; line-height: 1.15; }
  header p { color: var(--muted); margin: 0; font-size: 15px; line-height: 1.5; max-width: 720px; }
  nav { display: flex; gap: 6px; margin: 26px 0 0; border-bottom: 1px solid var(--line); flex-wrap: wrap; }
  nav button { background: none; border: 0; border-bottom: 3px solid transparent; padding: 10px 14px; font-size: 15px;
               color: var(--muted); cursor: pointer; font-weight: 600; }
  nav button.on { color: var(--navy); border-bottom-color: var(--navy); }
  section { display: none; padding-top: 22px; }
  section.on { display: block; }
  .card { background: var(--card); border: 1px solid var(--line); border-radius: 6px; padding: 24px 26px; }
  .row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; }
  .row label { font-size: 13px; color: var(--muted); font-weight: 600; }
  select, .pill { font-size: 15px; padding: 7px 10px; border: 1px solid var(--line); border-radius: 4px; background: #fff; color: var(--ink); }
  .pill { cursor: pointer; }
  .pill.on { background: var(--navy); color: #fff; border-color: var(--navy); }
  .arrow { font-size: 18px; width: 38px; cursor: pointer; }
  .fitxa-cap { display: flex; justify-content: space-between; align-items: flex-end; gap: 20px; flex-wrap: wrap;
               border-bottom: 2px solid var(--navy); padding-bottom: 14px; margin-bottom: 16px; }
  .fitxa-cap .tit { font-size: 12px; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); font-weight: 700; }
  .fitxa-cap .mes { font-family: Georgia, serif; font-size: 24px; color: var(--navy); margin-top: 4px; }
  .big { font-family: Georgia, serif; font-size: 52px; color: var(--comertia); line-height: 1; font-weight: 700; }
  .big small { font-size: 14px; color: var(--muted); display: block; font-family: inherit; font-weight: 600; text-align: right; margin-top: 4px; }
  .bars { margin: 6px 0 4px; }
  .bar-row { display: grid; grid-template-columns: 200px 1fr 64px; align-items: center; gap: 12px; padding: 6px 0; }
  .bar-row .nom { font-size: 14px; }
  .bar-row.com .nom { font-weight: 700; color: var(--comertia); }
  .track { position: relative; height: 18px; }
  .zero { position: absolute; top: -4px; bottom: -4px; width: 1px; background: #9aa4af; }
  .fill { position: absolute; top: 0; height: 18px; border-radius: 2px; transition: all .35s ease; }
  .val { font-size: 14px; font-weight: 700; text-align: right; font-variant-numeric: tabular-nums; }
  .lectura { font-size: 16px; line-height: 1.55; margin: 16px 0 0; padding: 14px 16px; background: #f7f3ea; border-left: 4px solid var(--ocre); }
  .peu { font-size: 12px; color: var(--muted); line-height: 1.5; margin-top: 14px; }
  .stats { display: flex; gap: 14px; flex-wrap: wrap; margin: 4px 0 14px; }
  .stat { flex: 1 1 180px; border: 1px solid var(--line); border-radius: 4px; padding: 12px 14px; }
  .stat b { display: block; font-family: Georgia, serif; font-size: 26px; color: var(--navy); }
  .stat span { font-size: 13px; color: var(--muted); }
  svg text { font-size: 11px; fill: #6b7684; }
  .tl-row { display: grid; grid-template-columns: 110px 1fr 90px; align-items: center; gap: 14px; padding: 10px 0; border-bottom: 1px solid var(--line); }
  .tl-row .m { font-weight: 700; color: var(--navy); }
  .tl-track { position: relative; height: 34px; }
  .tl-line { position: absolute; top: 16px; left: 0; right: 0; height: 2px; background: var(--line); }
  .tl-gap { position: absolute; top: 14px; height: 6px; background: #f1e3c6; }
  .dot { position: absolute; top: 9px; width: 16px; height: 16px; border-radius: 50%; transform: translateX(-50%); border: 2px solid #fff; }
  .dot.c { background: var(--comertia); } .dot.i { background: var(--navy); }
  .tl-lbl { position: absolute; top: -4px; font-size: 11px; color: var(--muted); transform: translateX(-50%); white-space: nowrap; }
  .tl-days { font-family: Georgia, serif; font-size: 20px; color: var(--ocre); font-weight: 700; text-align: right; }
  .llegenda { display: flex; gap: 18px; font-size: 13px; color: var(--muted); margin: 6px 0 0; flex-wrap: wrap; }
  .llegenda i { display: inline-block; width: 12px; height: 12px; border-radius: 50%; vertical-align: -1px; margin-right: 6px; }
  footer { margin-top: 30px; font-size: 12px; color: var(--muted); line-height: 1.6; }
  @media (max-width: 640px) {
    .bar-row { grid-template-columns: 120px 1fr 56px; }
    .tl-row { grid-template-columns: 70px 1fr 64px; }
    header h1 { font-size: 27px; }
  }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="eyebrow">Observatori del Comerç · J3B3 Consulting</div>
    <h1>L'Indicador Comertia, en context</h1>
    <p>Exemple de treball per a la conversa amb Comertia. Cada mes, la xifra de l'Indicador al costat dels formats de distribució que publica l'INE. Dades fins a l'agost de 2026.</p>
  </header>

  <nav>
    <button class="on" data-s="fitxa">La fitxa del mes</button>
    <button data-s="dif">Contra qui es mesura</button>
    <button data-s="cal">Tres setmanes abans</button>
  </nav>

  <section id="fitxa" class="on">
    <div class="card">
      <div class="row">
        <button class="pill arrow" id="prev" aria-label="Mes anterior">‹</button>
        <select id="mes"></select>
        <button class="pill arrow" id="next" aria-label="Mes següent">›</button>
      </div>
      <div class="fitxa-cap">
        <div><div class="tit">Indicador Comertia en context</div><div class="mes" id="f-mes"></div></div>
        <div class="big" id="f-com"></div>
      </div>
      <div class="bars" id="f-bars"></div>
      <p class="lectura" id="f-lect"></p>
      <p class="peu">Variació interanual de la facturació a preus corrents, la mateixa base que l'Indicador Comertia. Formats de distribució: INE, Índices de Comercio al por Menor per modo de distribució, Espanya, sense estacions de servei, dades ajustades de calendari (l'INE no publica aquest desglossament per comunitats). Catalunya, total: ICM de Catalunya, sèrie original.</p>
    </div>
  </section>

  <section id="dif">
    <div class="card">
      <div class="row" id="formats"></div>
      <div class="stats">
        <div class="stat"><b id="s-mm"></b><span>diferencial mitjà dels últims 12 mesos</span></div>
        <div class="stat"><b id="s-mesos"></b><span>mesos amb la mitjana de 12 mesos per sota de zero</span></div>
        <div class="stat"><b id="s-bat"></b><span>mesos en què Comertia creix més</span></div>
      </div>
      <svg id="chart" viewBox="0 0 920 340" width="100%" role="img" aria-label="Diferencial mensual de Comertia"></svg>
      <div class="llegenda"><span><i style="background:#c9d3de"></i>Diferencial del mes (punts)</span><span><i style="background:var(--navy)"></i>Mitjana mòbil de 12 mesos</span></div>
      <p class="lectura" id="d-lect"></p>
    </div>
  </section>

  <section id="cal">
    <div class="card">
      <p style="margin:0 0 6px; font-size:15px; line-height:1.55;">Dia en què es publica cada mes: l'Indicador Comertia i l'Índex de Comerç al Detall de l'INE.</p>
      <div class="llegenda" style="margin-bottom:8px;"><span><i style="background:var(--comertia)"></i>Indicador Comertia</span><span><i style="background:var(--navy)"></i>INE</span></div>
      <div id="tl"></div>
      <p class="lectura" id="c-lect"></p>
      <p class="peu">Dates de l'INE: dia en què el motor de l'Observatori va incorporar cada mes. Dates de Comertia: nota de premsa, premsa o PDF de l'Indicador.</p>
    </div>
  </section>

  <footer>Document de treball, no publicat. Fonts: Comertia, Indicador Comertia (notes de premsa i PDF mensual, xifres de l'última edició publicada); INE, Índices de Comercio al por Menor. Elaboració: Observatori del Comerç, J3B3 Consulting.</footer>
</div>

<script>
const MESOS = __MESOS__;
const CAL = __CAL__;
const FORMATS = ["Grans cadenes", "Petites cadenes", "Empreses unilocalitzades", "Grans superfícies", "Catalunya, total"];
const NOMS_MES = ["gener","febrer","març","abril","maig","juny","juliol","agost","setembre","octubre","novembre","desembre"];
const COL = {"Comertia":"#bf8a2e","Grans cadenes":"#003366","Empreses unilocalitzades":"#5b7a99","Petites cadenes":"#8aa1b8","Grans superfícies":"#a9b7c6","Catalunya, total":"#2f7d72"};

const fmt = v => (v > 0 ? "+" : v < 0 ? "−" : "") + Math.abs(v).toFixed(1).replace(".", ",");
const nomMes = m => { const [a, b] = m.split("-"); return NOMS_MES[+b - 1] + " de " + a; };
const nomMesCurt = m => { const [a, b] = m.split("-"); return NOMS_MES[+b - 1].slice(0, 3) + " " + a.slice(2); };
const deMes = m => (/^[aeiou]/.test(NOMS_MES[+m.split("-")[1] - 1]) ? "d'" : "de ");

// Pestanyes
document.querySelectorAll("nav button").forEach(b => b.onclick = () => {
  document.querySelectorAll("nav button").forEach(x => x.classList.toggle("on", x === b));
  document.querySelectorAll("section").forEach(s => s.classList.toggle("on", s.id === b.dataset.s));
});

// 1. Fitxa del mes
const sel = document.getElementById("mes");
MESOS.forEach((m, i) => { const o = document.createElement("option"); o.value = i; o.textContent = nomMes(m.mes); sel.appendChild(o); });
sel.value = MESOS.length - 1;
document.getElementById("prev").onclick = () => { if (+sel.value > 0) { sel.value = +sel.value - 1; fitxa(); } };
document.getElementById("next").onclick = () => { if (+sel.value < MESOS.length - 1) { sel.value = +sel.value + 1; fitxa(); } };
sel.onchange = fitxa;

function fitxa() {
  const m = MESOS[+sel.value];
  document.getElementById("f-mes").textContent = nomMes(m.mes);
  document.getElementById("f-com").innerHTML = fmt(m["Comertia"]) + "%<small>Indicador Comertia</small>";
  const files = ["Comertia", ...FORMATS].filter(s => m[s] !== null).map(s => ({s, v: m[s]})).sort((a, b) => b.v - a.v);
  const max = Math.max(...files.map(f => Math.abs(f.v)), 1);
  const span = 2 * max; const z = 50;
  document.getElementById("f-bars").innerHTML = files.map(f => {
    const w = Math.abs(f.v) / span * 100;
    const left = f.v >= 0 ? z : z - w;
    return `<div class="bar-row ${f.s === "Comertia" ? "com" : ""}"><div class="nom">${f.s}</div>
      <div class="track"><div class="zero" style="left:${z}%"></div>
      <div class="fill" style="left:${left}%;width:${w}%;background:${COL[f.s]}"></div></div>
      <div class="val" style="color:${f.v < 0 ? "#c0392b" : "#1d2733"}">${fmt(f.v)}%</div></div>`;
  }).join("");
  const pos = files.findIndex(f => f.s === "Comertia") + 1;
  const dg = m["Comertia"] - m["Grans cadenes"], dp = m["Comertia"] - m["Petites cadenes"];
  const t1 = Math.abs(dg) < 0.05 ? "creix com les grans cadenes"
           : `creix ${fmt(Math.abs(dg)).replace("+", "")} punts ${dg > 0 ? "per sobre" : "per sota"} de les grans cadenes`;
  const t2 = Math.abs(dp) < 0.05 ? "igual que les petites cadenes"
           : `i ${fmt(Math.abs(dp)).replace("+", "")} punts ${dp > 0 ? "per sobre" : "per sota"} de les petites cadenes`;
  document.getElementById("f-lect").textContent =
    `El mes ${deMes(m.mes)}${nomMes(m.mes)}, Comertia ${t1} ${t2}. Queda en la posició ${pos} de ${files.length} sèries.`;
}
fitxa();

// 2. Diferencial contra cada format
let fmtSel = "Grans cadenes";
const fb = document.getElementById("formats");
fb.innerHTML = '<label>Comparar amb:</label>' + FORMATS.map(f => `<button class="pill ${f === fmtSel ? "on" : ""}" data-f="${f}">${f}</button>`).join("");
fb.querySelectorAll("button").forEach(b => b.onclick = () => { fmtSel = b.dataset.f; fb.querySelectorAll("button").forEach(x => x.classList.toggle("on", x === b)); dif(); });

function dif() {
  const d = MESOS.map(m => ({mes: m.mes, v: (m["Comertia"] !== null && m[fmtSel] !== null) ? m["Comertia"] - m[fmtSel] : null}));
  const mm = d.map((x, i) => {
    if (i < 11) return null;
    const w = d.slice(i - 11, i + 1).map(y => y.v);
    return w.some(v => v === null) ? null : w.reduce((a, b) => a + b, 0) / 12;
  });
  const mmv = mm.filter(v => v !== null);
  const sota = mmv.filter(v => v < 0).length;
  const bat = d.filter(x => x.v !== null && x.v > 0).length;
  document.getElementById("s-mm").textContent = fmt(mmv[mmv.length - 1]) + " p.";
  document.getElementById("s-mesos").textContent = `${sota} de ${mmv.length}`;
  document.getElementById("s-bat").textContent = `${bat} de ${d.length}`;

  const W = 920, H = 340, M = {t: 16, r: 16, b: 34, l: 44};
  const vals = d.map(x => x.v).filter(v => v !== null).concat(mmv);
  const lim = Math.ceil(Math.max(...vals.map(Math.abs)) / 2) * 2;
  const x = i => M.l + (i + 0.5) * (W - M.l - M.r) / d.length;
  const y = v => M.t + (lim - v) / (2 * lim) * (H - M.t - M.b);
  const bw = (W - M.l - M.r) / d.length * 0.7;
  let s = "";
  for (let t = -lim; t <= lim; t += lim / 2) {
    s += `<line x1="${M.l}" x2="${W - M.r}" y1="${y(t)}" y2="${y(t)}" stroke="${t === 0 ? "#9aa4af" : "#eef1f4"}"/>`;
    s += `<text x="${M.l - 6}" y="${y(t) + 4}" text-anchor="end">${fmt(t)}</text>`;
  }
  d.forEach((p, i) => {
    if (p.v === null) return;
    const y0 = y(0), y1 = y(p.v);
    s += `<rect x="${x(i) - bw / 2}" y="${Math.min(y0, y1)}" width="${bw}" height="${Math.abs(y1 - y0)}" fill="${p.v >= 0 ? "#d7c39b" : "#c9d3de"}"><title>${nomMes(p.mes)}: ${fmt(p.v)} punts</title></rect>`;
    if (i % 3 === 0) s += `<text x="${x(i)}" y="${H - 12}" text-anchor="middle">${nomMesCurt(p.mes)}</text>`;
  });
  let path = "";
  mm.forEach((v, i) => { if (v !== null) path += (path ? " L " : "M ") + x(i) + " " + y(v); });
  s += `<path d="${path}" fill="none" stroke="#003366" stroke-width="2.5"/>`;
  mm.forEach((v, i) => { if (v !== null) s += `<circle cx="${x(i)}" cy="${y(v)}" r="3" fill="#003366"><title>Mitjana de 12 mesos fins a ${nomMes(d[i].mes)}: ${fmt(v)} punts</title></circle>`; });
  document.getElementById("chart").innerHTML = s;

  const ult = mmv[mmv.length - 1];
  document.getElementById("d-lect").textContent = sota === mmv.length
    ? `Contra ${fmtSel.toLowerCase()}, la mitjana de 12 mesos queda per sota de zero tots els ${mmv.length} mesos de la sèrie. Ara és de ${fmt(ult)} punts.`
    : sota === 0
      ? `Contra ${fmtSel.toLowerCase()}, la mitjana de 12 mesos queda per sobre de zero tots els ${mmv.length} mesos de la sèrie. Ara és de ${fmt(ult)} punts.`
      : `Contra ${fmtSel.toLowerCase()}, la mitjana de 12 mesos queda per sota de zero ${sota} de ${mmv.length} mesos. Ara és de ${fmt(ult)} punts.`;
}
dif();

// 3. Calendari de publicació
function tl() {
  const dia = s => new Date(s + "T12:00:00");
  const rows = CAL.map(c => {
    const ini = dia(c.mes + "-01"); ini.setMonth(ini.getMonth() + 1);  // primer dia del mes següent
    const span = 40 * 864e5;
    const pc = d => Math.min(100, Math.max(0, (dia(d) - ini) / span * 100));
    const dfmt = d => { const x = dia(d); return x.getDate() + "/" + (x.getMonth() + 1); };
    let h = `<div class="tl-row"><div class="m">${nomMesCurt(c.mes)}</div><div class="tl-track"><div class="tl-line"></div>`;
    if (c.comertia) h += `<div class="tl-gap" style="left:${pc(c.comertia)}%;width:${pc(c.ine) - pc(c.comertia)}%"></div>
       <div class="dot c" style="left:${pc(c.comertia)}%" title="Comertia: ${dfmt(c.comertia)}"></div><div class="tl-lbl" style="left:${pc(c.comertia)}%">${dfmt(c.comertia)}</div>`;
    h += `<div class="dot i" style="left:${pc(c.ine)}%" title="INE: ${dfmt(c.ine)}"></div><div class="tl-lbl" style="left:${pc(c.ine)}%">${dfmt(c.ine)}</div></div>`;
    h += `<div class="tl-days">${c.dies !== null ? c.dies + " dies" : "<span style='font-size:12px;color:#6b7684'>sense data</span>"}</div></div>`;
    return h;
  });
  document.getElementById("tl").innerHTML = rows.join("");
  const ds = CAL.map(c => c.dies).filter(v => v !== null).sort((a, b) => a - b);
  const med = ds.length % 2 ? ds[(ds.length - 1) / 2] : (ds[ds.length / 2 - 1] + ds[ds.length / 2]) / 2;
  document.getElementById("c-lect").textContent =
    `L'Indicador Comertia arriba entre ${ds[0]} i ${ds[ds.length - 1]} dies abans que l'INE (mediana de ${String(med).replace(".", ",")}). Durant unes tres setmanes, és l'única xifra del mes que hi ha sobre la taula.`;
}
tl();
</script>
</body>
</html>
"""


def main():
    mesos, calendari = carrega()
    html = (HTML.replace("__MESOS__", json.dumps(mesos, ensure_ascii=False))
                .replace("__CAL__", json.dumps(calendari, ensure_ascii=False)))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Escrit: {OUT}")
    print(f"  {len(mesos)} mesos, de {mesos[0]['mes']} a {mesos[-1]['mes']}")
    print("  Calendari:", ", ".join(f"{c['mes']}: {c['dies']} dies" for c in calendari))


if __name__ == "__main__":
    main()
