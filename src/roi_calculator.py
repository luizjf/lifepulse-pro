"""
roi_calculator.py — Calculadora de ROI de Retenção
LifePulse Pro

Calcula ROI projetado e real de ações de retenção.
"""

from src.config import CUSTO_RETENCAO_MEDIO, MARGEM_OPERACIONAL

class ROICalculator:
    """Calcula ROI de ações de retenção."""
    
    def calcular_roi_projetado(self, mensalidade: float, meses: int, custo: float = CUSTO_RETENCAO_MEDIO) -> float:
        """
        ROI Projetado = ((Receita Retida - Custo) / Custo) * 100
        
        Considera margem operacional de 30%.
        """
        receita_bruta = mensalidade * meses
        receita_liquida = receita_bruta * MARGEM_OPERACIONAL
        roi = ((receita_liquida - custo) / custo) * 100
        return round(roi, 1)
    
    def calcular_ltv(self, mensalidade: float, meses_esperados: int = 36) -> float:
        """Lifetime Value projetado."""
        return mensalidade * meses_esperados * MARGEM_OPERACIONAL
    
    def vale_reter(self, mensalidade: float, score_risco: float, sinistralidade: float = 1.0) -> bool:
        """
        Decide se vale a pena investir em retenção.
        
        Critérios:
        - Score > 50 (risco médio/alto)
        - LTV 12m > 3x custo de retenção
        - Sinistralidade < 1.5 (não dá muito prejuízo)
        """
        ltv_12m = self.calcular_ltv(mensalidade, 12)
        return (
            score_risco > 50 and
            ltv_12m > (CUSTO_RETENCAO_MEDIO * 3) and
            sinistralidade < 1.5
        )
