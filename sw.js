const V='alice-v6';
const CORE=["./", "index.html", "manifest.webmanifest", "ffbb.json", "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png", "img/affiche.jpg", "img/duo.jpg", "img/lun-1.jpg", "img/lun-2.jpg", "img/lun-3.jpg", "img/lun-4.jpg", "img/mar-1.jpg", "img/mar-2.jpg", "img/mar-3.jpg", "img/mar-4.jpg", "img/mar-5.jpg", "img/mar-6.jpg", "img/mar-7.jpg", "img/ombre.jpg", "img/sam-1.jpg", "img/sam-2.jpg", "img/sam-3.jpg", "img/sam-4.jpg", "img/sam-5.jpg", "img/sam-6.jpg"];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==V).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const r=e.request; if(r.method!=='GET') return;
  const u=new URL(r.url); if(u.origin!==location.origin) return;
  if(u.pathname.endsWith('ffbb.json')||r.mode==='navigate'){
    e.respondWith(fetch(r).then(x=>{const c=x.clone();caches.open(V).then(h=>h.put(r,c));return x}).catch(()=>caches.match(r).then(m=>m||caches.match('index.html'))));
    return;
  }
  e.respondWith(caches.match(r).then(m=>m||fetch(r).then(x=>{const c=x.clone();caches.open(V).then(h=>h.put(r,c));return x})));
});
