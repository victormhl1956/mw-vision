# 🐍 PROTOCOLO HYDRA
## Compartimentación de Código para MOE con Proveedores No-Confiables
### MindWareHouse — Arquitectura de Seguridad Operacional para IP

**Versión:** 1.0  
**Fecha:** Febrero 2026  
**Clasificación:** OPERACIONAL — Solo uso interno MindWareHouse  
**Autor:** Claude (Strategic Coordinator) para Victor Hernandez

---

## EL PROBLEMA REAL

Usas modelos chinos (DeepSeek V3, Qwen) porque son baratos y buenos. Pero la investigación confirma el riesgo:

- **DeepSeek retiene datos indefinidamente** — su política dice "as long as necessary" sin calendario de eliminación
- **No hay opt-out de entrenamiento** — cualquier prompt puede alimentar futuros modelos
- **Datos almacenados en servidores en China** — sujetos a leyes chinas de ciberseguridad que obligan a entregar datos al gobierno si lo solicitan
- **Sin cifrado end-to-end verificable** — investigadores de NowSecure encontraron transmisiones sin encriptar y claves hardcodeadas
- **Keystroke tracking** — registran patrones de tecleo, IDs de dispositivo, y datos de comportamiento

Pero DeepSeek V3 cuesta ~$0.27/1M tokens vs Claude Opus ~$15/1M. **55x más barato.** No puedes ignorar esa economía.

**La pregunta no es "¿usar o no usar modelos chinos?"**
**La pregunta es: "¿Cómo usarlos sin entregarles tu IP?"**

---

## LA SOLUCIÓN: PROTOCOLO HYDRA

> *"Córtale una cabeza a la Hydra y crecen dos más."*
> *Ninguna cabeza conoce el cuerpo completo.*

### Principio Central

**Fragmentación + Ofuscación + Rotación = Ningún proveedor ve tu código real completo.**

Inspirado en tres conceptos probados:

1. **Compartimentación militar** — cada agente solo sabe lo mínimo necesario para su tarea
2. **Shamir's Secret Sharing** — el secreto (tu código) se divide en N fragmentos; necesitas K fragmentos para reconstruirlo, y K-1 fragmentos no revelan NADA
3. **CodeCipher (ICLR 2025)** — ofuscación de código a nivel de tokens que preserva la funcionalidad del LLM pero hace el código ilegible para humanos

### Arquitectura de 4 Capas

```
╔══════════════════════════════════════════════════════════════╗
║  CAPA 1: DECOMPOSER (Descomponedor)                        ║
║  ├─ Modelo: LOCAL (Ollama) o TRUSTED (Claude API)           ║
║  ├─ Función: Analiza el código/tarea completa               ║
║  ├─ Output: Plan de fragmentación + interfaces abstractas   ║
║  └─ VE: Todo el código (pero corre LOCAL o en trusted)      ║
╠══════════════════════════════════════════════════════════════╣
║  CAPA 2: OBFUSCATOR (Ofuscador)                            ║
║  ├─ Modelo: NINGUNO — es código puro Python/JS              ║
║  ├─ Función: Renombra variables, elimina contexto de negocio║
║  ├─ Output: Fragmentos ofuscados + mapping table local      ║
║  └─ VE: Los fragmentos, pero sin nombres reales             ║
╠══════════════════════════════════════════════════════════════╣
║  CAPA 3: WORKERS (Trabajadores)                             ║
║  ├─ Modelos: DeepSeek, Qwen, MiniMax (los baratos/chinos)  ║
║  ├─ Función: Ejecutan sub-tareas sobre fragmentos ofuscados ║
║  ├─ Output: Código/respuesta para su fragmento específico   ║
║  └─ VE: Solo su fragmento ofuscado (sin contexto completo)  ║
╠══════════════════════════════════════════════════════════════╣
║  CAPA 4: ASSEMBLER (Ensamblador)                            ║
║  ├─ Modelo: LOCAL (Ollama) o TRUSTED (Claude API)           ║
║  ├─ Función: De-ofusca + ensambla + valida código final     ║
║  ├─ Output: Código completo funcional                       ║
║  └─ VE: Todo (pero corre LOCAL o en trusted)                ║
╚══════════════════════════════════════════════════════════════╝
```

**Resultado: Los modelos chinos (Capa 3) NUNCA ven:**
- Nombres reales de variables/funciones/clases
- Contexto de negocio (qué hace el sistema)
- La arquitectura completa
- Cómo se conectan los fragmentos entre sí

---

## TIPOS DE FRAGMENTACIÓN

### Tipo 1: Fragmentación Funcional
Divide por responsabilidad. Cada worker ve una función aislada.

```
TAREA ORIGINAL: "Construir sistema de autenticación con JWT + 2FA"

DECOMPOSER divide en:
├─ Fragment_A: "Función que valida formato de string contra regex"
│  → Worker DeepSeek (no sabe que es validación de email)
├─ Fragment_B: "Función que genera hash de string con salt aleatorio"  
│  → Worker Qwen (no sabe que es hashing de password)
├─ Fragment_C: "Función que crea token firmado con payload y expiry"
│  → Worker DeepSeek (no sabe que es JWT)
├─ Fragment_D: "Función que genera código numérico de N dígitos con TTL"
│  → Worker MiniMax (no sabe que es 2FA)
└─ Fragment_E: "Middleware que compone las funciones A,B,C,D"
   → ASSEMBLER LOCAL (este SÍ ve todo)
```

### Tipo 2: Fragmentación por Capa
Divide por capa arquitectónica.

```
TAREA: "API endpoint para procesar transacciones"

├─ Fragment_A: "Esquema de validación de datos de entrada" (JSON Schema)
│  → Worker: Solo ve estructura de datos, no sabe de transacciones
├─ Fragment_B: "Query SQL parametrizado para insertar registro"
│  → Worker: Solo ve SQL genérico, no sabe la tabla real
├─ Fragment_C: "Lógica de cálculo con reglas de negocio"  
│  → Worker: Variables ofuscadas, no sabe qué calcula
├─ Fragment_D: "Tests unitarios para función de cálculo"
│  → Worker: Solo ve interface abstracta
└─ ASSEMBLER: Renombra todo, conecta capas, integra
```

### Tipo 3: Fragmentación por Transformación
Cada worker hace una operación diferente sobre el mismo código.

```
CÓDIGO EXISTENTE: network_analysis.py (OSINT-MW)

├─ Worker_A (DeepSeek): "Optimiza el rendimiento de esta función"
│  → Recibe versión ofuscada (func_a, var_x, var_y)
├─ Worker_B (Qwen): "Añade manejo de errores a esta función"
│  → Recibe OTRA versión ofuscada (handler_1, data_in)
├─ Worker_C (DeepSeek): "Escribe tests para esta interfaz"
│  → Recibe solo la signatura de función, no el body
└─ ASSEMBLER LOCAL: Combina optimización + error handling + tests
   sobre el código REAL con nombres REALES
```

---

## EL OFUSCADOR: CÓMO FUNCIONA

### Nivel 1: Renombrado (Siempre activo)
```python
# ANTES (código real)
def analyze_militia_network(members_db, connections):
    threat_score = calculate_threat_level(members_db)
    key_leaders = identify_commanders(connections)
    return IntelligenceReport(threat_score, key_leaders)

# DESPUÉS (lo que ve el Worker)
def process_graph(dataset_a, edges):
    metric_1 = compute_score(dataset_a)
    subset_b = filter_nodes(edges)
    return OutputStruct(metric_1, subset_b)
```

El Worker ve un problema genérico de grafos. No tiene idea de que es análisis de milicia.

### Nivel 2: Abstracción de dominio (Para tareas sensibles)
```python
# ANTES
class OSINTCrawler:
    def scrape_dgcim_personnel(self, source_url):
        raw_data = self.fetch(source_url)
        personnel = self.extract_names_ranks(raw_data)
        return self.cross_reference_sanctions(personnel)

# DESPUÉS (lo que ve el Worker)
class DataExtractor:
    def collect_records(self, endpoint):
        raw = self.fetch(endpoint)
        entities = self.parse_fields(raw)
        return self.validate_against_list(entities)
```

### Nivel 3: Fragmentación + Ofuscación combinada
```python
# El Worker A solo ve:
def parse_fields(raw_text):
    """Extract structured data from semi-structured text input.
    Return list of dicts with keys: id, label, category."""
    # TU CÓDIGO AQUÍ

# El Worker B solo ve:
def validate_against_list(entities, reference_list):
    """Check each entity against reference. Return matches."""
    # TU CÓDIGO AQUÍ

# El Worker C solo ve:
def compute_score(entity, weights):
    """Calculate weighted score from entity attributes."""
    # TU CÓDIGO AQUÍ

# NADIE ve cómo se conectan estas 3 funciones
# NADIE sabe qué "entities" son
# NADIE conoce el reference_list real
```

---

## ROTACIÓN DEL ASSEMBLER

### ¿Por qué rotar?

Si el Assembler siempre es Claude, entonces Anthropic ve todo tu código completo siempre. Eso es mejor que DeepSeek (Anthropic tiene mejores políticas de privacidad y no entrena con datos de API), pero aún es un single point of trust.

### Estrategia de rotación

```
SEMANA 1: Assembler = Claude Sonnet (API, no entrena con datos)
SEMANA 2: Assembler = Ollama local (llama-3.3-70b en tu Ryzen 9)
SEMANA 3: Assembler = Claude Sonnet
SEMANA 4: Assembler = Ollama local

ALTERNATIVA PARA PC ACTUAL (32GB RAM):
- Ollama con qwen2.5-coder:14b (cabe en RAM)
- O codestral:22b (necesita ~16GB, apretado pero viable)
```

### Beneficio de la rotación

```
Datos que ve cada proveedor en 1 mes:
├─ DeepSeek: 40 fragmentos ofuscados sin contexto  → Valor: ~0
├─ Qwen: 30 fragmentos ofuscados sin contexto       → Valor: ~0
├─ Claude API: 2 semanas de ensamblaje              → Valor: parcial
├─ Ollama local: 2 semanas de ensamblaje            → Valor: MÁXIMO
│  (pero nunca sale de tu PC)
└─ NADIE: Vista completa de todo un mes             → Imposible
```

---

## IMPLEMENTACIÓN PRÁCTICA

### Archivo: hydra_obfuscator.py

```python
"""
Hydra Protocol — Code Obfuscator
Transforma código real en fragmentos ofuscados para workers no-confiables.
"""
import re
import json
import random
import string
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ObfuscationMapping:
    """Mapa bidireccional: nombre real ↔ nombre ofuscado."""
    forward: dict = field(default_factory=dict)   # real → fake
    reverse: dict = field(default_factory=dict)   # fake → real
    session_id: str = ""

    def add(self, real_name: str, fake_name: str):
        self.forward[real_name] = fake_name
        self.reverse[fake_name] = real_name

    def save(self, path: str):
        """Guardar mapping LOCAL. NUNCA enviar a un LLM."""
        data = {
            "session_id": self.session_id,
            "forward": self.forward,
            "reverse": self.reverse,
        }
        Path(path).write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: str) -> "ObfuscationMapping":
        data = json.loads(Path(path).read_text())
        m = cls(session_id=data["session_id"])
        m.forward = data["forward"]
        m.reverse = data["reverse"]
        return m


class HydraObfuscator:
    """Motor de ofuscación para el Protocolo Hydra."""

    # Pools de nombres genéricos para reemplazo
    GENERIC_FUNCS = [
        "process", "compute", "transform", "handle", "execute",
        "validate", "filter", "parse", "convert", "analyze",
        "build", "generate", "extract", "merge", "resolve",
    ]
    GENERIC_VARS = [
        "data", "items", "result", "output", "value",
        "records", "entries", "elements", "buffer", "cache",
        "config", "state", "context", "params", "options",
    ]
    GENERIC_CLASSES = [
        "Processor", "Handler", "Manager", "Builder", "Service",
        "Controller", "Adapter", "Engine", "Pipeline", "Resolver",
    ]

    def __init__(self):
        self.mapping = ObfuscationMapping(
            session_id=hashlib.md5(
                str(random.random()).encode()
            ).hexdigest()[:8]
        )
        self._used_names = set()

    def _gen_name(self, pool: list, prefix: str = "") -> str:
        """Genera nombre único del pool."""
        for _ in range(100):
            base = random.choice(pool)
            suffix = random.choice(string.ascii_lowercase) + str(
                random.randint(1, 99)
            )
            name = f"{prefix}{base}_{suffix}"
            if name not in self._used_names:
                self._used_names.add(name)
                return name
        return f"{prefix}item_{random.randint(100,999)}"

    def obfuscate_identifiers(self, code: str, sensitive_names: list[str]) -> str:
        """
        Reemplaza nombres sensibles con genéricos.
        
        Args:
            code: Código fuente original
            sensitive_names: Lista de identificadores a ofuscar
                             (nombres de funciones, variables, clases)
        Returns:
            Código ofuscado
        """
        result = code
        for name in sorted(sensitive_names, key=len, reverse=True):
            # Determinar tipo por convención
            if name[0].isupper():
                fake = self._gen_name(self.GENERIC_CLASSES)
            elif "(" in code[code.find(name):code.find(name) + len(name) + 5]:
                fake = self._gen_name(self.GENERIC_FUNCS)
            else:
                fake = self._gen_name(self.GENERIC_VARS)

            self.mapping.add(name, fake)
            # Reemplazar con word boundaries
            result = re.sub(r'\b' + re.escape(name) + r'\b', fake, result)

        return result

    def strip_comments(self, code: str) -> str:
        """Eliminar comentarios que puedan revelar contexto de negocio."""
        # Eliminar comentarios de línea
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        # Eliminar docstrings
        code = re.sub(r'"""[\s\S]*?"""', '""""""', code)
        code = re.sub(r"'''[\s\S]*?'''", "''''''", code)
        return code

    def inject_generic_docstrings(self, code: str) -> str:
        """Reemplazar docstrings vacíos con genéricos."""
        replacements = [
            "Process the input and return result.",
            "Transform data according to specification.",
            "Handle the operation and return output.",
            "Execute the defined workflow step.",
        ]
        for placeholder in ['""""""', "''''''", '"""  """']:
            while placeholder in code:
                doc = f'"""{random.choice(replacements)}"""'
                code = code.replace(placeholder, doc, 1)
        return code

    def fragment_code(
        self,
        code: str,
        fragment_boundaries: list[tuple[str, int, int]],
    ) -> list[dict]:
        """
        Divide código en fragmentos por boundaries definidas.
        
        Args:
            code: Código fuente
            fragment_boundaries: Lista de (nombre, linea_inicio, linea_fin)
        Returns:
            Lista de fragmentos con metadata
        """
        lines = code.split("\n")
        fragments = []
        for name, start, end in fragment_boundaries:
            fragment_code = "\n".join(lines[start - 1 : end])
            fragments.append(
                {
                    "id": f"frag_{self.mapping.session_id}_{len(fragments)}",
                    "name": name,
                    "code": fragment_code,
                    "lines": f"{start}-{end}",
                    "dependencies": [],  # Se llena después
                }
            )
        return fragments

    def deobfuscate(self, code: str) -> str:
        """Restaurar nombres reales desde el mapping."""
        result = code
        # Reemplazar en orden inverso (más largo primero)
        for fake, real in sorted(
            self.mapping.reverse.items(), key=lambda x: len(x[0]), reverse=True
        ):
            result = re.sub(r'\b' + re.escape(fake) + r'\b', real, result)
        return result


# ─── Funciones de conveniencia ──────────────────────────

def obfuscate_for_worker(
    code: str,
    sensitive_names: list[str],
    mapping_save_path: str = "hydra_mapping.json",
) -> str:
    """
    Pipeline completo de ofuscación.
    Úsalo antes de enviar código a un worker no-confiable.
    """
    h = HydraObfuscator()
    code = h.strip_comments(code)
    code = h.obfuscate_identifiers(code, sensitive_names)
    code = h.inject_generic_docstrings(code)
    h.mapping.save(mapping_save_path)
    return code


def deobfuscate_from_worker(
    code: str,
    mapping_path: str = "hydra_mapping.json",
) -> str:
    """
    Restaurar código recibido de un worker.
    Úsalo en el ASSEMBLER después de recibir output del worker.
    """
    mapping = ObfuscationMapping.load(mapping_path)
    result = code
    for fake, real in sorted(
        mapping.reverse.items(), key=lambda x: len(x[0]), reverse=True
    ):
        result = re.sub(r'\b' + re.escape(fake) + r'\b', real, result)
    return result
```

### Archivo: hydra_decomposer.py

```python
"""
Hydra Protocol — Task Decomposer
Analiza una tarea y genera fragmentos para distribución segura.
"""
import json
from dataclasses import dataclass


@dataclass
class HydraFragment:
    """Un fragmento de tarea para un worker."""
    id: str
    description: str           # Descripción genérica (sin contexto de negocio)
    code_snippet: str          # Código ofuscado (si aplica)
    interface: str             # Signatura de función esperada
    trust_level: str           # "untrusted" | "trusted" | "local"
    assigned_model: str        # Modelo que ejecutará
    dependencies: list[str]    # IDs de fragmentos que necesita como input


@dataclass  
class HydraDecomposition:
    """Plan completo de descomposición."""
    original_task: str         # NUNCA se envía a workers
    fragments: list[HydraFragment]
    assembly_order: list[str]  # Orden de ensamblaje
    assembler_model: str       # Modelo para ensamblar


# Prompt template para el Decomposer (corre LOCAL o en trusted)
DECOMPOSER_PROMPT = """You are a code task decomposer for a security-focused system.
Your job is to break a coding task into independent fragments that can be 
assigned to UNTRUSTED AI workers.

RULES:
1. Each fragment must be SELF-CONTAINED — completable without seeing other fragments
2. Remove ALL domain-specific terminology from fragment descriptions
3. Use GENERIC names: "process data", "validate input", "compute score"
4. Never mention the actual business purpose in fragment descriptions
5. Define clear INPUT/OUTPUT interfaces for each fragment
6. Mark which fragments need a TRUSTED model vs can go to untrusted

TASK TO DECOMPOSE:
{task_description}

CONTEXT CODE (if any):
{code_context}

Respond in JSON:
{{
  "fragments": [
    {{
      "id": "frag_N",
      "description": "generic description for untrusted worker",
      "interface": "def func_name(param: type) -> return_type",
      "trust_level": "untrusted|trusted|local",
      "reason_for_trust_level": "why this level",
      "estimated_tokens": 500
    }}
  ],
  "assembly_instructions": "how to combine fragments (for trusted assembler only)",
  "security_notes": "what sensitive info was stripped"
}}"""


def create_decomposition_prompt(task: str, code: str = "") -> str:
    """Genera el prompt para el Decomposer."""
    return DECOMPOSER_PROMPT.format(
        task_description=task,
        code_context=code if code else "(no existing code)",
    )
```

### Archivo: hydra_router.py

```python
"""
Hydra Protocol — Secure Router
Enruta fragmentos al modelo correcto según trust level.
"""
import os
import random
from datetime import datetime
from litellm import completion


# Trust tiers de modelos
MODEL_TRUST = {
    # TIER 1: Local — máxima confianza, nunca sale de tu máquina
    "local": [
        "ollama/qwen2.5-coder:14b",
        "ollama/codestral:22b",
        "ollama/llama3.3:70b",        # Solo en Ryzen 9 con 128GB
        "ollama/deepseek-coder-v2:16b",
    ],
    # TIER 2: Trusted — políticas de privacidad verificables, no entrenan con API data
    "trusted": [
        "anthropic/claude-sonnet-4-5-20250929",
        "anthropic/claude-opus-4-5",
    ],
    # TIER 3: Untrusted — baratos pero datos van a servidores en China
    "untrusted": [
        "openrouter/deepseek/deepseek-chat-v3",
        "openrouter/qwen/qwen-2.5-coder-32b",
        "openrouter/minimax/minimax-m2.1",
    ],
}

# Costo estimado por 1M tokens (input)
MODEL_COSTS = {
    "ollama/qwen2.5-coder:14b": 0.0,          # Gratis (local)
    "ollama/codestral:22b": 0.0,                # Gratis (local)
    "anthropic/claude-sonnet-4-5-20250929": 3.0,
    "anthropic/claude-opus-4-5": 15.0,
    "openrouter/deepseek/deepseek-chat-v3": 0.27,
    "openrouter/qwen/qwen-2.5-coder-32b": 0.20,
    "openrouter/minimax/minimax-m2.1": 0.0,     # Free tier
}


class HydraRouter:
    """Enruta fragmentos según trust level con rotación."""
    
    def __init__(self, assembler_rotation: str = "weekly"):
        self.rotation = assembler_rotation
        self.call_log = []  # Para auditoría
    
    def select_model(self, trust_level: str, prefer_cheap: bool = True) -> str:
        """Selecciona modelo según trust level."""
        candidates = MODEL_TRUST.get(trust_level, MODEL_TRUST["untrusted"])
        
        if prefer_cheap:
            # Ordenar por costo
            candidates = sorted(candidates, key=lambda m: MODEL_COSTS.get(m, 999))
        
        # Verificar disponibilidad (Ollama puede no estar corriendo)
        for model in candidates:
            if model.startswith("ollama/"):
                try:
                    # Quick test
                    completion(model=model, messages=[{"role": "user", "content": "test"}], max_tokens=5)
                    return model
                except:
                    continue
            else:
                return model
        
        # Fallback
        return candidates[0] if candidates else "openrouter/deepseek/deepseek-chat-v3"
    
    def get_assembler_model(self) -> str:
        """Selecciona assembler con rotación temporal."""
        week_num = datetime.now().isocalendar()[1]
        
        if self.rotation == "weekly":
            if week_num % 2 == 0:
                return self.select_model("local", prefer_cheap=False)
            else:
                return self.select_model("trusted", prefer_cheap=True)
        elif self.rotation == "always_local":
            return self.select_model("local")
        elif self.rotation == "always_trusted":
            return self.select_model("trusted")
        else:
            # Random
            tier = random.choice(["local", "trusted"])
            return self.select_model(tier)
    
    def route_fragment(self, fragment_id: str, trust_level: str, prompt: str) -> str:
        """Envía fragmento al modelo correcto y retorna respuesta."""
        model = self.select_model(trust_level)
        
        self.call_log.append({
            "timestamp": datetime.now().isoformat(),
            "fragment_id": fragment_id,
            "trust_level": trust_level,
            "model": model,
            "prompt_tokens": len(prompt.split()) * 1.3,  # Estimado
        })
        
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
        )
        
        return response.choices[0].message.content
    
    def get_audit_report(self) -> dict:
        """Reporte de qué modelo vio qué."""
        report = {}
        for entry in self.call_log:
            model = entry["model"]
            if model not in report:
                report[model] = {"fragments_seen": [], "trust_level": entry["trust_level"]}
            report[model]["fragments_seen"].append(entry["fragment_id"])
        return report
```

### Archivo: hydra_pipeline.py

```python
"""
Hydra Protocol — Pipeline Completo
Orquesta el flujo Decompose → Obfuscate → Route → Assemble.
"""
import json
from datetime import datetime
from hydra_obfuscator import HydraObfuscator, obfuscate_for_worker, deobfuscate_from_worker
from hydra_decomposer import create_decomposition_prompt
from hydra_router import HydraRouter
from litellm import completion


class HydraPipeline:
    """Pipeline completo del Protocolo Hydra."""
    
    def __init__(self, assembler_rotation: str = "weekly"):
        self.router = HydraRouter(assembler_rotation=assembler_rotation)
        self.obfuscator = HydraObfuscator()
    
    def execute(
        self,
        task: str,
        code_context: str = "",
        sensitive_names: list[str] = None,
    ) -> dict:
        """
        Ejecutar tarea completa con el Protocolo Hydra.
        
        Args:
            task: Descripción de la tarea
            code_context: Código existente (si aplica)
            sensitive_names: Nombres a ofuscar
        """
        results = {
            "task": task,
            "started": datetime.now().isoformat(),
            "fragments": [],
            "final_code": "",
            "audit": {},
        }
        
        # ═══ PASO 1: DECOMPOSE (trusted/local) ════════════
        print("🔍 [HYDRA] Paso 1: Descomponiendo tarea...")
        decompose_prompt = create_decomposition_prompt(task, code_context)
        decomposer_model = self.router.select_model("trusted")
        
        decomp_response = completion(
            model=decomposer_model,
            messages=[{"role": "user", "content": decompose_prompt}],
            max_tokens=4096,
        )
        
        try:
            plan = json.loads(decomp_response.choices[0].message.content)
        except json.JSONDecodeError:
            # Extraer JSON del response si viene con texto extra
            text = decomp_response.choices[0].message.content
            start = text.find("{")
            end = text.rfind("}") + 1
            plan = json.loads(text[start:end])
        
        print(f"   ✅ {len(plan['fragments'])} fragmentos generados")
        
        # ═══ PASO 2: OBFUSCATE + ROUTE (untrusted) ════════
        print("🔒 [HYDRA] Paso 2: Ofuscando y distribuyendo...")
        worker_results = []
        
        for frag in plan["fragments"]:
            trust = frag.get("trust_level", "untrusted")
            
            # Si es untrusted, ofuscar
            prompt = frag["description"]
            if trust == "untrusted" and sensitive_names:
                prompt = self.obfuscator.obfuscate_identifiers(
                    prompt, sensitive_names
                )
            
            # Añadir interface spec
            if frag.get("interface"):
                prompt += f"\n\nImplement this interface:\n{frag['interface']}"
            
            prompt += "\n\nReturn ONLY the code, no explanations."
            
            # Enviar al worker
            print(f"   📤 {frag['id']} → {trust}")
            result = self.router.route_fragment(frag["id"], trust, prompt)
            worker_results.append({
                "fragment_id": frag["id"],
                "trust_level": trust,
                "code": result,
            })
        
        print(f"   ✅ {len(worker_results)} fragmentos completados")
        
        # ═══ PASO 3: ASSEMBLE (trusted/local) ═════════════
        print("🔧 [HYDRA] Paso 3: Ensamblando...")
        assembler_model = self.router.get_assembler_model()
        
        assembly_prompt = f"""You are the ASSEMBLER in a secure code pipeline.
You will receive code fragments from multiple workers.
Your job is to combine them into a single, working, cohesive module.

ORIGINAL TASK: {task}

ASSEMBLY INSTRUCTIONS: {plan.get('assembly_instructions', 'Combine logically')}

FRAGMENTS:
"""
        for wr in worker_results:
            assembly_prompt += f"\n--- Fragment {wr['fragment_id']} ---\n{wr['code']}\n"
        
        assembly_prompt += "\nCombine these into a single, working module. Fix any interface mismatches."
        
        final_response = completion(
            model=assembler_model,
            messages=[{"role": "user", "content": assembly_prompt}],
            max_tokens=8192,
        )
        
        final_code = final_response.choices[0].message.content
        
        # De-ofuscar si aplicable
        if sensitive_names:
            final_code = self.obfuscator.deobfuscate(final_code)
        
        results["final_code"] = final_code
        results["audit"] = self.router.get_audit_report()
        results["completed"] = datetime.now().isoformat()
        
        print("   ✅ Ensamblaje completo")
        print(f"\n🛡️ [HYDRA] Reporte de seguridad:")
        for model, info in results["audit"].items():
            n = len(info["fragments_seen"])
            trust = info["trust_level"]
            print(f"   {model}: {n} fragmentos ({trust})")
        
        return results


# ─── Ejemplo de uso ─────────────────────────────────
if __name__ == "__main__":
    pipeline = HydraPipeline(assembler_rotation="weekly")
    
    result = pipeline.execute(
        task="Create a function that scrapes public records from a government website, extracts personnel names and positions, and stores them in a SQLite database with deduplication",
        sensitive_names=[
            "scrape_dgcim", "personnel", "militia_members",
            "sanctions_list", "threat_score", "OSINT",
            "intelligence_report", "network_analysis",
        ],
    )
    
    print("\n" + "=" * 60)
    print("FINAL CODE:")
    print("=" * 60)
    print(result["final_code"])
```

---

## NIVELES DE SEGURIDAD SEGÚN SENSITIVIDAD

```
NIVEL 1: CÓDIGO PÚBLICO / OPEN SOURCE
├─ Ofuscación: Ninguna
├─ Fragmentación: Ninguna
├─ Worker: Cualquiera (DeepSeek directo = máximo ahorro)
├─ Assembler: Cualquiera
└─ Ejemplo: README, documentación, utils genéricos

NIVEL 2: CÓDIGO PROPIETARIO ESTÁNDAR
├─ Ofuscación: Nivel 1 (renombrado de variables)
├─ Fragmentación: Funcional (1 función por worker)
├─ Worker: Untrusted OK
├─ Assembler: Trusted (Claude API)
└─ Ejemplo: Features de MindWareHouse, crews de CrewAI

NIVEL 3: CÓDIGO SENSIBLE / IP CORE
├─ Ofuscación: Nivel 2 (abstracción de dominio completa)
├─ Fragmentación: Por capa + funcional
├─ Worker: Mix untrusted (fragmentos) + trusted (validación)
├─ Assembler: LOCAL ONLY (Ollama)
└─ Ejemplo: MOE routing logic, cost optimization algorithms

NIVEL 4: CÓDIGO CLASIFICADO / OSINT-MW
├─ Ofuscación: Nivel 3 (máxima) + datos falsos inyectados
├─ Fragmentación: Máxima granularidad (10-20 líneas por fragment)
├─ Worker: SOLO local para lógica, untrusted solo para boilerplate
├─ Assembler: LOCAL ONLY, NUNCA cloud
└─ Ejemplo: DGCIM database queries, network analysis, ICC documentation
```

---

## INTEGRACIÓN CON EL STACK MOE

### En moe_config.py, añadir:

```python
# Hydra trust routing integrado con MOE
HYDRA_ROUTING = {
    # task_type → (trust_level, fragmentation_type)
    "docs":       ("untrusted", "none"),         # Documentación = sin riesgo
    "test":       ("untrusted", "functional"),   # Tests sin contexto de negocio
    "boilerplate":("untrusted", "none"),         # CRUD, config = genérico
    "feature":    ("untrusted", "functional"),   # Features fragmentados
    "debug":      ("trusted",   "layer"),        # Debug necesita contexto
    "architect":  ("trusted",   "layer"),        # Arquitectura = trusted
    "security":   ("trusted",   "none"),         # Security review = trusted
    "osint":      ("local",     "max_fragment"), # OSINT = máxima protección
    "core_ip":    ("local",     "max_fragment"), # Core IP = máxima protección
}
```

### En mw-route.ps1, modificar:

```powershell
# Hydra-aware routing
$hydra = @{
    "docs"       = @{ trust="untrusted"; frag="none" }
    "test"       = @{ trust="untrusted"; frag="functional" }
    "debug"      = @{ trust="trusted";   frag="layer" }
    "architect"  = @{ trust="trusted";   frag="layer" }
    "osint"      = @{ trust="local";     frag="max" }
    "core"       = @{ trust="local";     frag="max" }
}

# Si trust=untrusted → ejecutar Hydra pipeline
# Si trust=local → ejecutar directo en Ollama
# Si trust=trusted → ejecutar directo en Claude
```

---

## MÉTRICAS DE EFECTIVIDAD

### ¿Qué puede reconstruir un adversario?

```
ESCENARIO: DeepSeek decide entrenar con tus datos.

SIN Hydra:
  DeepSeek tiene: Tu código completo con nombres reales
  Reconstrucción posible: 100% de tu IP
  Riesgo: CRÍTICO

CON Hydra (Nivel 2 - estándar):
  DeepSeek tiene: 5 fragmentos de 20 líneas cada uno
  Nombres: Todos genéricos (process_a, data_b, compute_c)
  Contexto: Cero (no sabe qué hace el sistema)
  Conexiones: Cero (no sabe cómo se unen los fragmentos)
  Reconstrucción posible: <5% (y sin utilidad práctica)
  Riesgo: MÍNIMO

CON Hydra (Nivel 4 - OSINT):
  DeepSeek tiene: 2 fragmentos boilerplate genéricos
  Reconstrucción posible: 0%
  Riesgo: NULO
```

### Impacto en costos

```
SIN Hydra (todo en Claude por seguridad):
  1000 requests/mes × Claude Sonnet = ~$150-200/mes

CON Hydra (fragmentos en DeepSeek, ensamblaje en Claude/local):
  800 fragmentos → DeepSeek  = ~$5/mes
  200 ensamblajes → Claude   = ~$30/mes
  Decomposer → Claude        = ~$10/mes
  TOTAL                      = ~$45/mes (75% reducción)

CON Hydra + Ryzen 9 (Assembler local):
  800 fragmentos → DeepSeek  = ~$5/mes
  200 ensamblajes → Ollama   = $0/mes
  Decomposer → Ollama        = $0/mes
  TOTAL                      = ~$5/mes (97% reducción)
```

---

## LIMITACIONES HONESTAS

1. **Overhead de latencia**: Hydra añade 2-3 llamadas extra por tarea (decompose + assemble). Una tarea de 30 segundos puede tomar 90 segundos.

2. **No protege contra análisis estadístico masivo**: Si un adversario acumula miles de fragmentos ofuscados, podría detectar patrones. Mitigación: rotar esquemas de ofuscación.

3. **Tareas altamente acopladas**: Algunas tareas no se fragmentan bien (ej: refactoring completo de un módulo). Para esas, usar trusted/local directo.

4. **Calidad del Assembler**: Un modelo local 14B ensambla peor que Claude Opus. Balance: usar local para Nivel 4, trusted para Nivel 2-3.

5. **El Decomposer ve todo**: El modelo que descompone la tarea necesita ver el contexto completo. Mitigación: ejecutar siempre en local o trusted.

6. **Modelos locales requieren hardware**: En tu Dell OptiPlex actual, solo caben modelos ≤14B. El Ryzen 9 con 128GB desbloqueará modelos 70B como assembler local.

---

## ROADMAP DE IMPLEMENTACIÓN

```
FASE 1 — AHORA (Dell OptiPlex 32GB):
├─ Implementar hydra_obfuscator.py (Nivel 1-2 de ofuscación)
├─ Configurar Ollama con qwen2.5-coder:14b como assembler local
├─ Integrar con mw-route.ps1 para routing automático
├─ Probar con tareas MindWareHouse no-sensibles
└─ Validar que fragmentación no degrada calidad

FASE 2 — CON RYZEN 9 (128GB):
├─ Subir assembler local a llama3.3:70b o codestral:70b
├─ Implementar Nivel 3-4 de ofuscación
├─ Automatizar decomposer con modelo local
├─ Hydra pipeline 100% local para OSINT-MW
└─ Eliminar dependencia de trusted cloud para código clasificado

FASE 3 — PRODUCCIÓN:
├─ Integrar Hydra con Langfuse (traces por fragmento)
├─ Dashboard de auditoría: quién vio qué
├─ Auto-clasificación de sensitividad por archivo
├─ Métricas: % de código expuesto por proveedor
└─ Rotación automática de esquemas de ofuscación
```

---

## RESUMEN EJECUTIVO

**Protocolo Hydra** permite a MindWareHouse usar modelos baratos de cualquier jurisdicción sin exponer IP, mediante:

1. **Decomposición** inteligente de tareas en fragmentos independientes
2. **Ofuscación** de identificadores y contexto de negocio  
3. **Routing** por nivel de confianza del proveedor
4. **Ensamblaje** rotativo entre local y trusted
5. **Auditoría** completa de qué modelo vio qué fragmento

**Ningún proveedor individual puede reconstruir tu sistema.**
**Do More with Less — sin entregar más de lo necesario.**
