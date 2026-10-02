"""
Exemple interactiu per a la reunió amb Comertia.

Dues peces, i prou:
  1. La xifra de l'Indicador en euros i en volum: l'Indicador és facturació
     (preus corrents); descomptant el que han pujat els preus del comerç a
     Catalunya, surt el creixement en volum. És l'ajuda metodològica que s'ofereix.
  2. Amb qui us compareu: l'últim any, en volum, Comertia al costat dels formats
     de distribució de l'INE.

Pàgina HTML autocontinguda amb l'estil de l'Observatori (Manrope, navy, ocre). Porta
dades de Comertia: la sortida va a `data/raw/comertia/` (ignorat pel git) i NO es
publica. Llegeix `posicio_competitiva.csv` (sortida de comertia_posicio_competitiva.py),
`data/cache/icm.parquet` i `data/cache/icm_distribucion.parquet`.

Deflactor: efecte preu implícit de l'ICM de Catalunya sense estacions de servei,
(1 + nominal) / (1 + real) − 1 sobre les variacions interanuals (sèrie original).
És una aproximació: el panell de Comertia inclou restauració i automoció.

Ús: python analisi/comertia_demo_reunio.py
"""
import json
import os

import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "data", "raw", "comertia")
CACHE = os.path.join(ROOT, "data", "cache")
OUT = os.path.join(RAW, "exemple_interactiu_comertia.html")

SENSE_473 = "Comercio al por menor sin Estaciones de Servicio (47 sin 473)"
FORMATS = {"Grandes cadenas": "Grans cadenes", "Empresas unilocalizadas": "Empreses unilocalitzades",
           "Grandes Superficies": "Grans superfícies", "Pequeñas cadenas": "Petites cadenes"}
MESOS_GRAFIC = 13   # com el gràfic del PDF de l'Indicador


def carrega():
    pc = pd.read_csv(os.path.join(RAW, "posicio_competitiva.csv"))
    pc["data"] = pd.to_datetime(pc["mes"])
    com = pc.set_index("data")["Comertia"]

    icm = pd.read_parquet(os.path.join(CACHE, "icm.parquet"))
    icm["data"] = pd.to_datetime(icm["data"])
    cat = (icm[(icm["ambit"] == "Cataluña") & (icm["branca"] == SENSE_473) & (icm["indicador"] == "var_anual")]
           .pivot_table(index="data", columns="tipus", values="valor"))
    preu = ((1 + cat["nominal"] / 100) / (1 + cat["real"] / 100) - 1) * 100

    m = pd.DataFrame({"euros": com, "preu": preu, "cat_real": cat["real"]}).dropna(subset=["euros", "preu"])
    m["volum"] = ((1 + m["euros"] / 100) / (1 + m["preu"] / 100) - 1) * 100

    fr = pd.read_parquet(os.path.join(CACHE, "icm_distribucion.parquet"))
    fr["data"] = pd.to_datetime(fr["data"])
    fr = (fr[(fr["tipus"] == "real") & (fr["indicador"] == "var_anual")]
          .pivot_table(index="data", columns="modo", values="valor"))

    ult = m.index.max()
    any_ = m[m.index > ult - pd.DateOffset(months=12)]
    comparativa = [{"nom": "Comertia", "v": round(any_["volum"].mean(), 1)}]
    for es, ca in FORMATS.items():
        comparativa.append({"nom": ca, "v": round(fr.loc[any_.index, es].mean(), 1)})
    comparativa.append({"nom": "Catalunya, comerç al detall", "v": round(any_["cat_real"].mean(), 1)})

    mesos = [{"mes": d.strftime("%Y-%m"), "euros": round(r.euros, 1), "volum": round(r.volum, 1),
              "preu": round(r.preu, 1)} for d, r in m.tail(MESOS_GRAFIC).iterrows()]
    resum_any = {"euros": round(any_["euros"].mean(), 1), "volum": round(any_["volum"].mean(), 1),
                 "des": any_.index.min().strftime("%Y-%m"), "fins": ult.strftime("%Y-%m")}
    return mesos, sorted(comparativa, key=lambda x: -x["v"]), resum_any


HTML = r"""<!doctype html>
<html lang="ca">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>L'Indicador Comertia, en euros i en volum</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  :root { --navy:#0b3a66; --ocre:#b07d2b; --teal:#2f7d72; --red:#c0392b;
          --ink:#1a2b3a; --body:#37485a; --g1:#5e6b78; --g2:#9aa6b2; --line:#e4e9ee; }
  * { box-sizing: border-box; }
  body { margin:0; background:#fff; color:var(--body); font-family:'Manrope', system-ui, -apple-system, sans-serif; }
  .wrap { max-width:880px; margin:0 auto; padding:44px 24px 64px; }
  .kicker { font-size:12px; font-weight:700; letter-spacing:.16em; text-transform:uppercase; color:var(--ocre); }
  h1 { font-size:clamp(28px,4vw,40px); font-weight:800; letter-spacing:-.03em; line-height:1.1; color:var(--ink); margin:10px 0 12px; }
  .deck { font-size:17px; line-height:1.6; max-width:62ch; margin:0 0 8px; }
  hr { border:0; border-top:2px solid var(--ink); margin:34px 0 26px; }
  .no { font-size:11px; font-weight:700; letter-spacing:.16em; text-transform:uppercase; color:var(--ocre); }
  h2 { font-size:clamp(20px,2.6vw,26px); font-weight:800; letter-spacing:-.015em; line-height:1.2; color:var(--ink); margin:4px 0 10px; max-width:40ch; }
  .note { font-size:15.5px; line-height:1.6; max-width:64ch; margin:0 0 22px; }
  .xifres { display:grid; grid-template-columns:1fr 1fr; border-top:1px solid var(--line); border-bottom:1px solid var(--line); margin:0 0 8px; }
  .xifra { padding:22px 18px; }
  .xifra + .xifra { border-left:1px solid var(--line); }
  .xifra .v { font-size:52px; font-weight:800; letter-spacing:-.04em; line-height:1; font-variant-numeric:tabular-nums; }
  .xifra .l { font-size:14px; font-weight:700; color:var(--ink); margin-top:10px; }
  .xifra .s { font-size:13px; color:var(--g1); margin-top:4px; line-height:1.45; }
  .mes { font-size:13px; color:var(--g1); margin:14px 0 4px; }
  .mes b { color:var(--ink); }
  svg text { font-family:'Manrope', system-ui, sans-serif; font-size:11px; fill:var(--g1); }
  .llegenda { display:flex; gap:22px; font-size:13px; color:var(--g1); margin:4px 0 0; flex-wrap:wrap; }
  .llegenda i { display:inline-block; width:22px; height:3px; vertical-align:middle; margin-right:8px; }
  .ajuda { font-size:13px; color:var(--g1); margin:6px 0 0; }
  .insight { border-top:3px solid var(--navy); background:#f6f8fa; padding:16px 20px; margin:22px 0 0; font-size:16px; line-height:1.6; color:var(--ink); }
  .insight .t { font-size:11px; font-weight:700; letter-spacing:.16em; text-transform:uppercase; color:var(--ocre); margin-bottom:6px; }
  .insight b { background:linear-gradient(180deg,transparent 60%,rgba(176,125,43,.25) 60%,rgba(176,125,43,.25) 92%,transparent 92%); }
  .bar-row { display:grid; grid-template-columns:230px 1fr 64px; align-items:center; gap:14px; padding:8px 0; border-bottom:1px solid var(--line); }
  .bar-row .n { font-size:15px; }
  .bar-row.com .n { font-weight:800; color:var(--ocre); }
  .track { position:relative; height:16px; }
  .zero { position:absolute; top:-6px; bottom:-6px; width:1px; background:var(--g2); }
  .fill { position:absolute; top:0; height:16px; border-radius:2px; }
  .val { font-size:15px; font-weight:800; text-align:right; font-variant-numeric:tabular-nums; }
  .font { font-size:12px; color:var(--g2); line-height:1.55; margin-top:16px; }
  footer { margin-top:44px; padding-top:14px; border-top:1px solid var(--line); font-size:12px; color:var(--g2); line-height:1.6; }
  @media (max-width:640px) { .xifres { grid-template-columns:1fr; } .xifra + .xifra { border-left:0; border-top:1px solid var(--line); }
    .bar-row { grid-template-columns:130px 1fr 54px; } .xifra .v { font-size:42px; } }
</style>
</head>
<body>
<div class="wrap">
  <div class="kicker">Observatori del Comerç · J3B3 Consulting</div>
  <h1>L'Indicador Comertia, en euros i en volum</h1>
  <p class="deck">L'Indicador mesura la facturació dels socis en euros. Quan els preus pugen, una part d'aquest creixement és inflació. Descomptant-la, s'obté el que creix el volum de vendes, que és la mateixa base amb què l'INE i Idescat publiquen les seves sèries.</p>

  <hr>
  <div class="no">1 · La xifra del mes</div>
  <h2 id="t1"></h2>
  <div class="mes">Mes: <b id="mes-nom"></b> <span id="mes-ajuda">· toca un altre mes al gràfic</span></div>
  <div class="xifres">
    <div class="xifra"><div class="v" style="color:var(--ocre)" id="x-euros"></div><div class="l">En euros</div><div class="s">La xifra de l'Indicador Comertia, tal com es publica.</div></div>
    <div class="xifra"><div class="v" style="color:var(--navy)" id="x-volum"></div><div class="l">En volum</div><div class="s" id="x-preu"></div></div>
  </div>
  <svg id="g1" viewBox="0 0 840 300" width="100%" role="img" aria-label="Indicador Comertia en euros i en volum"></svg>
  <div class="llegenda"><span><i style="background:var(--ocre)"></i>En euros (Indicador)</span><span><i style="background:var(--navy)"></i>En volum (descomptant preus)</span></div>
  <div class="insight" id="ins1"><div class="t">Lectura</div><span></span></div>

  <hr>
  <div class="no">2 · Amb qui us compareu</div>
  <h2>En volum, Comertia creix menys que les grans cadenes i molt per sobre de les petites</h2>
  <p class="note" id="nota2"></p>
  <div id="barres"></div>
  <p class="font">Comertia: Indicador en euros, deflactat amb l'efecte preu del comerç al detall de Catalunya. Formats: INE, Índices de Comercio al por Menor per modo de distribució, Espanya, sense estacions de servei, preus constants (l'INE no publica aquest desglossament per comunitats). Catalunya: ICM de Catalunya sense estacions de servei, preus constants.</p>

  <footer>Document de treball per a la conversa amb Comertia. No publicat. Fonts: Comertia, Indicador Comertia (xifres de l'última edició publicada); INE, Índices de Comercio al por Menor. L'efecte preu és el del comerç al detall català sense estacions de servei; el panell de Comertia inclou també restauració i automoció, o sigui que és una aproximació. Elaboració: Observatori del Comerç, J3B3 Consulting.</footer>
</div>

<script>
const MESOS = __MESOS__;
const COMP = __COMP__;
const ANY = __ANY__;
const NOMS = ["gener","febrer","març","abril","maig","juny","juliol","agost","setembre","octubre","novembre","desembre"];
const fmt = v => (v > 0 ? "+" : v < 0 ? "−" : "") + Math.abs(v).toFixed(1).replace(".", ",");
const nom = m => { const [a, b] = m.split("-"); return NOMS[+b - 1] + " de " + a; };
const curt = m => { const [a, b] = m.split("-"); return NOMS[+b - 1].slice(0, 3) + " " + a.slice(2); };
let sel = MESOS.length - 1;

function mostra() {
  const m = MESOS[sel];
  document.getElementById("t1").textContent =
    `${nom(m.mes).charAt(0).toUpperCase() + nom(m.mes).slice(1)}: ${fmt(m.euros)}% en euros, ${fmt(m.volum)}% en volum`;
  document.getElementById("mes-nom").textContent = nom(m.mes);
  document.getElementById("x-euros").textContent = fmt(m.euros) + "%";
  document.getElementById("x-volum").textContent = fmt(m.volum) + "%";
  document.getElementById("x-preu").textContent =
    `Descomptant que els preus del comerç a Catalunya han variat un ${fmt(m.preu)}% en un any.`;
  dibuixa();
}

function dibuixa() {
  const W = 840, H = 300, M = {t: 18, r: 18, b: 34, l: 40};
  const vals = MESOS.flatMap(m => [m.euros, m.volum]);
  const lo = Math.min(0, Math.floor(Math.min(...vals))), hi = Math.ceil(Math.max(...vals)) + 1;
  const x = i => M.l + i * (W - M.l - M.r) / (MESOS.length - 1);
  const y = v => M.t + (hi - v) / (hi - lo) * (H - M.t - M.b);
  let s = "";
  for (let t = lo; t <= hi; t += 2) {
    s += `<line x1="${M.l}" x2="${W - M.r}" y1="${y(t)}" y2="${y(t)}" stroke="${t === 0 ? "#9aa6b2" : "#eef1f4"}"/>`;
    s += `<text x="${M.l - 8}" y="${y(t) + 4}" text-anchor="end">${t}%</text>`;
  }
  // franja de l'efecte preu entre les dues línies
  let area = MESOS.map((m, i) => `${x(i)},${y(m.euros)}`).join(" ") + " " +
             MESOS.map((m, i) => `${x(i)},${y(m.volum)}`).reverse().join(" ");
  s += `<polygon points="${area}" fill="rgba(176,125,43,.10)"/>`;
  s += `<rect x="${x(sel) - 14}" y="${M.t}" width="28" height="${H - M.t - M.b}" fill="rgba(11,58,102,.06)"/>`;
  [["euros", "#b07d2b"], ["volum", "#0b3a66"]].forEach(([k, c]) => {
    s += `<polyline points="${MESOS.map((m, i) => `${x(i)},${y(m[k])}`).join(" ")}" fill="none" stroke="${c}" stroke-width="2.6"/>`;
    MESOS.forEach((m, i) => s += `<circle cx="${x(i)}" cy="${y(m[k])}" r="${i === sel ? 5 : 3.2}" fill="${i === sel ? c : "#fff"}" stroke="${c}" stroke-width="2"/>`);
  });
  MESOS.forEach((m, i) => {
    s += `<text x="${x(i)}" y="${H - 12}" text-anchor="middle" style="${i === sel ? "font-weight:800;fill:#1a2b3a" : ""}">${curt(m.mes)}</text>`;
    s += `<rect x="${x(i) - 22}" y="0" width="44" height="${H}" fill="transparent" style="cursor:pointer" data-i="${i}"><title>${nom(m.mes)}: ${fmt(m.euros)}% en euros, ${fmt(m.volum)}% en volum</title></rect>`;
  });
  const g = document.getElementById("g1");
  g.innerHTML = s;
  g.querySelectorAll("rect[data-i]").forEach(r => r.onclick = () => { sel = +r.dataset.i; document.getElementById("mes-ajuda").style.display = "none"; mostra(); });
}

const part = Math.round((ANY.euros - ANY.volum) / ANY.euros * 100);
document.querySelector("#ins1 span").innerHTML =
  `En els últims 12 mesos, l'Indicador creix un <b>${fmt(ANY.euros)}%</b> de mitjana en euros i un <b>${fmt(ANY.volum)}%</b> en volum. ` +
  `Prop ${part >= 40 && part < 50 ? "de la meitat" : "d'un " + part + "%"} del creixement que es publica correspon a l'augment de preus.`;

document.getElementById("nota2").textContent =
  `Variació interanual en volum, mitjana de ${nom(ANY.des)} a ${nom(ANY.fins)}. Tot a preus constants, perquè les xifres siguin comparables.`;
const max = Math.max(...COMP.map(c => Math.abs(c.v)));
document.getElementById("barres").innerHTML = COMP.map(c => {
  const w = Math.abs(c.v) / (2 * max) * 100, left = c.v >= 0 ? 50 : 50 - w;
  const col = c.nom === "Comertia" ? "#b07d2b" : (c.v < 0 ? "#c0392b" : "#0b3a66");
  return `<div class="bar-row ${c.nom === "Comertia" ? "com" : ""}"><div class="n">${c.nom}</div>
    <div class="track"><div class="zero" style="left:50%"></div><div class="fill" style="left:${left}%;width:${w}%;background:${col}"></div></div>
    <div class="val" style="color:${c.v < 0 ? "#c0392b" : "#1a2b3a"}">${fmt(c.v)}%</div></div>`;
}).join("");

mostra();
</script>
</body>
</html>
"""


def main():
    mesos, comparativa, resum_any = carrega()
    html = (HTML.replace("__MESOS__", json.dumps(mesos, ensure_ascii=False))
                .replace("__COMP__", json.dumps(comparativa, ensure_ascii=False))
                .replace("__ANY__", json.dumps(resum_any, ensure_ascii=False)))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Escrit: {OUT}")
    print(f"  Últim any: {resum_any['euros']}% en euros, {resum_any['volum']}% en volum")
    print("  Comparativa:", ", ".join(f"{c['nom']} {c['v']}" for c in comparativa))


if __name__ == "__main__":
    main()
