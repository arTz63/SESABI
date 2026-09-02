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
    pdf.set_x(pdf.l_margin)
    linha_limpa = linha.encode("latin-1", "replace").decode("latin-1").strip()

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
        if (
            "503" in str(e)
            or "UNAVAILABLE" in str(e)
            or "429" in str(e)
            or "RESOURCE_EXHAUSTED" in str(e)
        ):
          time.sleep(2)
          continue
        else:
          break

  raise Exception(
      f"Servidor ocupado após várias tentativas. Detalhe: {ultimo_erro}"
  )


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
      options=[
          "R$ 100 - R$ 500",
          "R$ 500 - R$ 1.000",
          "R$ 1.000 - R$ 2.000",
          "R$ 2.000+ (High-Ticket)",
      ],
  )

if st.button("🚀 EXECUTAR PIPELINE COMPLETO DE INTELIGÊNCIA"):
  if not is_authenticated:
    st.error("Insira a Chave VIP 'VIP-MASTER-2026' na barra lateral.")
  elif not gemini_api_key:
    st.error("Insira sua Chave de API do Gemini na barra lateral.")
  elif not nicho or not publico:
    st.warning("Preencha o Nicho e o Público-Alvo.")
  else:
    with st.spinner(
        "⚡ Gerando Dossiê Estratégico e Plano de Ação em tempo real..."
    ):
      try:
        client = genai.Client(api_key=gemini_api_key.strip())

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
- Ferramentas, APIs e softwares recomendados para escalar essaoperação.

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
        st.error(f"Erro na API do Gemini: {str(e)}")
        dossie_texto = None
        sugestoes_texto = None

      if dossie_texto:
        st.success(
            f"✅ Análise completa gerada com sucesso! (Processado por:"
            f" {modelo_usado})"
        )
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
            st.warning(f"Erro no PDF Comercial: {str(e)}")

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
            st.warning(f"Erro no PDF do Plano de Ação: {str(e)}")
