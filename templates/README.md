# Templates de Importação — LifePulse Pro

## 📥 Como Usar

1. **Baixe** o template Excel
2. **Preencha** com seus dados reais
3. **Salve** como .xlsx ou .csv
4. **Importe** no sistema (aba "Importar Dados")

---

## 📋 Template 1: Beneficiários (OBRIGATÓRIO)

**Campos OBRIGATÓRIOS:**
- `id_beneficiario` — ID único (ex: BEN000001)
- `nome` — Nome completo
- `mensalidade` — Valor mensal em R$
- `data_adesao` — Data de entrada (AAAA-MM-DD)

**Campos OPCIONAIS (melhoram análise):**
- `data_nascimento` — Nascimento (AAAA-MM-DD)
- `sexo` — M ou F
- `codigo_plano` — Nome do plano
- `telefone`, `email`, `cidade`, `uf`
- `qtd_dependentes` — Quantidade de dependentes
- `forma_pagamento` — Boleto, Débito, Cartão
- `inadimplente` — true/false

**⚠️ NÃO PREENCHA (sistema calcula):**
- ~~score_risco~~ → Calculado automaticamente
- ~~nivel_risco~~ → Baixo/Médio/Alto (calculado)
- ~~dificuldade_retencao~~ → IA classifica
- ~~motivo_principal~~ → IA extrai de protocolos

---

## 📋 Template 2: Protocolos SAC (OPCIONAL)

Melhora muito a precisão da análise!

**Campos:**
- `numero_protocolo` — ID do protocolo
- `id_beneficiario` — Relacionar com beneficiário
- `data_abertura` — Data/hora (AAAA-MM-DD HH:MM:SS)
- `canal` — Telefone, Email, Chat, App
- `categoria` — Cobertura, Financeiro, Rede, etc
- `transcricao` — Texto do atendimento (IMPORTANTE!)
- `status` — ABERTO, EM_ANALISE, RESOLVIDO

**💡 Dica:** A `transcricao` é analisada por IA para extrair:
- Sentimento (positivo/neutro/negativo)
- Motivo principal
- Urgência
- Menção a cancelamento/ANS/Procon

---

## ✅ Validação Automática

O sistema valida automaticamente:
- Campos obrigatórios presentes
- Formatos de data corretos
- IDs únicos
- Valores numéricos válidos

Erros são mostrados na tela para correção.

---

**LifePulse Pro** — Sistema Preditivo de Retenção ANS
