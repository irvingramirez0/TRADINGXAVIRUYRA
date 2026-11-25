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
//     node 09_AUTOMATION/verificar_sitio.mjs http://127.0.0.1:8899 build
//
// El tercer argumento, `build`, sirve para probar un build local servido con
// `python -m http.server`, que NO resuelve `/bootcamp/dia-13` sin extensión
// (devuelve 404 aunque el archivo exista). GitHub Pages y `quartz build
// --serve` sí lo resuelven. Sin esta opción, probar en local daba 6 fallos
// falsos y parecía que el sitio estaba roto.
//
// Requiere Chrome instalado y conexión al sitio. Sale con código 1 si algo
// falla, para que sirva en un pipeline.


import { spawn } from "node:child_process"
const CHROME="C:/Program Files/Google/Chrome/Application/chrome.exe"
const B=process.argv[2]||"https://irvingramirez0.github.io/TRADINGXAVIRUYRA"
// Servidor de archivos planos: hay que pedir `.html` explícitamente.
const ARCHIVOS_PLANOS = process.argv[3]==="build"
const u = ruta => B + (ARCHIVOS_PLANOS && !/\.[a-z0-9]+$/i.test(ruta) ? ruta + ".html" : ruta)
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
const nTarjetas = await A.ev("document.querySelectorAll('.xr-tarjeta').length")
check(`portada: ${nTarjetas} tarjetas de entrada`, nTarjetas >= 9)
check("portada: sin anotaciones (es portada)", await A.ev("!document.querySelector('.xr-anot')"))
A.cerrar()

// 2. Bootcamp índice
A=await abrir(B+"/bootcamp/","qa-c2",9402)
const nDias = await A.ev("document.querySelectorAll('.xr-dia').length")
check(`bootcamp: ${nDias} días listados`, nDias >= 29)
check("bootcamp: panel", await A.ev("!!document.querySelector('.xr-panel')"))
check("bootcamp: cada día enlaza a su página", await A.ev(`[...document.querySelectorAll('.xr-dia-titulo')].length===${nDias} && [...document.querySelectorAll('.xr-dia-titulo')].every(a=>/dia-[0-9][0-9]/.test(a.getAttribute('href')||''))`))
A.cerrar()

// 3. Un día
A=await abrir(u("/bootcamp/dia-13"),"qa-c3",9403)
check("dia-13: ficha de fuente", await A.ev("!!document.querySelector('.xr-ficha')"))
check("dia-13: enlace al vídeo en el minuto", await A.ev("/youtube\.com\/watch\?v=.+&t=\d+s/.test((document.querySelector('.xr-boton-fuente')||{}).href||'')"))
check("dia-13: enlaza concepto IFVG", await A.ev("[...document.querySelectorAll('a.internal')].some(a=>a.getAttribute('href').includes('inverse-fair-value-gap-ifvg'))"))
check("dia-13: navegación anterior/siguiente", await A.ev("document.body.innerHTML.includes('Día 12') && document.body.innerHTML.includes('Día 14')"))
A.cerrar()

// 3-bis. Un día recién transcrito y SIN trabajar.
//
// Este caso existe por un fallo real: el Día 21 se publicó con
// `confianza: explícito` y enlace al segundo 0 sin tener una sola fila de
// evidencia. La página tiene que decir «transcrita, sin trabajar», no fingir
// que está analizada. Es el estado más fácil de romper sin querer al tocar el
// generador, así que se comprueba aparte y contra la página que lo padeció.
A=await abrir(u("/bootcamp/dia-21"),"qa-c3b",9408)
check("dia-21: enlaza fuentes citadas", await A.ev("/youtube\.com\/watch\?v=.+&t=\d+s/.test((document.querySelector('.xr-boton-fuente')||{}).href||'')"))
check("dia-21: no enlaza al segundo 0", await A.ev("!/[?&]t=0s/.test((document.querySelector('.xr-boton-fuente')||{}).href||'')"))
check("dia-21: apunte del curriculum marcado como historial", await A.ev("/cuando se catalogó/i.test(document.body.textContent)"))
A.cerrar()

// 3-ter. Portada: ningún botón debe abrir el segundo cero.
A=await abrir(B+"/bootcamp/","qa-t0",9410)
check("bootcamp: ningún botón abre el segundo 0", await A.ev("![...document.querySelectorAll('.xr-boton-fuente')].some(a=>/[?&]t=0s/.test(a.href||''))"))
A.cerrar()
A=await abrir(B+"/conceptos/","qa-core",9411)
check("conceptos: ruta por dependencia publicada", await A.ev("!!document.querySelector('a[href*=\"ruta\"]')"))
A.cerrar()
A=await abrir(B+"/comprobador/","qa-comp",9412)
check("comprobador: cifra honesta de operaciones", await A.ev("/0[\\/\\s]+\\d+ operaciones con cita formal/.test(document.body.textContent)"))
check("comprobador: no dice 'Todo tiene fuente'", await A.ev("!/Todo tiene fuente/.test(document.body.textContent)"))
A.cerrar()

// 4. Concepto con imágenes
A=await abrir(u("/conceptos/inverse-fair-value-gap-ifvg"),"qa-c4",9404)
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

// 8. Calidad de lectura e interacción.
//
// Estas cinco comprobaciones existen porque cada una era un defecto real y
// ninguno se veía mirando la página: un texto de 95 caracteres por línea se
// lee mal sin parecer roto, y un foco de teclado invisible solo lo nota quien
// navega con Tab. Se miden sobre el DOM renderizado, no sobre el CSS.
A=await abrir(u("/conceptos/judas-swing"),"qa-c8",9409)
check(
  "lectura: la línea no pasa de 75 caracteres",
  await A.ev(`(() => {
    const par=[...document.querySelectorAll("article p")].find(p=>p.textContent.length>120)
    if(!par) return false
    const cs=getComputedStyle(par)
    const s=document.createElement("span")
    s.textContent="0".repeat(75); s.style.cssText="position:absolute;visibility:hidden;font:"+cs.font
    par.appendChild(s); const ancho=s.getBoundingClientRect().width; s.remove()
    return par.getBoundingClientRect().width <= ancho
  })()`),
)
check(
  "lectura: el gris secundario se lee (>=4.5:1)",
  await A.ev(`(() => {
    const lum=c=>{const v=c.match(/[\\d.]+/g).slice(0,3).map(Number).map(x=>{x/=255;return x<=0.03928?x/12.92:Math.pow((x+0.055)/1.055,2.4)});return 0.2126*v[0]+0.7152*v[1]+0.0722*v[2]}
    const bg=lum(getComputedStyle(document.body).backgroundColor)
    const el=document.querySelector(".xr-chip")
    if(!el) return true
    const L=lum(getComputedStyle(el).color)
    return (Math.max(L,bg)+0.05)/(Math.min(L,bg)+0.05) >= 4.5
  })()`),
)
check(
  "teclado: el foco dibuja un anillo visible",
  await A.ev(`(() => {
    const reglas=[...document.styleSheets].flatMap(sh=>{try{return [...sh.cssRules]}catch(e){return []}})
    return reglas.some(r=>r.cssText && r.cssText.includes("focus-visible") && /outline:\\s*2px/.test(r.cssText))
  })()`),
)
check(
  "formulario de anotaciones: no ocupa media pantalla",
  await A.ev(`(() => {
    const f=document.querySelector(".xr-anot-form")
    return !!f && f.getBoundingClientRect().height < 400
  })()`),
)
check(
  "movimiento: hay ruta para quien pide menos animación",
  await A.ev(`(() => {
    const reglas=[...document.styleSheets].flatMap(sh=>{try{return [...sh.cssRules]}catch(e){return []}})
    return reglas.some(r=>r.cssText && r.cssText.includes("prefers-reduced-motion"))
  })()`),
)
A.cerrar()

console.log(`\n${n-fallos}/${n} comprobaciones OK`)
process.exit(fallos?1:0)
