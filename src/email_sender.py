"""
email_sender.py — Envio de Relatórios por E-mail
LifePulse Pro

Envia relatórios de retenção por e-mail.
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
from typing import Optional, List
import pandas as pd

log = logging.getLogger(__name__)

class EmailSender:
    """Envia relatórios por e-mail."""
    
    def __init__(self):
        # Configurações do servidor SMTP
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_user)
    
    def enviar_relatorio_alto_risco(
        self,
        to_email: str,
        df_alto_risco: pd.DataFrame,
        stats: dict,
        nome_analista: str = "Sistema LifePulse Pro"
    ) -> bool:
        """
        Envia relatório de beneficiários de alto risco.
        
        Args:
            to_email: Email do destinatário
            df_alto_risco: DataFrame com beneficiários de alto risco
            stats: Dicionário com estatísticas gerais
            nome_analista: Nome do analista responsável
        
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            # Validar configuração
            if not self.smtp_user or not self.smtp_password:
                log.error("Credenciais SMTP não configuradas. Configure SMTP_USER e SMTP_PASSWORD no .env")
                return False
            
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"⚠️ LifePulse Pro - Relatório de Alto Risco ({datetime.now().strftime('%d/%m/%Y')})"
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Corpo do e-mail em HTML
            html_body = self._gerar_html_relatorio(df_alto_risco, stats, nome_analista)
            
            # Anexar corpo HTML
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Anexar CSV (opcional)
            if not df_alto_risco.empty:
                csv_data = df_alto_risco.to_csv(index=False).encode('utf-8')
                csv_part = MIMEApplication(csv_data, _subtype='csv')
                csv_part.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=f'alto_risco_{datetime.now().strftime("%Y%m%d")}.csv'
                )
                msg.attach(csv_part)
            
            # Enviar
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            log.info(f"✓ Relatório enviado para {to_email}")
            return True
        
        except Exception as e:
            log.error(f"Erro ao enviar e-mail: {e}")
            return False
    
    def _gerar_html_relatorio(
        self,
        df_alto_risco: pd.DataFrame,
        stats: dict,
        nome_analista: str
    ) -> str:
        """Gera HTML do relatório."""
        
        # Top 10 alto risco
        top10 = df_alto_risco.head(10) if not df_alto_risco.empty else pd.DataFrame()
        
        # Gerar linhas da tabela
        linhas_html = ""
        if not top10.empty:
            for _, row in top10.iterrows():
                cor_score = "#f56565" if row.get('score_risco', 0) > 80 else "#ed8936"
                linhas_html += f"""
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">{row.get('id_beneficiario', 'N/A')}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">{row.get('nome', 'N/A')}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: 700; color: {cor_score};">
                        {row.get('score_risco', 0):.1f}%
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">R$ {row.get('mensalidade', 0):,.2f}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">{row.get('dificuldade', 'N/A')}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">
                        {'✅ Sim' if row.get('vale_reter') else '❌ Não'}
                    </td>
                </tr>
                """
        else:
            linhas_html = """
            <tr>
                <td colspan="6" style="padding: 20px; text-align: center; color: #48bb78;">
                    ✅ Nenhum beneficiário de alto risco no momento!
                </td>
            </tr>
            """
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f7fafc;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 800;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .alert {{
            background: linear-gradient(135deg, #fc5c7d 0%, #6a82fb 100%);
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 18px;
            font-weight: 700;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            padding: 30px;
            background: #f7fafc;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: 800;
            color: #667eea;
            margin: 0;
        }}
        .stat-label {{
            font-size: 14px;
            color: #718096;
            text-transform: uppercase;
            margin: 5px 0 0 0;
        }}
        .content {{
            padding: 30px;
        }}
        .content h2 {{
            color: #1a202c;
            font-size: 22px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background: #f7fafc;
            padding: 12px;
            text-align: left;
            font-size: 12px;
            color: #718096;
            text-transform: uppercase;
            font-weight: 600;
            border-bottom: 2px solid #e2e8f0;
        }}
        .footer {{
            background: #1a202c;
            color: #a0aec0;
            padding: 20px;
            text-align: center;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>💙 LifePulse Pro</h1>
            <p>Sistema Preditivo de Retenção ANS</p>
        </div>
        
        <!-- Alert -->
        <div class="alert">
            ⚠️ ALERTA: R$ {stats.get('receita_risco_anual', 0):,.2f} em receita anual em risco — AJA AGORA!
        </div>
        
        <!-- Stats -->
        <div class="stats">
            <div class="stat">
                <p class="stat-value">{stats.get('total_beneficiarios', 0):,}</p>
                <p class="stat-label">Beneficiários</p>
            </div>
            <div class="stat">
                <p class="stat-value" style="color: #f56565;">{stats.get('alto_risco', 0):,}</p>
                <p class="stat-label">Alto Risco</p>
            </div>
            <div class="stat">
                <p class="stat-value" style="color: #ed8936;">R$ {stats.get('receita_risco_mensal', 0):,.2f}</p>
                <p class="stat-label">Receita em Risco (mês)</p>
            </div>
        </div>
        
        <!-- Content -->
        <div class="content">
            <h2>📊 Top 10 Beneficiários de Alto Risco</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nome</th>
                        <th>Score</th>
                        <th>Mensalidade</th>
                        <th>Dificuldade</th>
                        <th>Vale Reter?</th>
                    </tr>
                </thead>
                <tbody>
                    {linhas_html}
                </tbody>
            </table>
            
            <p style="margin-top: 30px; color: #718096; font-size: 14px;">
                <strong>Próximos Passos:</strong><br>
                1. Acesse o LifePulse Pro para ver recomendações detalhadas<br>
                2. Priorize beneficiários com maior score e que valem reter<br>
                3. Execute ações de retenção e registre no sistema<br>
                4. Acompanhe ROI em tempo real
            </p>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p><strong>LifePulse Pro</strong> — O pulso vital da sua operadora em tempo real</p>
            <p style="margin-top: 10px; font-size: 12px;">
                Relatório gerado por: {nome_analista} | {datetime.now().strftime('%d/%m/%Y às %H:%M')}
            </p>
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    def testar_configuracao(self) -> tuple[bool, str]:
        """
        Testa se as configurações de e-mail estão corretas.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            if not self.smtp_user or not self.smtp_password:
                return False, "❌ Credenciais SMTP não configuradas. Configure SMTP_USER e SMTP_PASSWORD no arquivo .env"
            
            # Testar conexão
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
            
            return True, f"✅ Configuração OK! Pronto para enviar de: {self.from_email}"
        
        except Exception as e:
            return False, f"❌ Erro na configuração: {str(e)}"
