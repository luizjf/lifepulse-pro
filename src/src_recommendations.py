"""
recommendations.py — Recomendações Personalizadas por IA
LifePulse Pro - Funcionalidade Principal

Gera plano de ações personalizado para cada beneficiário.
"""

import os
import json
import logging
from typing import Dict, List

log = logging.getLogger(__name__)

# Ações de retenção com custos e % de sucesso
ACOES_RETENCAO = [
    {
        "id": 1,
        "acao": "Escalação imediata para gerente sênior",
        "custo": 200,
        "taxa_sucesso": 49,
        "aplicavel_para": ["menciona_ans_procon", "menciona_cancelamento", "urgencia_alta"]
    },
    {
        "id": 2,
        "acao": "Plano de ação emergencial documentado",
        "custo": 100,
        "taxa_sucesso": 40,
        "aplicavel_para": ["alto_risco", "dificuldade_dificil"]
    },
    {
        "id": 3,
        "acao": "Desconto agressivo 20-30% por 6 meses",
        "custo": 810,
        "taxa_sucesso": 90,
        "aplicavel_para": ["motivo_preco", "alto_valor"]
    },
    {
        "id": 4,
        "acao": "Plano personalizado sob medida",
        "custo": 300,
        "taxa_sucesso": 89,
        "aplicavel_para": ["alto_valor", "tempo_cliente_longo"]
    },
    {
        "id": 5,
        "acao": "Força-tarefa: resolver TODAS pendências em 24h",
        "custo": 400,
        "taxa_sucesso": 90,
        "aplicavel_para": ["muitos_protocolos", "menciona_cancelamento"]
    },
    {
        "id": 6,
        "acao": "Isenção de carências em procedimentos solicitados",
        "custo": 250,
        "taxa_sucesso": 48,
        "aplicavel_para": ["motivo_cobertura", "negativas_frequentes"]
    },
    {
        "id": 7,
        "acao": "Benefícios exclusivos (telemedicina, farmácia)",
        "custo": 180,
        "taxa_sucesso": 42,
        "aplicavel_para": ["medio_risco"]
    },
    {
        "id": 8,
        "acao": "Reunião presencial de emergência (visita ao cliente)",
        "custo": 350,
        "taxa_sucesso": 92,
        "aplicavel_para": ["alto_valor", "dificuldade_dificil"]
    }
]

class RecommendationEngine:
    """Motor de recomendações personalizado por IA."""
    
    def __init__(self):
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
    
    def gerar_recomendacoes(self, beneficiario: Dict, protocolos: List[Dict]) -> Dict:
        """
        Gera recomendações personalizadas usando IA.
        
        Retorna:
        {
            'score': 82,
            'perfil': {...},  # Dados para gráfico radar
            'alertas': [...],
            'plano_acoes': [...]  # Top 8 ações ordenadas por relevância
        }
        """
        # Classificar perfil
        perfil = self._classificar_perfil(beneficiario, protocolos)
        
        # Gerar alertas
        alertas = self._gerar_alertas(beneficiario, protocolos)
        
        # Selecionar ações (com ou sem IA)
        if self.anthropic_key or self.openai_key:
            plano_acoes = self._selecionar_acoes_ia(beneficiario, protocolos, perfil)
        else:
            plano_acoes = self._selecionar_acoes_regras(beneficiario, protocolos, perfil)
        
        return {
            'score': beneficiario.get('score_risco', 0),
            'perfil': perfil,
            'alertas': alertas,
            'plano_acoes': plano_acoes
        }
    
    def _classificar_perfil(self, ben: Dict, prots: List[Dict]) -> Dict:
        """Classifica perfil para gráfico radar (5 dimensões)."""
        
        # Reincidência (0-50)
        qtd_prot = len(prots)
        reincidencia = min(50, qtd_prot * 5)
        
        # ANS/Procon (0-50)
        mencoes_ans = sum(1 for p in prots if 'ans' in p.get('transcricao', '').lower() 
                         or 'procon' in p.get('transcricao', '').lower())
        ans_procon = min(50, mencoes_ans * 25)
        
        # Financeiro (0-50)
        inadimplente = ben.get('inadimplente', False)
        mencoes_preco = sum(1 for p in prots if 'preço' in p.get('transcricao', '').lower() 
                           or 'caro' in p.get('transcricao', '').lower())
        financeiro = (30 if inadimplente else 0) + min(20, mencoes_preco * 10)
        
        # Cobertura (0-50)
        mencoes_negativa = sum(1 for p in prots if 'negado' in p.get('transcricao', '').lower() 
                              or 'negativa' in p.get('transcricao', '').lower())
        cobertura = min(50, mencoes_negativa * 15)
        
        return {
            'Reincidência': reincidencia,
            'ANS/Procon': ans_procon,
            'Financeiro': financeiro,
            'Cobertura': cobertura
        }
    
    def _gerar_alertas(self, ben: Dict, prots: List[Dict]) -> List[str]:
        """Gera alertas baseado em padrões detectados."""
        alertas = []
        
        if ben.get('score_risco', 0) > 80:
            alertas.append("⚠️ RISCO CRÍTICO: Score acima de 80%")
        
        # Verificar menções
        transcricoes = ' '.join([p.get('transcricao', '') for p in prots]).lower()
        
        if 'ans' in transcricoes or 'procon' in transcricoes:
            alertas.append("🚨 Menção a órgãos regulatórios (ANS/Procon)")
        
        if 'cancelar' in transcricoes or 'cancelamento' in transcricoes:
            alertas.append("🔴 Intenção de cancelamento ou ação judicial")
        
        if len(prots) > 5:
            alertas.append("📞 Alta reincidência de protocolos")
        
        if 'negado' in transcricoes or 'negativa' in transcricoes:
            alertas.append("❌ Problemas com cobertura / negativas de guia")
        
        return alertas
    
    def _selecionar_acoes_regras(self, ben: Dict, prots: List[Dict], perfil: Dict) -> List[Dict]:
        """Seleciona ações usando regras de negócio."""
        score = ben.get('score_risco', 0)
        mensalidade = ben.get('mensalidade', 0)
        transcricoes = ' '.join([p.get('transcricao', '') for p in prots]).lower()
        
        # Tags do beneficiário
        tags = []
        if score > 70:
            tags.append('alto_risco')
        if mensalidade > 1000:
            tags.append('alto_valor')
        if 'ans' in transcricoes or 'procon' in transcricoes:
            tags.append('menciona_ans_procon')
        if 'cancelar' in transcricoes:
            tags.append('menciona_cancelamento')
        if 'preço' in transcricoes or 'caro' in transcricoes:
            tags.append('motivo_preco')
        if len(prots) > 5:
            tags.append('muitos_protocolos')
        if 'negado' in transcricoes or 'negativa' in transcricoes:
            tags.append('negativas_frequentes')
        
        # Pontuar ações
        acoes_pontuadas = []
        for acao in ACOES_RETENCAO:
            pontos = 0
            for tag_acao in acao['aplicavel_para']:
                if tag_acao in tags:
                    pontos += 1
            
            if pontos > 0:
                acoes_pontuadas.append({
                    **acao,
                    'relevancia': pontos
                })
        
        # Ordenar por relevância e taxa de sucesso
        acoes_pontuadas.sort(key=lambda x: (x['relevancia'], x['taxa_sucesso']), reverse=True)
        
        return acoes_pontuadas[:8]
    
    def _selecionar_acoes_ia(self, ben: Dict, prots: List[Dict], perfil: Dict) -> List[Dict]:
        """Seleciona ações usando IA (Anthropic/OpenAI)."""
        try:
            # Preparar contexto
            contexto = f"""
Beneficiário: {ben.get('nome')}
Score de Risco: {ben.get('score_risco')}%
Mensalidade: R$ {ben.get('mensalidade')}
Protocolos: {len(prots)}
Perfil: {perfil}

Últimos protocolos:
{chr(10).join([p.get('transcricao', '')[:200] for p in prots[:3]])}

Selecione as 8 ações mais adequadas da lista abaixo e ordene por prioridade:
{json.dumps(ACOES_RETENCAO, indent=2, ensure_ascii=False)}

Retorne APENAS um JSON array com os IDs ordenados: [1, 3, 5, ...]
"""
            
            if self.anthropic_key:
                return self._chamar_anthropic(contexto)
            elif self.openai_key:
                return self._chamar_openai(contexto)
            else:
                return self._selecionar_acoes_regras(ben, prots, perfil)
        
        except Exception as e:
            log.error(f"Erro na IA: {e}")
            return self._selecionar_acoes_regras(ben, prots, perfil)
    
    def _chamar_anthropic(self, contexto: str) -> List[Dict]:
        """Chama Anthropic Claude."""
        import anthropic
        client = anthropic.Anthropic(api_key=self.anthropic_key)
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": contexto}]
        )
        
        ids_ordenados = json.loads(response.content[0].text)
        return [acao for acao in ACOES_RETENCAO if acao['id'] in ids_ordenados]
    
    def _chamar_openai(self, contexto: str) -> List[Dict]:
        """Chama OpenAI GPT-4."""
        import openai
        client = openai.OpenAI(api_key=self.openai_key)
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": contexto}],
            max_tokens=500
        )
        
        ids_ordenados = json.loads(response.choices[0].message.content)
        return [acao for acao in ACOES_RETENCAO if acao['id'] in ids_ordenados]
