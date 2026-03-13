"""
ai_integration.py — Integração com IA (Anthropic/OpenAI)
LifePulse Pro

Análise de protocolos SAC usando LLMs.
"""

import os
import json
import logging
from typing import Optional, Dict
from src.config import AI_CONFIG, PROMPT_ANALISE_PROTOCOLO

log = logging.getLogger(__name__)

class AIIntegration:
    """Integra com APIs de IA para análise de protocolos."""
    
    def __init__(self):
        self.provider = os.getenv('AI_PROVIDER', AI_CONFIG['provider'])
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
    
    def analisar_protocolo(self, transcricao: str) -> Optional[Dict]:
        """
        Analisa transcrição de protocolo usando IA.
        
        Retorna:
        {
            'sentimento': 'positivo'|'neutro'|'negativo',
            'motivo_principal': str,
            'urgencia': 'baixa'|'media'|'alta',
            'menciona_cancelamento': bool,
            'menciona_ans_procon': bool
        }
        """
        if not self.anthropic_key and not self.openai_key:
            log.warning("Sem API keys configuradas. Usando análise simplificada.")
            return self._analisar_simples(transcricao)
        
        try:
            if self.provider == 'anthropic' and self.anthropic_key:
                return self._analisar_anthropic(transcricao)
            elif self.provider == 'openai' and self.openai_key:
                return self._analisar_openai(transcricao)
            else:
                return self._analisar_simples(transcricao)
        except Exception as e:
            log.error(f"Erro na IA: {e}")
            return self._analisar_simples(transcricao)
    
    def _analisar_anthropic(self, transcricao: str) -> Dict:
        """Análise usando Anthropic Claude."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_key)
            
            response = client.messages.create(
                model=AI_CONFIG['model_anthropic'],
                max_tokens=AI_CONFIG['max_tokens'],
                temperature=AI_CONFIG['temperature'],
                messages=[{
                    "role": "user",
                    "content": PROMPT_ANALISE_PROTOCOLO.format(transcricao=transcricao)
                }]
            )
            
            result = json.loads(response.content[0].text)
            return result
        except Exception as e:
            log.error(f"Erro Anthropic: {e}")
            return self._analisar_simples(transcricao)
    
    def _analisar_openai(self, transcricao: str) -> Dict:
        """Análise usando OpenAI."""
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_key)
            
            response = client.chat.completions.create(
                model=AI_CONFIG['model_openai'],
                messages=[{
                    "role": "user",
                    "content": PROMPT_ANALISE_PROTOCOLO.format(transcricao=transcricao)
                }],
                max_tokens=AI_CONFIG['max_tokens'],
                temperature=AI_CONFIG['temperature']
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            log.error(f"Erro OpenAI: {e}")
            return self._analisar_simples(transcricao)
    
    def _analisar_simples(self, transcricao: str) -> Dict:
        """Análise baseada em keywords (fallback)."""
        trans_lower = transcricao.lower()
        
        # Sentimento
        palavras_neg = ['problema', 'ruim', 'insatisfeito', 'cancelar', 'reclamação']
        palavras_pos = ['obrigado', 'satisfeito', 'ótimo', 'excelente']
        
        if any(p in trans_lower for p in palavras_neg):
            sentimento = 'negativo'
        elif any(p in trans_lower for p in palavras_pos):
            sentimento = 'positivo'
        else:
            sentimento = 'neutro'
        
        # Motivo
        motivos_map = {
            'cobertura': 'Problemas com cobertura',
            'preço': 'Preço elevado',
            'caro': 'Preço elevado',
            'negado': 'Negativas frequentes',
            'atendimento': 'Atendimento ruim',
            'rede': 'Rede credenciada limitada',
        }
        motivo = 'Outros'
        for keyword, mot in motivos_map.items():
            if keyword in trans_lower:
                motivo = mot
                break
        
        # Urgência
        urgencia = 'alta' if 'urgente' in trans_lower or 'cancelar' in trans_lower else 'media'
        
        return {
            'sentimento': sentimento,
            'motivo_principal': motivo,
            'urgencia': urgencia,
            'menciona_cancelamento': 'cancelar' in trans_lower or 'cancelamento' in trans_lower,
            'menciona_ans_procon': 'ans' in trans_lower or 'procon' in trans_lower
        }
