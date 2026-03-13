"""
config.py — Configurações e Constantes do LifePulse Pro
Sistema Preditivo de Retenção ANS

Todas as constantes, pesos e configurações centralizadas aqui.
"""

# ═══════════════════════════════════════════════════════════════════════════
# THEME & UI
# ═══════════════════════════════════════════════════════════════════════════

THEME = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "success": "#48bb78",
    "warning": "#ed8936",
    "danger": "#f56565",
    "text": "#1a202c",
    "bg": "#ffffff",
}

# ═══════════════════════════════════════════════════════════════════════════
# RISK SCORING — Pesos para cálculo de score
# ═══════════════════════════════════════════════════════════════════════════

RISK_WEIGHTS = {
    "tempo_cliente": 0.20,        # 20% - Quanto menos tempo, maior risco
    "protocolos": 0.25,           # 25% - Mais protocolos = mais insatisfação
    "sentimento": 0.20,           # 20% - Sentimento negativo em protocolos
    "sinistralidade": 0.15,       # 15% - Alta sinistralidade = alto custo
    "inadimplencia": 0.20,        # 20% - Inadimplente = alto risco
}

# Limites de score para classificação
RISK_THRESHOLDS = {
    "baixo": (0, 40),
    "medio": (40, 70),
    "alto": (70, 100),
}

# ═══════════════════════════════════════════════════════════════════════════
# RETENTION DIFFICULTY — Classificação por IA
# ═══════════════════════════════════════════════════════════════════════════

DIFFICULTY_RULES = {
    "facil": {
        "max_protocolos": 2,
        "min_tempo_meses": 24,
        "keywords_negativas": [],
    },
    "moderado": {
        "max_protocolos": 5,
        "keywords_negativas": ["preço", "caro", "reajuste"],
    },
    "dificil": {
        "keywords_negativas": ["ANS", "Procon", "cancelar", "advogado"],
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# ROI CALCULATION
# ═══════════════════════════════════════════════════════════════════════════

# Custos médios
CUSTO_RETENCAO_MEDIO = 200.00  # R$ custo médio de uma ação de retenção
CAC_MEDIO = 1000.00            # R$ custo de aquisição de cliente
MARGEM_OPERACIONAL = 0.30      # 30% de margem sobre mensalidade

# ═══════════════════════════════════════════════════════════════════════════
# AI INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════

AI_CONFIG = {
    "provider": "anthropic",  # ou "openai"
    "model_anthropic": "claude-3-5-sonnet-20241022",
    "model_openai": "gpt-4-turbo-preview",
    "max_tokens": 1000,
    "temperature": 0.3,
}

# Prompts para análise de protocolos
PROMPT_ANALISE_PROTOCOLO = """Analise esta transcrição de atendimento SAC de operadora de saúde:

"{transcricao}"

Retorne um JSON com:
1. sentimento: "positivo", "neutro" ou "negativo"
2. motivo_principal: categorize em uma destas: "Problemas com cobertura", "Preço elevado", "Negativas frequentes", "Atendimento ruim", "Rede credenciada limitada", "Demora autorização", "Insatisfação geral", "Outros"
3. urgencia: "baixa", "media" ou "alta"
4. menciona_cancelamento: true/false
5. menciona_ans_procon: true/false

JSON:"""

# ═══════════════════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════════════════

DB_PATH = "database/lifepulse.db"

# ═══════════════════════════════════════════════════════════════════════════
# DADOS SINTÉTICOS
# ═══════════════════════════════════════════════════════════════════════════

PLANOS = ["Basic", "Standard", "Premium", "VIP"]
PLANOS_PROB = [0.3, 0.35, 0.25, 0.1]

ESPECIALIDADES = [
    "Cardiologia", "Ortopedia", "Pediatria", "Ginecologia",
    "Oftalmologia", "Dermatologia", "Psiquiatria", "Neurologia"
]

MOTIVOS_PROTOCOLOS = [
    "Problemas com cobertura",
    "Preço elevado",
    "Negativas frequentes",
    "Atendimento ruim",
    "Rede credenciada limitada",
    "Demora autorização",
    "Insatisfação geral",
    "Outros"
]
