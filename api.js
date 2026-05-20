// ═══════════════════════════════════════════════════════════
//  api.js — Comunicação com a API FastAPI + utilitários
// ═══════════════════════════════════════════════════════════

const BASE = '';

async function apiFetch(path, opts = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Erro ${res.status}`);
  }
  return res.json();
}

// ── TRANSAÇÕES ───────────────────────────────────────────

const API = {
  listar:    (p = {}) => apiFetch('/api/transacoes?' + new URLSearchParams(p)),
  criar:     (body)   => apiFetch('/api/transacoes',    { method: 'POST',   body: JSON.stringify(body) }),
  atualizar: (id, b)  => apiFetch(`/api/transacoes/${id}`, { method: 'PUT', body: JSON.stringify(b) }),
  deletar:   (id)     => apiFetch(`/api/transacoes/${id}`, { method: 'DELETE' }),
  relatorio: (p = {}) => apiFetch('/api/relatorio?'    + new URLSearchParams(p)),
  anos:      ()       => apiFetch('/api/anos'),
  clusters:  (p = {}) => apiFetch('/api/clusters?'     + new URLSearchParams(p)),
};

// ── HELPERS UI ───────────────────────────────────────────

const MESES_NOME = [
  '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
];

function fmtBRL(v) {
  return 'R$ ' + Number(v).toFixed(2)
    .replace('.', ',')
    .replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

// Preenche select de meses — síncrono, sem depender da API
function mesOptions(sel, valorSel) {
  sel.innerHTML = MESES_NOME.slice(1).map((n, i) =>
    `<option value="${i + 1}" ${(i + 1) === valorSel ? 'selected' : ''}>${n}</option>`
  ).join('');
}

// Preenche select de anos — tenta API, cai para ano atual se falhar
async function anoOptions(sel, valorSel, incluiTodos = false) {
  let anos = [];
  try {
    anos = await API.anos();
  } catch (_) {
    // servidor offline ou sem dados: usa o ano atual
  }
  const cur = new Date().getFullYear();
  if (!anos.includes(cur)) anos.unshift(cur);

  const vazio = incluiTodos ? '<option value="">Todos</option>' : '';
  sel.innerHTML = vazio + anos.map(a =>
    `<option value="${a}" ${a === valorSel ? 'selected' : ''}>${a}</option>`
  ).join('');
}

function flash(msg, tipo = 'success') {
  const el = document.getElementById('flashArea');
  if (!el) return;
  el.innerHTML = `<div class="flash ${tipo}">${msg}</div>`;
  setTimeout(() => { if (el) el.innerHTML = ''; }, 3500);
}

function mostrarErroServidor(el) {
  el.innerHTML = `
    <div class="erro-servidor">
      <span class="icon">⚠️</span>
      <strong>Servidor não encontrado.</strong>
      <p>Verifique se o XAMPP está rodando e execute:<br>
      <code>uvicorn main:app --reload</code></p>
    </div>`;
}

// ── GRÁFICO BARRAS ───────────────────────────────────────

function desenharBarras(canvasId, evolucao) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.parentElement.offsetWidth, H = canvas.height;
  canvas.width = W;
  const P = { top: 24, right: 20, bottom: 40, left: 68 };
  const w = W - P.left - P.right, h = H - P.top - P.bottom;
  const maxVal = Math.max(...evolucao.map(e => e.ganhos), ...evolucao.map(e => e.gastos), 1);
  const n = evolucao.length, gw = w / n, bw = Math.min(gw * .28, 20);
  ctx.clearRect(0, 0, W, H);
  for (let i = 0; i <= 4; i++) {
    const y = P.top + h - h * i / 4;
    ctx.strokeStyle = 'rgba(42,48,69,.8)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(P.left, y); ctx.lineTo(P.left + w, y); ctx.stroke();
    const v = maxVal * i / 4;
    ctx.fillStyle = '#7a8299'; ctx.font = '11px DM Sans,sans-serif'; ctx.textAlign = 'right';
    ctx.fillText(v >= 1000 ? 'R$' + (v / 1000).toFixed(1) + 'k' : 'R$' + v.toFixed(0), P.left - 6, y + 4);
  }
  evolucao.forEach((e, i) => {
    const cx = P.left + gw * i + gw / 2;
    ctx.fillStyle = 'rgba(74,222,128,.85)';
    ctx.beginPath(); ctx.roundRect(cx - bw - 2, P.top + h - (e.ganhos / maxVal) * h, bw, (e.ganhos / maxVal) * h, [3, 3, 0, 0]); ctx.fill();
    ctx.fillStyle = 'rgba(248,113,113,.85)';
    ctx.beginPath(); ctx.roundRect(cx + 2, P.top + h - (e.gastos / maxVal) * h, bw, (e.gastos / maxVal) * h, [3, 3, 0, 0]); ctx.fill();
    ctx.fillStyle = '#7a8299'; ctx.font = '11px DM Sans,sans-serif'; ctx.textAlign = 'center';
    ctx.fillText(e.label, cx, P.top + h + 20);
  });
  [[W - 130, '#4ade80', 'Ganhos'], [W - 65, '#f87171', 'Gastos']].forEach(([x, c, l]) => {
    ctx.fillStyle = c; ctx.fillRect(x, 8, 11, 11);
    ctx.fillStyle = '#e8eaf0'; ctx.font = '11px DM Sans'; ctx.textAlign = 'left'; ctx.fillText(l, x + 15, 17);
  });
}

function desenharLinha(canvasId, evolucao) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.parentElement.offsetWidth, H = canvas.height;
  canvas.width = W;
  const P = { top: 20, right: 20, bottom: 36, left: 68 };
  const w = W - P.left - P.right, h = H - P.top - P.bottom;
  const todos = [...evolucao.map(e => e.ganhos), ...evolucao.map(e => e.gastos), ...evolucao.map(e => e.saldo)];
  const maxV = Math.max(...todos, 1), minV = Math.min(...todos, 0), span = maxV - minV || 1;
  const yPos = v => P.top + h - ((v - minV) / span) * h;
  const xPos = i => P.left + (w / (evolucao.length - 1)) * i;
  ctx.clearRect(0, 0, W, H);
  for (let i = 0; i <= 4; i++) {
    const y = P.top + h - h * i / 4;
    ctx.strokeStyle = 'rgba(42,48,69,.7)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(P.left, y); ctx.lineTo(P.left + w, y); ctx.stroke();
    const v = minV + span * i / 4;
    ctx.fillStyle = '#7a8299'; ctx.font = '11px DM Sans,sans-serif'; ctx.textAlign = 'right';
    ctx.fillText(v >= 1000 ? 'R$' + (v / 1000).toFixed(1) + 'k' : 'R$' + v.toFixed(0), P.left - 6, y + 4);
  }
  [['ganhos', '#4ade80'], ['gastos', '#f87171'], ['saldo', '#60a5fa']].forEach(([key, cor]) => {
    ctx.strokeStyle = cor; ctx.lineWidth = 2.5; ctx.lineJoin = 'round';
    ctx.beginPath();
    evolucao.forEach((e, i) => { i === 0 ? ctx.moveTo(xPos(i), yPos(e[key])) : ctx.lineTo(xPos(i), yPos(e[key])); });
    ctx.stroke();
    evolucao.forEach((e, i) => {
      ctx.beginPath(); ctx.arc(xPos(i), yPos(e[key]), 4, 0, 2 * Math.PI);
      ctx.fillStyle = cor; ctx.fill(); ctx.strokeStyle = '#0f1117'; ctx.lineWidth = 2; ctx.stroke();
    });
  });
  ctx.fillStyle = '#7a8299'; ctx.font = '11px DM Sans,sans-serif'; ctx.textAlign = 'center';
  evolucao.forEach((e, i) => ctx.fillText(e.label, xPos(i), P.top + h + 20));
}

function desenharDonutGG(canvasId, totalGanhos, totalGastos) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d'), S = 130;
  canvas.width = canvas.height = S;
  const total = totalGanhos + totalGastos; if (!total) return;
  let angle = -Math.PI / 2;
  [{ v: totalGanhos, c: '#4ade80' }, { v: totalGastos, c: '#f87171' }].forEach(f => {
    const sl = (f.v / total) * 2 * Math.PI;
    ctx.beginPath(); ctx.moveTo(65, 65); ctx.arc(65, 65, 52, angle, angle + sl);
    ctx.closePath(); ctx.fillStyle = f.c; ctx.fill(); angle += sl;
  });
  ctx.beginPath(); ctx.arc(65, 65, 32, 0, 2 * Math.PI); ctx.fillStyle = '#181c27'; ctx.fill();
}

function desenharScatter(canvasId, grupos, perfis) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.parentElement.offsetWidth, H = canvas.height;
  canvas.width = W;
  const P = { top: 30, right: 20, bottom: 42, left: 70 };
  const w = W - P.left - P.right, h = H - P.top - P.bottom;
  const todos = Object.values(grupos).flat();
  const maxV = Math.max(...todos.map(t => t.valor), 1), minV = Math.min(...todos.map(t => t.valor), 0), spanV = maxV - minV || 1;
  const xPos = mes => P.left + ((mes - 1) / 11) * w;
  const yPos = val => P.top + h - ((val - minV) / spanV) * h;
  ctx.clearRect(0, 0, W, H);
  for (let i = 0; i <= 4; i++) {
    const y = P.top + h - h * i / 4;
    ctx.strokeStyle = 'rgba(42,48,69,.7)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(P.left, y); ctx.lineTo(P.left + w, y); ctx.stroke();
    const v = minV + spanV * i / 4;
    ctx.fillStyle = '#7a8299'; ctx.font = '10px DM Sans'; ctx.textAlign = 'right';
    ctx.fillText(v >= 1000 ? 'R$' + (v / 1000).toFixed(1) + 'k' : 'R$' + v.toFixed(0), P.left - 6, y + 3);
  }
  ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'].forEach((m, i) => {
    if (i % 2 === 0) { ctx.fillStyle = '#7a8299'; ctx.font = '10px DM Sans'; ctx.textAlign = 'center'; ctx.fillText(m, xPos(i + 1), P.top + h + 18); }
  });
  Object.entries(grupos).forEach(([cid, txs]) => {
    const cor = perfis[cid]?.cor || '#60a5fa';
    txs.forEach(t => {
      ctx.beginPath(); ctx.arc(xPos(t.mes), yPos(t.valor), 5, 0, 2 * Math.PI);
      ctx.fillStyle = cor + 'cc'; ctx.fill(); ctx.strokeStyle = cor; ctx.lineWidth = 1.5; ctx.stroke();
    });
  });
  let lx = P.left;
  Object.entries(perfis).forEach(([cid, p]) => {
    const n = (grupos[cid] || []).length;
    ctx.fillStyle = p.cor; ctx.fillRect(lx, 8, 10, 10);
    ctx.fillStyle = '#e8eaf0'; ctx.font = '10px DM Sans'; ctx.textAlign = 'left';
    ctx.fillText(`${p.nome} (${n})`, lx + 14, 16);
    lx += ctx.measureText(`${p.nome} (${n})`).width + 28;
  });
}

function desenharCotovelo(canvasId, cotovelo, kAtual) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.parentElement.offsetWidth, H = canvas.height;
  canvas.width = W;
  const P = { top: 20, right: 20, bottom: 40, left: 60 };
  const w = W - P.left - P.right, h = H - P.top - P.bottom;
  const inercias = cotovelo.map(c => c.inercia);
  const maxI = Math.max(...inercias, 1), minI = Math.min(...inercias, 0), spanI = maxI - minI || 1;
  const n = cotovelo.length;
  const xPos = i => P.left + (i / (n - 1)) * w;
  const yPos = v => P.top + h - ((v - minI) / spanI) * h;
  ctx.clearRect(0, 0, W, H);
  for (let i = 0; i <= 4; i++) {
    const y = P.top + h - h * i / 4;
    ctx.strokeStyle = 'rgba(42,48,69,.7)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(P.left, y); ctx.lineTo(P.left + w, y); ctx.stroke();
    ctx.fillStyle = '#7a8299'; ctx.font = '10px DM Sans'; ctx.textAlign = 'right';
    ctx.fillText((minI + spanI * i / 4).toFixed(2), P.left - 6, y + 3);
  }
  ctx.strokeStyle = '#60a5fa'; ctx.lineWidth = 2.5; ctx.lineJoin = 'round';
  ctx.beginPath();
  cotovelo.forEach((c, i) => { i === 0 ? ctx.moveTo(xPos(i), yPos(c.inercia)) : ctx.lineTo(xPos(i), yPos(c.inercia)); });
  ctx.stroke();
  cotovelo.forEach((c, i) => {
    const ia = c.k === kAtual;
    ctx.beginPath(); ctx.arc(xPos(i), yPos(c.inercia), ia ? 7 : 4, 0, 2 * Math.PI);
    ctx.fillStyle = ia ? '#fbbf24' : '#60a5fa'; ctx.fill();
    if (ia) { ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.stroke(); }
    ctx.fillStyle = '#7a8299'; ctx.font = '10px DM Sans'; ctx.textAlign = 'center';
    ctx.fillText('k=' + c.k, xPos(i), P.top + h + 18);
  });
  const idx = cotovelo.findIndex(c => c.k === kAtual);
  if (idx >= 0) {
    ctx.fillStyle = '#fbbf24'; ctx.font = 'bold 10px DM Sans'; ctx.textAlign = 'center';
    ctx.fillText('← atual', xPos(idx), yPos(cotovelo[idx].inercia) - 12);
  }
}
