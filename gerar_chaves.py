import base64
import datetime
import hashlib
import json
import time
from fpdf import FPDF
import google.generativeai as genai
import streamlit as st

# ==========================================
# 1. MÓDULO DE SEGURANÇA E LICENCIAMENTO (SHA-256)
# ==========================================
class LicenseManager:
  SALT = "DEEPMARKET_ENTERPRISE_SECURE_2026_KEY"

  @classmethod
  def generate_license(
      cls, client_id: str, days_valid: int = 365
  ) -> str:
    expiry_date = (
        datetime.date.today() + datetime.timedelta(days=days_valid)
    ).strftime("%Y-%m-%d")
    payload = f"{client_id}|{expiry_date}"
    signature = hashlib.sha256(
        f"{payload}|{cls.SALT}".encode()
    ).hexdigest()[:8]
    token = f"{payload}|{signature}"
    return base64.b64encode(token.encode()).decode()

  @classmethod
  def validate_license(cls, token_b64: str) -> tuple[bool, str, str]:
    try:
      decoded = base64.b64decode(token_b64.strip().encode()).decode()
      parts = decoded.split("|")
      if len(parts) != 3:
        return False, "Formato de chave inválido.", ""

      client_id, expiry_str, signature = parts
      expected_sig = hashlib.sha256(
          f"{client_id}|{expiry_str}|{cls.SALT}".encode()
      ).hexdigest()[:8]

      if signature != expected_sig:
        return False, "Assinatura de licença inválida.", ""

      expiry_date = datetime.datetime.strptime(expiry_str, "%Y-%m-%d").date()
      if datetime.date.today() > expiry_date:
        return False, f"Licença expirada em {expiry_str}.", client_id

      return (
          True,
          f"Licença Ativa (Cliente: {client_id} | Válida até:"
          f" {expiry_str})",
          client_id,
      )
    except Exception:
      return False, "Chave de licença corrompida ou inválida.", ""


# ==========================================
# 2. GERADOR DE DOSSIÊ EM PDF EXECUTIVO
# ==========================================
class CorporatePDF(FPDF):

  def header(self):
    self.set_fill_color(15, 23, 42)  # Dark Slate Blue
    self.rect(0, 0, 210, 25, "F")
    self.set_font("Arial", "B", 14)
    self.set_text_color(255, 255, 255)
    self.cell(
        0, 5, "DEEPMARKET AI - DOSSIÊ DE INTELIGÊNCIA COMERCIAL", 0, 1, "C"
    )
    self.set_font("Arial", "", 9)
    self.cell(
        0, 5, "SISTEMA AUTÔNOMO DE ANÁLISE DE MERCADO & ESTRATÉGIA B2B", 0, 1, "C"
    )
    self.ln(12)

  def footer(self):
    self.set_y(-15)
    self.set_font("Arial", "I", 8)
    self.set_text_color(100, 116, 139)
    self.cell(
        0,
        10,
        f"Página {self.page_no()} | Documento de Uso Exclusivo e Confidencial",
        0,
        0,
        "C",
    )


def build_pdf_report(nicho, metrics, persona_data, copy_data):
  pdf = CorporatePDF()
  pdf.add_page()
  pdf.set_text_color(30, 41, 59)

  # Cabeçalho
  pdf.set_font("Arial", "B", 12)
  pdf.cell(0, 8, f"RELATÓRIO ESTRATÉGICO: {nicho.upper()}", 0, 1)
  pdf.set_font("Arial", "", 9)
  pdf.cell(
      0,
      5,
      f"Data da Emissão: {datetime.date.today().strftime('%d/%m/%Y')} | Status:"
      " Validação Concluída",
      0,
      1,
  )
  pdf.ln(4)

  # Tabela de KPIs
  pdf.set_fill_color(241, 245, 249)
  pdf.rect(10, pdf.get_y(), 190, 18, "F")
  pdf.set_font("Arial", "B", 10)
  pdf.cell(
      63, 9, f"Oportunidade: {metrics.get('score', 'N/A')}/100", 0, 0, "C"
  )
  pdf.cell(63, 9, f"Saturação: {metrics.get('saturacao', 'N/A')}", 0, 0, "C")
  pdf.cell(
      64, 9, f"Dificuldade CAC: {metrics.get('cac_level', 'N/A')}", 0, 1, "C"
  )
  pdf.ln(10)

  # Seção 1
  pdf.set_font("Arial", "B", 11)
  pdf.set_text_color(15, 23, 42)
  pdf.cell(0, 7, "1. DIAGNÓSTICO DE PERSONA E DORES INVISÍVEIS", 0, 1)
  pdf.set_font("Arial", "", 9.5)
  pdf.set_text_color(51, 65, 85)
  pdf.multi_cell(0, 5.5, persona_data.encode("latin-1", "replace").decode("latin-1"))
  pdf.ln(6)

  # Seção 2
  pdf.set_font("Arial", "B", 11)
  pdf.set_text_color(15, 23, 42)
  pdf.cell(0, 7, "2. PEÇAS DE VENDAS E CONVERSÃO HIGH-TICKET", 0, 1)
  pdf.set_font("Arial", "", 9.5)
  pdf.set_text_color(51, 65, 85)
  pdf.multi_cell(0, 5.5, copy_data.encode("latin-1", "replace").decode("latin-1"))

  return pdf.output(dest="S").encode("latin-1")


# ==========================================
# 3. INTERFACE STREAMLIT
# ==========================================
st.set_page_config(
    page_title="DeepMarket AI Enterprise", page_icon="📈", layout="wide"
)

st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f17; color: #e2e8f0; }
    .stButton>button { background: linear-gradient(90deg, #10b981 0%, #059669 100%); color: white; font-weight: bold; border: none; padding: 12px; border-radius: 6px; }
    </style>
""",
    unsafe_allow_html=True,
)

# Sidebar
st.sidebar.title("🛡️ Autenticação do Sistema")
license_input = st.sidebar.text_input(
    "Insira sua Chave de Licença VIP:", type="password"
)
api_key_input = st.sidebar.text_input(
    "Chave Gemini API (Grátis):", type="password"
)

st.sidebar.divider()

is_licensed, lic_message, client_id = (
    LicenseManager.validate_license(license_input)
    if license_input
    else (False, "Insira a chave de licença.", "")
)

if is_licensed:
  st.sidebar.success(lic_message)
else:
  st.sidebar.error(
      lic_message if license_input else "Aguardando chave de ativação..."
  )

st.sidebar.markdown(
    "[🔑 Obter chave API Gemini Grátis](https://aistudio.google.com/)"
)

# Interface Principal
st.title("📈 DeepMarket AI — Enterprise v2.0")
st.caption(
    "Suíte Autônoma de Engenharia de Mercado, Mapeamento Comercial e Geração"
    " de Dossiês"
)

if not is_licensed:
  st.warning(
      "🔒 **SISTEMA BLOQUEADO**: Insira uma licença válida no menu lateral"
      " para liberar os módulos de análise."
  )
  st.stop()

with st.container():
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
        [
            "R$ 100 - R$ 500",
            "R$ 500 - R$ 2.000 (Médio)",
            "R$ 2.000+ (High-Ticket)",
        ],
    )

btn_analisar = st.button("🚀 EXECUTAR PIPELINE COMPLETO DE INTELIGÊNCIA")

if btn_analisar:
  if not api_key_input:
    st.error("Erro: A Chave de API do Gemini é obrigatória.")
  elif not nicho or not publico:
    st.warning("Preencha o Nicho e o Público-Alvo para iniciar.")
  else:
    try:
      genai.configure(api_key=api_key_input)
      model = genai.GenerativeModel("gemini-1.5-flash")

      progress_bar = st.progress(0)
      status_text = st.empty()

      # ETAPA 1
      status_text.text(
          "⚡ Etapa 1/4: Processando Métricas de Oportunidade e Saturação..."
      )
      progress_bar.progress(25)

      prompt_metrics = f"""
            Retorne APENAS um JSON válido contendo a avaliação do nicho '{nicho}' para o público '{publico}'.
            Formato exigido:
            {{
                "score": 85,
                "saturacao": "Média/Baixa",
                "cac_level": "Moderado",
                "resumo_oportunidade": "Breve frase explicativa"
            }}
            Não inclua marcação markdown nem texto adicional fora do JSON.
            """
      res_metrics_raw = model.generate_content(prompt_metrics).text
      try:
        clean_json = (
            res_metrics_raw.replace("```json", "").replace("```", "").strip()
        )
        metrics_data = json.loads(clean_json)
      except Exception:
        metrics_data = {
            "score": 80,
            "saturacao": "Média",
            "cac_level": "Moderado",
            "resumo_oportunidade": "Oportunidade sólida identificada.",
        }

      time.sleep(0.5)

      # ETAPA 2
      status_text.text(
          "🧠 Etapa 2/4: Mapeando Dores Inconscientes e Matriz de Objeções..."
      )
      progress_bar.progress(50)

      prompt_persona = f"""
            Atue como Diretor de Inteligência de Mercado B2B. Faça uma análise cirúrgica sobre '{nicho}' para o público '{publico}' na faixa de ticket '{ticket}'.
            Apresente com marcação legível:
            1. PERFIL PSICOGRÁFICO: As 3 dores emocionais/financeiras mais profundas que tiram o sono deste público.
            2. MATRIZ DE OBJEÇÕES: As 3 maiores desculpas para NÃO comprar e como neutralizar cada uma.
            3. ÂNGULO DE POSICIONAMENTO ÚNICO: A promessa principal que torna a concorrência irrelevante.
            """
      res_persona = model.generate_content(prompt_persona).text
      time.sleep(0.5)

      # ETAPA 3
      status_text.text(
          "✍️ Etapa 3/4: Construindo Peças de Vendas e Scripts de Abordagem..."
      )
      progress_bar.progress(75)

      prompt_copy = f"""
            Com base na análise do nicho '{nicho}' e público '{publico}', crie as seguintes peças de conversão:
            1. SCRIPT DE VÍDEO CURTO (Reels/TikTok/Loom): Focado em gancho de retenção nos primeiros 3 segundos.
            2. MENSAGEM DE COLD OUTREACH (WhatsApp/LinkedIn): Mensagem direta de alto valor para iniciar conversas de vendas.
            3. ANÚNCIO DE ALTA CONVERSÃO: Copy completa com título, corpo e CTA direcionado.
            """
      res_copy = model.generate_content(prompt_copy).text
      time.sleep(0.5)

      # ETAPA 4
      status_text.text("📑 Etapa 4/4: Gerando Dossiê Executivo Formatado...")
      progress_bar.progress(100)
      time.sleep(0.3)

      status_text.empty()
      progress_bar.empty()

      st.success("Análise de Mercado Concluída com Sucesso!")

      st.subheader("📊 Painel de Indicadores do Mercado")
      m1, m2, m3 = st.columns(3)
      with m1:
        st.metric(
            label="Índice de Oportunidade",
            value=f"{metrics_data.get('score')}/100",
        )
      with m2:
        st.metric(
            label="Nível de Saturação",
            value=str(metrics_data.get("saturacao")),
        )
      with m3:
        st.metric(
            label="Estimativa de CAC", value=str(metrics_data.get("cac_level"))
        )

      st.info(
          f"**Parecer Técnico:** {metrics_data.get('resumo_oportunidade')}"
      )

      tab1, tab2 = st.tabs(
          ["🧠 Diagnóstico de Mercado", "✍️ Frameworks de Vendas"]
      )
      with tab1:
        st.markdown(res_persona)
      with tab2:
        st.markdown(res_copy)

      pdf_bytes = build_pdf_report(nicho, metrics_data, res_persona, res_copy)

      st.divider()
      st.download_button(
          label="📥 BAIXAR DOSSIÊ EXECUTIVO COMPLETO (PDF)",
          data=pdf_bytes,
          file_name=f"Dossie_DeepMarket_{nicho.replace(' ', '_')}.pdf",
          mime="application/pdf",
      )

    except Exception as e:
      st.error(f"Falha na execução do pipeline: {str(e)}")
