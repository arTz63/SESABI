import base64
import datetime
import json
import time
from fpdf import FPDF
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


# Função para gerar a análise via Gemini
def gerar_analise_gemini(api_key, nicho, publico, ticket):
  genai.configure(api_key=api_key)

  modelos_para_testar = [
      "gemini-2.5-flash",
      "gemini-2.0-flash",
      "gemini-1.5-flash",
  ]

  prompt = f"""
    Atue como Diretor Estratégico de Inteligência de Mercado B2B.
    Gere um dossiê completo, profundo e altamente profissional em Markdown para:
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
    - As 3 maiores dores viscerais e profundas que esse público enfrenta.
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

  # Fallback dinâmico caso nenhum dos nomes acima esteja ativo na conta
  try:
    for m in genai.list_models():
      if "generateContent" in m.supported_generation_methods:
        try:
          model = genai.GenerativeModel(m.name)
          response = model.generate_content(prompt)
          if response and response.text:
            return response.text
        except Exception:
          continue
  except Exception:
    pass

  raise Exception(f"Erro de conexão com Gemini API: {ultimo_erro}")


# Função para gerar o relatório PDF
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


# Barra Lateral
st.sidebar.title("🛡️ Autenticação do Sistema")
vip_key = st.sidebar.text_input("Insira sua Chave de Licença VIP:", type="password")
gemini_api_key = st.sidebar.text_input(
    "Chave Gemini API (Grátis):", type="password"
)

VALID_VIP_KEY = "VIP-MASTER-2026"
is_authenticated = False

if vip_key:
  if vip_key.strip() in [VALID_VIP_KEY, "ARTHUR-VIP"]:
    st.sidebar.success("Licença Master Ativa (Acesso Total)")
    is_authenticated = True
  else:
    st.sidebar.error("Chave de licença corrompida ou inválida.")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "[🔑 Obter chave API Gemini Grátis](https://aistudio.google.com/)"
)

# Painel Principal
st.title("📈 DeepMarket AI — Enterprise v2.0")
st.caption(
    "Suíte Autônoma de Engenharia de Mercado, Mapeamento Comercial e Geração"
    " de Dossiês"
)

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

if st.button("🚀 EXECUTAR PIPELINE COMPLETO DE INTELIGÊNCIA"):
  if not is_authenticated:
    st.error("Insira a Chave VIP 'VIP-MASTER-2026' na barra lateral.")
  elif not gemini_api_key:
    st.error("Insira sua Chave de API do Gemini na barra lateral.")
  elif not nicho or not publico:
    st.warning("Preencha o Nicho e o Público-Alvo.")
  else:
    with st.spinner("⚡ Gerando Dossiê Estratégico em tempo real..."):
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
        st.error(f"Erro no processamento: {str(e)}")
