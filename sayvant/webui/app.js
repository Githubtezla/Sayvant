"use strict";
/* Sayvant Einstellungen. Python-Seite: sayvant/settings_app.py (window.pywebview.api).
   Texte sind deutsch und laufen durch t(); Englisch steht in i18n.js. */

const ICONS = {
  home: '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
  general: '<line x1="21" x2="14" y1="4" y2="4"/><line x1="10" x2="3" y1="4" y2="4"/><line x1="21" x2="12" y1="12" y2="12"/><line x1="8" x2="3" y1="12" y2="12"/><line x1="21" x2="16" y1="20" y2="20"/><line x1="12" x2="3" y1="20" y2="20"/><line x1="14" x2="14" y1="2" y2="6"/><line x1="8" x2="8" y1="10" y2="14"/><line x1="16" x2="16" y1="18" y2="22"/>',
  keyboard: '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01M8 12h.01M12 12h.01M16 12h.01M7 16h10"/>',
  wave: '<path d="M2 10v3"/><path d="M6 6v11"/><path d="M10 3v18"/><path d="M14 8v7"/><path d="M18 5v13"/><path d="M22 10v3"/>',
  sparkles: '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>',
  book: '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
  history: '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
  copy: '<rect width="14" height="14" x="8" y="8" rx="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>',
  trash: '<path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>',
  plus: '<path d="M5 12h14"/><path d="M12 5v14"/>',
  search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  zap: '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
  cpu: '<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2M15 20v2M2 15h2M2 9h2M20 15h2M20 9h2M9 2v2M9 20v2"/>',
  cloud: '<path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>',
  mouse: '<rect x="5" y="2" width="14" height="20" rx="7"/><path d="M12 6v4"/>',
  file: '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8M16 13H8M16 17H8"/>',
  off: '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/>',
  server: '<rect width="20" height="8" x="2" y="2" rx="2"/><rect width="20" height="8" x="2" y="14" rx="2"/><path d="M6 6h.01M6 18h.01"/>',
  route: '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/>',
  pen: '<path d="M12 20h9"/><path d="M16.376 3.622a1 1 0 0 1 3.002 3.002L7.368 18.635a2 2 0 0 1-.855.506l-2.872.838a.5.5 0 0 1-.62-.62l.838-2.872a2 2 0 0 1 .506-.854z"/>',
  hexagon: '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>',
  globe: '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
  languages: '<path d="m5 8 6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="m22 22-5-10-5 10"/><path d="M14 18h6"/>',
  mic: '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/>',
  clipboard: '<rect width="8" height="4" x="8" y="2" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>',
  bell: '<path d="M10.268 21a2 2 0 0 0 3.464 0"/><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"/>',
  power: '<path d="M12 2v10"/><path d="M18.4 6.6a9 9 0 1 1-12.77.04"/>',
  info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
  refresh: '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
  arrow: '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
  square: '<rect width="12" height="12" x="6" y="6" rx="2"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2m-7.07-14.07 1.41 1.41m11.32 11.32 1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>',
};
const icon = (n) => `<svg viewBox="0 0 24 24">${ICONS[n] || ""}</svg>`;

const PAGES = [
  ["home", "Übersicht", "home"],
  ["general", "Allgemein", "general"],
  ["hotkeys", "Kurzbefehle", "keyboard"],
  ["engine", "Erkennung", "wave"],
  ["cleanup", "Nachbearbeitung", "sparkles"],
  ["dictionary", "Wörterbuch", "book"],
  ["history", "Verlauf", "history"],
];

const KEY_LABELS = {
  de: { ctrl: "Strg", ctrl_l: "Strg links", ctrl_r: "Strg rechts", shift: "Umschalt", shift_l: "Umschalt links",
    shift_r: "Umschalt rechts", alt: "Alt", alt_l: "Alt", alt_r: "AltGr", win: "Win", win_l: "Win", win_r: "Win rechts",
    space: "Leertaste", esc: "Esc", capslock: "Feststell", enter: "Eingabe", menu: "Menü", tab: "Tab", backspace: "Rücktaste",
    pageup: "Bild auf", pagedown: "Bild ab", insert: "Einfg", delete: "Entf", home: "Pos1", end: "Ende", pause: "Pause",
    scrolllock: "Rollen", printscreen: "Druck" },
  en: { ctrl: "Ctrl", ctrl_l: "Left Ctrl", ctrl_r: "Right Ctrl", shift: "Shift", shift_l: "Left Shift",
    shift_r: "Right Shift", alt: "Alt", alt_l: "Alt", alt_r: "AltGr", win: "Win", win_l: "Win", win_r: "Right Win",
    space: "Space", esc: "Esc", capslock: "Caps Lock", enter: "Enter", menu: "Menu", tab: "Tab", backspace: "Backspace",
    pageup: "Page Up", pagedown: "Page Down", insert: "Insert", delete: "Delete", home: "Home", end: "End", pause: "Pause",
    scrolllock: "Scroll Lock", printscreen: "Print" },
};
const MOUSE_LABELS = { off: "Aus (Maus)", x1: "Maustaste 4 (Zurück)", x2: "Maustaste 5 (Vorwärts)", middle: "Mittlere Maustaste" };

const S = {
  cfg: null, saved: "", keys: {}, keyStates: {}, meta: null, page: "home", lang: "de",
  repl: [], snip: [], history: [], stats: null, q: "", capture: null, results: {}, connected: false,
  openEntries: new Set(), trial: { state: "idle", out: null }, meterTimer: null,
};

/* Hilfen */
const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const api = () => window.pywebview.api;

function t(text, vars) {
  let out = S.lang === "en" && window.EN && window.EN[text] !== undefined ? window.EN[text] : text;
  if (vars) for (const [k, v] of Object.entries(vars)) out = out.split("{" + k + "}").join(String(v));
  return out;
}
function resolveLang() {
  const v = S.cfg?.ui_language || "auto";
  S.lang = v === "auto" ? (S.meta?.windows_lang || "de") : v;
  document.documentElement.lang = S.lang;
  const a = S.cfg?.appearance || "auto";
  if (a === "auto") delete document.documentElement.dataset.theme;
  else document.documentElement.dataset.theme = a;
  document.documentElement.dataset.design = S.cfg?.design || "creme";
}
function designPicker() {
  const items = [
    ["creme", t("Creme"), t("Warm, Serifen, ruhig"), "Aa"],
    ["modern", t("Modern"), t("Windows 11, Indigo"), "Aa"],
    ["graphite", t("Graphit"), t("Schwarz-weiß, schlicht"), "Aa"],
  ];
  return `<div class="designs">${items.map(([id, name, desc, h]) => `
    <button class="design ${S.cfg.design === id ? "on" : ""}" data-action="set" data-path="design" data-value="${id}">
      <div class="prev ${id}"><div class="h">${h}</div><div class="l"></div><div class="b"></div></div>
      <div class="name">${name}</div><div class="desc">${desc}</div></button>`).join("")}</div>`;
}
const locale = () => (S.lang === "en" ? "en-GB" : "de-DE");
function getPath(obj, path) { return path.split(".").reduce((o, k) => (o == null ? undefined : o[k]), obj); }
function setPath(obj, path, value) {
  const parts = path.split(".");
  let o = obj;
  for (let i = 0; i < parts.length - 1; i++) o = o[parts[i]];
  o[parts[parts.length - 1]] = value;
}
function keyName(p) {
  const u = p.base_url || "";
  if (u.includes("openrouter.ai")) return "openrouter";
  if (u.includes("api.openai.com")) return "openai";
  return "api:" + p.id;
}
function activeProfile() {
  const ps = S.cfg.api.profiles;
  return ps.find((p) => p.id === S.cfg.api.profile) || ps[0];
}
function pretty(combo) {
  if (!combo) return [];
  const labels = KEY_LABELS[S.lang] || KEY_LABELS.de;
  return combo.split("+").map((k) => labels[k] || k.toUpperCase());
}
function keycaps(combo) {
  const parts = pretty(combo);
  if (!parts.length) return `<span class="keys"><span class="none">${t("Nicht belegt")}</span></span>`;
  return `<span class="keys">${parts.map((p) => `<kbd class="keycap">${esc(p)}</kbd>`).join('<span class="plus">+</span>')}</span>`;
}
const fmt = (n) => Number(n || 0).toLocaleString(locale());

/* Bausteine */
function toggle(path, extra = "") {
  return `<label class="switch"><input type="checkbox" data-bind="${path}" ${getPath(S.cfg, path) ? "checked" : ""} ${extra}><span class="track"></span></label>`;
}
function select(path, options) {
  const v = String(getPath(S.cfg, path) ?? "");
  return `<select class="select" data-bind="${path}">${Object.entries(options).map(([k, label]) =>
    `<option value="${esc(k)}" ${k === v ? "selected" : ""}>${esc(label)}</option>`).join("")}</select>`;
}
function seg(path, options, rerender = true) {
  const v = String(getPath(S.cfg, path));
  return `<div class="seg">${Object.entries(options).map(([k, label]) =>
    `<button data-action="seg" data-path="${path}" data-value="${esc(k)}" ${rerender ? 'data-rerender="1"' : ""} class="${v === k ? "on" : ""}">${esc(label)}</button>`).join("")}</div>`;
}
function row(title, desc, control, opts = {}) {
  return `<div class="row ${opts.disabled ? "disabled" : ""}">
    ${opts.icon ? `<div class="row-icon">${icon(opts.icon)}</div>` : ""}
    <div class="row-text"><div class="row-title">${title}</div>${desc ? `<div class="row-desc">${desc}</div>` : ""}</div>
    <div class="row-control">${control}</div></div>`;
}
function card(inner, head) {
  return `<section class="card">${head ? `<div class="card-head"><div><h3>${head[0]}</h3>${head[1] ? `<p>${head[1]}</p>` : ""}</div></div>` : ""}${inner}</section>`;
}
function pageHead(eyebrow, title, sub, right = "") {
  return `<div class="page-head"><div><div class="eyebrow">${eyebrow}</div><h1 class="page-title">${title}</h1><p class="page-sub">${sub}</p></div>${right}</div>`;
}
function choiceCard(path, val, ic, title, desc) {
  const on = String(getPath(S.cfg, path)) === val;
  return `<button class="choice ${on ? "on" : ""}" data-action="set" data-path="${path}" data-value="${val}">
    <span class="check">${icon("check")}</span><span class="choice-icon">${icon(ic)}</span>
    <span class="choice-title">${title}</span><span class="choice-desc">${desc}</span></button>`;
}
function keyState(name) {
  if (name in S.keys) return S.keys[name] ? `<span class="badge accent">${t("Wird gespeichert")}</span>` : `<span class="badge warn">${t("Wird entfernt")}</span>`;
  return S.keyStates[name] ? `<span class="badge ok">${icon("check")}${t("Hinterlegt")}</span>` : `<span class="badge">${t("Kein Schlüssel")}</span>`;
}
function keyField(name, placeholder) {
  const val = typeof S.keys[name] === "string" ? S.keys[name] : "";
  return `<div class="field-line">
    <input class="input mono" type="password" autocomplete="off" spellcheck="false" placeholder="${esc(placeholder || t("Schlüssel einfügen"))}" data-key="${esc(name)}" value="${esc(val)}">
    ${keyState(name)}
    ${(S.keyStates[name] || name in S.keys) ? `<button class="btn ghost small" data-action="key-remove" data-name="${esc(name)}">${t("Entfernen")}</button>` : ""}
  </div>`;
}
function result(id) {
  const r = S.results[id];
  if (!r) return "";
  return `<div class="result ${r.cls}">${icon(r.cls === "ok" ? "check" : r.cls === "bad" ? "x" : "info")}<span>${esc(r.text)}</span></div>`;
}
function engineLabel() {
  if (S.cfg.engine === "api") return activeProfile().name;
  return (S.meta.local_models[S.cfg.local.model] || S.cfg.local.model).split(" (")[0];
}
function cleanupLabel() {
  const names = { off: t("Aus"), claude: "Anthropic", openai: "OpenAI", openrouter: "OpenRouter", custom: t("Eigener Endpunkt") };
  return names[S.cfg.cleanup.mode] || S.cfg.cleanup.mode;
}

/* Seite: Übersicht */
function greeting() {
  const h = new Date().getHours();
  return h < 11 ? t("Guten Morgen") : h < 18 ? t("Guten Tag") : t("Guten Abend");
}
function trialCard() {
  const tr = S.trial;
  let out;
  if (tr.state === "recording") out = `<div class="trial-out empty">${t("Sprich jetzt. Klick auf Fertig, wenn du fertig bist.")}</div>`;
  else if (tr.state === "busy") out = `<div class="trial-out empty">${t("Erkenne …")}</div>`;
  else if (tr.out && tr.out.error) out = `<div class="result bad">${icon("x")}<span>${esc(tr.out.error)}</span></div>`;
  else if (tr.out && tr.out.final) out = `<div class="trial-out">${esc(tr.out.final)}</div>
      <div class="trial-meta"><span class="badge">${esc(tr.out.engine || "")}</span>${tr.out.total ? `<span class="badge">${tr.out.total} s</span>` : ""}
      ${tr.out.error_cleanup ? `<span class="badge warn">${esc(tr.out.error_cleanup)}</span>` : ""}
      ${tr.out.raw && tr.out.raw.trim() !== tr.out.final.trim() ? `<span class="badge teal">${t("nachbearbeitet")}</span>` : ""}</div>`;
  else if (tr.out) out = `<div class="trial-out empty">${esc(tr.out.note || t("Nichts gehört"))}</div>`;
  else out = `<div class="trial-out empty">${t("Hier erscheint, was Sayvant verstanden hat. Es wird nichts eingefügt.")}</div>`;
  const btn = tr.state === "recording"
    ? `<button class="btn primary" data-action="trial-stop">${icon("square")}${t("Fertig")}</button>`
    : `<button class="btn primary" data-action="trial-start" ${tr.state === "busy" || !S.connected ? "disabled" : ""}>${icon("mic")}${t("Testdiktat starten")}</button>`;
  const meter = `<div class="meter ${tr.state === "recording" ? "live" : ""}" id="meter">${"<span></span>".repeat(24)}</div>`;
  return card(`<div class="trial"><div class="trial-bar">${btn}${meter}</div>${out}</div>`,
    [t("Ausprobieren"), t("Sprich ein paar Sätze und sieh, was mit deinen Einstellungen herauskommt.")]);
}
function pageHome() {
  const st = S.stats;
  const hk = S.cfg.hotkeys;
  let welcome = "";
  if (S.meta.first_run) {
    welcome = `<section class="welcome"><div class="eyebrow">${t("Willkommen")}</div>
      <h2>${t("Sprechen statt tippen, in jedem Programm.")}</h2>
      <p>${t("Sayvant wandelt deine Stimme direkt dort in Text um, wo dein Cursor steht. Die Erkennung läuft lokal auf diesem PC.")}</p>
      <div class="steps3"><span class="s"><i>1</i>${t("Cursor in ein Textfeld setzen")}</span><span class="s"><i>2</i>${t("{key} halten und sprechen", { key: esc(pretty(hk.hold).join(" + ")) })}</span><span class="s"><i>3</i>${t("Loslassen")}</span></div>
      <button class="btn primary" data-action="welcome-done">${t("Verstanden")}</button></section>`;
  }
  const stats = st ? `<div class="stats">
      <div class="stat"><div class="stat-label">${t("Heute")}</div><div class="stat-value">${fmt(st.words_today)}<small>${t("Wörter")}</small></div></div>
      <div class="stat"><div class="stat-label">${t("Insgesamt")}</div><div class="stat-value">${fmt(st.words)}<small>${t("Wörter")}</small></div></div>
      <div class="stat"><div class="stat-label">${t("Zeit gespart")}</div><div class="stat-value">${fmt(st.saved_minutes)}<small>${t("Min.")}</small></div></div>
      <div class="stat"><div class="stat-label">${t("Tempo")}</div><div class="stat-value">${st.wpm ? fmt(st.wpm) : "–"}<small>${t("Wörter/Min.")}</small></div></div>
    </div>` : "";
  let week = "";
  if (st) {
    const max = Math.max(1, ...st.week.map((d) => d.words));
    const bars = st.week.map((d) => {
      const day = new Date(d.day + "T12:00:00").toLocaleDateString(locale(), { weekday: "short" });
      const h = d.words ? Math.max(8, Math.round((d.words / max) * 92)) : 4;
      return `<div class="bar-wrap" title="${fmt(d.words)} ${t("Wörter")}"><div class="bar ${d.words ? "" : "zero"}" style="height:${h}px"></div><div class="bar-label">${esc(day)}</div></div>`;
    }).join("");
    week = card(`<div class="week">${bars}</div><div class="week-foot"><span>${t("Wörter pro Tag, letzte 7 Tage")}</span><span>${fmt(st.count)} ${t("Diktate insgesamt")}</span></div>`,
      [t("Deine Woche"), ""]);
  }
  const how = card(`<div class="how">
      <div class="how-item"><b>${t("Halten")}</b>${keycaps(hk.hold)}<span>${t("Gedrückt halten, sprechen, loslassen.")}</span></div>
      <div class="how-item"><b>${t("Freihändig")}</b>${keycaps([hk.hold, hk.handsfree_key].filter(Boolean).join("+"))}<span>${t("Danach loslassen und frei weitersprechen.")}</span></div>
      <div class="how-item"><b>${t("Maus")}</b><span class="keys"><kbd class="keycap">${esc(t(MOUSE_LABELS[hk.mouse_button] || ""))}</kbd></span><span>${hk.mouse_button === "off" ? t("Nicht belegt") : t("Halten oder kurz klicken.")}</span></div>
    </div>`, [t("So diktierst du"), ""]);
  const setup = `<div class="section-title">${t("Einrichtung")}</div><div class="setup">
      <button data-action="nav" data-page="engine"><span class="k">${t("Erkennung")}</span><span class="v">${icon(S.cfg.engine === "api" ? "cloud" : "cpu")}${esc(engineLabel())}</span></button>
      <button data-action="nav" data-page="cleanup"><span class="k">${t("Nachbearbeitung")}</span><span class="v">${icon("sparkles")}${esc(cleanupLabel())}</span></button>
      <button data-action="nav" data-page="general"><span class="k">${t("Sprache")}</span><span class="v">${icon("globe")}${esc(S.meta.languages[S.cfg.language] || S.cfg.language)}</span></button>
    </div>`;
  return `<div class="hero"><div class="eyebrow">Sayvant</div><h1>${greeting()}</h1><p>${t("Halte {key} gedrückt und sprich. Der Text erscheint dort, wo dein Cursor steht.", { key: esc(pretty(hk.hold).join(" + ") || "…") })}</p></div>` +
    welcome + stats + week + trialCard() + how + setup;
}

/* Seite: Allgemein */
function pageGeneral() {
  const c = S.cfg;
  const devices = { "": t("Standardgerät von Windows") };
  for (const d of S.meta.devices) devices[d] = d;
  if (c.audio.device && !(c.audio.device in devices)) devices[c.audio.device] = c.audio.device + " " + t("(nicht verbunden)");
  return pageHead(t("Einstellungen"), t("Allgemein"), t("Sprache, Mikrofon und wie der Text in deinen Programmen landet.")) +
    `<div class="section-title">${t("Darstellung")}</div>` +
    card(designPicker(), [t("Design"), t("Wirkt sofort, auch auf die Anzeige am Bildschirmrand und das Symbol.")]) +
    card(row(t("Sprache der Oberfläche"), t("Folgt standardmäßig der Sprache von Windows."), select("ui_language", S.meta.ui_languages), { icon: "languages" }) +
      row(t("Farbschema"), t("Hell, dunkel oder passend zu Windows."), seg("appearance", { auto: t("Wie Windows"), light: t("Hell"), dark: t("Dunkel") }), { icon: "sun" })) +
    `<div class="section-title">${t("Aufnahme")}</div>` +
    card(
      row(t("Sprache des Diktats"), t("Automatisch erkennt Deutsch, Englisch und 23 weitere Sprachen."), select("language", S.meta.languages), { icon: "globe" }) +
      row(t("Mikrofon"), t("Wird nur während des Diktierens geöffnet."), select("audio.device", devices) +
        `<button class="btn small" data-action="meter-toggle">${S.meterTimer ? t("Stopp") : t("Pegel prüfen")}</button>`, { icon: "mic" }) +
      (S.meterTimer ? `<div class="row"><div class="row-text"><div class="row-desc">${t("Sprich etwas, die Balken sollten sich bewegen.")}</div></div><div class="meter live" id="meter">${"<span></span>".repeat(32)}</div></div>` : "") +
      row(t("Signaltöne"), t("Kurzer Ton bei Start und Ende der Aufnahme."), toggle("audio.sounds"), { icon: "bell" })
    ) +
    `<div class="section-title">${t("Einfügen")}</div>` +
    card(
      row(t("Methode"), c.paste.method === "type" ? t("Tippt Zeichen für Zeichen. Zeilenumbrüche lösen in Chats das Senden aus.") : t("Fügt per Strg+V ein. Schnell und zuverlässig."),
        seg("paste.method", { clipboard: t("Zwischenablage"), type: t("Tippen") }), { icon: "clipboard" }) +
      row(t("Diktat in der Zwischenablage lassen"), t("Danach mit Strg+V beliebig oft erneut einfügbar."), toggle("paste.keep_in_clipboard", 'data-rerender="1"')) +
      row(t("Vorherigen Inhalt wiederherstellen"), t("Holt nach dem Einfügen zurück, was vorher in der Zwischenablage lag."), toggle("paste.restore_clipboard"), { disabled: c.paste.keep_in_clipboard }) +
      row(t("Aus dem Verlauf von Win+V heraushalten"), t("Strg+V funktioniert trotzdem, das Diktat erscheint nur nicht in der Win+V-Liste."), toggle("paste.keep_out_of_history")) +
      row(t("Leerzeichen anhängen"), t("Damit der nächste Satz nicht direkt am letzten klebt."), toggle("paste.trailing_space"))
    ) +
    `<div class="section-title">${t("Programm")}</div>` +
    card(
      row(t("Mit Windows starten"), t("Sayvant liegt nach der Anmeldung bereit im Infobereich."), toggle("autostart"), { icon: "power" }) +
      row(t("Anzeige am Bildschirmrand"), t("Die kleine Pille unten zeigt Pegel und Status."), toggle("overlay.enabled")) +
      row(t("Verlauf speichern"), t("Diktate bleiben lokal auf diesem PC."), toggle("history.enabled", 'data-rerender="1"'), { icon: "history" }) +
      row(t("Aufbewahrung"), t("Ältere Einträge werden beim Start gelöscht. 0 heißt unbegrenzt."),
        `<input class="input num" type="number" min="0" max="3650" data-bind="history.keep_days" value="${esc(c.history.keep_days)}"><span class="row-desc">${t("Tage")}</span>`,
        { disabled: !c.history.enabled })
    );
}

/* Seite: Kurzbefehle */
function hotkeyRow(field, title, desc) {
  const control = S.capture === field
    ? `<span class="capturing"><span class="pulse"></span>${t("Tasten drücken …")}</span><button class="btn small" data-action="capture-cancel">${t("Abbrechen")}</button>`
    : `${keycaps(S.cfg.hotkeys[field])}
       <button class="btn small" data-action="capture" data-field="${field}" ${S.connected ? "" : "disabled"}>${t("Ändern")}</button>
       ${S.cfg.hotkeys[field] ? `<button class="btn ghost small icon" title="${t("Entfernen")}" data-action="hk-clear" data-field="${field}">${icon("x")}</button>` : ""}`;
  return row(title, desc, control);
}
function pageHotkeys() {
  const hk = S.cfg.hotkeys;
  const mouse = {};
  for (const [k, v] of Object.entries(MOUSE_LABELS)) mouse[k] = t(v);
  return pageHead(t("Einstellungen"), t("Kurzbefehle"), t("Halten, sprechen, loslassen. Mit Tastatur oder Maus.")) +
    (S.connected ? "" : `<div class="note warn">${icon("info")}<span>${t("Sayvant läuft gerade nicht. Tasten lassen sich nur aufnehmen, während Sayvant im Infobereich läuft.")}</span></div>`) +
    `<div class="section-title">${t("Tastatur")}</div>` +
    card(
      hotkeyRow("hold", t("Halten zum Sprechen"), t("Kurzes Antippen und Kombinationen wie Strg+C lösen nichts aus.")) +
      hotkeyRow("handsfree_key", t("Freihändig weitersprechen"), t("Während des Haltens zusätzlich drücken. Beenden mit der Haltetaste oder Klick auf die Pille.")) +
      hotkeyRow("toggle", t("Eigener Umschalter"), t("Startet und stoppt eine freihändige Aufnahme, z. B. F9.")) +
      hotkeyRow("cancel", t("Abbrechen"), t("Verwirft die laufende Aufnahme.")) +
      row(t("Mindestdauer zum Halten"), t("Kürzeres Drücken zählt als normales Tippen."),
        `<div class="range"><input type="range" min="0" max="1000" step="50" data-bind="hotkeys.min_hold_ms" value="${esc(hk.min_hold_ms)}"><span class="range-val" id="minhold">${esc(hk.min_hold_ms)} ms</span></div>`)
    ) +
    `<div class="section-title">${t("Maus")}</div>` +
    card(
      row(t("Maustaste"), t("Die gewählte Taste verliert ihre normale Funktion, z. B. Vor im Browser."), select("hotkeys.mouse_button", mouse), { icon: "mouse" }) +
      row(t("Verhalten"), "", seg("hotkeys.mouse_mode", { auto: t("Halten oder Klicken"), hold: t("Nur halten"), toggle: t("Klick an/aus") }, false), { disabled: hk.mouse_button === "off" })
    );
}

/* Seite: Erkennung */
function pageEngine() {
  const c = S.cfg;
  let detail;
  if (c.engine === "local") {
    const prov = { cpu: t("Prozessor (CPU)"), directml: S.meta.dml ? t("Grafikkarte (DirectML)") : t("Grafikkarte (nicht installiert)") };
    detail = card(
      row(t("Modell"), t("Parakeet ist auf der CPU am schnellsten. Whisper kann mehr Sprachen, ist aber deutlich langsamer."), select("local.model", S.meta.local_models)) +
      row(t("Ausführung"), "", seg("local.provider", prov, false)) +
      row(t("Genauigkeit"), t("int8 ist kleiner und schneller bei kaum sichtbarem Unterschied."), seg("local.quantization", { int8: "int8", "": t("Voll") }, false)),
      [t("Lokale Erkennung"), t("Läuft offline auf diesem PC. Das Modell wird beim ersten Mal einmalig geladen.")]);
  } else {
    const p = activeProfile();
    const idx = c.api.profiles.indexOf(p);
    const kn = keyName(p);
    const tabs = c.api.profiles.map((x) => `<button class="tab ${x.id === p.id ? "on" : ""}" data-action="profile" data-id="${esc(x.id)}">${esc(x.name || "…")}</button>`).join("") +
      `<button class="tab add" data-action="profile-add">${icon("plus")}${t("Neu")}</button>`;
    const shared = kn === "openrouter" ? t("Der Schlüssel gilt auch für die Nachbearbeitung über OpenRouter.")
      : kn === "openai" ? t("Der Schlüssel gilt auch für die Nachbearbeitung über OpenAI.") : "";
    detail = card(`<div class="tabs">${tabs}</div>
      <div class="form">
        <label>${t("Name")}</label><input class="input" data-bind="api.profiles.${idx}.name" data-rerender-blur="1" value="${esc(p.name)}">
        <label>${t("Typ")}</label>${select(`api.profiles.${idx}.kind`, S.meta.kinds)}
        <label>${t("Basis-URL")}</label><input class="input mono" spellcheck="false" data-bind="api.profiles.${idx}.base_url" data-rerender-blur="1" value="${esc(p.base_url)}">
        <label>${t("Modell")}</label><div class="field-line"><input class="input mono" spellcheck="false" list="model-list" data-bind="api.profiles.${idx}.model" value="${esc(p.model)}">
          ${kn === "openrouter" ? `<button class="btn small" data-action="or-models">${icon("refresh")}${t("Audiomodelle laden")}</button>` : ""}</div>
        <datalist id="model-list">${(S.meta.or_models || []).map((m) => `<option value="${esc(m)}">`).join("")}</datalist>
        <label>${t("API-Schlüssel")}</label>${keyField(kn)}
        <span></span><div class="field-line"><button class="btn" data-action="test-profile">${icon("zap")}${t("Verbindung testen")}</button>
          ${c.api.profiles.length > 1 ? `<button class="btn ghost danger" data-action="profile-delete">${icon("trash")}${t("Profil löschen")}</button>` : ""}</div>
        ${S.results.profile ? `<span></span>${result("profile")}` : ""}
        ${shared ? `<span></span><div class="row-desc">${shared}</div>` : ""}
      </div>`, [t("Aktives Profil"), t("Der markierte Anbieter wird für jedes Diktat genutzt.")]) +
      card(
        row(t("Bei Fehlern lokal erkennen"), t("Fällt die API aus, erkennt Sayvant offline weiter."), toggle("api.fallback_local")) +
        row(t("Zeitlimit"), t("Wie lange auf die API gewartet wird."), `<input class="input num" type="number" min="5" max="300" data-bind="api.timeout" value="${esc(c.api.timeout)}"><span class="row-desc">${t("Sekunden")}</span>`)
      );
  }
  return pageHead(t("Einstellungen"), t("Erkennung"), t("Wo aus deiner Stimme Text wird.")) +
    `<div class="choices">${choiceCard("engine", "local", "cpu", t("Lokal"), t("Offline, kostenlos, privat"))}${choiceCard("engine", "api", "cloud", t("API-Anbieter"), t("OpenAI, Groq, OpenRouter oder eigener Server"))}</div>` +
    detail + `<div class="note">${icon("info")}<span>${t("Anthropic nimmt kein Audio an. Claude gibt es deshalb in der Nachbearbeitung.")}</span></div>`;
}

/* Seite: Nachbearbeitung */
function providerForm(kind) {
  const c = S.cfg.cleanup;
  const model = (path, list) => `<input class="input mono" spellcheck="false" list="${path}-list" data-bind="cleanup.${path}" value="${esc(c[path])}">
      <datalist id="${path}-list">${list.map((m) => `<option value="${esc(m)}">`).join("")}</datalist>`;
  const test = (provider) => `<span></span><div class="field-line"><button class="btn" data-action="test-cleanup" data-provider="${provider}">${icon("zap")}${t("Schlüssel testen")}</button></div>
      ${S.results[provider] ? `<span></span>${result(provider)}` : ""}`;
  if (kind === "claude") return card(`<div class="form"><label>${t("Modell")}</label>${model("claude_model", S.meta.claude_models)}
      <label>${t("API-Schlüssel")}</label>${keyField("claude", "sk-ant-…")}${test("claude")}</div>`,
    ["Anthropic", t("Claude direkt über die Anthropic-API. Haiku ist schnell und günstig.")]);
  if (kind === "openai") return card(`<div class="form"><label>${t("Modell")}</label>${model("openai_model", S.meta.openai_models)}
      <label>${t("API-Schlüssel")}</label>${keyField("openai", "sk-…")}${test("openai")}</div>`,
    ["OpenAI", t("Direkt über die OpenAI-API. Der Schlüssel gilt auch für die Erkennung über OpenAI.")]);
  if (kind === "openrouter") return card(`<div class="form"><label>${t("Modell")}</label>${model("openrouter_model", S.meta.or_cleanup_models)}
      <label>${t("API-Schlüssel")}</label>${keyField("openrouter", "sk-or-…")}${test("openrouter")}</div>`,
    ["OpenRouter", t("Ein Schlüssel für viele Modelle, auch Claude. Gilt auch für die Erkennung.")]);
  if (kind === "custom") return card(`<div class="form">
      <label>${t("Basis-URL")}</label><input class="input mono" spellcheck="false" data-bind="cleanup.custom_base_url" value="${esc(c.custom_base_url)}">
      <label>${t("Modell")}</label><input class="input mono" spellcheck="false" data-bind="cleanup.custom_model" value="${esc(c.custom_model)}">
      <label>${t("Schlüssel")}</label>${keyField("llm", t("Optional"))}</div>`,
    [t("Eigener Endpunkt"), t("Jeder OpenAI-kompatible Chat-Endpunkt, z. B. Ollama oder LM Studio auf diesem PC.")]);
  return "";
}
function pageCleanup() {
  const c = S.cfg.cleanup;
  const off = c.mode === "off";
  let style = card(
    row(t("Stufe"), c.level === "medium" ? t("Glättet zusätzlich Grammatik, löst Selbstkorrekturen auf und setzt Aufzählungen als Liste.") : t("Nur Füllwörter, Stottern und Zeichensetzung. Der Wortlaut bleibt."), seg("cleanup.level", S.meta.levels)) +
    row(t("Stil"), "", select("cleanup.style", S.meta.styles)) +
    row(t("Fenstertitel als Hinweis"), t("Hilft bei Namen und Tonfall. Gesendet wird sonst nur der erkannte Text."), toggle("cleanup.use_window_context")) +
    row(t("Eigene Regeln"), t("Ersetzt die eingebauten Anweisungen durch deine eigene Textdatei."), `<button class="btn" data-action="open-prompt">${icon("file")}${t("Bearbeiten")}</button>`),
    [t("Wie bereinigt wird"), off ? t("Wähle oben einen Anbieter, um die Nachbearbeitung einzuschalten.") : ""]);
  if (off) style = style.replace('<section class="card">', '<section class="card" style="opacity:.55;pointer-events:none">');
  return pageHead(t("Einstellungen"), t("Nachbearbeitung"), t("Füllwörter raus, Zeichensetzung rein, auf Wunsch ein anderer Ton.")) +
    `<div class="choices">
      ${choiceCard("cleanup.mode", "off", "off", t("Aus"), t("Rohtext der Erkennung"))}
      ${choiceCard("cleanup.mode", "claude", "pen", "Anthropic", "Claude")}
      ${choiceCard("cleanup.mode", "openai", "hexagon", "OpenAI", "GPT")}
      ${choiceCard("cleanup.mode", "openrouter", "route", "OpenRouter", t("Viele Modelle"))}
      ${choiceCard("cleanup.mode", "custom", "server", t("Eigener Endpunkt"), "Ollama, LM Studio")}
    </div>` + providerForm(c.mode) + style;
}

/* Seite: Wörterbuch */
function pairsEditor(kind, rows, leftPh, rightPh, multiline) {
  const items = rows.map(([k, v], i) => `<div class="pair">
      <input class="input" placeholder="${esc(leftPh)}" data-pair="${kind}" data-i="${i}" data-side="0" value="${esc(k)}">
      <span class="arrow">→</span>
      ${multiline ? `<textarea class="input" rows="1" placeholder="${esc(rightPh)}" data-pair="${kind}" data-i="${i}" data-side="1">${esc(v)}</textarea>`
        : `<input class="input" placeholder="${esc(rightPh)}" data-pair="${kind}" data-i="${i}" data-side="1" value="${esc(v)}">`}
      <button class="btn ghost icon" title="${t("Entfernen")}" data-action="pair-del" data-kind="${kind}" data-i="${i}">${icon("trash")}</button>
    </div>`).join("");
  return `<div class="pairs">${items || `<div class="pairs-empty">${t("Noch keine Einträge.")}</div>`}
    <div><button class="btn small" data-action="pair-add" data-kind="${kind}">${icon("plus")}${t("Eintrag hinzufügen")}</button></div></div>`;
}
function pageDictionary() {
  const terms = S.cfg.dictionary.terms;
  return pageHead(t("Einstellungen"), t("Wörterbuch"), t("Namen, Korrekturen und Textbausteine.")) +
    card(`<div class="card-body"><div class="chips" data-action="focus-chips">
        ${terms.map((x, i) => `<span class="chip">${esc(x)}<button data-action="term-del" data-i="${i}" title="${t("Entfernen")}">${icon("x")}</button></span>`).join("")}
        <input id="term-input" placeholder="${terms.length ? t("Weiteren Begriff eingeben, Enter") : t("Begriff eingeben und Enter drücken")}">
      </div></div>`, [t("Namen und Fachbegriffe"), t("So geschrieben, wie sie sein sollen. Hilft der Nachbearbeitung und der API-Erkennung.")]) +
    card(pairsEditor("repl", S.repl, t("Erkannt, z. B. clawed"), t("Richtig, z. B. Claude"), false), [t("Ersetzungen"), t("Wird immer ersetzt, als ganzes Wort, egal ob groß oder klein.")]) +
    card(pairsEditor("snip", S.snip, t("Auslöser, z. B. meine Adresse"), t("Text, der eingefügt wird"), true), [t("Textbausteine"), t("Sagst du nur den Auslöser, wird stattdessen der Text eingefügt.")]);
}

/* Seite: Verlauf */
function dayLabel(ts) {
  const d = new Date(ts * 1000), now = new Date();
  const start = (x) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime();
  const diff = Math.round((start(now) - start(d)) / 86400000);
  if (diff === 0) return t("Heute");
  if (diff === 1) return t("Gestern");
  return d.toLocaleDateString(locale(), { weekday: "long", day: "numeric", month: "long" });
}
function pageHistory() {
  const right = `<button class="btn ghost danger" data-action="history-clear" ${S.history.length ? "" : "disabled"}>${icon("trash")}${t("Alles löschen")}</button>`;
  let body = "";
  if (!S.history.length) {
    body = `<div class="empty"><div class="empty-icon">${icon(S.q ? "search" : "mic")}</div>
      <div><b>${S.q ? t("Nichts gefunden") : t("Noch keine Diktate")}</b></div>
      <div>${S.q ? t("Probier einen anderen Suchbegriff.") : t("Sobald du diktierst, erscheint der Text hier.")}</div></div>`;
  } else {
    let last = "";
    for (const e of S.history) {
      const day = dayLabel(e.ts);
      if (day !== last) { body += `<div class="day">${esc(day)}</div>`; last = day; }
      const time = new Date(e.ts * 1000).toLocaleTimeString(locale(), { hour: "2-digit", minute: "2-digit" });
      const open = S.openEntries.has(e.id);
      const cleaned = e.cleanup && e.cleanup !== "Textbaustein";
      body += `<article class="entry ${open ? "open" : ""}">
        <div class="entry-head"><span class="entry-time">${time}</span>
          <span class="badge">${esc(e.engine || "")}</span><span class="badge">${(e.seconds || 0).toFixed(1)} s</span>
          ${cleaned ? `<span class="badge teal">${icon("sparkles")}${t("nachbearbeitet")}</span>` : ""}
          ${e.cleanup === "Textbaustein" ? `<span class="badge accent">${t("Textbaustein")}</span>` : ""}
          ${e.window ? `<span class="badge" title="${esc(e.window)}">${esc(e.window.length > 40 ? e.window.slice(0, 40) + "…" : e.window)}</span>` : ""}
          <span class="entry-actions">
            <button class="btn ghost small" data-action="h-copy" data-id="${e.id}" data-field="final">${icon("copy")}${t("Kopieren")}</button>
            ${e.raw !== e.final ? `<button class="btn ghost small" data-action="h-copy" data-id="${e.id}" data-field="raw">${t("Rohtext")}</button>` : ""}
            <button class="btn ghost small icon" title="${t("Löschen")}" data-action="h-del" data-id="${e.id}">${icon("trash")}</button>
          </span></div>
        <div class="entry-text" data-action="h-open" data-id="${e.id}">${esc(e.final)}</div>
        ${open && e.raw !== e.final ? `<div class="entry-raw">${t("Rohtext")}: ${esc(e.raw)}</div>` : ""}
      </article>`;
    }
  }
  return pageHead(t("Sayvant"), t("Verlauf"), t("Alle Diktate, durchsuchbar. Klick auf einen Text zeigt ihn ganz."), right) +
    `<div class="page-head" style="margin-top:-8px"><div class="searchbox">${icon("search")}<input class="input" id="h-search" placeholder="${t("Verlauf durchsuchen")}" value="${esc(S.q)}"></div></div>` + body;
}

const RENDER = { home: pageHome, general: pageGeneral, hotkeys: pageHotkeys, engine: pageEngine, cleanup: pageCleanup, dictionary: pageDictionary, history: pageHistory };

/* Darstellung */
function renderChrome() {
  $("#nav").innerHTML = PAGES.map(([id, label, ic]) =>
    `<button class="${S.page === id ? "active" : ""}" data-action="nav" data-page="${id}">${icon(ic)}<span>${t(label)}</span></button>`).join("");
  $("#foot-links").innerHTML = `<button class="link" data-action="open-log">${t("Protokoll")}</button><button class="link" data-action="open-folder">${t("Datenordner")}</button><button class="link" data-action="open-repo" title="${esc(S.meta.repo_url)}">GitHub</button>`;
  $("#version").textContent = t("Version {v}", { v: S.meta.version });
  $("#savebar").innerHTML = `<div class="savebar-text"><span class="dotw"></span>${t("Ungespeicherte Änderungen")}</div>
    <div class="savebar-actions"><button class="btn ghost" data-action="discard">${t("Verwerfen")}</button>
    <button class="btn primary" data-action="save">${t("Speichern")} <kbd class="hint">${t("Strg+S")}</kbd></button></div>`;
}
function render(keepScroll = true) {
  const content = $("#content");
  const top = content.scrollTop;
  resolveLang();
  renderChrome();
  content.innerHTML = RENDER[S.page]();
  if (keepScroll) content.scrollTop = top;
  updateSavebar();
}
function dirty() { return JSON.stringify(S.cfg) !== S.saved || Object.keys(S.keys).length > 0; }
function updateSavebar() { $("#savebar").hidden = !dirty() || S.page === "history" || S.page === "home"; }
function toast(text, bad = false) {
  const el = document.createElement("div");
  el.className = "toast" + (bad ? " bad" : "");
  el.innerHTML = `<span class="t-icon">${icon(bad ? "x" : "check")}</span><span>${esc(text)}</span>`;
  $("#toasts").appendChild(el);
  setTimeout(() => { el.classList.add("out"); setTimeout(() => el.remove(), 220); }, bad ? 4200 : 2200);
}
function confirmDialog(title, text, okLabel) {
  return new Promise((resolve) => {
    const m = $("#modal");
    m.innerHTML = `<div class="modal"><h3>${esc(title)}</h3><p>${esc(text)}</p>
      <div class="modal-actions"><button class="btn ghost" data-m="0">${t("Abbrechen")}</button><button class="btn primary" data-m="1">${esc(okLabel || t("Löschen"))}</button></div></div>`;
    m.hidden = false;
    m.onclick = (ev) => {
      const b = ev.target.closest("[data-m]");
      if (!b && ev.target !== m) return;
      m.hidden = true;
      resolve(b ? b.dataset.m === "1" : false);
    };
  });
}

/* Daten */
function syncLists() {
  S.repl = Object.entries(S.cfg.dictionary.replacements || {});
  S.snip = Object.entries(S.cfg.snippets || {});
}
function writeLists() {
  S.cfg.dictionary.replacements = Object.fromEntries(S.repl.filter(([k]) => k.trim()).map(([k, v]) => [k.trim(), v]));
  S.cfg.snippets = Object.fromEntries(S.snip.filter(([k]) => k.trim()).map(([k, v]) => [k.trim(), v]));
}
async function load(page) {
  const st = await api().get_state();
  S.cfg = st.cfg; S.meta = st.meta; S.keyStates = st.keys; S.keys = {}; S.results = {};
  S.saved = JSON.stringify(S.cfg);
  if (page) S.page = page;
  syncLists();
  await loadPageData();
  render(false);
}
async function loadPageData() {
  if (S.page === "history") S.history = await api().history(S.q);
  if (S.page === "home") S.stats = await api().stats();
}
async function save() {
  if (!dirty()) return;
  writeLists();
  const langBefore = JSON.parse(S.saved).ui_language;
  const res = await api().save(S.cfg, S.keys);
  if (!res.ok) { toast(res.error || t("Speichern fehlgeschlagen"), true); return; }
  S.keyStates = res.keys; S.keys = {};
  S.saved = JSON.stringify(S.cfg);
  if (langBefore !== S.cfg.ui_language) { await load(); } else { render(); }
  toast(res.applied ? t("Gespeichert und übernommen") : t("Gespeichert"));
}
async function nav(page) {
  stopMeter();
  S.page = page;
  await loadPageData();
  render(false);
  $("#content").scrollTop = 0;
}

/* Pegelanzeige und Testdiktat */
function drawMeter(level) {
  const m = $("#meter");
  if (!m) return;
  const bars = m.children;
  const v = Math.min(1, Math.sqrt(Math.max(0, level)) * 3.4);
  S.meterHist = (S.meterHist || []).concat([v]).slice(-bars.length);
  for (let i = 0; i < bars.length; i++) {
    const x = S.meterHist[S.meterHist.length - bars.length + i] || 0;
    bars[i].style.height = Math.max(6, Math.round(x * 30)) + "px";
  }
}
function stopMeter() {
  if (S.meterTimer) { clearInterval(S.meterTimer); S.meterTimer = null; api().mic_stop(false); }
}
async function startMeter() {
  const r = await api().mic_start(S.cfg.audio.device || "");
  if (!r.ok) { toast(r.error || t("Mikrofon nicht verfügbar"), true); return false; }
  S.meterHist = [];
  S.meterTimer = setInterval(async () => drawMeter(await api().mic_level()), 70);
  return true;
}

/* Ereignisse */
const ACTIONS = {
  async nav(el) { await nav(el.dataset.page); },
  set(el) { setPath(S.cfg, el.dataset.path, el.dataset.value); S.results = {}; render(); },
  seg(el) {
    setPath(S.cfg, el.dataset.path, el.dataset.value);
    if (el.dataset.rerender) render();
    else { el.parentElement.querySelectorAll("button").forEach((b) => b.classList.toggle("on", b === el)); updateSavebar(); }
  },
  save, async discard() { await load(); toast(t("Änderungen verworfen")); },
  "key-remove"(el) { S.keys[el.dataset.name] = null; render(); },
  profile(el) { S.cfg.api.profile = el.dataset.id; S.results = {}; render(); },
  "profile-add"() {
    const id = Math.random().toString(16).slice(2, 10);
    S.cfg.api.profiles.push({ id, name: t("Profil {n}", { n: S.cfg.api.profiles.length + 1 }), kind: "transcriptions", base_url: "http://localhost:8000/v1", model: "" });
    S.cfg.api.profile = id; render();
  },
  async "profile-delete"() {
    const p = activeProfile();
    if (!(await confirmDialog(t("Profil löschen?"), t("Das Profil „{name}“ wird entfernt.", { name: p.name })))) return;
    if (keyName(p).startsWith("api:")) S.keys[keyName(p)] = null;
    S.cfg.api.profiles = S.cfg.api.profiles.filter((x) => x.id !== p.id);
    S.cfg.api.profile = S.cfg.api.profiles[0].id; render();
  },
  async "test-profile"() {
    const p = activeProfile(), n = keyName(p);
    S.results.profile = { cls: "info", text: t("Teste …") }; render();
    S.results.profile = await api().test_profile(p, n in S.keys ? (S.keys[n] || "") : null); render();
  },
  async "test-cleanup"(el) {
    const prov = el.dataset.provider;
    const model = { claude: S.cfg.cleanup.claude_model, openai: S.cfg.cleanup.openai_model, openrouter: S.cfg.cleanup.openrouter_model }[prov];
    S.results[prov] = { cls: "info", text: t("Teste …") }; render();
    S.results[prov] = await api().test_cleanup(prov, model, prov in S.keys ? (S.keys[prov] || "") : null); render();
  },
  async "or-models"() {
    S.results.profile = { cls: "info", text: t("Lade Modellliste …") }; render();
    const models = await api().openrouter_models();
    S.meta.or_models = models;
    S.results.profile = models.length ? { cls: "ok", text: t("{n} Modelle mit Audio-Eingang. Im Modellfeld zur Auswahl.", { n: models.length }) } : { cls: "bad", text: t("Liste nicht ladbar.") };
    render();
  },
  async capture(el) {
    const r = await api().capture_start();
    if (!r.ok) { toast(r.error || t("Aufnehmen nicht möglich"), true); return; }
    S.capture = el.dataset.field; render();
  },
  async "capture-cancel"() { await api().capture_cancel(); S.capture = null; render(); },
  "hk-clear"(el) { S.cfg.hotkeys[el.dataset.field] = ""; render(); },
  "open-prompt"() { api().open_prompt(); },
  "open-log"() { api().open_log(); },
  "open-folder"() { api().open_folder(); },
  "open-repo"() { api().open_url(S.meta.repo_url); },
  "focus-chips"(el, ev) { if (ev.target === el) $("#term-input").focus(); },
  "term-del"(el) { S.cfg.dictionary.terms.splice(+el.dataset.i, 1); render(); $("#term-input").focus(); },
  "pair-add"(el) { (el.dataset.kind === "repl" ? S.repl : S.snip).push(["", ""]); writeLists(); render(); },
  "pair-del"(el) { (el.dataset.kind === "repl" ? S.repl : S.snip).splice(+el.dataset.i, 1); writeLists(); render(); },
  "h-open"(el) { const id = +el.dataset.id; S.openEntries.has(id) ? S.openEntries.delete(id) : S.openEntries.add(id); render(); },
  async "h-copy"(el) { await api().history_copy(+el.dataset.id, el.dataset.field); toast(t("In die Zwischenablage kopiert")); },
  async "h-del"(el) { await api().history_delete(+el.dataset.id); S.history = await api().history(S.q); render(); },
  async "history-clear"() {
    if (!(await confirmDialog(t("Ganzen Verlauf löschen?"), t("Alle gespeicherten Diktate werden endgültig entfernt.")))) return;
    await api().history_clear(); S.history = await api().history(S.q); render(); toast(t("Verlauf gelöscht"));
  },
  async "welcome-done"() { await api().dismiss_welcome(); S.meta.first_run = false; render(); },
  async "meter-toggle"() {
    if (S.meterTimer) { stopMeter(); render(); return; }
    render(); if (await startMeter()) render();
  },
  async "trial-start"() {
    if (!(await startMeter())) return;
    S.trial = { state: "recording", out: null }; render();
    S.trialTimer = setTimeout(() => ACTIONS["trial-stop"](), 15000);
  },
  async "trial-stop"() {
    if (S.trial.state !== "recording") return;
    clearTimeout(S.trialTimer);
    clearInterval(S.meterTimer); S.meterTimer = null;
    S.trial = { state: "busy", out: null }; render();
    const r = await api().mic_stop(true);
    S.trial = { state: "idle", out: r.ok ? r : { error: r.error || t("Fehler") } };
    if (S.page === "home") S.stats = await api().stats();
    render();
  },
};

document.addEventListener("click", async (ev) => {
  const el = ev.target.closest("[data-action]");
  if (!el || el.disabled) return;
  const fn = ACTIONS[el.dataset.action];
  if (fn) await fn(el, ev);
});
document.addEventListener("input", (ev) => {
  const el = ev.target;
  if (el.dataset.bind) {
    let v = el.type === "checkbox" ? el.checked : el.value;
    if (el.type === "number" || el.type === "range") v = parseInt(v || "0", 10);
    setPath(S.cfg, el.dataset.bind, v);
    if (el.dataset.bind === "hotkeys.min_hold_ms") $("#minhold").textContent = v + " ms";
    if (el.dataset.bind === "audio.device" && S.meterTimer) { stopMeter(); }
    if (el.dataset.rerender || el.tagName === "SELECT") render(); else updateSavebar();
  } else if (el.dataset.key) {
    if (el.value) S.keys[el.dataset.key] = el.value; else delete S.keys[el.dataset.key];
    updateSavebar();
  } else if (el.dataset.pair) {
    (el.dataset.pair === "repl" ? S.repl : S.snip)[+el.dataset.i][+el.dataset.side] = el.value;
    writeLists(); updateSavebar();
  } else if (el.id === "h-search") {
    S.q = el.value;
    clearTimeout(S.searchTimer);
    S.searchTimer = setTimeout(async () => {
      S.history = await api().history(S.q); render();
      const s = $("#h-search"); s.focus(); s.setSelectionRange(s.value.length, s.value.length);
    }, 220);
  }
});
document.addEventListener("change", (ev) => {
  if (ev.target.dataset.key || ev.target.dataset.rerenderBlur) render();
});
document.addEventListener("keydown", (ev) => {
  if (ev.key === "s" && ev.ctrlKey) { ev.preventDefault(); save(); return; }
  if (ev.target.id === "term-input") {
    const v = ev.target.value.trim();
    if ((ev.key === "Enter" || ev.key === ",") && v) {
      ev.preventDefault();
      if (!S.cfg.dictionary.terms.includes(v)) S.cfg.dictionary.terms.push(v);
      render(); $("#term-input").focus();
    } else if (ev.key === "Backspace" && !ev.target.value && S.cfg.dictionary.terms.length) {
      S.cfg.dictionary.terms.pop(); render(); $("#term-input").focus();
    }
  }
});

/* Verbindung zur laufenden App */
async function poll() {
  if (S.hidden) return;
  let r;
  try { r = await api().poll(); } catch (e) { return; }
  const was = S.connected;
  S.connected = !!r.connected;
  $("#status").className = "status " + (!r.connected ? "" : r.state === "recording" ? "rec" : r.state === "busy" ? "busy" : "ok");
  $("#status-text").textContent = r.connected ? r.text : t("Läuft nicht");
  if (was !== S.connected && (S.page === "hotkeys" || S.page === "home") && S.trial.state === "idle") render();
  if (r.history_seq !== undefined && r.history_seq !== S.hseq) {
    const first = S.hseq === undefined;
    S.hseq = r.history_seq;
    if (!first && !S.q && (S.page === "history" || S.page === "home") && S.trial.state === "idle") { await loadPageData(); render(); }
  }
  if (S.capture && r.capture && r.capture.done) {
    let v = r.capture.value || "";
    if ((S.capture === "handsfree_key" || S.capture === "cancel") && v.includes("+")) v = v.split("+").pop();
    S.cfg.hotkeys[S.capture] = v;
    S.capture = null;
    render();
    toast(v ? t("Übernommen: {keys}", { keys: pretty(v).join(" + ") }) : t("Kurzbefehl entfernt"));
  }
}

window.addEventListener("pywebviewready", async () => {
  S.ready = true;
  await load(S.showPage || (await api().initial_page()));
  poll();
  setInterval(poll, 600);
});
window.addEventListener("focus", async () => {
  if (S.showing) return;
  if (S.cfg && !dirty() && !S.meterTimer && S.trial.state === "idle" && S.page !== "history") await load();
});

/* Vorgestartetes Fenster (settings_app.Background): Einblenden lädt den aktuellen Stand,
   Verstecken beendet Mikrofon und Aufnahme. Ungespeichertes verfällt wie beim Schließen. */
window.sayvantShow = async (page) => {
  S.hidden = false;
  if (!S.ready) { S.showPage = page; return; }
  S.showing = true;
  try {
    S.trial = { state: "idle", out: null }; S.openEntries = new Set();
    await load(page);
    $("#content").scrollTop = 0;
  } finally { S.showing = false; }
  poll();
};
window.sayvantHide = () => {
  S.hidden = true;
  stopMeter();
  clearTimeout(S.trialTimer);
  if (S.capture) { S.capture = null; api().capture_cancel(); }
  $("#modal").hidden = true;
};
