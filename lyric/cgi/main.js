// Cinematic 3D CGI lyric video – "ఉన్నంతలో మనకున్నంతలో" (Bhaja Govindam – Reality), 60 s, 9:16.
// Everything is modelled procedurally (no images). window.render(t) draws the frame at time t.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const RW = 720, RH = 1280;                      // internal render size (CSS-scaled to 1080x1920)
const canvas = document.getElementById('gl');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(RW, RH, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 0.82;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// ---------------- utils ----------------
function rng(s) { return () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const cl = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const ease = v => { v = cl(v); return v * v * (3 - 2 * v); };
const lerp = (a, b, k) => a + (b - a) * k;
const V = (x, y, z) => new THREE.Vector3(x, y, z);
function hash(x, y) { const s = Math.sin(x * 127.1 + y * 311.7) * 43758.5453; return s - Math.floor(s); }
function vnoise(x, y) { const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi, u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
  return lerp(lerp(hash(xi, yi), hash(xi + 1, yi), u), lerp(hash(xi, yi + 1), hash(xi + 1, yi + 1), u), v); }
const fbm = (x, y) => vnoise(x, y) * 0.55 + vnoise(x * 2.1, y * 2.1) * 0.28 + vnoise(x * 4.3, y * 4.3) * 0.17;
const std = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.75, metalness: 0.0, ...o });
const glowMat = (color, intensity = 3) => new THREE.MeshStandardMaterial({ color: 0x000000, emissive: color, emissiveIntensity: intensity });
function mesh(geo, mat, x = 0, y = 0, z = 0, cast = true) { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = cast; m.receiveShadow = true; return m; }

function skyDome(top, mid, bottom, sunDir = V(0, 0.1, -1), sunCol = 0xffd9a0, sunSize = 0.02) {
  const mat = new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { top: { value: new THREE.Color(top) }, mid: { value: new THREE.Color(mid) }, bot: { value: new THREE.Color(bottom) }, sd: { value: sunDir.clone().normalize() }, sc: { value: new THREE.Color(sunCol) }, ss: { value: sunSize } },
    vertexShader: 'varying vec3 vp; void main(){ vp = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }',
    fragmentShader: `uniform vec3 top,mid,bot,sc,sd; uniform float ss; varying vec3 vp;
      void main(){ float h = vp.y; vec3 c = h>0.0 ? mix(mid, top, pow(clamp(h,0.0,1.0),0.6)) : mix(mid, bot, pow(clamp(-h*3.0,0.0,1.0),0.7));
        float d = max(dot(vp, sd), 0.0); c += sc * (pow(d, 900.0)*2.0 + pow(d, 12.0)*0.16*min(ss*4.0,1.0) + pow(d,2.0)*0.03);
        gl_FragColor = vec4(c, 1.0); }` });
  const m = new THREE.Mesh(new THREE.SphereGeometry(400, 32, 16), mat); m.renderOrder = -1; return m;
}
function terrain(size, seg, amp, freq, color, seed = 0, flat = true, edgeRise = 0) {
  const g = new THREE.PlaneGeometry(size, size, seg, seg); g.rotateX(-Math.PI / 2);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i); const d = Math.hypot(x, z) / (size / 2);
    p.setY(i, (fbm(x * freq + seed, z * freq + seed) - 0.5) * amp + edgeRise * Math.pow(d, 3)); }
  g.computeVertexNormals();
  const m = new THREE.Mesh(g, std(color, { flatShading: flat, roughness: 0.95 })); m.receiveShadow = true; return m;
}
function sunLight(scene, color, intensity, pos, target = V(0, 0, 0), shadowSize = 12) {
  const l = new THREE.DirectionalLight(color, intensity); l.position.copy(pos); l.target.position.copy(target);
  l.castShadow = true; l.shadow.mapSize.set(1024, 1024); const c = l.shadow.camera; c.left = c.bottom = -shadowSize; c.right = c.top = shadowSize; c.near = 0.5; c.far = 200; l.shadow.bias = -0.0008; l.shadow.normalBias = 0.03;
  scene.add(l, l.target); return l;
}
function points(n, seed, fn, color, size, opacity = 1) {
  const r = rng(seed), pos = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { const p = fn(r, i); pos[i * 3] = p[0]; pos[i * 3 + 1] = p[1]; pos[i * 3 + 2] = p[2]; }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const m = new THREE.PointsMaterial({ color, size, sizeAttenuation: true, transparent: true, opacity, blending: THREE.AdditiveBlending, depthWrite: false, map: dotTex() });
  const pts = new THREE.Points(g, m); pts.userData.base = pos.slice(); return pts;
}
let _dot; function dotTex() { if (_dot) return _dot; const c = document.createElement('canvas'); c.width = c.height = 64; const x = c.getContext('2d'); const g = x.createRadialGradient(32, 32, 0, 32, 32, 32); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.3, 'rgba(255,255,255,0.6)'); g.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = g; x.fillRect(0, 0, 64, 64); _dot = new THREE.CanvasTexture(c); return _dot; }
function tree(x, z, s, col = 0x2f5a35) { const g = new THREE.Group(); g.add(mesh(new THREE.CylinderGeometry(0.08 * s, 0.12 * s, 1.2 * s, 6), std(0x4a3222), 0, 0.6 * s, 0));
  const leaf = std(col, { flatShading: true }); g.add(mesh(new THREE.ConeGeometry(0.75 * s, 1.6 * s, 7), leaf, 0, 1.7 * s, 0)); g.add(mesh(new THREE.ConeGeometry(0.55 * s, 1.2 * s, 7), leaf, 0, 2.4 * s, 0)); g.position.set(x, 0, z); return g; }
function roundTree(x, z, s, col = 0x3b6b30) { const g = new THREE.Group(); g.add(mesh(new THREE.CylinderGeometry(0.1 * s, 0.16 * s, 1.6 * s, 6), std(0x4a3222), 0, 0.8 * s, 0));
  const leaf = std(col, { flatShading: true }); const r = rng(Math.floor(x * 13 + z * 7)); for (let i = 0; i < 5; i++) g.add(mesh(new THREE.IcosahedronGeometry((0.55 + r() * 0.35) * s, 0), leaf, (r() - 0.5) * 0.9 * s, (1.8 + r() * 0.7) * s, (r() - 0.5) * 0.9 * s)); g.position.set(x, 0, z); return g; }

// ---------------- character rig ----------------
function person(opts = {}) {
  const s = opts.scale || 1, skin = std(opts.skin || 0xc98f6a, { roughness: 0.6 }), cloth = std(opts.shirt || 0xe9e2d4, { roughness: 0.8 }), pants = std(opts.pants || 0x34465a, { roughness: 0.85 }), hair = std(opts.hair || 0x1b1410);
  const root = new THREE.Group(), hips = new THREE.Group(); root.add(hips); hips.position.y = 0.95;
  const J = { root, hips };
  const cap = (r, l, m) => { const x = new THREE.Mesh(new THREE.CapsuleGeometry(r, l, 4, 10), m); x.castShadow = true; x.position.y = -l / 2 - r * 0.2; return x; };
  hips.add(mesh(new THREE.SphereGeometry(0.15, 12, 8), pants, 0, 0, 0)); hips.children[0].scale.set(1.15, 0.8, 0.8);
  const spine = new THREE.Group(); hips.add(spine); J.spine = spine;
  const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.17, 0.32, 4, 12), cloth); torso.position.y = 0.3; torso.scale.set(1.05, 1, 0.68); torso.castShadow = true; spine.add(torso);
  const neck = new THREE.Group(); neck.position.y = 0.56; spine.add(neck); J.neck = neck;
  neck.add(mesh(new THREE.CylinderGeometry(0.05, 0.06, 0.1, 8), skin, 0, 0.04, 0));
  const head = mesh(new THREE.SphereGeometry(0.12, 18, 14), skin, 0, 0.2, 0.01); head.scale.set(0.92, 1.1, 1); neck.add(head);
  const hr = mesh(new THREE.SphereGeometry(0.125, 16, 12, 0, Math.PI * 2, 0, Math.PI * 0.55), hair, 0, 0.225, -0.012); hr.scale.set(0.96, 1.08, 1.05); neck.add(hr);
  if (opts.longHair) neck.add(mesh(new THREE.CapsuleGeometry(0.1, 0.25, 4, 8), hair, 0, 0.08, -0.08));
  for (const side of [1, -1]) {
    const sh = new THREE.Group(); sh.position.set(0.21 * side, 0.5, 0); spine.add(sh);
    sh.add(cap(0.055, 0.24, cloth)); const el = new THREE.Group(); el.position.y = -0.31; sh.add(el);
    el.add(cap(0.045, 0.22, skin)); el.add(mesh(new THREE.SphereGeometry(0.05, 8, 6), skin, 0, -0.3, 0));
    const hp = new THREE.Group(); hp.position.set(0.1 * side, -0.05, 0); hips.add(hp);
    hp.add(cap(0.075, 0.34, pants)); const kn = new THREE.Group(); kn.position.y = -0.44; hp.add(kn);
    kn.add(cap(0.06, 0.34, pants)); const ft = mesh(new THREE.BoxGeometry(0.1, 0.07, 0.24), std(0x2a201a), 0, -0.45, 0.05); kn.add(ft);
    const k = side > 0 ? 'L' : 'R'; J['sh' + k] = sh; J['el' + k] = el; J['hp' + k] = hp; J['kn' + k] = kn;
  }
  if (opts.saree) { const sk = new THREE.Mesh(new THREE.ConeGeometry(0.32, 0.85, 14, 1, true), std(opts.saree, { side: THREE.DoubleSide })); sk.position.y = -0.38; sk.castShadow = true; hips.add(sk); }
  root.scale.setScalar(s);
  root.traverse(o => { if (o.isMesh) o.castShadow = true; });
  return { root, J, pose: p => applyPose(J, p) };
}
// pose: shoulder [flexX, abdZ], elbow [flexX, bendZ], hip flexX, knee flexX (all radians), side L = character's left (+x)
const P0 = { shL: [0, 0.12], shR: [0, 0.12], elL: [-0.15, 0], elR: [-0.15, 0], hpL: 0, hpR: 0, knL: 0, knR: 0, spine: 0, head: [0, 0], hipsY: 0.95, hipsZ: 0 };
function applyPose(J, p) {
  p = { ...P0, ...p };
  J.shL.rotation.set(p.shL[0], 0, p.shL[1]); J.shR.rotation.set(p.shR[0], 0, -p.shR[1]);
  J.elL.rotation.set(p.elL[0], 0, -p.elL[1]); J.elR.rotation.set(p.elR[0], 0, p.elR[1]);
  J.hpL.rotation.set(p.hpL, 0, 0.03); J.hpR.rotation.set(p.hpR, 0, -0.03); J.knL.rotation.set(p.knL, 0, 0); J.knR.rotation.set(p.knR, 0, 0);
  J.spine.rotation.set(p.spine, 0, 0); J.neck.rotation.set(p.head[0], p.head[1], 0); J.hips.position.y = p.hipsY; J.hips.position.z = p.hipsZ;
}
const POSE = {
  stand: ph => ({ shL: [0.03 * Math.sin(ph), 0.12], shR: [-0.03 * Math.sin(ph), 0.12], spine: 0.02 * Math.sin(ph * 0.7) }),
  hips: () => ({ shL: [0.2, 0.75], shR: [0.2, 0.75], elL: [-0.2, 1.7], elR: [-0.2, 1.7], head: [-0.15, 0], spine: -0.05 }),
  walk: ph => { const s = Math.sin(ph); return { hpL: -0.45 * s, hpR: 0.45 * s, knL: 0.6 * Math.max(0, Math.sin(ph + 1.2)), knR: 0.6 * Math.max(0, Math.sin(ph + 1.2 + Math.PI)), shL: [0.4 * s, 0.1], shR: [-0.4 * s, 0.1], elL: [-0.35, 0], elR: [-0.35, 0], hipsY: 0.95 + 0.02 * Math.abs(Math.cos(ph)) }; },
  run: ph => { const s = Math.sin(ph); return { hpL: -0.85 * s - 0.15, hpR: 0.85 * s - 0.15, knL: 1.2 * Math.max(0.1, Math.sin(ph + 1.3)), knR: 1.2 * Math.max(0.1, Math.sin(ph + 1.3 + Math.PI)), shL: [0.8 * s, 0.12], shR: [-0.8 * s, 0.12], elL: [-1.4, 0], elR: [-1.4, 0], spine: 0.25, head: [-0.15, 0], hipsY: 0.9 + 0.06 * Math.abs(Math.cos(ph)) }; },
  sitRelax: ph => ({ hipsY: 0.42, hpL: -1.45, hpR: -1.35, knL: 1.5, knR: 1.3, spine: -0.18 + 0.02 * Math.sin(ph), head: [-0.35, 0], shL: [-2.6, 0.5], shR: [-2.6, 0.5], elL: [0, 2.1], elR: [0, 2.1] }),
  jump: ph => ({ shL: [-0.2, 2.6], shR: [-0.2, 2.6], elL: [0, 0.2], elR: [0, 0.2], hpL: -0.3, hpR: -0.1, knL: 0.5, knR: 0.3, head: [-0.3, 0], spine: -0.1 }),
  open: ph => ({ shL: [-0.2, 1.35 + 0.05 * Math.sin(ph)], shR: [-0.2, 1.35 + 0.05 * Math.sin(ph)], elL: [-0.1, 0.1], elR: [-0.1, 0.1], head: [-0.3, 0], spine: -0.12 }),
  reach: ph => ({ shR: [-0.3, 2.85 + 0.06 * Math.sin(ph)], elR: [-0.05, 0], shL: [0.05, 0.15], head: [-0.45, 0] }),
  think: ph => ({ shR: [-0.6, 0.25], elR: [-2.3, 0], shL: [0.15, 0.2], elL: [-1.2, 0.6], head: [0.12, 0.25], spine: 0.08 }),
  sad: ph => ({ shL: [0.1, 0.06], shR: [0.1, 0.06], spine: 0.25, head: [0.4, 0] }),
  hold: ph => ({ shL: [-0.05, 0.42], shR: [-0.05, 0.42], elL: [-0.1, 0], elR: [-0.1, 0], head: [-0.05, 0] }),
  dance: ph => { const s = Math.sin(ph); return { shL: [-0.3, 2.2 + 0.4 * s], shR: [-0.3, 2.2 - 0.4 * s], elL: [0, 0.6], elR: [0, 0.6], hpL: -0.3 * s, hpR: 0.3 * s, knL: 0.4 + 0.3 * s, knR: 0.4 - 0.3 * s, spine: 0.1 * s, hipsY: 0.9 + 0.05 * Math.abs(s) }; },
  balloon: ph => ({ shR: [-0.2, 2.75], elR: [0, 0.1], shL: [-0.2, 1.1 + 0.1 * Math.sin(ph)], elL: [0, 0.2], hpL: -0.25, hpR: 0.15, knL: 0.5, knR: 0.35, head: [-0.4, 0] }),
};

// ---------------- scenes ----------------
const SC = [];
function addScene(t0, t1, build) { const scene = new THREE.Scene(); const camera = new THREE.PerspectiveCamera(40, RW / RH, 0.1, 900); const upd = build(scene, camera); SC.push({ t0, t1, scene, camera, upd }); }
const cam = (c, pos, look) => { c.position.copy(pos); c.lookAt(look); };

// 1. ఉన్నంతలో… అదే సుఖము – cozy home, man relaxed on the porch at golden hour
addScene(0, 4.4, (S, C) => {
  S.add(skyDome(0x2c4a74, 0xf2a35e, 0x3a2a24, V(-0.6, 0.06, -1), 0xffc98a)); S.fog = new THREE.FogExp2(0xe8a070, 0.018);
  S.add(new THREE.HemisphereLight(0xffd7a8, 0x30402a, 0.6)); sunLight(S, 0xffb070, 3.2, V(-14, 6, -12), V(0, 0, 0), 10);
  S.add(terrain(160, 120, 3.5, 0.05, 0x5c7a3a, 3, true));
  const house = new THREE.Group(); const wall = std(0xd9c3a0), roof = std(0x8a3b26, { flatShading: true });
  house.add(mesh(new THREE.BoxGeometry(3.2, 2.2, 2.6), wall, 0, 1.1, 0));
  const rg = new THREE.CylinderGeometry(0.01, 2.4, 1.4, 4, 1); rg.rotateY(Math.PI / 4); const r = mesh(rg, roof, 0, 2.9, 0); r.scale.set(1.0, 1, 0.82); house.add(r);
  const win = glowMat(0xffb04a, 2.6); house.add(mesh(new THREE.PlaneGeometry(0.7, 0.6), win, -0.8, 1.3, 1.31, false)); house.add(mesh(new THREE.PlaneGeometry(0.7, 0.6), win, 0.85, 1.3, 1.31, false));
  house.add(mesh(new THREE.BoxGeometry(0.8, 1.5, 0.06), std(0x5a3a22), 0, 0.75, 1.31));
  house.add(mesh(new THREE.BoxGeometry(3.6, 0.25, 1.0), std(0x8a6a4a), 0, 0.12, 1.75));
  house.add(mesh(new THREE.BoxGeometry(0.35, 0.9, 0.35), std(0x7a5a44), 0.9, 3.2, -0.4));
  const pl = new THREE.PointLight(0xffa040, 4, 6, 1.6); pl.position.set(0, 1.4, 2.2); house.add(pl);
  S.add(house);
  const man = person({ shirt: 0x5b7fb5 }); man.root.position.set(1.0, 0.25, 1.95); man.root.rotation.y = -0.25; S.add(man.root);
  const smoke = points(40, 4, (r) => [0.9 + (r() - 0.5) * 0.3, 3.5 + r() * 2.5, -0.4 + (r() - 0.5) * 0.3], 0xd8c8b8, 0.5, 0.25); S.add(smoke);
  [[-6, -4, 1.3], [-8, -9, 1.6], [6, -6, 1.4], [9, -12, 1.8], [-4, -14, 1.2], [4.5, 2, 1.0]].forEach(([x, z, s]) => S.add(roundTree(x, z, s)));
  const flies = points(60, 5, r => [(r() - 0.5) * 8, 0.4 + r() * 2.5, (r() - 0.5) * 6 + 1], 0xffd27a, 0.08, 0.9); S.add(flies);
  return (u, lt) => { man.pose(POSE.sitRelax(lt * 2));
    const a = smoke.geometry.attributes.position, b = smoke.userData.base; for (let i = 0; i < a.count; i++) { a.setY(i, 3.5 + ((b[i * 3 + 1] - 3.5 + lt * 0.5) % 2.5)); a.setX(i, b[i * 3] + Math.sin(lt + i) * 0.15 * (a.getY(i) - 3.5)); } a.needsUpdate = true;
    const f = flies.geometry.attributes.position, fb = flies.userData.base; for (let i = 0; i < f.count; i++) { f.setY(i, fb[i * 3 + 1] + 0.2 * Math.sin(lt * 1.5 + i)); f.setX(i, fb[i * 3] + 0.2 * Math.cos(lt + i * 1.7)); } f.needsUpdate = true;
    cam(C, V(lerp(4.5, 3.2, ease(u)), lerp(2.4, 1.9, ease(u)), lerp(8.5, 6.2, ease(u))), V(0.4, 1.3, 1.0)); };
});

// 2. ఎవరికి తలలొంచకా… గుణం వరము – hero on the mountain peak, flag, low-angle crane
addScene(4.4, 10.0, (S, C) => {
  S.add(skyDome(0x1d3d6e, 0xffb46a, 0x2a2430, V(0.3, 0.05, -1), 0xffd59a)); S.fog = new THREE.FogExp2(0xd39a78, 0.012);
  S.add(new THREE.HemisphereLight(0xffd0a0, 0x203040, 0.5)); sunLight(S, 0xffc080, 3.5, V(6, 8, -20), V(0, 8, 0), 6);
  const mg = new THREE.ConeGeometry(9, 16, 9, 6); const p = mg.attributes.position; for (let i = 0; i < p.count; i++) { const y = p.getY(i); if (y < 7.9) { p.setX(i, p.getX(i) * (0.85 + fbm(i, 1) * 0.35)); p.setZ(i, p.getZ(i) * (0.85 + fbm(1, i) * 0.35)); } } mg.computeVertexNormals();
  const mt = mesh(mg, std(0x6a5a52, { flatShading: true }), 0, 0, 0); S.add(mt);
  const top = mesh(new THREE.CylinderGeometry(0.9, 1.6, 0.8, 7), std(0x5e5048, { flatShading: true }), 0, 8.0, 0); S.add(top);
  for (let i = 0; i < 9; i++) { const r = rng(20 + i); const m = mesh(new THREE.ConeGeometry(6 + r() * 6, 7 + r() * 9, 7, 3), std(i % 2 ? 0x4c4a58 : 0x5a5060, { flatShading: true }), (r() - 0.5) * 70, -2, -25 - r() * 50); S.add(m); }
  const man = person({ shirt: 0xe7dccb, pants: 0x2d3a48 }); man.root.position.set(0, 8.4, 0); S.add(man.root);
  const pole = mesh(new THREE.CylinderGeometry(0.025, 0.025, 2.4, 6), std(0x9a9a9a, { metalness: 0.6 }), 0.8, 9.6, -0.1); S.add(pole);
  const fg = new THREE.PlaneGeometry(1.1, 0.7, 12, 4); fg.translate(0.55, 0, 0); const flag = mesh(fg, std(0xff8a2a, { side: THREE.DoubleSide, roughness: 0.6 }), 0.82, 10.45, -0.1); S.add(flag);
  const fb = fg.attributes.position.array.slice();
  const sparkle = points(50, 21, r => { const a = r() * 6.28, rr = 0.8 + r() * 1.5; return [Math.cos(a) * rr, 9 + r() * 2.5, Math.sin(a) * rr]; }, 0xffe2a0, 0.12, 0); S.add(sparkle);
  const clouds = new THREE.Group(); for (let i = 0; i < 14; i++) { const r = rng(40 + i); const c = mesh(new THREE.IcosahedronGeometry(2 + r() * 2, 1), std(0xf3d6c4, { flatShading: true, transparent: true, opacity: 0.85 }), (r() - 0.5) * 40, 3 + r() * 2, (r() - 0.5) * 30, false); c.scale.y = 0.4; clouds.add(c); } S.add(clouds);
  return (u, lt, t) => { man.pose(t < 6.6 ? POSE.stand(lt) : POSE.hips(lt));
    const a = fg.attributes.position; for (let i = 0; i < a.count; i++) { const x = fb[i * 3]; a.setZ(i, Math.sin(x * 5 - lt * 7) * 0.12 * x); } a.needsUpdate = true;
    sparkle.material.opacity = ease((t - 8.2) / 0.6); sparkle.rotation.y = lt * 0.4;
    clouds.position.x = lt * 0.6;
    const k = ease(u), ang = lerp(-0.6, 0.5, k), rad = lerp(9, 4.2, k);
    cam(C, V(Math.sin(ang) * rad, lerp(5.5, 8.6, k), Math.cos(ang) * rad), V(0, lerp(8.8, 9.6, k), 0)); };
});

// 3. ఏదెలాగ రాసెనో… భయము – the book of fate in a starry void, a path of light, calm walker
addScene(10.0, 15.1, (S, C) => {
  S.add(skyDome(0x05081a, 0x1a1640, 0x05060c, V(0, 0.3, -1), 0x8070ff, 0.5)); S.fog = new THREE.FogExp2(0x0a0a20, 0.03);
  S.add(new THREE.AmbientLight(0x6070a0, 0.35));
  const stars = points(1500, 30, r => { const a = r() * 6.28, b = Math.acos(2 * r() - 1), R = 120; return [R * Math.sin(b) * Math.cos(a), Math.abs(R * Math.cos(b)) * 0.8 + 5, R * Math.sin(b) * Math.sin(a)]; }, 0xffffff, 0.6, 0.9); S.add(stars);
  const book = new THREE.Group(); book.position.set(0, 2.2, -3); book.rotation.x = 0.6; S.add(book);
  book.add(mesh(new THREE.BoxGeometry(4.4, 0.12, 3.0), std(0x5a2a1a, { roughness: 0.5 }), 0, -0.08, 0));
  const pageMat = std(0xfff2d8, { emissive: 0xffd9a0, emissiveIntensity: 0.6, side: THREE.DoubleSide });
  for (const s of [1, -1]) { const g = new THREE.PlaneGeometry(2.05, 2.8, 20, 1); g.rotateX(-Math.PI / 2); const p = g.attributes.position; for (let i = 0; i < p.count; i++) { const x = p.getX(i); p.setY(i, 0.25 * Math.sin((x + 1.025) / 2.05 * Math.PI) ); } g.translate(1.03 * s, 0.02, 0); g.computeVertexNormals(); book.add(new THREE.Mesh(g, pageMat)); }
  // glowing "writing" lines appear on the right page
  const lines = []; for (let i = 0; i < 7; i++) { const l = mesh(new THREE.BoxGeometry(1.4, 0.01, 0.04), glowMat(0xffb040, 4), 1.05, 0.28, -1.0 + i * 0.3, false); l.scale.x = 0.001; book.add(l); lines.push(l); }
  const quill = new THREE.Group(); const qg = new THREE.ConeGeometry(0.12, 1.6, 6); qg.translate(0, 0.8, 0); quill.add(mesh(qg, std(0xfff3e0, { emissive: 0xffe0b0, emissiveIntensity: 0.4 }))); book.add(quill);
  const bl = new THREE.PointLight(0xffc070, 10, 12, 1.5); bl.position.set(0, 1.2, 0); book.add(bl);
  const motes = points(400, 31, r => [(r() - 0.5) * 3.5, r() * 6, (r() - 0.5) * 2.5], 0xffcf7a, 0.08, 0.9); motes.position.set(0, 2.2, -3); S.add(motes);
  // path of light from the book toward camera
  const path = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 14, 1, 40), new THREE.MeshBasicMaterial({ color: 0xffc070, transparent: true, opacity: 0.55, blending: THREE.AdditiveBlending, depthWrite: false })); path.rotation.x = -Math.PI / 2; path.position.set(0, 0.02, 4); S.add(path);
  const floor = mesh(new THREE.CircleGeometry(30, 48), std(0x0c0c18, { roughness: 0.3, metalness: 0.4 }), 0, 0, 0, false); floor.rotation.x = -Math.PI / 2; S.add(floor);
  const man = person({ shirt: 0x2b2b38, pants: 0x1c1c26 }); S.add(man.root);
  return (u, lt, t) => {
    lines.forEach((l, i) => { const k = ease((lt - 0.4 - i * 0.22) / 0.3); l.scale.x = Math.max(0.001, k); l.position.x = 0.35 + 0.7 * k; });
    const qi = Math.min(6, Math.floor((lt - 0.4) / 0.22)), qk = cl(((lt - 0.4) % 0.22) / 0.22); quill.position.set(0.35 + 1.4 * (qi < 0 ? 0 : qk), 0.35, -1.0 + Math.max(0, qi) * 0.3); quill.rotation.set(-0.5, 0, -0.6 + 0.1 * Math.sin(lt * 20));
    const m = motes.geometry.attributes.position, mb = motes.userData.base; for (let i = 0; i < m.count; i++) m.setY(i, (mb[i * 3 + 1] + lt * 0.8) % 6); m.needsUpdate = true;
    const wz = lerp(2.6, -0.2, cl((lt - 1.0) / 4.0)); man.root.position.set(0, 0, wz); man.root.rotation.y = Math.PI; man.pose(lt > 1.0 ? POSE.walk(lt * 5) : POSE.stand(lt));
    const k = ease(u); cam(C, V(lerp(1.2, -0.9, k), lerp(4.6, 3.6, k), lerp(3.4, 4.8, k)), V(0, lerp(2.1, 1.7, k), -3.0)); };
});

// 4. అది అలాగ జరగక… నమ్మకము – fork in the road, one path collapses, walk the other toward a lamp of faith
addScene(15.1, 20.6, (S, C) => {
  S.add(skyDome(0x2a3f66, 0xe99a6a, 0x2c2a2c, V(0.5, 0.04, -1), 0xffb070)); S.fog = new THREE.FogExp2(0xb98a7a, 0.02);
  S.add(new THREE.HemisphereLight(0xffd0a0, 0x2a3040, 0.55)); sunLight(S, 0xffa870, 2.8, V(10, 6, -18), V(0, 0, 0), 12);
  S.add(terrain(160, 100, 2.4, 0.06, 0x51693a, 7, true));
  const road = std(0xa08664, { roughness: 1 });
  const strip = (pts, w) => { const curve = new THREE.CatmullRomCurve3(pts); const N = 60, pos = [], idx = []; for (let i = 0; i <= N; i++) { const p = curve.getPoint(i / N), tg = curve.getTangent(i / N), n = V(-tg.z, 0, tg.x).normalize().multiplyScalar(w / 2); pos.push(p.x + n.x, p.y + 0.06, p.z + n.z, p.x - n.x, p.y + 0.06, p.z - n.z); if (i < N) idx.push(i * 2, i * 2 + 1, i * 2 + 2, i * 2 + 1, i * 2 + 3, i * 2 + 2); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals(); const m = new THREE.Mesh(g, road); m.receiveShadow = true; return m; };
  S.add(strip([V(0, 0, 14), V(0, 0, 7), V(0, 0, 2)], 2.2));
  S.add(strip([V(0, 0, 2.2), V(-2.5, 0, -4), V(-7, 0, -12), V(-12, 0, -22)], 1.8));
  S.add(strip([V(0, 0, 2.2), V(2.5, 0, -4), V(6, 0, -12), V(10, 0, -24)], 1.8));
  const post = mesh(new THREE.CylinderGeometry(0.07, 0.08, 2.6, 6), std(0x5a3e28), 0, 1.3, 2.6); S.add(post);
  const bd = (x, rot, col) => { const b = mesh(new THREE.BoxGeometry(1.3, 0.35, 0.06), std(col), x, 2.2 - (rot > 0 ? 0.45 : 0), 2.6); b.rotation.y = rot; S.add(b); return b; };
  bd(-0.6, 0.3, 0xb07a4a); bd(0.6, -0.3, 0xb07a4a);
  const xMark = mesh(new THREE.TorusGeometry(0.12, 0.03, 6, 12), glowMat(0xff4030, 3), -0.65, 2.2, 2.7, false); S.add(xMark);
  const okMark = mesh(new THREE.TorusGeometry(0.12, 0.03, 6, 12), glowMat(0x40ff70, 3), 0.65, 1.75, 2.7, false); S.add(okMark);
  // boulders fall onto the left path
  const rocks = []; for (let i = 0; i < 6; i++) { const r = rng(60 + i); const m = mesh(new THREE.DodecahedronGeometry(0.5 + r() * 0.5, 0), std(0x6a625a, { flatShading: true }), -3 - r() * 2.5, 12, -4 - r() * 4); m.userData = { y: 0.4 + r() * 0.3, d: r() * 0.4 }; S.add(m); rocks.push(m); }
  // lamp of faith on the right path
  const lamp = new THREE.Group(); lamp.position.set(5.2, 0, -9); S.add(lamp);
  lamp.add(mesh(new THREE.CylinderGeometry(0.35, 0.6, 1.1, 8), std(0x7a5a3a, { flatShading: true }), 0, 0.55, 0));
  const bowl = mesh(new THREE.SphereGeometry(0.5, 16, 8, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), std(0xb5652a), 0, 1.6, 0); lamp.add(bowl);
  const flame = mesh(new THREE.ConeGeometry(0.16, 0.6, 12), glowMat(0xffa030, 6), 0, 1.95, 0, false); lamp.add(flame);
  const fl = new THREE.PointLight(0xffa040, 10, 14, 1.6); fl.position.set(0, 2.2, 0); lamp.add(fl);
  const man = person({ shirt: 0x7a9a6a }); S.add(man.root);
  [[-9, -3], [8, 2], [-6, 6], [11, -8], [-13, -14]].forEach(([x, z], i) => S.add(tree(x, z, 1.2 + (i % 3) * 0.3)));
  return (u, lt, t) => {
    rocks.forEach(m => { const k = cl((t - 15.4 - m.userData.d) / 0.6); m.position.y = lerp(12, m.userData.y, k * k); m.rotation.x = k * 3; });
    let px, pz, ry = Math.PI;
    if (lt < 1.6) { px = 0; pz = lerp(9, 3.2, lt / 1.6); } else if (lt < 2.2) { px = 0; pz = 3.2; } else { const k = ease((lt - 2.2) / 3.0); const pt = new THREE.CatmullRomCurve3([V(0, 0, 3.2), V(2.5, 0, -4), V(5, 0, -8.5)]).getPoint(k); px = pt.x; pz = pt.z; ry = Math.PI - 0.5; }
    man.root.position.set(px, 0, pz); man.root.rotation.y = ry; man.pose(lt < 1.6 || lt > 2.2 ? POSE.walk(lt * 5.5) : { ...POSE.stand(lt), head: [0, lt < 1.9 ? -0.6 : 0.6] });
    const faith = ease((t - 18.1) / 0.8); flame.scale.set(1 + faith * 0.8 + 0.1 * Math.sin(lt * 25), 1 + faith * 1.5 + 0.15 * Math.sin(lt * 31), 1 + faith * 0.8); fl.intensity = 5 + faith * 18;
    const k = ease(u); cam(C, V(lerp(1.5, 4.0, k), lerp(3.2, 2.6, k), lerp(14, 2.0, k)), V(lerp(0, 4.5, k), 1.4, lerp(2, -8, k))); };
});

// 5. ఏవో తెలియని పరుగులు తీసే తొందరలో – city rush, crowd running, giant clock
addScene(20.6, 25.6, (S, C) => {
  S.add(skyDome(0x0e1a2c, 0x5a4a5a, 0x101014, V(0, 0.15, -1), 0xffa070, 0.4)); S.fog = new THREE.FogExp2(0x30303a, 0.035);
  S.add(new THREE.HemisphereLight(0x8090b0, 0x202020, 0.6)); sunLight(S, 0xffc0a0, 1.6, V(-6, 12, 8), V(0, 0, 0), 14);
  const gnd = mesh(new THREE.PlaneGeometry(200, 200), std(0x2a2a2e, { roughness: 0.35, metalness: 0.3 }), 0, 0, 0, false); gnd.rotation.x = -Math.PI / 2; S.add(gnd);
  const wc = document.createElement('canvas'); wc.width = 64; wc.height = 128; const wx = wc.getContext('2d'); wx.fillStyle = '#15161c'; wx.fillRect(0, 0, 64, 128); const wr = rng(70);
  for (let y = 4; y < 124; y += 10) for (let x = 4; x < 60; x += 10) if (wr() > 0.45) { wx.fillStyle = wr() > 0.5 ? '#ffd58a' : '#ffb060'; wx.fillRect(x, y, 6, 6); }
  const wt = new THREE.CanvasTexture(wc); wt.magFilter = THREE.NearestFilter;
  const bm = new THREE.MeshStandardMaterial({ color: 0x22252e, emissive: 0xffffff, emissiveMap: wt, emissiveIntensity: 1.6, roughness: 0.8 });
  for (let i = 0; i < 40; i++) { const r = rng(80 + i), w = 3 + r() * 4, h = 8 + r() * 26, side = i % 2 ? 1 : -1; const b = mesh(new THREE.BoxGeometry(w, h, w), bm, side * (7 + r() * 10), h / 2, 10 - i * 3.2 - r() * 2); S.add(b); }
  // giant clock
  const ck = new THREE.Group(); ck.position.set(0, 13, -30); S.add(ck);
  ck.add(mesh(new THREE.CylinderGeometry(5, 5, 0.6, 48), std(0xf1e6cc, { emissive: 0xffe8c0, emissiveIntensity: 0.6 }), 0, 0, 0, false)); ck.children[0].rotation.x = Math.PI / 2;
  ck.add(mesh(new THREE.TorusGeometry(5, 0.3, 8, 48), std(0xb08a3a, { metalness: 0.7, roughness: 0.3 }), 0, 0, 0.1, false));
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; ck.add(mesh(new THREE.BoxGeometry(0.2, 0.7, 0.1), std(0x222222), Math.sin(a) * 4.2, Math.cos(a) * 4.2, 0.35, false)); ck.children[ck.children.length - 1].rotation.z = -a; }
  const hh = new THREE.Group(), mh = new THREE.Group(); hh.position.z = mh.position.z = 0.45; ck.add(hh, mh);
  hh.add(mesh(new THREE.BoxGeometry(0.35, 2.6, 0.1), std(0x111111), 0, 1.2, 0, false)); mh.add(mesh(new THREE.BoxGeometry(0.22, 3.8, 0.1), std(0x111111), 0, 1.8, 0.05, false));
  const crowd = []; const cols = [0x8a3a3a, 0x3a5a8a, 0x5a7a4a, 0xa08a5a, 0x6a4a7a, 0x3a3a3a];
  for (let i = 0; i < 26; i++) { const r = rng(90 + i); const p = person({ shirt: cols[i % 6], pants: 0x23262e, scale: 0.95 + r() * 0.1 }); const dir = r() > 0.5 ? 1 : -1;
    p.data = { x: (r() - 0.5) * 30, z: 4 - r() * 34, dir, sp: 3 + r() * 2.5, ph: r() * 6 }; S.add(p.root); crowd.push(p); }
  const hero = person({ shirt: 0xe9e2d4, pants: 0x2d3a48 }); S.add(hero.root);
  return (u, lt) => {
    const sp = 1 + lt * 0.35;
    crowd.forEach(p => { const d = p.data; const x = ((d.x + d.dir * lt * d.sp * sp + 60) % 30 + 30) % 30 - 15; p.root.position.set(x, 0, d.z); p.root.rotation.y = d.dir * Math.PI / 2; p.pose(POSE.run(lt * 9 * sp + d.ph)); });
    hero.root.position.set(0, 0, lerp(2, -10, ease(u))); hero.root.rotation.y = Math.PI; hero.pose(POSE.run(lt * 10));
    const spin = lt * lt * 1.8 + lt * 3; mh.rotation.z = -spin; hh.rotation.z = -spin / 12;
    const k = ease(u); cam(C, V(Math.sin(lt * 0.4) * 1.2, lerp(2.0, 3.5, k), lerp(9, -3, k)), V(0, lerp(3, 9, k), lerp(-10, -30, k)));
    C.rotation.z += 0.012 * Math.sin(lt * 17) * k; };
});

// 6. నీకే నువ్వే దొరకక… తెలివను భ్రమలో – foggy mirror without a true reflection, hourglass draining
addScene(25.6, 30.6, (S, C) => {
  S.add(skyDome(0x0a1620, 0x2a4450, 0x0a1014, V(0, 0.2, -1), 0x80b0c0, 0.6)); S.fog = new THREE.FogExp2(0x2a3e48, 0.06);
  S.add(new THREE.HemisphereLight(0x9ac0d0, 0x101820, 0.5)); sunLight(S, 0xbfe0ff, 1.6, V(-4, 8, 6), V(0, 1, 0), 6);
  const fl = mesh(new THREE.CircleGeometry(30, 48), std(0x1a262c, { roughness: 0.2, metalness: 0.5 }), 0, 0, 0, false); fl.rotation.x = -Math.PI / 2; S.add(fl);
  const mirror = new THREE.Group(); mirror.position.set(0.9, 0, -1.2); mirror.rotation.y = -0.35; S.add(mirror);
  mirror.add(mesh(new THREE.TorusGeometry(1.0, 0.08, 10, 48), std(0xc9a24a, { metalness: 0.8, roughness: 0.3 }), 0, 1.6, 0)); mirror.children[0].scale.set(0.8, 1.25, 1);
  const glass = mesh(new THREE.CircleGeometry(1.0, 48), new THREE.MeshBasicMaterial({ color: 0x5a7a88 }), 0, 1.6, -0.01, false); glass.scale.set(0.8, 1.25, 1); mirror.add(glass);
  mirror.add(mesh(new THREE.CylinderGeometry(0.05, 0.3, 0.6, 8), std(0xc9a24a, { metalness: 0.8, roughness: 0.3 }), 0, 0.3, 0));
  // a blurred, wrong "reflection" – a shadowy figure that fades in and out
  const ghostMat = new THREE.MeshBasicMaterial({ color: 0x0a1418, transparent: true, opacity: 0.5 });
  const ghost = person({ shirt: 0x000000 }); ghost.root.traverse(o => { if (o.isMesh) { o.material = ghostMat; o.castShadow = false; } }); ghost.root.scale.setScalar(0.62); ghost.root.position.set(0, 0.6, -0.05); ghost.root.rotation.y = Math.PI; mirror.add(ghost.root);
  const mistM = new THREE.MeshBasicMaterial({ color: 0xc8dce6, transparent: true, opacity: 0.25, depthWrite: false, map: dotTex() });
  const mist = []; for (let i = 0; i < 6; i++) { const m = mesh(new THREE.PlaneGeometry(1.4, 0.9), mistM.clone(), 0, 1.0 + i * 0.25, 0.08, false); mirror.add(m); mist.push(m); }
  const man = person({ shirt: 0x445566 }); man.root.position.set(-0.9, 0, 0.6); man.root.rotation.y = 2.4; S.add(man.root);
  // hourglass
  const hg = new THREE.Group(); hg.position.set(-1.6, 0, -2.6); S.add(hg);
  const glassM = new THREE.MeshStandardMaterial({ color: 0xcfe6f0, transparent: true, opacity: 0.28, roughness: 0.05, metalness: 0.1, depthWrite: false });
  const lpts = []; for (let i = 0; i <= 20; i++) { const y = i / 20 * 2; const r = 0.08 + 0.55 * Math.pow(Math.abs(y - 1), 0.8); lpts.push(new THREE.Vector2(r, y)); }
  hg.add(mesh(new THREE.LatheGeometry(lpts, 32), glassM, 0, 0.25, 0, false));
  hg.add(mesh(new THREE.CylinderGeometry(0.75, 0.75, 0.12, 24), std(0x6a4a2a), 0, 0.2, 0)); hg.add(mesh(new THREE.CylinderGeometry(0.75, 0.75, 0.12, 24), std(0x6a4a2a), 0, 2.3, 0));
  const sandM = std(0xe2b46a, { emissive: 0x7a5020, emissiveIntensity: 0.6 });
  const sTop = mesh(new THREE.ConeGeometry(0.5, 0.75, 24), sandM, 0, 1.62, 0); sTop.rotation.x = Math.PI; hg.add(sTop);
  const sBot = mesh(new THREE.ConeGeometry(0.55, 0.6, 24), sandM, 0, 0.6, 0); hg.add(sBot);
  const stream = mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.9, 6), sandM, 0, 0.95, 0, false); hg.add(stream);
  const dust = points(300, 110, r => [(r() - 0.5) * 12, r() * 5, (r() - 0.5) * 10], 0xcfe6f0, 0.05, 0.6); S.add(dust);
  return (u, lt, t) => {
    man.pose(POSE.think(lt));
    ghostMat.opacity = 0.25 + 0.3 * Math.abs(Math.sin(lt * 1.3)); ghost.root.position.x = 0.12 * Math.sin(lt * 2.3); ghost.pose(POSE.sad(lt));
    mist.forEach((m, i) => { m.position.x = 0.35 * Math.sin(lt * 0.7 + i); m.material.opacity = 0.18 + 0.1 * Math.sin(lt + i); });
    const k2 = cl((t - 27.0) / 3.5); sTop.scale.setScalar(Math.max(0.02, 1 - k2 * 0.9)); sBot.scale.setScalar(0.25 + k2 * 0.8); stream.visible = k2 > 0 && k2 < 1;
    const d = dust.geometry.attributes.position, db = dust.userData.base; for (let i = 0; i < d.count; i++) d.setY(i, (db[i * 3 + 1] + lt * 0.15) % 5); d.needsUpdate = true;
    const k = ease(u), ang = lerp(0.9, 0.2, k), rad = lerp(6.5, 4.2, k);
    cam(C, V(Math.sin(ang) * rad - 0.4, lerp(2.4, 1.8, k), Math.cos(ang) * rad + 0.2), V(lerp(-0.2, -0.6, k), 1.4, -1.2)); };
});

// 7. చాలా ఆశల నడుమన… అన్ని చూడు – bubbles of desire pop; the camera reveals family at sunrise
addScene(30.6, 36.1, (S, C) => {
  const sky = skyDome(0x1a2440, 0x6a5a7a, 0x20202a, V(0, 0.08, -1), 0xffc090, 0.6); S.add(sky); S.fog = new THREE.FogExp2(0x5a5068, 0.02);
  const hemi = new THREE.HemisphereLight(0xc0b0e0, 0x2a2a30, 0.5); S.add(hemi); const sun = sunLight(S, 0xffc890, 1.0, V(0, 6, -20), V(0, 0, 0), 10);
  S.add(terrain(160, 100, 2.0, 0.05, 0x5a7240, 11, true));
  const man = person({ shirt: 0xe7dccb }); man.root.position.set(0, 0, 0); man.root.rotation.y = 0.2; S.add(man.root);
  const wife = person({ shirt: 0xc8506a, pants: 0xc8506a, longHair: true, saree: 0xd8506a }); wife.root.position.set(1.0, 0, 0.1); wife.root.rotation.y = 0.0; wife.root.visible = false; S.add(wife.root);
  const kid = person({ shirt: 0xffc0d0, pants: 0x6a8ad0, scale: 0.62, longHair: true }); kid.root.position.set(-0.85, 0, 0.1); kid.root.visible = false; S.add(kid.root);
  const bubbleM = new THREE.MeshStandardMaterial({ color: 0xbfe0ff, transparent: true, opacity: 0.22, roughness: 0.05, metalness: 0.2, emissive: 0x6080a0, emissiveIntensity: 0.35, depthWrite: false });
  const gold = std(0xffc040, { metalness: 0.9, roughness: 0.25, emissive: 0x6a4a10, emissiveIntensity: 0.4 });
  const objs = [
    () => { const g = new THREE.Group(); g.add(mesh(new THREE.BoxGeometry(0.7, 0.22, 0.32), std(0xd03030, { metalness: 0.6, roughness: 0.3 }))); g.add(mesh(new THREE.BoxGeometry(0.38, 0.16, 0.28), std(0x202838), 0, 0.17, 0)); return g; },
    () => { const g = new THREE.Group(); g.add(mesh(new THREE.BoxGeometry(0.5, 0.4, 0.4), std(0xe8d8b8))); const r = mesh(new THREE.ConeGeometry(0.42, 0.3, 4), std(0x903a2a), 0, 0.35, 0); r.rotation.y = Math.PI / 4; g.add(r); return g; },
    () => { const g = mesh(new THREE.CylinderGeometry(0.28, 0.28, 0.06, 24), gold); g.rotation.x = Math.PI / 2; return g; },
    () => mesh(new THREE.BoxGeometry(0.22, 0.42, 0.04), std(0x222a3a, { emissive: 0x3a6ad0, emissiveIntensity: 0.8 })),
    () => mesh(new THREE.TorusGeometry(0.2, 0.05, 10, 24), gold),
    () => { const g = new THREE.Group(); for (let i = 0; i < 3; i++) g.add(mesh(new THREE.BoxGeometry(0.5, 0.05, 0.25), std(0x5aa05a), 0, i * 0.06, 0)); return g; },
  ];
  const bubbles = []; for (let i = 0; i < 9; i++) { const r = rng(130 + i); const g = new THREE.Group(); g.add(mesh(new THREE.SphereGeometry(0.55, 24, 16), bubbleM, 0, 0, 0, false)); const o = objs[i % objs.length](); g.add(o);
    const a = i / 9 * Math.PI * 2; g.userData = { a, rad: 1.6 + r() * 0.8, y: 1.6 + r() * 1.8, sp: 0.3 + r() * 0.3, o, pop: 33.6 + i * 0.08 }; S.add(g); bubbles.push(g); }
  const burst = points(400, 140, r => [0, 0, 0], 0xcfe8ff, 0.07, 0); S.add(burst); const bdir = []; { const r = rng(141); for (let i = 0; i < 400; i++) bdir.push([(r() - 0.5), (r() - 0.5), (r() - 0.5)]); }
  const top = new THREE.Color(0x1a2440), mid = new THREE.Color(0x6a5a7a), top2 = new THREE.Color(0x3a6aa0), mid2 = new THREE.Color(0xffb878);
  return (u, lt, t) => {
    const reveal = ease((t - 34.9) / 0.9);
    sky.material.uniforms.top.value.copy(top).lerp(top2, reveal); sky.material.uniforms.mid.value.copy(mid).lerp(mid2, reveal); sky.material.uniforms.sd.value.set(0, lerp(0.08, 0.12, reveal), -1).normalize();
    S.fog.color.set(0x5a5068).lerp(new THREE.Color(0xe8a87c), reveal); sun.intensity = 1.0 + 2.5 * reveal; hemi.intensity = 0.5 + 0.3 * reveal;
    bubbles.forEach((b, i) => { const d = b.userData; const ang = d.a + lt * d.sp; b.position.set(Math.cos(ang) * d.rad, d.y + 0.2 * Math.sin(lt * 1.3 + i), Math.sin(ang) * d.rad); d.o.rotation.y = lt * 1.2 + i;
      const pk = cl((t - d.pop) / 0.15); b.scale.setScalar(Math.max(0.001, (t < 30.9 + i * 0.12 ? ease((t - 30.6 - i * 0.12) / 0.3) : 1) * (1 - pk) + pk * 0.001)); b.visible = pk < 1; });
    const bk = cl((t - 33.6) / 1.2); const bp = burst.geometry.attributes.position;
    for (let i = 0; i < bp.count; i++) { const b = bubbles[i % 9]; const d = b.userData, ang = d.a + (d.pop - 30.6) * d.sp; bp.setXYZ(i, Math.cos(ang) * d.rad + bdir[i][0] * bk * 4, d.y + bdir[i][1] * bk * 4, Math.sin(ang) * d.rad + bdir[i][2] * bk * 4); }
    bp.needsUpdate = true; burst.material.opacity = t > 33.6 ? 1 - bk : 0;
    const fam = t > 34.6; wife.root.visible = kid.root.visible = fam;
    man.pose(fam ? POSE.hold(lt) : (t < 33.6 ? POSE.reach(lt * 2) : POSE.stand(lt))); wife.pose(POSE.hold(lt)); kid.pose(POSE.hold(lt));
    if (fam) { man.root.rotation.y = 0; }
    const k = ease(u), back = ease((t - 34.6) / 1.4);
    cam(C, V(lerp(2.2, 0.8, k), lerp(1.6, 2.0, k) + back * 0.6, lerp(4.5, 3.6, k) + back * 4.5), V(0, lerp(2.2, 1.6, k) - back * 0.4, 0)); };
});

// 8. ప్రాణం చిటికెలో తేలును ఆనందాల్లో – sunrise meadow, jump for joy, birds, sky lanterns
addScene(36.1, 41.33, (S, C) => {
  S.add(skyDome(0x3a78b0, 0xffc27a, 0x40302a, V(0, 0.07, -1), 0xffe0a0, 1.5)); S.fog = new THREE.FogExp2(0xc89068, 0.012);
  S.add(new THREE.HemisphereLight(0xffe0b0, 0x40502a, 0.7)); sunLight(S, 0xffd090, 3.4, V(0, 5, -25), V(0, 0, 0), 10);
  S.add(terrain(200, 120, 3.0, 0.04, 0x6a8a3a, 17, true));
  const sunM = mesh(new THREE.SphereGeometry(6, 24, 16), new THREE.MeshBasicMaterial({ color: 0xfff0c8 }), 0, 6, -160, false); S.add(sunM);
  const man = person({ shirt: 0xf2e8d8 }); S.add(man.root);
  const birds = []; for (let i = 0; i < 12; i++) { const r = rng(150 + i); const g = new THREE.Group(); const wm = std(0x2a2a30, { side: THREE.DoubleSide });
    const wl = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.18), wm); wl.position.x = 0.25; const wr2 = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.18), wm); wr2.position.x = -0.25;
    const pl = new THREE.Group(), pr = new THREE.Group(); pl.add(wl); pr.add(wr2); g.add(pl, pr); g.add(mesh(new THREE.SphereGeometry(0.07, 8, 6), wm)); g.userData = { pl, pr, x: (r() - 0.5) * 6, y: 3 + r() * 4, z: -4 - r() * 10, sp: 1.5 + r(), ph: r() * 6 }; S.add(g); birds.push(g); }
  const lanterns = []; for (let i = 0; i < 18; i++) { const r = rng(170 + i); const l = mesh(new THREE.CylinderGeometry(0.16, 0.12, 0.32, 8), glowMat(0xff9a3a, 2.5), (r() - 0.5) * 16, 0, -3 - r() * 16, false); l.userData = { y0: -2 - r() * 4, sp: 0.6 + r() * 0.5, d: r() * 2 }; S.add(l); lanterns.push(l); }
  const petals = points(200, 180, r => [(r() - 0.5) * 10, r() * 6, (r() - 0.5) * 8], 0xffd6a0, 0.09, 0.9); S.add(petals);
  [[-7, -6], [7, -9], [-12, -16], [13, -18]].forEach(([x, z]) => S.add(roundTree(x, z, 1.6, 0x4a7a30)));
  return (u, lt, t) => {
    const jumpT = lt - 0.9; const jump = jumpT > 0 ? Math.abs(Math.sin(jumpT * 2.6)) * 0.55 : 0;
    man.root.position.set(0, jump, 0); man.root.rotation.y = Math.PI; man.pose(jumpT > 0 ? POSE.jump(lt) : POSE.open(lt));
    birds.forEach(b => { const d = b.userData; b.position.set(d.x + Math.sin(lt * 0.3 + d.ph) * 1.5, d.y + lt * 0.5, d.z - lt * d.sp); const f = Math.sin(lt * 12 + d.ph) * 0.8; d.pl.rotation.z = f; d.pr.rotation.z = -f; });
    lanterns.forEach(l => { const d = l.userData; l.position.y = d.y0 + Math.max(0, lt - d.d) * d.sp * 1.6; });
    const p = petals.geometry.attributes.position, pb = petals.userData.base; for (let i = 0; i < p.count; i++) { p.setY(i, (pb[i * 3 + 1] + lt * 0.4) % 6); p.setX(i, pb[i * 3] + Math.sin(lt + i) * 0.4); } p.needsUpdate = true;
    const k = ease(u); cam(C, V(lerp(-1.5, 1.2, k), lerp(0.9, 1.6, k), lerp(4.2, 7.0, k)), V(0, lerp(1.5, 2.2, k), -4)); };
});

// C1. భజ గోవిందం – Krishna's flute and peacock feather floating in golden light
function featherTex() { const c = document.createElement('canvas'); c.width = 256; c.height = 512; const x = c.getContext('2d');
  for (let i = 0; i < 160; i++) { const y = 500 - i * 3; const w = 6 + Math.sin(i / 160 * Math.PI) * 110; x.strokeStyle = `rgba(${60 + i % 40},${150 + (i % 30)},${90 + i % 50},0.8)`; x.lineWidth = 2; x.beginPath(); x.moveTo(128, y); x.quadraticCurveTo(128 - w * 0.6, y - 10, 128 - w, y - 30); x.moveTo(128, y); x.quadraticCurveTo(128 + w * 0.6, y - 10, 128 + w, y - 30); x.stroke(); }
  const rings = [[78, '#3a8a3a'], [62, '#d8b040'], [46, '#2a9aa0'], [32, '#1a3aa0'], [18, '#0a0a3a']]; rings.forEach(([r, col]) => { x.fillStyle = col; x.beginPath(); x.ellipse(128, 130, r * 0.85, r, 0, 0, 7); x.fill(); });
  return new THREE.CanvasTexture(c); }
addScene(41.33, 46.3, (S, C) => {
  S.add(skyDome(0x140a20, 0x4a2a3a, 0x0a0610, V(0, 0.2, -1), 0xffb060, 0.8)); S.fog = new THREE.FogExp2(0x20101a, 0.03);
  S.add(new THREE.AmbientLight(0x806070, 0.4)); const kl = new THREE.PointLight(0xffc070, 14, 20, 1.5); kl.position.set(2, 3, 3); S.add(kl);
  const g = new THREE.Group(); S.add(g);
  const flute = mesh(new THREE.CylinderGeometry(0.11, 0.11, 4.2, 24), std(0x9a6a3a, { roughness: 0.45 }), 0, 0, 0); flute.rotation.z = Math.PI / 2 - 0.35; g.add(flute);
  for (let i = 0; i < 4; i++) { const b = mesh(new THREE.TorusGeometry(0.115, 0.025, 8, 24), std(0xffc040, { metalness: 0.9, roughness: 0.2 }), 0, -1.6 + i * 1.05, 0); b.rotation.x = Math.PI / 2; flute.add(b); }
  for (let i = 0; i < 6; i++) flute.add(mesh(new THREE.SphereGeometry(0.035, 8, 6), std(0x1a0a05), 0.0, -0.9 + i * 0.32, 0.1));
  const fm = new THREE.MeshStandardMaterial({ map: featherTex(), transparent: true, side: THREE.DoubleSide, roughness: 0.5, emissive: 0x204020, emissiveIntensity: 0.4, alphaTest: 0.05 });
  const fe = new THREE.Mesh(new THREE.PlaneGeometry(1.3, 2.6), fm); fe.position.set(1.7, 1.2, -0.2); fe.rotation.z = -0.5; g.add(fe);
  const motes = points(600, 200, r => [(r() - 0.5) * 9, (r() - 0.5) * 12, (r() - 0.5) * 6], 0xffc870, 0.1, 0.9); S.add(motes);
  const notesG = new THREE.Group(); S.add(notesG); const nm = glowMat(0xffd080, 2.4);
  for (let i = 0; i < 7; i++) { const r = rng(210 + i); const n = new THREE.Group(); n.add(mesh(new THREE.SphereGeometry(0.12, 12, 8), nm, 0, 0, 0, false)); n.add(mesh(new THREE.BoxGeometry(0.025, 0.45, 0.025), nm, 0.11, 0.22, 0, false)); n.add(mesh(new THREE.BoxGeometry(0.18, 0.04, 0.025), nm, 0.19, 0.43, 0, false)); n.userData = { x: (r() - 0.5) * 5, y: (r() - 0.5) * 5, ph: r() * 6 }; notesG.add(n); }
  return (u, lt) => {
    g.rotation.y = 0.3 * Math.sin(lt * 0.5) + lt * 0.15; g.position.y = 0.15 * Math.sin(lt * 1.2) + 1.6;
    fe.rotation.y = 0.4 * Math.sin(lt * 0.8);
    notesG.children.forEach((n, i) => { const d = n.userData; n.position.set(d.x + Math.sin(lt * 0.7 + d.ph) * 0.5, 1.6 + d.y + ((lt * 0.6 + i) % 4) - 2, -1 + Math.cos(lt + d.ph)); n.rotation.z = 0.3 * Math.sin(lt * 2 + d.ph); });
    const m = motes.geometry.attributes.position, mb = motes.userData.base; for (let i = 0; i < m.count; i++) m.setY(i, ((mb[i * 3 + 1] + 6 + lt * 0.5) % 12) - 6 + 1.6); m.needsUpdate = true;
    const k = ease(u); cam(C, V(lerp(-1.2, 1.0, k), lerp(1.4, 2.0, k), lerp(9, 6.5, k)), V(0, 1.7, 0)); };
});

// C2. బ్రతుకే కోలాహలం – village festival: fireworks, sky lanterns, people dancing
addScene(46.3, 51.3, (S, C) => {
  S.add(skyDome(0x050818, 0x2a1a3a, 0x0a0a10, V(0, 0.1, -1), 0xff8040, 0.3)); S.fog = new THREE.FogExp2(0x1a1424, 0.03);
  S.add(new THREE.HemisphereLight(0x6070a0, 0x201820, 0.4));
  S.add(terrain(160, 80, 1.0, 0.05, 0x2a3424, 23, true));
  const fire = new THREE.PointLight(0xff9040, 12, 16, 1.6); fire.position.set(0, 1, -1); S.add(fire);
  const torchM = glowMat(0xffa040, 4); [[-3, -2], [3, -2], [-4, -6], [4, -6]].forEach(([x, z]) => { S.add(mesh(new THREE.CylinderGeometry(0.05, 0.06, 1.8, 6), std(0x3a2a1a), x, 0.9, z)); S.add(mesh(new THREE.ConeGeometry(0.12, 0.35, 8), torchM, x, 1.95, z, false)); });
  // bunting
  const cols = [0xff4a4a, 0xffc040, 0x4ad06a, 0x4a8aff, 0xff6ad0, 0xff9a3a];
  for (let i = 0; i < 18; i++) { const x = -6 + i * 0.7, y = 3.6 - 0.35 * Math.sin(i / 17 * Math.PI); const f = mesh(new THREE.ConeGeometry(0.2, 0.42, 3), std(cols[i % 6], { emissive: cols[i % 6], emissiveIntensity: 0.5 }), x, y, -3, false); f.rotation.x = Math.PI; S.add(f); }
  const dancers = []; const dc = [0xe8d8c0, 0xd8506a, 0x4a8ad0, 0xffc040, 0x6ad06a];
  for (let i = 0; i < 5; i++) { const p = person({ shirt: dc[i], longHair: i % 2 == 1, saree: i % 2 == 1 ? dc[i] : null }); p.root.position.set(-2.4 + i * 1.2, 0, -1.5 + Math.abs(i - 2) * 0.4); S.add(p.root); dancers.push(p); }
  // fireworks
  const FW = []; for (let k = 0; k < 7; k++) { const r = rng(230 + k); const n = 220; const pts = points(n, 240 + k, () => [0, 0, 0], cols[k % 6], 0.22, 0); const dirs = []; for (let i = 0; i < n; i++) { const a = r() * 6.28, b = Math.acos(2 * r() - 1); dirs.push([Math.sin(b) * Math.cos(a), Math.cos(b), Math.sin(b) * Math.sin(a)]); }
    pts.userData = { t0: 46.5 + k * 0.62, c: [(r() - 0.5) * 14, 9 + r() * 6, -14 - r() * 10], dirs, R: 3 + r() * 2 }; S.add(pts); FW.push(pts); }
  const lan = []; for (let i = 0; i < 24; i++) { const r = rng(260 + i); const l = mesh(new THREE.CylinderGeometry(0.14, 0.1, 0.28, 8), glowMat(0xffa040, 2.6), (r() - 0.5) * 20, 0, -6 - r() * 18, false); l.userData = { y0: -1 - r() * 5, sp: 0.7 + r() * 0.5 }; S.add(l); lan.push(l); }
  return (u, lt, t) => {
    dancers.forEach((p, i) => { p.pose(POSE.dance(lt * 6 + i)); p.root.rotation.y = 0.4 * Math.sin(lt * 2 + i); });
    fire.intensity = 11 + 3 * Math.sin(lt * 13);
    FW.forEach(f => { const d = f.userData, k = (t - d.t0) / 1.6; const a = f.geometry.attributes.position;
      if (k < 0 || k > 1) { f.material.opacity = 0; return; } const e = 1 - Math.pow(1 - k, 3);
      for (let i = 0; i < a.count; i++) a.setXYZ(i, d.c[0] + d.dirs[i][0] * d.R * e, d.c[1] + d.dirs[i][1] * d.R * e - k * k * 1.5, d.c[2] + d.dirs[i][2] * d.R * e); a.needsUpdate = true; f.material.opacity = 1 - k; });
    lan.forEach(l => { const d = l.userData; l.position.y = d.y0 + lt * d.sp * 1.5; });
    const k = ease(u); cam(C, V(lerp(-3, 3, k), lerp(1.6, 2.4, k), lerp(7.5, 6.0, k)), V(0, lerp(1.6, 4.0, k), -3)); };
});

// C3. భజ గోవిందం – a great diya on a glowing rangoli, sparks rising
function rangoliTex() { const c = document.createElement('canvas'); c.width = c.height = 1024; const x = c.getContext('2d'); x.fillStyle = '#20150e'; x.fillRect(0, 0, 1024, 1024); x.translate(512, 512);
  const cols = ['#ff4a6a', '#ffc040', '#4ad0a0', '#4a8aff', '#ff8a3a', '#c86aff'];
  for (let ring = 0; ring < 6; ring++) { const R = 470 - ring * 70, n = 8 + ring * 2; for (let i = 0; i < n; i++) { x.save(); x.rotate(i / n * Math.PI * 2); x.fillStyle = cols[(ring + i) % 6]; x.beginPath(); x.ellipse(0, -R + 30, 22 + ring * 2, 42, 0, 0, 7); x.fill(); x.restore(); }
    x.strokeStyle = '#fff2d8'; x.lineWidth = 6; x.beginPath(); x.arc(0, 0, R - 70, 0, 7); x.stroke(); }
  for (let i = 0; i < 60; i++) { x.save(); x.rotate(i / 60 * Math.PI * 2); x.fillStyle = '#fff2d8'; x.beginPath(); x.arc(0, -490, 8, 0, 7); x.fill(); x.restore(); }
  return new THREE.CanvasTexture(c); }
addScene(51.3, 56.19, (S, C) => {
  S.add(skyDome(0x0a0610, 0x2a140c, 0x050302, V(0, 0.3, -1), 0xff9040, 0.3)); S.fog = new THREE.FogExp2(0x140a06, 0.05);
  S.add(new THREE.AmbientLight(0x604030, 0.3));
  const fl = mesh(new THREE.CircleGeometry(4, 64), new THREE.MeshStandardMaterial({ map: rangoliTex(), roughness: 0.9, emissive: 0xffffff, emissiveMap: rangoliTex(), emissiveIntensity: 0.25 }), 0, 0.01, 0, false); fl.rotation.x = -Math.PI / 2; S.add(fl);
  const gnd = mesh(new THREE.CircleGeometry(40, 32), std(0x1a120c), 0, 0, 0, false); gnd.rotation.x = -Math.PI / 2; S.add(gnd);
  const lp = []; for (let i = 0; i <= 16; i++) { const a = i / 16 * Math.PI / 2; lp.push(new THREE.Vector2(0.05 + Math.sin(a) * 0.9, 0.5 - Math.cos(a) * 0.5)); } lp.push(new THREE.Vector2(0.8, 0.5));
  const bowl = mesh(new THREE.LatheGeometry(lp, 40), std(0xb5652a, { roughness: 0.6 }), 0, 0.02, 0); S.add(bowl);
  S.add(mesh(new THREE.CylinderGeometry(0.82, 0.82, 0.03, 32), std(0xd8a040, { metalness: 0.5, roughness: 0.4 }), 0, 0.46, 0, false));
  const flame = mesh(new THREE.SphereGeometry(0.22, 16, 12), glowMat(0xffb040, 7), 0, 0.85, 0, false); S.add(flame);
  const core = mesh(new THREE.SphereGeometry(0.1, 12, 8), glowMat(0xfff4d0, 10), 0, 0.72, 0, false); S.add(core);
  const L1 = new THREE.PointLight(0xffa040, 14, 14, 1.4); L1.position.set(0, 1.1, 0); L1.castShadow = false; S.add(L1);
  const small = []; for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; const d = new THREE.Group(); d.position.set(Math.cos(a) * 3.3, 0, Math.sin(a) * 3.3); d.add(mesh(new THREE.SphereGeometry(0.16, 12, 6, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), std(0xb5652a), 0, 0.16, 0)); const f = mesh(new THREE.ConeGeometry(0.05, 0.18, 8), glowMat(0xffa030, 6), 0, 0.28, 0, false); d.add(f); d.userData.f = f; S.add(d); small.push(d); }
  const sparks = points(500, 300, r => [(r() - 0.5) * 1.2, r() * 8, (r() - 0.5) * 1.2], 0xffc060, 0.07, 0.9); S.add(sparks);
  return (u, lt) => {
    flame.scale.set(1 + 0.08 * Math.sin(lt * 23), 1.9 + 0.2 * Math.sin(lt * 31), 1 + 0.08 * Math.sin(lt * 19)); L1.intensity = 13 + 2 * Math.sin(lt * 17);
    small.forEach((d, i) => { const on = ease((lt - 0.2 - i * 0.12) / 0.2); d.userData.f.scale.setScalar(Math.max(0.01, on * (1 + 0.15 * Math.sin(lt * 20 + i)))); });
    const s = sparks.geometry.attributes.position, sb = sparks.userData.base; for (let i = 0; i < s.count; i++) { const y = (sb[i * 3 + 1] + lt * 1.2) % 8; s.setY(i, 0.9 + y); s.setX(i, sb[i * 3] * (1 + y * 0.4) + Math.sin(lt * 2 + i) * 0.1); s.setZ(i, sb[i * 3 + 2] * (1 + y * 0.4)); } s.needsUpdate = true;
    const k = ease(u), ang = lerp(0.2, 1.4, k); cam(C, V(Math.sin(ang) * lerp(7.5, 5.0, k), lerp(5.5, 2.4, k), Math.cos(ang) * lerp(7.5, 5.0, k)), V(0, 0.7, 0)); };
});

// C4. బరువే కాదే క్షణం – light as balloons: drifting up into a golden sky
addScene(56.19, 60.0, (S, C) => {
  S.add(skyDome(0x4a86c0, 0xffd29a, 0xa08060, V(0.3, 0.1, -1), 0xfff0c0, 1.2)); S.fog = new THREE.FogExp2(0xd0a888, 0.008);
  S.add(new THREE.HemisphereLight(0xffffff, 0x8a7050, 0.55)); sunLight(S, 0xffe0b0, 2.6, V(8, 10, -10), V(0, 4, 0), 8);
  const clouds = new THREE.Group(); for (let i = 0; i < 26; i++) { const r = rng(320 + i); const c = mesh(new THREE.IcosahedronGeometry(2 + r() * 3, 1), std(0xfff4ea, { flatShading: true }), (r() - 0.5) * 50, -6 + r() * 6, -10 - r() * 40, false); c.scale.y = 0.45; clouds.add(c); } S.add(clouds);
  const man = person({ shirt: 0xf2e8d8 }); S.add(man.root);
  const bc = [0xff5a6a, 0x5ab0ff, 0xffd040, 0x7ae08a, 0xc87aff]; const balloons = [];
  for (let i = 0; i < 5; i++) { const b = mesh(new THREE.SphereGeometry(0.42, 24, 18), new THREE.MeshPhysicalMaterial({ color: bc[i], roughness: 0.15, clearcoat: 1, emissive: bc[i], emissiveIntensity: 0.15 }), 0, 0, 0, false); b.scale.y = 1.2; S.add(b); balloons.push(b); }
  const strM = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.7 }); const strings = balloons.map(() => { const g = new THREE.BufferGeometry().setFromPoints([V(0, 0, 0), V(0, 1, 0)]); const l = new THREE.Line(g, strM); S.add(l); return l; });
  const feather = mesh(new THREE.PlaneGeometry(0.25, 0.8), new THREE.MeshStandardMaterial({ color: 0xffffff, side: THREE.DoubleSide, emissive: 0x806040, emissiveIntensity: 0.3 }), 2, 3, 1, false); S.add(feather);
  return (u, lt) => {
    const rise = lt * 0.9; man.root.position.set(0, rise, 0); man.pose(POSE.balloon(lt * 2)); man.root.rotation.y = 0.3 * Math.sin(lt * 0.5);
    man.root.updateMatrixWorld(true); const hand = new THREE.Vector3(); man.J.elR.localToWorld(hand.set(0, -0.32, 0));
    balloons.forEach((b, i) => { const a = i / 5 * Math.PI * 2; b.position.set(hand.x + Math.cos(a + lt * 0.3) * 0.55, hand.y + 1.6 + (i % 2) * 0.35 + 0.08 * Math.sin(lt * 2 + i), hand.z + Math.sin(a + lt * 0.3) * 0.45);
      strings[i].geometry.setFromPoints([hand.clone(), b.position.clone().add(V(0, -0.5, 0))]); });
    feather.position.set(1.6 + Math.sin(lt * 1.3) * 0.6, 2.4 + rise * 0.6 - lt * 0.2, 1); feather.rotation.set(Math.sin(lt * 2) * 0.6, lt, Math.sin(lt * 1.7) * 0.8);
    clouds.position.y = -rise * 0.4;
    const k = ease(u); cam(C, V(lerp(1.5, -1.0, k), rise + lerp(1.2, 0.4, k), lerp(6.5, 9.5, k)), V(0, rise + 1.8, 0)); };
});

// ---------------- post-processing ----------------
const comp = new EffectComposer(renderer); comp.setSize(RW, RH);
const rp = new RenderPass(SC[0].scene, SC[0].camera); comp.addPass(rp);
const bloom = new UnrealBloomPass(new THREE.Vector2(RW, RH), 0.55, 0.45, 1.35); comp.addPass(bloom);
const grade = new ShaderPass({ uniforms: { tDiffuse: { value: null }, time: { value: 0 } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }',
  fragmentShader: `uniform sampler2D tDiffuse; uniform float time; varying vec2 vUv;
    float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)) + time*7.0) * 43758.5453); }
    void main(){ vec3 c = texture2D(tDiffuse, vUv).rgb;
      float l = dot(c, vec3(0.299,0.587,0.114)); c = mix(c, c * vec3(1.05,1.0,0.92), 0.6); c = mix(vec3(l), c, 1.08);
      c = mix(c*vec3(0.92,1.0,1.08), c*vec3(1.06,1.0,0.9), smoothstep(0.2,0.7,l));
      vec2 d = vUv - 0.5; c *= 1.0 - 0.55 * pow(length(d*vec2(1.0,0.75))*1.4, 2.2);
      c += (h(vUv*vec2(720.0,1280.0)) - 0.5) * 0.035;
      gl_FragColor = vec4(c, 1.0); }` });
comp.addPass(grade); comp.addPass(new OutputPass());

// ---------------- lyrics ----------------
const LY = [
  [0.0, 1.8, 'ఉన్నంతలో మనకున్నంతలో', ''], [1.8, 4.4, 'బతికితే అదే సుఖము', 'అదే సుఖము'],
  [4.4, 6.6, 'ఎవరికి తలలొంచకా', ''], [6.6, 8.2, 'నువ్వు నీ కాళ్లపై', ''], [8.2, 10.0, 'నిలబడే గుణం వరము', 'గుణం వరము'],
  [10.0, 11.6, 'ఏదెలాగ రాసెనో', ''], [11.6, 13.1, 'అలాగే జరుగును', ''], [13.1, 15.1, 'మరెందుకో భయము', 'భయము'],
  [15.1, 16.9, 'అది అలాగ జరగక', ''], [16.9, 18.1, 'ఎలాగ జరిగిన', ''], [18.1, 20.6, 'వదులుకోకు ఎప్పుడు నమ్మకము', 'నమ్మకము'],
  [20.6, 22.6, 'ఏవో తెలియని', ''], [22.6, 24.6, 'పరుగులు తీసే', ''], [24.6, 25.6, 'తొందరలో', 'తొందరలో'],
  [25.6, 28.6, 'నీకే నువ్వే దొరకక', ''], [28.6, 29.6, 'సమయము గడపకు', ''], [29.6, 30.6, 'తెలివను భ్రమలో', 'తెలివను భ్రమలో'],
  [30.6, 33.6, 'చాలా ఆశల నడుమన', ''], [33.6, 36.1, 'చాల్లే అన్ని చూడు', 'చూడు'],
  [36.1, 39.1, 'ప్రాణం చిటికెలో తేలును', ''], [39.1, 41.3, 'ఆనందాల్లో...', 'ఆనందాల్లో...'],
  [41.3, 46.3, 'భజ గోవిందం భజ గోవిందం', '*'], [46.3, 51.3, 'బ్రతుకే కోలాహలం', '*'],
  [51.3, 56.3, 'భజ గోవిందం భజ గోవిందం', '*'], [56.3, 59.6, 'బరువే కాదే క్షణం', '*'],
];
const ly = document.getElementById('ly'), flashEl = document.getElementById('flash'), blackEl = document.getElementById('black');
let curLy = -1;
function lyrics(t) {
  const i = LY.findIndex(l => t >= l[0] && t < l[1]);
  if (i !== curLy) { curLy = i; if (i >= 0) { const [, , s, hl] = LY[i]; ly.className = hl === '*' ? 'chorus' : '';
      ly.innerHTML = hl && hl !== '*' && s.includes(hl) ? s.replace(hl, `<span class="hl">${hl}</span>`) : s;
      let fs = hl === '*' ? 96 : 84; ly.style.fontSize = fs + 'px'; while (ly.scrollWidth > 1000 && fs > 50) { fs -= 4; ly.style.fontSize = fs + 'px'; } } else ly.innerHTML = ''; }
  if (i < 0) return; const [a, b] = LY[i], u = t - a;
  ly.style.opacity = ease(u / 0.25) * ease((b - t) / 0.2);
  ly.style.transform = `translateY(${18 * (1 - ease(u / 0.35))}px) scale(${1 + 0.05 * (1 - ease(u / 0.35))})`;
  ly.style.filter = `blur(${4 * (1 - ease(u / 0.25))}px)`;
}

// ---------------- frame ----------------
window.render = function (t) {
  const i = Math.max(0, SC.findIndex(s => t >= s.t0 && t < s.t1)); const s = SC[i < 0 ? SC.length - 1 : i];
  const sc = SC[SC.findIndex(x => t >= x.t0 && t < x.t1)] || SC[SC.length - 1];
  sc.upd(cl((t - sc.t0) / (sc.t1 - sc.t0)), t - sc.t0, t);
  rp.scene = sc.scene; rp.camera = sc.camera; grade.uniforms.time.value = t;
  comp.render();
  // flash across every cut, dip from black at start, fade at the end
  let f = 0; for (const x of SC.slice(1)) { const d = t - x.t0; if (d > -0.18 && d < 0.4) f = Math.max(f, d < 0 ? (1 + d / 0.18) * 0.75 : 0.75 * (1 - d / 0.4)); }
  flashEl.style.opacity = f;
  blackEl.style.opacity = t < 0.35 ? 1 - ease(t / 0.35) : (t > 59.2 ? ease((t - 59.2) / 0.8) : 0);
  lyrics(t);
};
window.__ready = document.fonts.load('84px TeluguCap', 'ఉన్నంతలో').then(() => true);
