// Comprueba el sitio publicado contra sus casos de uso reales.
//
// Qué hace: abre cada tipo de página en Chrome headless (por CDP, sin
// dependencias) y comprueba el comportamiento del lector, no solo el HTML:
// que el título sea único, que el panel y la ficha estén, que los 21 días del
// bootcamp enlacen a su página, que las imágenes carguen de verdad
// (naturalWidth > 0), que las anotaciones monten y que la página 404 exista.
//
// Por qué así: `curl | grep` da falsos positivos (ya pasó con la clase
// `xr-dia`, que también aparece en `xr-dias` y en `xr-dia-titulo`) y no
// distingue un componente que se carga de uno que se pinta. Aquí se evalúa en
// el DOM ya renderizado.
//
// Uso:
//     node 09_AUTOMATION/verificar_sitio.mjs
//     node 09_AUTOMATION/verificar_sitio.mjs http://localhost:8080
//
// Requiere Chrome instalado y conexión al sitio. Sale con código 1 si algo
// falla, para que sirva en un pipeline.


import { spawn } from "node:child_process"
const CHROME="C:/Program Files/Google/Chrome/Application/chrome.exe"
const B=process.argv[2]||"https://irvingramirez0.github.io/TRADINGXAVIRUYRA"
const dormir=ms=>new Promise(r=>setTimeout(r,ms))

async function abrir(url,perfil,puerto){
  const p=spawn(CHROME,["--headless=new","--disable-gpu",`--remote-debugging-port=${puerto}`,
    "--user-data-dir="+process.env.TEMP+"/"+perfil,"--no-first-run",url],{stdio:"ignore"})
  let ws=null
  for(let i=0;i<25;i++){
    await dormir(600)
    try{const t=await(await fetch(`http://127.0.0.1:${puerto}/json/list`)).json()
      const pg=t.find(x=>x.type==="page"&&x.url.indexOf("http")===0)
      if(pg){ws=pg.webSocketDebuggerUrl;break}}catch(e){}
  }
  if(!ws){p.kill();throw new Error("no arranco")}
  const s=new WebSocket(ws);let id=0;const pend=new Map()
  s.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&pend.has(m.id)){pend.get(m.id)(m);pend.delete(m.id)}}
  await new Promise(r=>s.onopen=r)
  const send=(me,pr={})=>new Promise(r=>{const i=++id;pend.set(i,r);s.send(JSON.stringify({id:i,method:me,params:pr}))})
  const ev=async e=>{const r=await send("Runtime.evaluate",{expression:e,returnByValue:true,awaitPromise:true});
    return r.result?.result?.value ?? ("EXC:"+(r.result?.exceptionDetails?.exception?.description||"").split("\n")[0])}
  await send("Runtime.enable");await dormir(1500)
  return {ev,cerrar:()=>{s.close();p.kill()}}
}

const ok=(c)=>c?"OK  ":"FALLA"
let n=0, fallos=0
const check=(nombre,cond)=>{n++;if(!cond)fallos++;console.log(`  ${ok(cond)} ${nombre}`)}

// 1. Portada
let A=await abrir(B+"/","qa-c1",9401)
check("portada: título único", await A.ev("document.querySelectorAll('h1').length")===1)
check("portada: panel con cifras", await A.ev("document.querySelectorAll('.xr-cifra').length")>=5)
check("portada: 7 tarjetas de entrada", await A.ev("document.querySelectorAll('.xr-tarjeta').length")===7)
check("portada: sin anotaciones (es portada)", await A.ev("!document.querySelector('.xr-anot')"))
A.cerrar()

// 2. Bootcamp índice
A=await abrir(B+"/bootcamp/","qa-c2",9402)
check("bootcamp: 21 días listados", await A.ev("document.querySelectorAll('.xr-dia').length")===21)
check("bootcamp: panel", await A.ev("!!document.querySelector('.xr-panel')"))
check("bootcamp: cada día enlaza a su página", await A.ev("[...document.querySelectorAll('.xr-dia-titulo')].length===21 && [...document.querySelectorAll('.xr-dia-titulo')].every(a=>/dia-[0-9][0-9]/.test(a.getAttribute('href')||''))"))
A.cerrar()

// 3. Un día
A=await abrir(B+"/bootcamp/dia-13","qa-c3",9403)
check("dia-13: ficha de fuente", await A.ev("!!document.querySelector('.xr-ficha')"))
check("dia-13: enlace al vídeo en el minuto", await A.ev("/youtube\.com\/watch\?v=.+&t=\d+s/.test((document.querySelector('.xr-boton-fuente')||{}).href||'')"))
check("dia-13: enlaza concepto IFVG", await A.ev("[...document.querySelectorAll('a.internal')].some(a=>a.getAttribute('href').includes('inverse-fair-value-gap-ifvg'))"))
check("dia-13: navegación anterior/siguiente", await A.ev("document.body.innerHTML.includes('Día 12') && document.body.innerHTML.includes('Día 14')"))
A.cerrar()

// 4. Concepto con imágenes
A=await abrir(B+"/conceptos/inverse-fair-value-gap-ifvg","qa-c4",9404)
check("ifvg: imagen carga (naturalWidth>0)", await A.ev("[...document.querySelectorAll('article img')].every(i=>i.naturalWidth>0)"))
check("ifvg: una imagen en el cuerpo (la otra es la de redes)", await A.ev("document.querySelectorAll('article p img, article figure img').length>=1"))
check("ifvg: anotaciones montadas", await A.ev("document.querySelector('.xr-anot')?.dataset.iniciado==='1'"))
check("ifvg: secciones disponibles", await A.ev("document.querySelectorAll('#xr-anot-seccion option').length")>5)
A.cerrar()

// 5. Página sin imágenes y sin ficha (índice)
A=await abrir(B+"/reglas/","qa-c5",9405)
check("reglas: índice con tarjetas", await A.ev("document.querySelectorAll('.xr-tarjeta').length")>100)
check("reglas: sin ficha (es índice)", await A.ev("!document.querySelector('.xr-ficha')"))
A.cerrar()

// 6. Operaciones: aviso de P&L
A=await abrir(B+"/operaciones/","qa-c6",9406)
check("operaciones: aviso P&L visible", await A.ev("document.body.textContent.includes('P&L autodeclarado')"))
A.cerrar()

// 7. 404
A=await abrir(B+"/esto-no-existe","qa-c7",9407)
check("404: página de error", await A.ev("document.title.includes('404') || document.body.textContent.includes('404')"))
A.cerrar()

console.log(`\n${n-fallos}/${n} comprobaciones OK`)
process.exit(fallos?1:0)
