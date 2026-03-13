"""
database.py — Database Manager Thread-Safe
LifePulse Pro - Sistema Preditivo de Retenção ANS

Gerencia todas as operações do banco SQLite.
"""

import sqlite3
import pandas as pd
from pathlib import Path
import logging
from typing import Optional

log = logging.getLogger(__name__)

class DatabaseManager:
    """Gerenciador de banco de dados SQLite thread-safe."""
    
    def __init__(self, db_path: str = "database/lifepulse.db"):
        """Inicializa conexão com banco."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._create_tables()
        log.info(f"✓ Database conectado: {self.db_path}")
    
    def _create_tables(self):
        """Cria tabelas se não existirem."""
        cursor = self.conn.cursor()
        
        # Beneficiários
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS beneficiarios (
            id_beneficiario TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            data_nascimento DATE,
            sexo TEXT,
            codigo_plano TEXT,
            mensalidade REAL NOT NULL,
            data_adesao DATE,
            situacao TEXT DEFAULT 'ATIVO',
            telefone TEXT,
            email TEXT,
            cidade TEXT,
            uf TEXT,
            qtd_dependentes INTEGER DEFAULT 0,
            forma_pagamento TEXT,
            inadimplente BOOLEAN DEFAULT 0,
            score_risco REAL,
            nivel_risco TEXT,
            dificuldade_retencao TEXT,
            motivo_principal TEXT,
            vale_reter BOOLEAN,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Protocolos SAC
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS protocolos_sac (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_protocolo TEXT UNIQUE,
            id_beneficiario TEXT,
            data_abertura DATETIME,
            canal TEXT,
            categoria TEXT,
            transcricao TEXT,
            status TEXT DEFAULT 'ABERTO',
            sentimento TEXT,
            urgencia TEXT,
            menciona_cancelamento BOOLEAN,
            FOREIGN KEY (id_beneficiario) REFERENCES beneficiarios(id_beneficiario)
        )""")
        
        # Ações de Retenção
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS acoes_retencao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_beneficiario TEXT,
            data_acao DATETIME,
            tipo_acao TEXT,
            analista_responsavel TEXT,
            custo_estimado REAL,
            custo_real REAL,
            resultado TEXT DEFAULT 'EM_ABERTO',
            roi_3m REAL,
            roi_6m REAL,
            roi_12m REAL,
            observacoes TEXT,
            FOREIGN KEY (id_beneficiario) REFERENCES beneficiarios(id_beneficiario)
        )""")
        
        self.conn.commit()
    
    def import_beneficiarios(self, df: pd.DataFrame) -> int:
        """Importa beneficiários. Retorna quantidade importada."""
        try:
            df.to_sql('beneficiarios', self.conn, if_exists='append', index=False)
            self.conn.commit()
            log.info(f"✓ {len(df)} beneficiários importados")
            return len(df)
        except Exception as e:
            log.error(f"Erro ao importar: {e}")
            self.conn.rollback()
            raise
    
    def import_protocolos(self, df: pd.DataFrame) -> int:
        """Importa protocolos SAC."""
        try:
            df.to_sql('protocolos_sac', self.conn, if_exists='append', index=False)
            self.conn.commit()
            return len(df)
        except Exception as e:
            self.conn.rollback()
            raise
    
    def get_beneficiarios_ativos(self) -> pd.DataFrame:
        """Retorna todos beneficiários ativos."""
        try:
            return pd.read_sql(
                "SELECT * FROM beneficiarios WHERE situacao = 'ATIVO' ORDER BY score_risco DESC",
                self.conn
            )
        except:
            return pd.DataFrame()
    
    def get_protocolos(self, id_beneficiario: str) -> pd.DataFrame:
        """Retorna protocolos de um beneficiário."""
        try:
            return pd.read_sql(
                f"SELECT * FROM protocolos_sac WHERE id_beneficiario = '{id_beneficiario}' ORDER BY data_abertura DESC",
                self.conn
            )
        except:
            return pd.DataFrame()
    
    def update_scores(self, df_updates: pd.DataFrame):
        """Atualiza scores calculados."""
        cursor = self.conn.cursor()
        for _, row in df_updates.iterrows():
            cursor.execute("""
                UPDATE beneficiarios 
                SET score_risco = ?, nivel_risco = ?, dificuldade_retencao = ?, 
                    motivo_principal = ?, vale_reter = ?
                WHERE id_beneficiario = ?
            """, (
                row.get('score_risco'),
                row.get('nivel_risco'),
                row.get('dificuldade_retencao'),
                row.get('motivo_principal'),
                row.get('vale_reter'),
                row['id_beneficiario']
            ))
        self.conn.commit()
    
    def registrar_acao(self, id_ben: str, tipo: str, analista: str, custo: float, obs: str = "") -> int:
        """Registra nova ação de retenção."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO acoes_retencao 
            (id_beneficiario, data_acao, tipo_acao, analista_responsavel, custo_real, observacoes)
            VALUES (?, datetime('now'), ?, ?, ?, ?)
        """, (id_ben, tipo, analista, custo, obs))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_stats(self) -> dict:
        """Retorna estatísticas gerais."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM beneficiarios WHERE situacao = 'ATIVO'")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM beneficiarios WHERE nivel_risco = 'Alto'")
            alto_risco = cursor.fetchone()[0]
            cursor.execute("SELECT SUM(mensalidade) FROM beneficiarios WHERE nivel_risco = 'Alto'")
            receita_risco = cursor.fetchone()[0] or 0
            
            return {
                'total_beneficiarios': total,
                'alto_risco': alto_risco,
                'receita_risco_mensal': receita_risco,
                'receita_risco_anual': receita_risco * 12,
            }
        except:
            return {'total_beneficiarios': 0, 'alto_risco': 0, 'receita_risco_mensal': 0, 'receita_risco_anual': 0}
