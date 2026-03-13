"""
retention_classifier.py — Classificador de Dificuldade de Retenção
LifePulse Pro

Classifica beneficiários em Fácil/Moderado/Difícil de reter.
"""

import pandas as pd
from src.config import DIFFICULTY_RULES

class RetentionClassifier:
    """Classifica dificuldade de retenção."""
    
    def classify(self, ben: pd.Series, protocolos: pd.DataFrame) -> str:
        """
        Classifica em: Fácil, Moderado ou Difícil.
        
        Critérios:
        - Fácil: <= 2 protocolos, cliente há 2+ anos, sem keywords negativas
        - Moderado: 3-5 protocolos, menciona preço/custos
        - Difícil: Menciona ANS/Procon/Cancelamento, 6+ protocolos
        """
        qtd_prot = len(protocolos)
        meses_cliente = self._calcular_meses_cliente(ben.get('data_adesao'))
        
        # Keywords em protocolos
        transcricoes = ' '.join(protocolos['transcricao'].fillna('').astype(str).tolist()).lower()
        
        # Difícil
        keywords_dificil = DIFFICULTY_RULES['dificil']['keywords_negativas']
        if any(kw in transcricoes for kw in keywords_dificil) or qtd_prot > 6:
            return 'Difícil'
        
        # Fácil
        if qtd_prot <= DIFFICULTY_RULES['facil']['max_protocolos'] and meses_cliente >= 24:
            return 'Fácil'
        
        # Moderado (default)
        return 'Moderado'
    
    def _calcular_meses_cliente(self, data_adesao) -> int:
        """Calcula meses como cliente."""
        if pd.isna(data_adesao):
            return 0
        from datetime import datetime
        return int((datetime.now() - pd.to_datetime(data_adesao)).days / 30)
