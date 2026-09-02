import FPDF
import google.generativeai as genai
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="DeepMarket AI — Enterprise v2.0",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS para o botão verde
st.markdown(
    """
<style>
    div.stButton > button:first-child {
        background-color: #10B981;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
    }
    div.stButton > button:first-child:hover {
        background-color: #059669;
        color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Função rápida para gerar toda a análise em uma única requisição
def gerar_analise_gemini(api_key, nicho, publico, ticket):
  genai.configure(api_key=api_key)

  # Modelos padrão ativos
  modelos_para_testar = [
      "gemini-1.5-flash",
      "gemini-1.5-pro",
      "gemini-1.0-pro",
  ]

  prompt = f"""
    Atue como Diretor Estratégico de Inteligência de Mercado. Gere um dossiê completo, profundo e profissional em Markdown para:
    - Nicho / Produto: {nicho}
    - Público-Alvo: {publico}
    - Ticket da Oferta: {ticket}

    Estruture a resposta EXATAMENTE com os seguintes tópicos:

    # DOSSIÊ EXECUTIVO DE MERCADO

    ## 1. MÉTRICAS DE OPORTUNIDADE E SATURAÇÃO
    - Nota de Oportunidade (0 a 100) com justificativa técnica.
    - Nível de Saturação do mercado atual.
    - Estimativa e nível de dificuldade do CAC (Custo de Aquisição de Cliente).

    ## 2. DIAGNÓSTICO PSICOGRÁFICO E DORES INVISÍVEIS
    - As 3 maiores dores viscerais/emocionais que esse público enfrenta.
    - As 3 maiores objeções para comprar no ticket {ticket} e como neutralizá-las.
    - O principal desejo de status e transformação buscado pelo cliente.

    ## 3. ENGENHARIA DE POSICIONAMENTO E SCRIPTS DE VENDAS
    - Proposta Única de Valor (PUV) irresistível.
    - Script de Abordagem Direct / Cold Outreach (WhatsApp / LinkedIn) de alta conversão.
    - Copy de Anúncio (Título chamativo, Corpo da mensagem e CTA).
    """

  ultimo_erro = None
  for nome_modelo in modelos_para_testar:
    try:
      model = genai.GenerativeModel(nome_modelo)
      response = model.generate_content(prompt)
      if response and response.text:
        return response.text
    except Exception as e:
      ultimo_erro = e
      continue

  raise Exception(f"Falha ao conectar com o Gemini: {ultimo_erro}")


# Função para gerar o arquivo PDF do Dossiê
def gerar_pdf(texto):
  pdf = FPDF()
  pdf.add_page()
  pdf.set_font("Helvetica", size=11)

  linhas = texto.split("\n")
  for linha in linhas:
    linha_limpa = linha.encode("latin-1", "replace").decode("latin-1")
    if linha.startswith("# "):
      pdf.set_font("Helvetica", style="B", size=16)
      pdf.cell(0, 10, linha_limpa.replace("# ", ""), ln=True)
      pdf.set_font("Helvetica", size=11)
    elif linha.startswith("## "):
      pdf.set_font("Helvetica", style="B", size=13)
      pdf.cell(0, 8, linha_limpa.replace("## ", ""), ln=True)
      pdf.set_font("Helvetica", size=11)
    else:
      pdf.multi_cell(0, 6, linha_limpa)

  return bytes(pdf.output())


# --- BARRA LATERAL (AUTENTICAÇÃO) ---
st.sidebar.title("🛡️ Autenticação do Sistema")

vip_key = st.sidebar.text_input("Insira sua Chave de Licença VIP:", type="password")

gemini_api_key = st.sidebar.text_input(
    "Chave Gemini API (Grátis):", type="password"
)

VALID_VIP_KEY = "VIP-MASTER-2026"
is_authenticated = False

if vip_key:
  if vip_key.strip() == VALID_VIP_KEY:
    st.sidebar.success("Licença Master Ativa (Acesso Total)")
    is_authenticated = True
  else:
    st.sidebar.error("Chave de licença corrompida ou inválida.")
    is_authenticated = False

st.sidebar.markdown("---")
st.sidebar.markdown(
    "[🔑 Obter chave API Gemini Grátis](https://aistudio.google.com/)"
)

# --- PAINEL PRINCIPAL ---
st.title("📈 DeepMarket AI — Enterprise v2.0")
st.caption(
    "Suíte Autônoma de Engenharia de Mercado, Mapeamento Comercial e Geração"
    " de Dossiês"
)

st.write("")

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
  nicho = st.text_input(
      "Nicho / Produto de Análise:",
      placeholder="Ex: Software de Gestão de Clínicas",
  )

with col2:
  publico = st.text_input(
      "Público-Alvo Prioritário:",
      placeholder="Ex: Médicos Donos de Consultórios Médios",
  )

with col3:
  ticket = st.selectbox(
      "Ticket da Oferta:",
      options=["R$ 100 - R$ 500", "R$ 500 - R$ 2.000", "R$ 2.000+ (High-Ticket)"],
      index=0,
  )

# Execução do Pipeline
if st.button("🚀 EXECUTAR PIPELINE COMPLETO DE INTELIGÊNCIA"):
  if not is_authenticated:
    st.error(
        "Por favor, insira uma Chave de Licença VIP válida na barra lateral"
        " para prosseguir."
    )
  elif not gemini_api_key:
    st.error("Por favor, insira sua Chave Gemini API na barra lateral.")
  elif not nicho or not publico:
    st.warning("Preencha o Nicho/Produto e o Público-Alvo antes de executar.")
  else:
    with st.spinner(
        "⚡ Gerando Dossiê Estratégico de Mercado (levará apenas alguns"
        " segundos)..."
    ):
      try:
        dossie_texto = gerar_analise_gemini(
            gemini_api_key, nicho, publico, ticket
        )

        st.success("✅ Dossiê gerado com sucesso!")
        st.markdown("---")
        st.markdown(dossie_texto)

        pdf_bytes = gerar_pdf(dossie_texto)

        st.download_button(
            label="📥 BAIXAR DOSSIÊ EXECUTIVO (PDF)",
            data=pdf_bytes,
            file_name=f"Dossie_DeepMarket_{nicho.replace(' ', '_')}.pdf",
            mime="application/pdf",
        )
      except Exception as e:
        st.error(f"Erro na comunicação com a API: {str(e)}")
