# Painel Principal
st.title("📈 DeepMarket AI — Enterprise v2.0")
st.caption(
    "Suíte Autônoma de Engenharia de Mercado, Mapeamento Comercial e Geração"
    " de Dossiês"
)

# Sugestões Prontas (Templates para facilitar a vida do usuário)
TEMPLATES = {
    "Personalizado (Digitar do zero)": {"nicho": "", "publico": ""},
    "🏥 Saúde & Estética High-Ticket": {
        "nicho": (
            "Automação de Agendamento, Confirmação e Retenção de Pacientes"
        ),
        "publico": (
            "Médicos Donos de Clínicas de Cirurgia Plástica e Dermatologia"
        ),
    },
    "⚖️ Jurídico & Peças Processuais": {
        "nicho": "IA para Triagem Automática de Processos e Redação de Peças",
        "publico": "Sócios de Escritórios de Advocacia de Médio Porte",
    },
    "💰 Finanças & PMEs": {
        "nicho": (
            "Conciliação Financeira Automática e Centralização de Extratos"
        ),
        "publico": "Donos de PMEs e Gestores Financeiros de Redes de Franquia",
    },
    "🚀 Gestão de Tráfego & Agências": {
        "nicho": "Prospecção Ativa Outbound e Agendamento de Reuniões B2B",
        "publico": "Agências de Marketing e Gestores de Tráfego Pago",
    },
}

template_escolhido = st.selectbox(
    "💡 Sugestões de Nichos Lucrativos (Clique para Autopreencher):",
    options=list(TEMPLATES.keys()),
)

valores_template = TEMPLATES[template_escolhido]

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
  nicho = st.text_input(
      "Nicho / Produto de Análise:",
      value=valores_template["nicho"],
      placeholder="Ex: Software de Gestão de Clínicas",
  )
with col2:
  publico = st.text_input(
      "Público-Alvo Prioritário:",
      value=valores_template["publico"],
      placeholder="Ex: Médicos Donos de Consultórios Médios",
  )
with col3:
  ticket = st.selectbox(
      "Ticket da Oferta:",
      options=[
          "R$ 100 - R$ 500",
          "R$ 500 - R$ 1.000",
          "R$ 1.000 - R$ 2.000",
          "R$ 2.000+ (High-Ticket)",
      ],
  )
