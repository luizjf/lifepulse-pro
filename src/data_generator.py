"""
data_generator.py — Gerador de Dados Sintéticos Realistas
LifePulse Pro

Gera dados de teste para demonstração do sistema.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from src.config import PLANOS, PLANOS_PROB, MOTIVOS_PROTOCOLOS

class DataGenerator:
    """Gera dados sintéticos realistas."""
    
    def __init__(self, seed=42):
        random.seed(seed)
        np.random.seed(seed)
    
    def generate_beneficiarios(self, n=500) -> pd.DataFrame:
        """Gera beneficiários sintéticos."""
        hoje = datetime.now()
        
        data = []
        for i in range(1, n+1):
            data_nasc = hoje - timedelta(days=random.randint(18*365, 80*365))
            data_adesao = hoje - timedelta(days=random.randint(30, 2000))
            
            data.append({
                'id_beneficiario': f'BEN{i:06d}',
                'nome': f'Beneficiário {i}',
                'data_nascimento': data_nasc.strftime('%Y-%m-%d'),
                'sexo': random.choice(['M', 'F']),
                'codigo_plano': random.choices(PLANOS, PLANOS_PROB)[0],
                'mensalidade': round(random.uniform(300, 2500), 2),
                'data_adesao': data_adesao.strftime('%Y-%m-%d'),
                'situacao': 'ATIVO',
                'telefone': f'(11) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}',
                'email': f'beneficiario{i}@email.com',
                'cidade': random.choice(['São Paulo', 'Rio de Janeiro', 'Belo Horizonte']),
                'uf': random.choice(['SP', 'RJ', 'MG']),
                'qtd_dependentes': random.randint(0, 4),
                'forma_pagamento': random.choice(['Boleto', 'Débito Automático', 'Cartão']),
                'inadimplente': random.random() < 0.05,  # 5% inadimplentes
            })
        
        return pd.DataFrame(data)
    
    def generate_protocolos(self, df_ben: pd.DataFrame) -> pd.DataFrame:
        """Gera protocolos SAC para ~30% dos beneficiários."""
        data = []
        bens_com_prot = random.sample(list(df_ben['id_beneficiario']), int(len(df_ben) * 0.3))
        
        for id_ben in bens_com_prot:
            n_prot = random.randint(1, 8)
            for j in range(n_prot):
                data_aber = datetime.now() - timedelta(days=random.randint(0, 365))
                
                data.append({
                    'numero_protocolo': f'PROT-{len(data)+1:07d}',
                    'id_beneficiario': id_ben,
                    'data_abertura': data_aber.strftime('%Y-%m-%d %H:%M:%S'),
                    'canal': random.choice(['Telefone', 'Email', 'Chat', 'App']),
                    'categoria': random.choice(['Cobertura', 'Financeiro', 'Rede', 'Autorização']),
                    'transcricao': f'Protocolo de teste sobre {random.choice(MOTIVOS_PROTOCOLOS).lower()}',
                    'status': random.choice(['RESOLVIDO']*7 + ['EM_ANALISE']*2 + ['ABERTO']),
                    'sentimento': random.choice(['positivo']*3 + ['neutro']*4 + ['negativo']*3),
                    'urgencia': random.choice(['baixa']*5 + ['media']*3 + ['alta']*2),
                    'menciona_cancelamento': random.random() < 0.1,
                })
        
        return pd.DataFrame(data)
