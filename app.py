import re
import time
from fpdf import FPDF
from google import genai
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="DeepMarket AI — Enterprise v2.0",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f17; color: #e2e8f0; }
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.75rem 1.5rem;
        width: 100%;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def sanitizar_texto_pdf(texto):
  """Sanitiza o texto Markdown para exibição em PDF Latin-1 sem caracteres corrompidos."""
  substituicoes = {
      "“": '"',
      "”": '"',
      "‘": "'",
      "’": "'",
      "—": "-",
      "–": "-",
      "•": "*",
      "…": "...",
      "🚀": "",
      "📊": "",
      "💡": "",
      "🛡️": "",
      "🔑": "",
      "✅": "",
      "⚡": "",
      "📈": "",
  }
  for orig, dest in substituicoes.items():
    texto = texto.replace(orig, dest)

  # Remove marcadores de negrito markdown para não poluir o PDF
  texto = re.sub(r"\*\*(.*?)\*\*", r"\1", texto)

  # Converte caracteres não suportados pelo Latin-1 para similar limpo ou ignora
  return texto.encode("latin-1", "replace").decode("latin-1")


def gerar_pdf(texto):
  pdf = FPDF()
  pdf.set_auto_page_break(auto=True, margin=15)
  pdf.add_page()

  texto_limpo = sanitizar_texto_pdf(texto)

  for linha in texto_limpo.split("\n"):
    pdf.set_x(pdf.l_margin)
    linha_str = linha.strip()

    if not linha_str:
      pdf.ln(3)
      continue

    if linha_str.startswith("# "):
      pdf.set_font("Helvetica", style="B", size=14)
      pdf.multi_cell(0, 8, linha_str.replace("# ", ""))
      pdf.ln(2)
    elif linha_str.startswith("## "):
      pdf.set_font("Helvetica", style="B", size=12)
      pdf.multi_cell(0, 7, linha_str.replace("## ", ""))
      pdf.ln(2)
    elif linha_str.startswith("### "):
      pdf.set_font("Helvetica", style="B", size=10)
      pdf.multi_cell(0, 6, linha_str.replace("### ", ""))
      pdf.ln(1)
    else:
      pdf.set_font("Helvetica", size=9)
      pdf.multi_cell(0, 5, linha_str)
      pdf.ln(1)

  return bytes(pdf.output())


def obter_api_key():
  """Obtém a chave da API do Gemini priorizando as Secrets do servidor."""
  if "GEMINI_API_KEY" in st.secrets:
    return st.secrets["GEMINI_API_KEY"]
  elif "gemini_api_key_user" in st.session_state:
    return st.session_state["gemini_api_key_user"]
  return None


def validar_licenca(chave_inserida):
  """Valida a licença VIP do cliente contra as chaves autorizadas no servidor."""
  chave_limpa = chave_inserida.strip()
  chaves_validas = st.secrets.get(
      "VIP_KEYS", ["VIP-MASTER-2026", "ARTHUR-VIP"]
  )
  if isinstance(chaves_validas, str):
    chaves_validas = [chaves_validas]
  return chave_limpa in chaves_validas


def gerar_dossie_com_retry(client, prompt):
  modelos_prioridade = [
      "gemini-3.6-flash",
      "gemini-2.5-flash",
      "gemini-1.5-flash",
  ]
  ultimo_erro = None

  for modelo in modelos_prioridade:
    for tentativa in range(1, 4):
      try:
        response = client.models.generate_content(
            model=modelo, contents=prompt
        )
        if response and response.text:
          return response.text, modelo
      except Exception as e:
        ultimo_erro = str(e)
        if any(
            err in str(e)
            for err in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED"]
        ):
          time.sleep(2)
          continue
        else:
          break

  raise Exception(
      f"Servidor ocupado ou chave de API inválida. Detalhe: {ultimo_erro}"
  )


# Barra Lateral (Sidebar)
st.sidebar.title("🛡️ Acesso VIP ao Sistema")
vip_key = st.sidebar.text_input("Insira sua Licença VIP de Acesso:", type="password")

is_authenticated = validar_licenca(vip_key) if vip_key else False

if vip_key:
  if is_authenticated:
    st.sidebar.success("Licença Ativa (Acesso Liberado)")
  else:
    st.sidebar.error("Licença inválida ou expirada.")

# Caso a chave do servidor não esteja configurada nas secrets, libera um campo secundário em modo Dev
api_key_disponivel = obter_api_key()
if not api_key_disponivel and is_authenticated:
  st.sidebar.markdown("---")
  user_key_input = st.sidebar.text_input(
      "Chave API Gemini (Modo Dev):", type="password"
  )
  if user_key_input:
    st.session_state["gemini_api_key_user"] = user_key_input.strip()
    api_key_disponivel = user_key_input.strip()

# Painel Principal
st.title("📈 DeepMarket AI — Enterprise v2.0")
st.caption(
    "Suíte Autônoma de Engenharia de Mercado, Mapeamento Comercial e Geração"
    " de Dossiês"
)

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

if st.button("🚀 EXECUTAR PIPELINE COMPLETO DE INTELIGÊNCIA"):
  if not is_authenticated:
    st.error("Insira uma Licença VIP válida na barra lateral para prosseguir.")
  elif not api_key_disponivel:
    st.error(
        "Chave de API do servidor não localizada. Insira a chave no modo Dev na"
        " barra lateral."
    )
  elif not nicho or not publico:
    st.warning("Preencha o Nicho e o Público-Alvo.")
  else:
    with st.spinner("⚡ Processando inteligência de mercado..."):
      try:
        client = genai.Client(api_key=api_key_disponivel)

        prompt = f"""
Atue como Diretor Estratégico de Inteligência de Mercado B2B.
Gere uma análise dividida EXATAMENTE em duas partes usando a tag [DIVISOR_DE_SESSAO] entre elas.

- Nicho: {nicho}
- Público: {publico}
- Ticket: {ticket}

--- PARTE 1: DOSSIÊ EXECUTIVO DE MERCADO ---
# DOSSIÊ EXECUTIVO DE MERCADO

## 1. MÉTRICAS DE OPORTUNIDADE E SATURAÇÃO
- Nota de Oportunidade (0 a 100) e justificativa.
- Saturação do mercado.
- Dificuldade de CAC.

## 2. DIAGNÓSTICO PSICOGRÁFICO E DORES
- 3 Dores profundas deste público.
- 3 Objeções ao ticket {ticket} e soluções.
- Desejo principal de transformação.

## 3. SCRIPTS DE VENDAS E POSICIONAMENTO
- Proposta Única de Valor (PUV).
- Script de Abordagem Direct (WhatsApp/LinkedIn).
- Copy de Anúncio High-Ticket.

## 4. DIRETRIZ DE FECHAMENTO (REUNIÃO DE VENDAS)
- Roteiro de condução de reunião comercial.

[DIVISOR_DE_SESSAO]

--- PARTE 2: PLANO DE AÇÃO E SUGESTÕES TÁTICAS ---
# PLANO DE AÇÃO E RECOMENDAÇÕES PRÁTICAS

## 1. CRONOGRAMA DE IMPLEMENTAÇÃO (SEMANA A SEMANA)
- Passo a passo de execução técnica e comercial para os primeiros 30 dias.

## 2. STACK TECNOLÓGICO E FERRAMENTAS RECOMENDADAS
- Ferramentas, APIs e softwares recomendados para escalar essa operação.

## 3. CHECKLIST DE ENTRADA DO CLIENTE (ONBOARDING)
- Requisitos técnicos que o cliente precisa fornecer antes do início do projeto.
"""
        resultado_completo, modelo_usado = gerar_dossie_com_retry(
            client, prompt
        )

        if "[DIVISOR_DE_SESSAO]" in resultado_completo:
          partes = resultado_completo.split("[DIVISOR_DE_SESSAO]")
          dossie_texto = partes[0].strip()
          sugestoes_texto = partes[1].strip()
        else:
          dossie_texto = resultado_completo
          sugestoes_texto = "Plano de Ação integrado ao dossiê principal."

      except Exception as e:
        st.error(f"Erro no processamento: {str(e)}")
        dossie_texto = None
        sugestoes_texto = None

      if dossie_texto:
        st.success(f"✅ Análise concluída via {modelo_usado}!")
        st.markdown("---")

        tab1, tab2 = st.tabs(
            ["📊 Dossiê Comercial", "💡 Plano de Ação & Sugestões"]
        )

        with tab1:
          st.markdown(dossie_texto)
          try:
            pdf_bytes1 = gerar_pdf(dossie_texto)
            st.download_button(
                label="📥 BAIXAR DOSSIÊ COMERCIAL (PDF)",
                data=pdf_bytes1,
                file_name=f"Dossie_Comercial_{nicho.replace(' ', '_')}.pdf",
                mime="application/pdf",
                key="btn_pdf_dossie",
            )
          except Exception as e:
            st.warning(f"Erro ao compilar PDF Comercial: {str(e)}")

        with tab2:
          st.markdown(sugestoes_texto)
          try:
            pdf_bytes2 = gerar_pdf(sugestoes_texto)
            st.download_button(
                label="📥 BAIXAR PLANO DE AÇÃO (PDF)",
                data=pdf_bytes2,
                file_name=f"Plano_de_Acao_{nicho.replace(' ', '_')}.pdf",
                mime="application/pdf",
                key="btn_pdf_plano",
            )
          except Exception as e:
            st.warning(f"Erro ao compilar PDF do Plano de Ação: {str(e)}")
