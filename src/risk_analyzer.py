"""
risk_analyzer.py — Analisador de Risco de Churn
LifePulse Pro

Calcula score de risco baseado em múltiplos fatores ponderados.
"""

import pandas as pd
from datetime import datetime
from src.config import RISK_WEIGHTS, RISK_THRESHOLDS

class RiskAnalyzer:
    """Analisa risco de churn de beneficiários."""
    
    def calculate_score(self, ben: pd.Series, protocolos: pd.DataFrame) -> float:
        """
        Calcula score de risco (0-100).
        
        Fatores:
        - Tempo como cliente (20%)
        - Quantidade de protocolos (25%)
        - Sentimento de protocolos (20%)
        - Sinistralidade (15%)
        - Inadimplência (20%)
        """
        score = 0
        
        # 1. Tempo como cliente (menos tempo = mais risco)
        if pd.notna(ben.get('data_adesao')):
            meses = (datetime.now() - pd.to_datetime(ben['data_adesao'])).days / 30
            if meses < 6:
                score += 100 * RISK_WEIGHTS['tempo_cliente']
            elif meses < 12:
                score += 70 * RISK_WEIGHTS['tempo_cliente']
            elif meses < 24:
                score += 40 * RISK_WEIGHTS['tempo_cliente']
            else:
                score += 20 * RISK_WEIGHTS['tempo_cliente']
        
        # 2. Protocolos (mais protocolos = mais risco)
        qtd_prot = len(protocolos)
        if qtd_prot == 0:
            score += 10 * RISK_WEIGHTS['protocolos']
        elif qtd_prot <= 2:
            score += 30 * RISK_WEIGHTS['protocolos']
        elif qtd_prot <= 5:
            score += 60 * RISK_WEIGHTS['protocolos']
        else:
            score += 90 * RISK_WEIGHTS['protocolos']
        
        # 3. Sentimento (protocolos negativos = mais risco)
        if not protocolos.empty and 'sentimento' in protocolos.columns:
            neg = (protocolos['sentimento'] == 'negativo').sum()
            perc_neg = neg / len(protocolos) if len(protocolos) > 0 else 0
            score += perc_neg * 100 * RISK_WEIGHTS['sentimento']
        
        # 4. Inadimplência
        if ben.get('inadimplente', False):
            score += 100 * RISK_WEIGHTS['inadimplencia']
        
        return min(100, max(0, score))
    
    def classify_risk_level(self, score: float) -> str:
        """Classifica em Baixo/Médio/Alto."""
        if score < RISK_THRESHOLDS['medio'][0]:
            return 'Baixo'
        elif score < RISK_THRESHOLDS['alto'][0]:
            return 'Médio'
        else:
            return 'Alto'
    
    def process_batch(self, df_ben: pd.DataFrame, df_prot: pd.DataFrame) -> pd.DataFrame:
        """Processa lote de beneficiários."""
        scores = []
        for _, ben in df_ben.iterrows():
            prot_ben = df_prot[df_prot['id_beneficiario'] == ben['id_beneficiario']]
            score = self.calculate_score(ben, prot_ben)
            scores.append({
                'id_beneficiario': ben['id_beneficiario'],
                'score_risco': round(score, 1),
                'nivel_risco': self.classify_risk_level(score)
            })
        return pd.DataFrame(scores)
