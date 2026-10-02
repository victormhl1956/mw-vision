// Qué endpoints pide la interfaz, leídos del árbol sintáctico de TypeScript.
//
// Por qué con el compilador y no con grep. Un grep de `fetch(` encuentra las
// llamadas pero no resuelve `${API_BASE}/agents` a `/api/agents`, no distingue
// una llamada real de una comentada o de una que vive dentro de una cadena, y
// no dice en qué componente está. El dato que hace falta es el camino final,
// porque es lo que se cruza con la medición del backend: una interfaz
// perfectamente cableada contra un endpoint que devuelve una semilla sigue
// siendo un panel falso, y eso sólo se ve uniendo los dos lados.
//
// Sale por stdout en JSON. No juzga nada: sólo dice qué pide quién.
//
// Uso: node llamadas_ui.mjs <raiz-del-frontend>

import { createRequire } from "node:module";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative, sep } from "node:path";

// `import ts from "typescript"` sólo resuelve si el fichero vive dentro del
// proyecto; createRequire lo resuelve desde aquí pase lo que pase, así que la
// herramienta funciona igual ejecutada desde cualquier directorio.
const require = createRequire(import.meta.url);
const ts = require("typescript");

const raiz = process.argv[2];
if (!raiz) {
  console.error("uso: node llamadas_ui.mjs <raiz-del-frontend>");
  process.exit(3);
}

const OMITIR = new Set(["node_modules", "dist", "build", ".git", "coverage"]);

function ficheros(dir, acc = []) {
  for (const nombre of readdirSync(dir)) {
    if (OMITIR.has(nombre)) continue;
    const ruta = join(dir, nombre);
    const s = statSync(ruta);
    if (s.isDirectory()) ficheros(ruta, acc);
    else if (/\.(ts|tsx)$/.test(nombre) && !nombre.endsWith(".d.ts")) acc.push(ruta);
  }
  return acc;
}

// Constantes de módulo que son cadenas, para poder resolver `${API_BASE}/x`.
function constantesDeCadena(sf) {
  const mapa = new Map();
  const visitar = (n) => {
    if (ts.isVariableStatement(n)) {
      for (const d of n.declarationList.declarations) {
        if (!ts.isIdentifier(d.name) || !d.initializer) continue;
        const v = valorDeCadena(d.initializer, mapa);
        if (v !== null) mapa.set(d.name.text, v);
      }
    }
    ts.forEachChild(n, visitar);
  };
  ts.forEachChild(sf, visitar);
  return mapa;
}

// El valor de una expresión como cadena, o null si no se puede saber.
// Resuelve literales, plantillas, `a ?? b` (se queda con el respaldo, que es
// el valor por defecto que corre cuando no hay variable de entorno) y los
// identificadores que ya estén en el mapa.
function valorDeCadena(n, mapa) {
  if (ts.isStringLiteral(n) || ts.isNoSubstitutionTemplateLiteral(n)) return n.text;
  if (ts.isTemplateExpression(n)) {
    let salida = n.head.text;
    for (const span of n.templateSpans) {
      const trozo = valorDeCadena(span.expression, mapa);
      // Un hueco que no se puede resolver se marca, no se borra: mejor
      // «/api/agents/{?}» que un camino inventado.
      salida += trozo === null ? "{?}" : trozo;
      salida += span.literal.text;
    }
    return salida;
  }
  if (ts.isIdentifier(n)) return mapa.has(n.text) ? mapa.get(n.text) : null;
  if (ts.isBinaryExpression(n) &&
      (n.operatorToken.kind === ts.SyntaxKind.QuestionQuestionToken ||
       n.operatorToken.kind === ts.SyntaxKind.BarBarToken)) {
    // import.meta.env.X ?? 'http://localhost:8000/api' -> el respaldo.
    const der = valorDeCadena(n.right, mapa);
    if (der !== null) return der;
    return valorDeCadena(n.left, mapa);
  }
  if (ts.isParenthesizedExpression(n)) return valorDeCadena(n.expression, mapa);
  if (ts.isAsExpression(n) || ts.isTypeAssertionExpression?.(n)) {
    return valorDeCadena(n.expression, mapa);
  }
  if (ts.isCallExpression(n)) {
    // wsUrl('/ws') y parecidas: el argumento de cadena es el camino.
    for (const a of n.arguments) {
      const v = valorDeCadena(a, mapa);
      if (v !== null) return v;
    }
  }
  return null;
}

// El nombre de la función o componente que contiene al nodo.
function contenedor(n) {
  let p = n.parent;
  while (p) {
    if ((ts.isFunctionDeclaration(p) || ts.isMethodDeclaration(p)) && p.name) {
      return p.name.getText();
    }
    if ((ts.isArrowFunction(p) || ts.isFunctionExpression(p))) {
      const d = p.parent;
      if (ts.isVariableDeclaration(d) && ts.isIdentifier(d.name)) return d.name.text;
      if (ts.isPropertyAssignment(d) && d.name) return d.name.getText();
    }
    p = p.parent;
  }
  return "(nivel de módulo)";
}

// Normaliza un URL absoluto a su camino, para poder cruzarlo con el backend.
function camino(url) {
  const m = /^[a-z]+:\/\/[^/]+(\/.*)?$/i.exec(url);
  let c = m ? (m[1] ?? "/") : url;
  if (!c.startsWith("/")) c = "/" + c;
  // Los parámetros de ruta se normalizan al estilo de FastAPI.
  c = c.replace(/\{\?\}/g, "{param}");
  return c.split("?")[0].replace(/\/+$/, "") || "/";
}

const llamadas = [];
const sinResolver = [];

for (const ruta of ficheros(raiz)) {
  const texto = readFileSync(ruta, "utf8");
  const sf = ts.createSourceFile(ruta, texto, ts.ScriptTarget.Latest, true,
    ruta.endsWith(".tsx") ? ts.ScriptKind.TSX : ts.ScriptKind.TS);
  const mapa = constantesDeCadena(sf);
  const rel = relative(raiz, ruta).split(sep).join("/");

  const visitar = (n) => {
    let clase = null;
    let objetivo = null;
    let exigirCamino = false;

    if (ts.isCallExpression(n)) {
      const f = n.expression.getText();
      // `fetch` y axios son inequívocos. Un `.get(...)` cualquiera NO lo es:
      // `mapa.get(node.id)` no es una petición, y contarlo metía ruido en la
      // lista de endpoints. Para esos se exige que el receptor parezca un
      // cliente HTTP, y aun así el camino tiene que parecer un camino.
      const inequivoco = f === "fetch" || /^axios(\.\w+)?$/.test(f);
      const quizas = /\.(get|post|put|patch|delete)$/.test(f) &&
        /(axios|api|client|http|request|rest)/i.test(f);
      if (inequivoco || quizas) {
        clase = "http";
        objetivo = n.arguments[0];
        if (quizas) exigirCamino = true;
      }
    } else if (ts.isNewExpression(n) && n.expression.getText() === "WebSocket") {
      clase = "websocket";
      objetivo = n.arguments?.[0];
    }

    if (clase && objetivo) {
      const url = valorDeCadena(objetivo, mapa);
      const linea = sf.getLineAndCharacterOfPosition(n.getStart()).line + 1;
      const pareceCamino = url !== null &&
        (url.startsWith("/") || /^[a-z]+:\/\//i.test(url) ||
         url.startsWith("${"));
      if (url === null || (exigirCamino && !pareceCamino)) {
        if (!exigirCamino) {
          sinResolver.push({ fichero: rel, linea, clase,
                             texto: objetivo.getText().slice(0, 120) });
        }
      } else {
        llamadas.push({ fichero: rel, linea, clase, url, camino: camino(url),
                        donde: contenedor(n) });
      }
    }
    ts.forEachChild(n, visitar);
  };
  ts.forEachChild(sf, visitar);
}

// ───────────────────────────────────────────────────────────────────────────
// Datos escritos dentro del propio frontend
//
// Medir las llamadas no basta para decir «el frontend está bien». Un componente
// puede pedir por fetch Y además pintar una lista escrita a mano, o no pedir
// nada y pintar sólo literales. Lo segundo es un panel falso sin que el backend
// tenga ninguna culpa, y afirmarlo sin medirlo sería exactamente el error que
// este trabajo persigue.
//
// Qué cuenta como dato escrito dentro: un array de 2 o más objetos declarado en
// un fichero de componente o vista. Un array de cadenas (nombres de pestañas,
// clases de CSS) o un objeto de configuración NO cuenta: es presentación, no
// dato. La distinción es deliberadamente conservadora, porque un falso positivo
// aquí gasta el tiempo de alguien leyendo código que estaba bien.
// ───────────────────────────────────────────────────────────────────────────

const literales = [];
// Cuántos ficheros entraron de verdad en el filtro de componentes y vistas.
// Sin esto, medir un proyecto cuya interfaz NO está en components/ ni views/
// devuelve «0 literales», que se lee como un aprobado y es en realidad «no
// miré en ningún sitio». Exactamente el falso verde que persigue este trabajo,
// cometido al hacer la herramienta portable.
let ficherosDePanel = 0;
// Simulación en el propio navegador: el botón «refrescar» del panel de
// seguridad sumaba amenazas detectadas con Math.random(). Es la misma categoría
// que el simulador del backend, en el otro lado del cable, y no se ve midiendo
// las llamadas.
const simulaciones = [];

for (const ruta of ficheros(raiz)) {
  const rel = relative(raiz, ruta).split(sep).join("/");
  // Sólo donde hay paneles: componentes y vistas. Un literal en services/ o
  // stores/ es casi siempre configuración o un valor inicial.
  if (!/^(components|views)\//.test(rel)) continue;
  ficherosDePanel += 1;

  const texto = readFileSync(ruta, "utf8");
  const sf = ts.createSourceFile(ruta, texto, ts.ScriptTarget.Latest, true,
    ruta.endsWith(".tsx") ? ts.ScriptKind.TSX : ts.ScriptKind.TS);

  const visitar = (n) => {
    if (ts.isCallExpression(n)) {
      const f = n.expression.getText();
      // Math.random().toString(36) es una clave de React, no un dato: Toast.tsx
      // la usa para el id de cada aviso y marcarla sería gastar el tiempo de
      // quien lo lea. Lo que importa es el azar que acaba en una CIFRA.
      const esIdentificador = ts.isPropertyAccessExpression(n.parent) &&
        /^(toString|slice|substr|substring)$/.test(n.parent.name.text);
      if (/^Math\.(random|floor|ceil|round)$/.test(f) && !esIdentificador &&
          texto.slice(Math.max(0, n.getStart() - 200), n.getEnd())
            .includes("Math.random")) {
        simulaciones.push({
          fichero: rel,
          linea: sf.getLineAndCharacterOfPosition(n.getStart()).line + 1,
          donde: contenedor(n),
          texto: n.getText().slice(0, 120),
        });
      }
    }
    if (ts.isArrayLiteralExpression(n)) {
      const objetos = n.elements.filter((e) => ts.isObjectLiteralExpression(e));
      if (objetos.length >= 2) {
        // ¿Lo pinta alguien? Un array que sólo se usa para un tipo o un
        // valor por defecto de un formulario no es un panel.
        const nombre = nombreDeclarado(n);
        literales.push({
          fichero: rel,
          linea: sf.getLineAndCharacterOfPosition(n.getStart()).line + 1,
          nombre,
          filas: objetos.length,
          claves: [...new Set(objetos.flatMap((o) => o.properties
            .map((p) => (p.name ? p.name.getText() : "?"))))].slice(0, 8),
          donde: contenedor(n),
        });
      }
    }
    ts.forEachChild(n, visitar);
  };
  ts.forEachChild(sf, visitar);
}

function nombreDeclarado(n) {
  let p = n.parent;
  if (ts.isVariableDeclaration(p) && ts.isIdentifier(p.name)) return p.name.text;
  if (ts.isPropertyAssignment(p) && p.name) return p.name.getText();
  if (ts.isCallExpression(p)) return `(argumento de ${p.expression.getText()})`;
  return "(sin nombre)";
}

// Qué componentes piden algo a la API, directa o indirectamente, para poder
// decir cuáles pintan SÓLO literales.
const importaApi = new Map();
for (const ruta of ficheros(raiz)) {
  const rel = relative(raiz, ruta).split(sep).join("/");
  const texto = readFileSync(ruta, "utf8");
  const pide = /\b(fetch|useWebSocket|api|crewStore|useStore|websocketService)\b/
    .test(texto);
  importaApi.set(rel, pide);
}

console.log(JSON.stringify({
  raiz, llamadas, sin_resolver: sinResolver,
  literales: literales.map((l) => ({ ...l,
    el_fichero_pide_datos: importaApi.get(l.fichero) === true })),
  simulaciones,
  ficheros_de_panel_examinados: ficherosDePanel,
  carpetas_de_panel: ["components/", "views/"],
}, null, 2));
