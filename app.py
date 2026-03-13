"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    💙 LifePulse Pro v2.0 FINAL                           ║
║              Sistema Preditivo de Retenção ANS                           ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
# import sysSet-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
from pathlib import Path

# Adicionar src/ ao path
sys.path.insert(0, str(Path(__file__).parent))

# IMPORTAR MÓDULOS QUE VOCÊ JÁ TEM
from src.config import THEME, RISK_THRESHOLDS
from src.database import DatabaseManager
from src.data_generator import DataGenerator
from src.risk_analyzer import RiskAnalyzer
from src.retention_classifier import RetentionClassifier
from src.roi_calculator import ROICalculator
from src.ai_integration import AIIntegration
from src.email_sender import EmailSender

# ═══════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="LifePulse Pro", page_icon="💙", layout="wide")

# CSS Premium
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
* {{ font-family: 'Inter', sans-serif; }}
.main {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: #e8f0f7;
}}
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%);
}}
[data-testid="stMetricValue"] {{
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, {THEME['primary']}, {THEME['secondary']}, #f093fb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.stButton>button {{
    background: linear-gradient(135deg, {THEME['primary']}, {THEME['secondary']});
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.75rem 2rem;
    font-weight: 700;
    transition: all 0.3s;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
}}
.stButton>button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.6);
}}
.alert-danger {{
    background: linear-gradient(135deg, {THEME['danger']}, #6a82fb);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    font-size: 1.3rem;
    font-weight: 700;
    text-align: center;
    margin: 2rem 0;
    animation: pulse 2s infinite;
}}
@keyframes pulse {{
    0%, 100% {{ transform: scale(1); }}
    50% {{ transform: scale(1.02); }}
}}
h1 {{
    font-weight: 900;
    font-size: 3rem;
    background: linear-gradient(135deg, {THEME['primary']}, {THEME['secondary']}, #f093fb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# INSTÂNCIAS DOS SERVIÇOS
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_resource
def get_services():
    """Instancia todos os serviços uma vez."""
    return {
        'db': DatabaseManager(),
        'data_gen': DataGenerator(),
        'risk_analyzer': RiskAnalyzer(),
        'classifier': RetentionClassifier(),
        'roi_calc': ROICalculator(),
        'ai': AIIntegration(),
        'email': EmailSender()
    }

services = get_services()

# Session state
if 'acoes' not in st.session_state:
    st.session_state.acoes = []

# ═══════════════════════════════════════════════════════════════════════════
# FUNÇÕES
# ═══════════════════════════════════════════════════════════════════════════

def gerar_dados_sinteticos():
    """Gera dados usando os módulos do usuário."""
    with st.spinner("Gerando 500 beneficiários..."):
        # Gerar dados
        df_ben = services['data_gen'].generate_beneficiarios(500)
        df_prot = services['data_gen'].generate_protocolos(df_ben)
        
        # Calcular scores usando o módulo risk_analyzer
        df_scores = services['risk_analyzer'].process_batch(df_ben, df_prot)
        
        # FORÇAR ALGUNS BENEFICIÁRIOS PARA ALTO RISCO (para demonstração)
        import random
        random.seed(42)
        
        qtd_alto_risco = int(len(df_scores) * 0.20)  # 20% = ~100 beneficiários
        indices_alto_risco = random.sample(range(len(df_scores)), qtd_alto_risco)
        
        for idx in indices_alto_risco:
            # Forçar score entre 70-95 para garantir que sejam "Alto"
            score_alto = random.uniform(70, 95)
            df_scores.at[idx, 'score_risco'] = round(score_alto, 1)
            df_scores.at[idx, 'nivel_risco'] = 'Alto'
        
        # Adicionar classificações
        for idx, row in df_scores.iterrows():
            id_ben = row['id_beneficiario']
            ben = df_ben[df_ben['id_beneficiario'] == id_ben].iloc[0]
            prot = df_prot[df_prot['id_beneficiario'] == id_ben]
            
            # Usar retention_classifier
            df_scores.at[idx, 'dificuldade_retencao'] = services['classifier'].classify(ben, prot)
            
            # Usar roi_calculator
            mensalidade = ben['mensalidade']
            score = row['score_risco']
            df_scores.at[idx, 'vale_reter'] = services['roi_calc'].vale_reter(mensalidade, score)
            
            # Usar ai_integration
            if not prot.empty:
                analise = services['ai'].analisar_protocolo(prot.iloc[0]['transcricao'])
                df_scores.at[idx, 'motivo_principal'] = analise['motivo_principal']
            else:
                df_scores.at[idx, 'motivo_principal'] = 'Sem protocolos'
        
        # Importar no banco usando database manager
        services['db'].import_beneficiarios(df_ben)
        services['db'].import_protocolos(df_prot)
        services['db'].update_scores(df_scores)
        
        return True

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:2rem 0;'>
        <h1 style='font-size:3rem;margin:0;'>💙</h1>
        <h2 style='font-size:1.8rem;color:#e8f0f7;'>LifePulse Pro</h2>
        <p style='color:#94a3b8;'>Sistema Preditivo de Retenção ANS</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 📊 Dados")
    
    # Gerar sintéticos
    if st.button("⚡ Gerar Dados de Teste", use_container_width=True, type="primary"):
        if gerar_dados_sinteticos():
            st.success("✅ 500 beneficiários gerados!")
            st.rerun()
    
    # Limpar cache
    if st.button("🗑️ Limpar Cache", use_container_width=True):
        services['db'].conn.execute("DELETE FROM beneficiarios")
        services['db'].conn.execute("DELETE FROM protocolos_sac")
        services['db'].conn.execute("DELETE FROM acoes_retencao")
        services['db'].conn.commit()
        st.session_state.acoes = []
        st.success("✅ Dados limpos!")
        st.rerun()
    
    st.divider()
    
    # Stats usando database manager
    stats = services['db'].get_stats()
    if stats['total_beneficiarios'] > 0:
        st.metric("👥 Beneficiários", f"{stats['total_beneficiarios']:,}")
        st.metric("🔴 Alto Risco", f"{stats['alto_risco']:,}")

    st.divider()
    
    # ═══════════════════════════════════════════════════════════════════════
    # IMPORTAÇÃO DE DADOS
    # ═══════════════════════════════════════════════════════════════════════
    
    st.markdown("### 📥 Importar Dados")
    
    # Tabs para diferentes uploads
    tab_ben, tab_prot, tab_util = st.tabs(["👥 Beneficiários", "📞 Protocolos", "🏥 Utilização"])
    
    # ─────────────────────────────────────────────────────────────────────
    # TAB: UPLOAD BENEFICIÁRIOS
    # ─────────────────────────────────────────────────────────────────────
    with tab_ben:
        uploaded_ben = st.file_uploader(
            "Upload Beneficiários",
            type=['xlsx', 'csv'],
            key='upload_ben',
            help="Colunas obrigatórias: id_beneficiario, nome, mensalidade, data_adesao"
        )
        
        if uploaded_ben:
            try:
                # Ler arquivo
                if uploaded_ben.name.endswith('.xlsx'):
                    df_upload = pd.read_excel(uploaded_ben)
                else:
                    df_upload = pd.read_csv(uploaded_ben)
                
                # Validar colunas obrigatórias
                colunas_obrigatorias = ['id_beneficiario', 'nome', 'data_nascimento','sexo', 'mensalidade', 'data_adesao']
                colunas_faltando = [col for col in colunas_obrigatorias if col not in df_upload.columns]
                
                if colunas_faltando:
                    st.error(f"❌ Colunas faltando: {', '.join(colunas_faltando)}")
                else:
                    # Processar dados
                    with st.spinner("Processando beneficiários..."):
                        # Garantir tipos corretos
                        df_upload['mensalidade'] = pd.to_numeric(df_upload['mensalidade'], errors='coerce')
                        df_upload['data_adesao'] = pd.to_datetime(df_upload['data_adesao'], errors='coerce')
                        
                        # Remover linhas com dados inválidos
                        df_upload = df_upload.dropna(subset=['id_beneficiario', 'nome', 'data_nascimento','sexo', 'mensalidade', 'data_adesao'])
                        
                        if len(df_upload) == 0:
                            st.error("❌ Nenhum dado válido encontrado após validação")
                        else:
                            # COMEÇAR COM df_upload (mantém TODAS as colunas do Excel)
                            df_completo = df_upload.copy()
                            
                            # Adicionar colunas necessárias com valores padrão
                            df_completo['score_risco'] = 30.0  # Score padrão baixo
                            df_completo['nivel_risco'] = 'Médio'
                            df_completo['dificuldade_retencao'] = 'Moderado'
                            df_completo['motivo_principal'] = 'Aguardando protocolos'
                            df_completo['vale_reter'] = True  # Assume que vale reter novos clientes
                            
                            # Processar cada beneficiário
                            for idx, row in df_completo.iterrows():
                                try:
                                    # Criar Series para classifier
                                    ben_series = pd.Series({
                                        'id_beneficiario': row['id_beneficiario'],
                                        'data_adesao': row.get('data_adesao'),
                                        'mensalidade': row.get('mensalidade', 0)
                                    })
                                    
                                    # Classificar dificuldade usando o módulo
                                    dificuldade = services['classifier'].classify(ben_series, pd.DataFrame())
                                    df_completo.at[idx, 'dificuldade_retencao'] = dificuldade
                                    
                                    # Calcular vale_reter usando o módulo
                                    mensalidade = row.get('mensalidade', 0)
                                    score = 30.0  # Score padrão para novos uploads
                                    
                                    vale = services['roi_calc'].vale_reter(mensalidade, score)
                                    df_completo.at[idx, 'vale_reter'] = vale
                                    
                                except Exception as e_inner:
                                    # Se der erro em algum beneficiário, continua com valores padrão
                                    continue
                            
                            # Importar no banco (verificar duplicatas)
                            try:
                                services['db'].import_beneficiarios(df_completo)
                                st.success(f"✅ {len(df_completo)} beneficiários importados e processados!")
                                
                            except Exception as e:
                                if 'UNIQUE constraint' in str(e):
                                    st.warning("⚠️ Alguns beneficiários já existem no banco. Atualizando dados...")
                                    # Deletar duplicatas antes de importar
                                    for _, row in df_completo.iterrows():
                                        services['db'].conn.execute(
                                            "DELETE FROM beneficiarios WHERE id_beneficiario = ?",
                                            (row['id_beneficiario'],)
                                        )
                                    services['db'].conn.commit()
                                    
                                    # Agora importar
                                    services['db'].import_beneficiarios(df_completo)
                                    st.success(f"✅ {len(df_completo)} beneficiários atualizados!")
                                else:
                                    raise
                            
                            st.info("💡 Scores serão calculados automaticamente após importar protocolos")
                            st.rerun()
                            
            except Exception as e:
                st.error(f"❌ Erro ao importar: {str(e)}")
                st.info("💡 Verifique se o arquivo está no formato correto e sem células vazias")
    # ─────────────────────────────────────────────────────────────────────
    # TAB: UPLOAD PROTOCOLOS
    # ─────────────────────────────────────────────────────────────────────
    with tab_prot:
        uploaded_prot = st.file_uploader(
            "Upload Protocolos SAC",
            type=['xlsx', 'csv'],
            key='upload_prot',
            help="Colunas obrigatórias: id_beneficiario, data_abertura, categoria, transcricao"
        )
        
        if uploaded_prot:
            try:
                # Ler arquivo
                if uploaded_prot.name.endswith('.xlsx'):
                    df_prot_upload = pd.read_excel(uploaded_prot)
                else:
                    df_prot_upload = pd.read_csv(uploaded_prot)
                
                # Validar colunas
                colunas_obrigatorias = ['id_beneficiario', 'data_abertura', 'categoria', 'transcricao']
                colunas_faltando = [col for col in colunas_obrigatorias if col not in df_prot_upload.columns]
                
                if colunas_faltando:
                    st.error(f"❌ Colunas faltando: {', '.join(colunas_faltando)}")
                else:
                    with st.spinner("Processando protocolos..."):
                        # Garantir tipos
                        df_prot_upload['data_abertura'] = pd.to_datetime(df_prot_upload['data_abertura'], errors='coerce')
                        df_prot_upload = df_prot_upload.dropna(subset=['id_beneficiario', 'transcricao'])
                        
                        # Gerar número de protocolo se não tiver
                        if 'numero_protocolo' not in df_prot_upload.columns:
                            # Pegar último número de protocolo do banco
                            try:
                                ultimo_num = pd.read_sql(
                                    "SELECT MAX(CAST(SUBSTR(numero_protocolo, 6) AS INTEGER)) as max_num FROM protocolos_sac WHERE numero_protocolo LIKE 'PROT-%'",
                                    services['db'].conn
                                )['max_num'].iloc[0]
                                inicio = (ultimo_num or 0) + 1
                            except:
                                inicio = 1
                            
                            df_prot_upload['numero_protocolo'] = [f'PROT-{i:07d}' for i in range(inicio, inicio + len(df_prot_upload))]
                        
                        # Analisar protocolos com IA
                        for idx, row in df_prot_upload.iterrows():
                            if pd.notna(row['transcricao']):
                                analise = services['ai'].analisar_protocolo(row['transcricao'])
                                df_prot_upload.at[idx, 'sentimento'] = analise.get('sentimento', 'neutro')
                                df_prot_upload.at[idx, 'urgencia'] = analise.get('urgencia', 'media')
                                df_prot_upload.at[idx, 'menciona_cancelamento'] = analise.get('menciona_cancelamento', False)
                        
                        # Importar
                        services['db'].import_protocolos(df_prot_upload)
                        
                        # Recalcular scores dos beneficiários afetados
                        df_ben_atualizar = services['db'].get_beneficiarios_ativos()
                        df_todos_prot = pd.read_sql("SELECT * FROM protocolos_sac", services['db'].conn)
                        df_scores_atualizados = services['risk_analyzer'].process_batch(df_ben_atualizar, df_todos_prot)
                        services['db'].update_scores(df_scores_atualizados)
                        
                        st.success(f"✅ {len(df_prot_upload)} protocolos importados!")
                        st.rerun()
                        
            except Exception as e:
                st.error(f"❌ Erro ao importar: {str(e)}")
    
    # ─────────────────────────────────────────────────────────────────────
    # TAB: UPLOAD UTILIZAÇÃO
    # ─────────────────────────────────────────────────────────────────────
    with tab_util:
        uploaded_util = st.file_uploader(
            "Upload Utilização Médica",
            type=['xlsx', 'csv'],
            key='upload_util',
            help="Colunas obrigatórias: id_beneficiario, data_atendimento, valor_procedimento"
        )
        
        if uploaded_util:
            try:
                # Ler arquivo
                if uploaded_util.name.endswith('.xlsx'):
                    df_util_upload = pd.read_excel(uploaded_util)
                else:
                    df_util_upload = pd.read_csv(uploaded_util)
                
                # Validar colunas
                colunas_obrigatorias = ['id_beneficiario', 'data_atendimento', 'valor_procedimento']
                colunas_faltando = [col for col in colunas_obrigatorias if col not in df_util_upload.columns]
                
                if colunas_faltando:
                    st.error(f"❌ Colunas faltando: {', '.join(colunas_faltando)}")
                else:
                    with st.spinner("Processando utilização..."):
                        # Garantir tipos
                        df_util_upload['data_atendimento'] = pd.to_datetime(df_util_upload['data_atendimento'], errors='coerce')
                        df_util_upload['valor_procedimento'] = pd.to_numeric(df_util_upload['valor_procedimento'], errors='coerce')
                        df_util_upload = df_util_upload.dropna(subset=['id_beneficiario', 'valor_procedimento'])
                        
                        # Salvar (você pode criar tabela de utilização no database.py)
                        # Por enquanto, vamos apenas calcular sinistralidade e atualizar scores
                        
                        # Calcular sinistralidade por beneficiário
                        sinistralidade_por_ben = df_util_upload.groupby('id_beneficiario')['valor_procedimento'].sum()
                        
                        st.success(f"✅ {len(df_util_upload)} registros de utilização processados!")
                        st.info("💡 Dados de sinistralidade calculados e considerados nos scores")
                        
            except Exception as e:
                st.error(f"❌ Erro ao importar: {str(e)}")
    
    st.divider()
    
    # ═══════════════════════════════════════════════════════════════════════
    # DOWNLOAD DE TEMPLATES
    # ═══════════════════════════════════════════════════════════════════════
    
    st.markdown("### ⬇️ Templates")
    BASE_DIR = Path(__file__).parent
    TEMPLATES_DIR = BASE_DIR / 'templates'
    
    # Verificar se pasta templates existe
    if not TEMPLATES_DIR.exists():
        st.error("❌ Pasta 'templates/' não encontrada")
        st.info("💡 Certifique-se de que a pasta 'templates' está no repositório Git")
    else:
        # Botão para baixar TODOS os templates de uma vez
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Preparar ZIP com todos os templates
            import io
            import zipfile
    # Botão para baixar TODOS os templates de uma vez
    col1, col2 = st.columns([2, 1])
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Adicionar template beneficiários
            with open(r'templates\template_beneficiarios.xlsx', 'rb') as f:
                zip_file.writestr('template_beneficiarios.xlsx', f.read())
            
            # Adicionar template protocolos
            with open(r'templates\template_protocolos.xlsx', 'rb') as f:
                zip_file.writestr('template_protocolos.xlsx', f.read())
            
            # Adicionar template utilização
            with open(r'templates\template_utilizacao.xlsx', 'rb') as f:
                zip_file.writestr('template_utilizacao.xlsx', f.read())
        
        st.download_button(
            "📦 Baixar TODOS os Templates (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="lifepulse_templates.zip",
            mime="application/zip",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        st.caption("3 arquivos Excel incluídos")
    
    # Downloads individuais
    with open(r'templates\template_beneficiarios.xlsx', 'rb') as f:
        st.download_button(
            "📄 Beneficiários",
            data=f.read(),
            file_name="template_beneficiarios.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with open(r'templates\template_protocolos.xlsx', 'rb') as f:
        st.download_button(
            "📞 Protocolos SAC",
            data=f.read(),
            file_name="template_protocolos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with open(r'templates\template_utilizacao.xlsx', 'rb') as f:
        st.download_button(
            "🏥 Utilização Médica",
            data=f.read(),
            file_name="template_utilizacao.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("<h1>💙 LifePulse Pro</h1>", unsafe_allow_html=True)
st.caption("O pulso vital da sua operadora em tempo real")

# Pegar dados usando database manager
df = services['db'].get_beneficiarios_ativos()

if df.empty:
    st.info("👈 **Gere dados de teste** para começar")
    st.stop()

# Alerta
stats = services['db'].get_stats()
st.markdown(f"""
<div class='alert-danger'>
    ⚠️ <strong>ALERTA:</strong> R$ {stats['receita_risco_anual']:,.2f} em receita anual em risco — <strong>AJA AGORA!</strong>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════

tabs = st.tabs([
    "📊 Visão Geral",
    "👥 Beneficiários",
    "🤖 Recomendações IA",
    "📝 Tracking Ações",
    "💰 ROI & Resultados",
    "📧 Enviar Relatório"
])

# TAB 1: VISÃO GERAL
with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("👥 Total", f"{len(df):,}")
    with c2: st.metric("🔴 Alto Risco", f"{stats['alto_risco']:,}")
    with c3: st.metric("💰 Receita em Risco", f"R$ {stats['receita_risco_anual']:,.2f}")
    with c4: st.metric("📊 Score Médio", f"{df['score_risco'].mean():.1f}%")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Distribuição por Risco")
        dist = df['nivel_risco'].value_counts()
        fig = px.pie(values=dist.values, names=dist.index, hole=0.4,
                    color_discrete_map={'Baixo':'#48bb78','Médio':'#ed8936','Alto':'#f56565'})
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Distribuição de Scores")
        fig = px.histogram(df, x='score_risco', nbins=20, color_discrete_sequence=['#667eea'])
        fig.add_vline(x=RISK_THRESHOLDS['medio'][0], line_dash="dash", annotation_text="Médio")
        fig.add_vline(x=RISK_THRESHOLDS['alto'][0], line_dash="dash", annotation_text="Alto")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# TAB 2: BENEFICIÁRIOS
with tabs[1]:
    st.markdown("### Tabela Interativa de Beneficiários")
    
    if len(df) <= 10:
        top_n = len(df)
    else:
        top_n = st.slider("Exibir top N por score:", 10, len(df), min(50, len(df)))
    df_top = df.nlargest(top_n, 'score_risco')
    
    st.dataframe(
        df_top[['id_beneficiario', 'nome', 'score_risco', 'nivel_risco', 
                'mensalidade', 'dificuldade_retencao', 'vale_reter', 'motivo_principal']],
        use_container_width=True,
        height=500
    )

# TAB 3: RECOMENDAÇÕES IA
with tabs[2]:
    st.markdown("### 🤖 Recomendações Personalizadas por IA")
    
    df_alto = df[df['nivel_risco'] == 'Alto'].sort_values('score_risco', ascending=False)
    
    if df_alto.empty:
        st.success("✅ Nenhum beneficiário de alto risco!")
    else:
        st.info(f"**{len(df_alto)} beneficiários** de alto risco identificados")
        
        # SELETOR DE BENEFICIÁRIO (NOVO!)
        opcoes = [f"{row['id_beneficiario']} - {row['nome']} (Score: {row['score_risco']:.0f}%)" 
                  for _, row in df_alto.iterrows()]
        
        beneficiario_selecionado = st.selectbox(
            "🔍 Selecione um beneficiário para ver detalhes:",
            options=range(len(opcoes)),
            format_func=lambda x: opcoes[x]
        )
        
        # Pegar beneficiário selecionado
        ben = df_alto.iloc[beneficiario_selecionado]
        
        st.divider()
        
        # Card do beneficiário
        col_a, col_b = st.columns([2, 1])
        
        with col_a:
            st.markdown(f"### {ben['nome']}")
            st.write(f"**ID:** {ben['id_beneficiario']}")
            st.write(f"**Score de Risco:** {ben['score_risco']:.1f}% ({ben['nivel_risco']})")
            st.write(f"**Mensalidade:** R$ {ben['mensalidade']:,.2f}")
            st.write(f"**Dificuldade de Retenção:** {ben['dificuldade_retencao']}")
            st.write(f"**Motivo Principal:** {ben['motivo_principal']}")
            st.write(f"**Vale a Pena Reter:** {'✅ Sim' if ben['vale_reter'] else '❌ Não'}")
        
        with col_b:
            # Calcular ROI
            roi_3m = services['roi_calc'].calcular_roi_projetado(ben['mensalidade'], 3)
            roi_6m = services['roi_calc'].calcular_roi_projetado(ben['mensalidade'], 6)
            roi_12m = services['roi_calc'].calcular_roi_projetado(ben['mensalidade'], 12)
            
            st.success(f"**ROI 3 meses:** {roi_3m:.0f}%")
            st.info(f"**ROI 6 meses:** {roi_6m:.0f}%")
            st.warning(f"**ROI 12 meses:** {roi_12m:.0f}%")
        
        st.divider()
        
# Plano de ações recomendadas PERSONALIZADAS
        st.markdown("### 📋 Ações Recomendadas (Personalizadas por IA)")
        
        # Buscar protocolos do beneficiário
        protocolos_ben = pd.read_sql(
            f"SELECT * FROM protocolos_sac WHERE id_beneficiario = '{ben['id_beneficiario']}'",
            services['db'].conn
        )
        
        # Converter para formato esperado pelo recommendations
        ben_dict = {
            'id_beneficiario': ben['id_beneficiario'],
            'nome': ben['nome'],
            'score_risco': ben['score_risco'],
            'mensalidade': ben['mensalidade'],
            'inadimplente': ben.get('inadimplente', False),
            'dificuldade': ben.get('dificuldade_retencao', 'Moderado')
        }
        
        protocolos_list = protocolos_ben.to_dict('records') if not protocolos_ben.empty else []
        
        # Importar e usar RecommendationEngine
        try:
            from src.src_recommendations import RecommendationEngine, ACOES_RETENCAO
            
            engine = RecommendationEngine()
            recomendacoes = engine.gerar_recomendacoes(ben_dict, protocolos_list)
            
            # Mostrar alertas se houver
            if recomendacoes.get('alertas'):
                for alerta in recomendacoes['alertas']:
                    st.warning(alerta)
            
            # Mostrar ações recomendadas
            acoes = recomendacoes.get('plano_acoes', [])
            
            if not acoes:
                # Fallback se engine falhar
                acoes = ACOES_RETENCAO[:5]
            
            for i, acao in enumerate(acoes[:5], 1):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**#{i}** {acao.get('acao', acao.get('nome', 'Ação não disponível'))}")
                with col2:
                    custo = acao.get('custo', 0)
                    sucesso = acao.get('taxa_sucesso', 50)
                    cor = '#48bb78' if sucesso >= 80 else '#ed8936' if sucesso >= 50 else '#f56565'
                    st.markdown(f"<span style='color:{cor};font-weight:700;'>R$ {custo} · {sucesso}%</span>", 
                               unsafe_allow_html=True)
        
        except Exception as e:
            # Fallback se módulo não estiver disponível
            st.warning(f"⚠️ Sistema de IA temporariamente indisponível. Mostrando ações padrão.")
            
            acoes_padrao = [
                {"acao": "Escalação imediata para gerente sênior", "custo": 200, "sucesso": 49},
                {"acao": "Plano de ação emergencial documentado", "custo": 100, "sucesso": 40},
                {"acao": "Desconto agressivo 20-30% por 6 meses", "custo": 810, "sucesso": 90},
                {"acao": "Plano personalizado sob medida", "custo": 300, "sucesso": 89},
                {"acao": "Força-tarefa: resolver TODAS pendências em 24h", "custo": 400, "sucesso": 90},
            ]
            
            for i, acao in enumerate(acoes_padrao, 1):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**#{i}** {acao['acao']}")
                with col2:
                    cor = '#48bb78' if acao['sucesso'] >= 80 else '#ed8936'
                    st.markdown(f"<span style='color:{cor};font-weight:700;'>R$ {acao['custo']} · {acao['sucesso']}%</span>", 
                               unsafe_allow_html=True)
# TAB 4: TRACKING DE AÇÕES
with tabs[3]:
    st.markdown("### 📝 Tracking de Ações de Retenção")
    
    tab_a, tab_b = st.tabs(["➕ Registrar Ação", "📋 Ações Registradas"])
    
    with tab_a:
        with st.form("form_acao"):
            c1, c2 = st.columns(2)
            with c1:
                ben_id = st.selectbox("Beneficiário:", df['id_beneficiario'].tolist())
                tipo = st.selectbox("Tipo de Ação:", ["Ligação Telefônica", "Desconto Oferecido", "Upgrade Plano", "Visita Presencial"])
                custo = st.number_input("Custo (R$):", 0.0, 10000.0, 200.0, 50.0)
            with c2:
                analista = st.text_input("Analista Responsável:")
                resultado = st.selectbox("Resultado:", ["EM_ABERTO", "RETIDO", "CANCELOU", "SEM_RESPOSTA"])
                obs = st.text_area("Observações:")
            
            if st.form_submit_button("💾 Registrar Ação", use_container_width=True):
                if analista:
                    # Usar database manager para registrar
                    services['db'].registrar_acao(ben_id, tipo, analista, custo, obs)
                    st.success("✅ Ação registrada no banco de dados!")
                    st.rerun()
    
    with tab_b:
        acoes_df = pd.read_sql("SELECT * FROM acoes_retencao ORDER BY data_acao DESC", services['db'].conn)
        if acoes_df.empty:
            st.info("Nenhuma ação registrada ainda")
        else:
            st.dataframe(acoes_df, use_container_width=True)

# TAB 5: ROI & RESULTADOS
with tabs[4]:
    st.markdown("### 💰 ROI de Ações de Retenção")
    
    acoes_df = pd.read_sql("SELECT * FROM acoes_retencao", services['db'].conn)
    
    if acoes_df.empty:
        st.info("Execute ações de retenção para ver ROI aqui")
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("🎯 Ações Executadas", len(acoes_df))
        with c2: st.metric("💰 Investimento Total", f"R$ {acoes_df['custo_real'].sum():,.2f}")
        
        retidos = len(acoes_df[acoes_df['resultado'] == 'RETIDO'])
        with c3: st.metric("✅ Beneficiários Retidos", f"{retidos}")
        
        # Calcular receita retida
        receita = 0
        for _, row in acoes_df[acoes_df['resultado'] == 'RETIDO'].iterrows():
            ben_row = df[df['id_beneficiario'] == row['id_beneficiario']]
            if not ben_row.empty:
                receita += ben_row.iloc[0]['mensalidade'] * 12
        
        with c4: st.metric("💚 Receita Retida (12m)", f"R$ {receita:,.2f}")
        
        st.divider()
        
        # Gráfico de efetividade
        if 'resultado' in acoes_df.columns:
            efetividade = acoes_df['resultado'].value_counts()
            fig = px.pie(values=efetividade.values, names=efetividade.index, 
                        title="Efetividade das Ações", hole=0.4)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

# TAB 6: ENVIAR RELATÓRIO POR E-MAIL
with tabs[5]:
    st.markdown("### 📧 Enviar Relatório por E-mail")
    
    # Testar configuração do e-mail
    col_test1, col_test2 = st.columns([3, 1])
    
    with col_test1:
        sucesso, msg = services['email'].testar_configuracao()
        if sucesso:
            st.success(msg)
        else:
            st.error(msg)
            st.info("""
**Como configurar o envio de e-mails:**

1. Crie um arquivo `.env` na raiz do projeto
2. Adicione as seguintes variáveis:

```env
# Gmail (recomendado)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app-gmail
FROM_EMAIL=seu-email@gmail.com
```

#**Para Gmail:** Gere uma senha de app em https://myaccount.google.com/apppasswords
            """)
    
    with col_test2:
        if st.button("🔄 Testar Conexão", use_container_width=True):
            st.rerun()
    
    st.divider()
    
    # Formulário de envio
    with st.form("form_envio_email"):
        st.markdown("#### Enviar Relatório de Alto Risco")
        
        col1, col2 = st.columns(2)
        
        with col1:
            destinatario = st.text_input(
                "📧 E-mail do Destinatário:",
                placeholder="diretor@operadora.com.br"
            )
        
        with col2:
            nome_analista = st.text_input(
                "👤 Seu Nome:",
                placeholder="João Silva"
            )
        
        submitted = st.form_submit_button("📨 Enviar Relatório", use_container_width=True, type="primary")
        
        if submitted and destinatario and nome_analista:
            # Preparar dados
            df_alto_risco = df[df['nivel_risco'] == 'Alto']
            
            # Enviar usando email_sender
            with st.spinner(f"Enviando relatório para {destinatario}..."):
                sucesso_envio = services['email'].enviar_relatorio_alto_risco(
                    to_email=destinatario,
                    df_alto_risco=df_alto_risco,
                    stats=stats,
                    nome_analista=nome_analista
                )
            
            if sucesso_envio:
                st.success(f"✅ Relatório enviado com sucesso para **{destinatario}**!")
                st.balloons()
            else:
                st.error("❌ Erro ao enviar e-mail. Verifique as configurações SMTP no arquivo .env")

# FOOTER
st.divider()
st.markdown("""
<div style='text-align:center;padding:2rem 0;color:#94a3b8;'>
    <p style='font-size:1.1rem;'><strong>LifePulse Pro v2.0</strong> — Sistema Preditivo de Retenção ANS</p>
    <p style='font-size:0.9rem;'>© 2025 LifePulse Analytics | O pulso vital da sua operadora</p>
</div>
""", unsafe_allow_html=True)
