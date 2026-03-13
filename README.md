# 💙 LifePulse Pro v2.0

Sistema Preditivo de Retenção para Operadoras de Saúde (ANS)

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 Sobre o Projeto

LifePulse Pro é um sistema de análise preditiva que identifica beneficiários em risco de churn e recomenda ações personalizadas de retenção para operadoras de saúde.

### ✨ Funcionalidades

- 📊 **Análise Preditiva de Risco** - Score de 0-100 com algoritmo ponderado
- 🤖 **Recomendações IA** - Ações personalizadas usando Claude/GPT-4
- 📈 **Cálculo de ROI** - Retorno projetado de ações de retenção
- 📧 **Relatórios por E-mail** - Envio automático de alertas
- 📥 **Importação de Dados** - Templates Excel para beneficiários, protocolos e utilização
- 💰 **Tracking de Ações** - Registro e acompanhamento de resultados

## 🚀 Instalação
```bash
# 1. Clone o repositório
git clone https://github.com/luizjf/lifepulse-pro.git
cd lifepulse-pro

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente (opcional)
cp .env.example .env
# Edite .env com suas credenciais

# 5. Execute
streamlit run app.py
```

## 📊 Estrutura do Projeto
```
lifepulse-pro/
├── app.py                      # Aplicação principal
├── src/                        # Módulos do sistema
│   ├── config.py              # Configurações
│   ├── database.py            # Gerenciador SQLite
│   ├── risk_analyzer.py       # Cálculo de scores
│   ├── roi_calculator.py      # Cálculo de ROI
│   ├── ai_integration.py      # Integração IA
│   └── email_sender.py        # Envio de relatórios
├── templates/                  # Templates Excel
└── requirements.txt
```

## 💡 Como Usar

1. **Gere dados de teste** → Sidebar → "⚡ Gerar Dados de Teste"
2. **Ou importe seus dados** → Sidebar → "📥 Importar Dados"
3. **Explore as funcionalidades** → 6 abas com análises completas
4. **Envie relatórios** → Aba "📧 Enviar Relatório"

## 🎯 Business Case

Para operadora com 50.000 vidas:
- Redução de churn de 18% → 12% = **3.000 vidas retidas**
- Receita preservada: **R$ 18MM/ano**
- CAC economizado: **R$ 3.6MM**
- **ROI: 500-1200%**

## 🛠️ Tecnologias

- **Frontend:** Streamlit
- **Backend:** Python 3.11+
- **Banco de Dados:** SQLite
- **IA:** Anthropic Claude / OpenAI GPT-4
- **Visualização:** Plotly
- **Análise:** Pandas, NumPy

## 📧 Contato

Desenvolvido por [Seu Nome]
- LinkedIn: [seu-linkedin]
- Email: seu-email@exemplo.com

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes