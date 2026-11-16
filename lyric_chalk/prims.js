// Hand-drawn chalk primitives (from lyric/chalkboard/chalk.html)
function rng(s) { return () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const cl = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const ease = v => { v = cl(v); return v * v * (3 - 2 * v); };
const C = { w: '#f4f1e8', y: '#ffe27a', o: '#ffb36b', p: '#ff9fb8', r: '#ff7a6b', g: '#9fe8a0', b: '#9fd2ff', v: '#c9a8ff' };

// ---------- hand-drawn primitives (return point lists) ----------
let R = rng(1);
function wob(pts, a = 2.2) { const s1 = R() * 9, s2 = R() * 9; return pts.map(([x, y], i) => [x + a * Math.sin(i * 0.21 + s1) + a * 0.5 * Math.sin(i * 0.77 + s2), y + a * Math.cos(i * 0.19 + s2) + a * 0.5 * Math.sin(i * 0.63 + s1)]); }
function L(x1, y1, x2, y2) { const n = Math.max(2, Math.hypot(x2 - x1, y2 - y1) / 6 | 0); return wob(Array.from({ length: n + 1 }, (_, i) => [x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n]), 1.6); }
function E(cx, cy, rx, ry, a0 = -Math.PI / 2, a1 = a0 + Math.PI * 2.08) { const n = Math.max(8, Math.abs(a1 - a0) * Math.max(rx, ry) / 6 | 0); return wob(Array.from({ length: n + 1 }, (_, i) => { const a = a0 + (a1 - a0) * i / n; return [cx + rx * Math.cos(a), cy + ry * Math.sin(a)]; }), 1.8); }
const Ci = (cx, cy, r, a0, a1) => E(cx, cy, r, r, a0, a1);
function B(p0, p1, p2, p3) { const n = 40; return wob(Array.from({ length: n + 1 }, (_, i) => { const t = i / n, u = 1 - t; return [u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0], u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1]]; }), 1.5); }
function P(arr) { let out = []; for (let i = 0; i < arr.length - 1; i++) { const s = L(...arr[i], ...arr[i + 1]); out = out.concat(i ? s.slice(1) : s); } return out; }
const S = (pts, col = C.w, w = 7) => ({ pts, col, w });
const T = (x, y, str, size, col = C.w) => ({ text: str, x, y, size, col });
// stick figure: feet centre (x,y), height h
function man(x, y, h, pose = 'stand', col = C.w, face = 'smile', flip = 1) {
  const q = (a, b) => [x + a * h * flip, y + b * h];
  let head = q(0, -0.86), neck = q(0, -0.73), hip = q(0, -0.40), arms, legs;
  const st = [];
  if (pose === 'sit') { head = q(-0.06, -0.58); neck = q(-0.05, -0.46); hip = q(0, -0.12);
    legs = [[hip, q(0.22, -0.32), q(0.38, -0.02)], [hip, q(0.18, -0.28), q(0.30, -0.02)]];
    arms = [[q(-0.04, -0.42), q(0.12, -0.64), q(-0.02, -0.70)], [q(-0.04, -0.42), q(-0.20, -0.62), q(-0.10, -0.70)]]; }
  else if (pose === 'hips') { arms = [[q(0, -0.66), q(0.2, -0.54), q(0.07, -0.42)], [q(0, -0.66), q(-0.2, -0.54), q(-0.07, -0.42)]]; legs = [[hip, q(0.08, -0.2), q(0.16, 0)], [hip, q(-0.08, -0.2), q(-0.16, 0)]]; }
  else if (pose === 'run') { head = q(0.08, -0.84); neck = q(0.06, -0.72);
    arms = [[q(0.05, -0.64), q(0.2, -0.52), q(0.3, -0.62)], [q(0.05, -0.64), q(-0.12, -0.5), q(-0.24, -0.58)]];
    legs = [[hip, q(0.18, -0.24), q(0.3, -0.04)], [hip, q(-0.1, -0.2), q(-0.3, -0.16)]]; }
  else if (pose === 'jump') { arms = [[q(0, -0.66), q(0.18, -0.86), q(0.26, -1.04)], [q(0, -0.66), q(-0.18, -0.86), q(-0.26, -1.04)]]; legs = [[hip, q(0.14, -0.22), q(0.1, -0.02)], [hip, q(-0.14, -0.22), q(-0.1, -0.02)]]; }
  else if (pose === 'walk') { arms = [[q(0, -0.66), q(0.12, -0.52), q(0.2, -0.42)], [q(0, -0.66), q(-0.1, -0.52), q(-0.16, -0.40)]]; legs = [[hip, q(0.1, -0.2), q(0.18, 0)], [hip, q(-0.06, -0.2), q(-0.14, 0)]]; }
  else if (pose === 'think') { arms = [[q(0, -0.66), q(0.16, -0.56), q(0.06, -0.78)], [q(0, -0.66), q(-0.16, -0.5), q(-0.12, -0.38)]]; legs = [[hip, q(0.07, -0.2), q(0.13, 0)], [hip, q(-0.07, -0.2), q(-0.13, 0)]]; }
  else if (pose === 'hold') { arms = [[q(0, -0.66), q(0.22, -0.56), q(0.36, -0.5)], [q(0, -0.66), q(-0.22, -0.56), q(-0.36, -0.5)]]; legs = [[hip, q(0.07, -0.2), q(0.13, 0)], [hip, q(-0.07, -0.2), q(-0.13, 0)]]; }
  else if (pose === 'up') { arms = [[q(0, -0.66), q(0.12, -0.8), q(0.16, -1.0)], [q(0, -0.66), q(-0.18, -0.52), q(-0.22, -0.38)]]; legs = [[hip, q(0.07, -0.2), q(0.13, 0)], [hip, q(-0.07, -0.2), q(-0.13, 0)]]; }
  else { arms = [[q(0, -0.66), q(0.16, -0.52), q(0.22, -0.38)], [q(0, -0.66), q(-0.16, -0.52), q(-0.22, -0.38)]]; legs = [[hip, q(0.07, -0.2), q(0.13, 0)], [hip, q(-0.07, -0.2), q(-0.13, 0)]]; }
  const r = h * 0.12, w = Math.max(4, h * 0.03);
  st.push(S(Ci(head[0], head[1], r), col, w));
  st.push(S(P([neck, hip]), col, w));
  arms.forEach(a => st.push(S(P(a), col, w))); legs.forEach(a => st.push(S(P(a), col, w)));
  if (face === 'smile') { st.push(S(E(head[0], head[1] + r * 0.1, r * 0.5, r * 0.4, 0.3, Math.PI - 0.3), col, w * 0.6)); st.push(S(Ci(head[0] - r * 0.35, head[1] - r * 0.25, 1.5), col, w * 0.8)); st.push(S(Ci(head[0] + r * 0.35, head[1] - r * 0.25, 1.5), col, w * 0.8)); }
  if (face === 'sad') { st.push(S(E(head[0], head[1] + r * 0.65, r * 0.45, r * 0.3, Math.PI + 0.3, 2 * Math.PI - 0.3), col, w * 0.6)); }
  return st;
}
function heart(x, y, s, col = C.p, w = 8) { return [S(B([x, y + s * 0.9], [x - s * 1.6, y - s * 0.2], [x - s * 0.6, y - s * 1.3], [x, y - s * 0.4]), col, w), S(B([x, y - s * 0.4], [x + s * 0.6, y - s * 1.3], [x + s * 1.6, y - s * 0.2], [x, y + s * 0.9]), col, w)]; }
function sun(x, y, r, col = C.y, n = 10, rl = 50) { const s = [S(Ci(x, y, r), col, 8)]; for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2; s.push(S(L(x + Math.cos(a) * (r + 14), y + Math.sin(a) * (r + 14), x + Math.cos(a) * (r + 14 + rl), y + Math.sin(a) * (r + 14 + rl)), col, 6)); } return s; }
function star(x, y, r, col = C.y) { return [S(L(x - r, y, x + r, y), col, 5), S(L(x, y - r, x, y + r), col, 5), S(L(x - r * 0.6, y - r * 0.6, x + r * 0.6, y + r * 0.6), col, 4), S(L(x + r * 0.6, y - r * 0.6, x - r * 0.6, y + r * 0.6), col, 4)]; }
function bird(x, y, s, col = C.w) { return [S(P([[x - s, y - s * 0.4], [x - s * 0.4, y - s * 0.1], [x, y + s * 0.2]]), col, 5), S(P([[x, y + s * 0.2], [x + s * 0.4, y - s * 0.1], [x + s, y - s * 0.4]]), col, 5)]; }
function note(x, y, s, col = C.y) { return [S(Ci(x, y, s * 0.35), col, 6), S(L(x + s * 0.33, y, x + s * 0.33, y - s * 1.3), col, 6), S(P([[x + s * 0.33, y - s * 1.3], [x + s * 0.9, y - s * 1.0]]), col, 6)]; }
function cross(x, y, s, col = C.r, w = 10) { return [S(L(x - s, y - s, x + s, y + s), col, w), S(L(x + s, y - s, x - s, y + s), col, w)]; }
function tick(x, y, s, col = C.g, w = 10) { return [S(P([[x - s, y], [x - s * 0.3, y + s * 0.7], [x + s, y - s * 0.8]]), col, w)]; }
function rect(x, y, w2, h2, col = C.w, w = 7) { return [S(P([[x, y], [x + w2, y], [x + w2, y + h2], [x, y + h2], [x, y + 2]]), col, w)]; }
function seq(items, ts, te) {
  const len = it => { if (!it.text && !it.pts) throw new Error('bad item ' + JSON.stringify(it).slice(0, 200) + ' scene ' + SC.length); return it.text ? 260 : it.pts.reduce((a, p, i) => i ? a + Math.hypot(p[0] - it.pts[i - 1][0], p[1] - it.pts[i - 1][1]) : 0, 0); };
  const tot = items.reduce((a, it) => a + len(it) + 40, 0); let t = ts;
  items.forEach(it => { const d = (len(it) + 40) / tot * (te - ts); it.t0 = t; it.t1 = t + d * 0.92; t += d; });
  return items;
}
const G = (...a) => a.flat();
