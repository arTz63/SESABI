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


def gerar_pdf(texto):
  pdf = FPDF()
  pdf.set_auto_page_break(auto=True, margin=15)
  pdf.add_page()

  for linha in texto.split("\n"):
    # Reseta o alinhamento horizontal para evitar estouro de margem no FPDF
    pdf.set_x(pdf.l_margin)

    # Trata caracteres especiais para o padrao latin-1 do FPDF
    linha_limpa = (
        linha.encode("latin-1", "replace").decode("latin-1").strip()
    )

    if not linha_limpa:
      pdf.ln(3)
      continue

    if linha_limpa.startswith("# "):
      pdf.set_font("Helvetica", style="B", size=15)
      pdf.multi_cell(0, 8, linha_limpa.replace("# ", ""))
      pdf.ln(2)
    elif linha_limpa.startswith("## "):
      pdf.set_font("Helvetica", style="B", size=13)
      pdf.multi_cell(0, 7, linha_limpa.replace("## ", ""))
      pdf.ln(2)
    elif linha_limpa.startswith("### "):
      pdf.set_font("Helvetica", style="B", size=11)
      pdf.multi_cell(0, 6, linha_limpa.replace("### ", ""))
      pdf.ln(1)
    else:
      pdf.set_font("Helvetica", size=10)
      pdf.multi_cell(0, 5, linha_limpa)
      pdf.ln(1)

  return bytes(pdf.output())


# Sidebar
st.sidebar.title("🛡️ Autenticação do Sistema")
vip_key = st.sidebar.text_input("Insira sua Chave de Licença VIP:", type="password")
gemini_api_key = st.sidebar.text_input(
    "Chave Gemini API (Grátis):", type="password"
)

VALID_VIP_KEY = "VIP-MASTER-2026"
is_authenticated = (
    vip_key.strip() in [VALID_VIP_KEY, "ARTHUR-VIP"] if vip_key else False
)

if vip_key:
  if is_authenticated:
    st.sidebar.success("Licença Master Ativa (Acesso Total)")
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
      # 1. Chamada de Inteligência Gemini
      try:
        client = genai.Client(api_key=gemini_api_key.strip())

        prompt = f"""
Atue como Diretor Estratégico de Inteligência de Mercado B2B.
Gere um dossiê executivo direto, prático e profundo para:
- Nicho: {nicho}
- Público: {publico}
- Ticket: {ticket}

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
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        dossie_texto = response.text if response else None

      except Exception as e:
        st.error(f"Erro na API do Gemini: {str(e)}")
        dossie_texto = None

      # 2. Exibição e Geração do PDF
      if dossie_texto:
        st.success("✅ Dossiê gerado com sucesso!")
        st.markdown("---")
        st.markdown(dossie_texto)

        try:
          pdf_bytes = gerar_pdf(dossie_texto)
          st.download_button(
              label="📥 BAIXAR DOSSIÊ EXECUTIVO (PDF)",
              data=pdf_bytes,
              file_name=f"Dossie_DeepMarket_{nicho.replace(' ', '_')}.pdf",
              mime="application/pdf",
          )
        except Exception as e:
          st.warning(
              "O dossiê foi gerado acima, mas ocorreu um erro na formatação do"
              f" PDF: {str(e)}"
          )
