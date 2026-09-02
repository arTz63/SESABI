import re
import time
from fpdf import FPDF
from google import genai
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="DeepMarket AI — Enterprise Strategy Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS Enterprise
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f17; color: #e2e8f0; }
    
    /* Botão Principal */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        font-weight: 600;
        font-size: 16px;
        border-radius: 8px;
        border: none;
        padding: 0.85rem 1.5rem;
        width: 100%;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(90deg, #1d4ed8 0%, #1e40af 100%);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
    }
    
    /* Card de Autenticação */
    .login-card {
        background-color: #1e293b;
        padding: 2.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
        max-width: 450px;
        margin: 4rem auto;
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
      "🎯": "",
      "💰": "",
      "🔎": "",
  }
  for orig, dest in substituicoes.items():
    texto = texto.replace(orig, dest)

  texto = re.sub(r"\*\*(.*?)\*\*", r"\1", texto)
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
  if "GEMINI_API_KEY" in st.secrets:
    return st.secrets["GEMINI_API_KEY"]
  elif "gemini_api_key_user" in st.session_state:
    return st.session_state["gemini_api_key_user"]
  return None


def validar_licenca(chave_inserida):
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
      f"Servidor ocupado ou instabilidade de conexão. Detalhe: {ultimo_erro}"
  )


# Gerenciamento de Estado de Autenticação
if "autenticado" not in st.session_state:
  st.session_state["autenticado"] = False

# TELA 1: GATEWAY DE ACESSO (Módulo de Login Profissional)
if not st.session_state["autenticado"]:
  col_a, col_b, col_c = st.columns([1, 2, 1])
  with col_b:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("📈 DeepMarket AI")
    st.caption("Plataforma Enterprise de Inteligência e Engenharia de Mercado")
    st.markdown("---")

    st.subheader("Acesso à Plataforma")
    chave_input = st.text_input(
        "Insira sua Chave de Licença:",
        type="password",
        placeholder="DM-XXXX-XXXX-XXXX",
    )

    if st.button("Entrar no Sistema"):
      if validar_licenca(chave_input):
        st.session_state["autenticado"] = True
        st.rerun()
      else:
        st.error(
            "Chave de licença inválida ou expirada. Verifique suas credenciais."
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "💡 Ainda não possui licença corporativa? Entre em contato com nossa"
        " equipe comercial."
    )

# TELA 2: DASHBOARD PRINCIPAL (Exibido apenas após validação)
else:
  # Barra Lateral Minimizada para Status
  st.sidebar.title(" DeepMarket AI")
  st.sidebar.success("● Licença Ativa")

  if st.sidebar.button("Encerrar Sessão"):
    st.session_state["autenticado"] = False
    st.rerun()

  api_key_disponivel = obter_api_key()

  # Caso o servidor não tenha secret configurado
  if not api_key_disponivel:
    st.sidebar.markdown("---")
    user_key_input = st.sidebar.text_input(
        "Chave API Gemini (Desenvolvimento):", type="password"
    )
    if user_key_input:
      st.session_state["gemini_api_key_user"] = user_key_input.strip()
      api_key_disponivel = user_key_input.strip()

  # Painel Principal
  st.title("Geração de Dossiê Estratégico")
  st.caption(
      "Mapeamento de demanda, análise psicográfica de público e estrutura de"
      " vendas High-Ticket."
  )
  st.markdown("---")

  TEMPLATES = {
      "Personalizado (Definir parâmetros manualmente)": {
          "nicho": "",
          "publico": "",
      },
      "🏥 Saúde & Estética High-Ticket": {
          "nicho": (
              "Automação de Agendamento, Confirmação e Retenção de Pacientes"
          ),
          "publico": (
              "Médicos Donos de Clínicas de Cirurgia Plástica e Dermatologia"
          ),
      },
      "⚖️ Jurídico & Peças Processuais": {
          "nicho": (
              "Inteligência Artificial para Triagem de Processos e Peças"
          ),
          "publico": "Sócios de Escritórios de Advocacia Corporativa",
      },
      "💰 Finanças & PMEs": {
          "nicho": (
              "Conciliação Financeira Automática e Centralização de Extratos"
          ),
          "publico": (
              "Donos de PMEs e Gestores Financeiros de Redes de Franquias"
          ),
      },
      "🚀 B2B & Agências de Crescimento": {
          "nicho": "Prospecção Ativa Outbound e Agendamento de Reuniões B2B",
          "publico": "Agências de Marketing, Consultorias e Gestores de Tráfego",
      },
  }

  template_escolhido = st.selectbox(
      "💡 Selecionar Modelo Preconfigurado:", options=list(TEMPLATES.keys())
  )

  valores_template = TEMPLATES[template_escolhido]

  col1, col2, col3 = st.columns([2, 2, 1])
  with col1:
    nicho = st.text_input(
        "Nicho ou Solução Analisada:",
        value=valores_template["nicho"],
        placeholder="Ex: Software de Gestão Médica",
    )
  with col2:
    publico = st.text_input(
        "Público-Alvo Prioritário:",
        value=valores_template["publico"],
        placeholder="Ex: Sócios de Clínicas Médicas",
    )
  with col3:
    ticket = st.selectbox(
        "Faixa de Ticket:",
        options=[
            "R$ 100 - R$ 500",
            "R$ 500 - R$ 1.000",
            "R$ 1.000 - R$ 2.000",
            "R$ 2.000+ (High-Ticket)",
        ],
    )

  if st.button("📊 GERAR DOSSIÊ ESTRATÉGICO"):
    if not api_key_disponivel:
      st.error("Servidor indisponível no momento. Contate o suporte técnico.")
    elif not nicho or not publico:
      st.warning("Preencha o Nicho e o Público-Alvo para continuar.")
    else:
      # Feedback Etapa por Etapa profissional
      with st.status(
          "Iniciando análise de mercado...", expanded=True
      ) as status:
        st.write("🔎 Analisando dinâmicas de mercado e volume de busca...")
        time.sleep(1.2)

        st.write("🎯 Identificando perfil psicográfico e dores do público...")
        time.sleep(1.2)

        st.write("💰 Estruturando viabilidade financeira e precificação...")
        time.sleep(1.2)

        st.write("📊 Compilando dossiê comercial e scripts de abordagem...")

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

          status.update(
              label="📄 Dossiê concluído com sucesso!",
              state="complete",
              expanded=False,
          )

        except Exception as e:
          status.update(
              label="❌ Erro no processamento.", state="error", expanded=True
          )
          st.error(f"Detalhe do erro: {str(e)}")
          dossie_texto = None
          sugestoes_texto = None

      if dossie_texto:
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
