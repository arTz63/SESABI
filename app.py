import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# Configuração da página
st.set_page_config(
    page_title="DeepMarket AI — Enterprise v2.0",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para o botão verde e área de autenticação
st.markdown("""
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
""", unsafe_allow_html=True)

# Função para chamar o Gemini com Fallback Automático de Modelos (Resolve o erro 404)
def chamar_gemini(api_key, prompt):
    genai.configure(api_key=api_key)
    
    # Lista de modelos ordenados por preferência e estabilidade
    modelos_candidatos = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.5-pro",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash"
    ]
    
    ultimo_erro = None
    
    # 1. Tenta a lista de modelos candidatos
    for nome_modelo in modelos_candidatos:
        try:
            modelo = genai.GenerativeModel(nome_modelo)
            resposta = modelo.generate_content(prompt)
            if resposta and resposta.text:
                return resposta.text
        except Exception as e:
            ultimo_erro = e
            continue
            
    # 2. Se nenhum da lista responder, busca dinamicamente qualquer modelo ativo na conta
    try:
        modelos_disponiveis = [
            m.name for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
        for nome_m in modelos_disponiveis:
            try:
                modelo = genai.GenerativeModel(nome_m)
                resposta = modelo.generate_content(prompt)
                if resposta and resposta.text:
                    return resposta.text
            except Exception:
                continue
    except Exception:
        pass
        
    raise RuntimeError(f"{ultimo_erro}")

# Função para gerar o arquivo PDF do Dossiê
def gerar_pdf(texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    
    linhas = texto.split('\n')
    for linha in linhas:
        linha_limpa = linha.encode('latin-1', 'replace').decode('latin-1')
        if linha.startswith('# '):
            pdf.set_font("Helvetica", style='B', size=16)
            pdf.cell(0, 10, linha_limpa.replace('# ', ''), ln=True)
            pdf.set_font("Helvetica", size=11)
        elif linha.startswith('## '):
            pdf.set_font("Helvetica", style='B', size=13)
            pdf.cell(0, 8, linha_limpa.replace('## ', ''), ln=True)
            pdf.set_font("Helvetica", size=11)
        else:
            pdf.multi_cell(0, 6, linha_limpa)
            
    return bytes(pdf.output())

# --- BARRA LATERAL (AUTENTICAÇÃO) ---
st.sidebar.title("🛡️ Autenticação do Sistema")

vip_key = st.sidebar.text_input(
    "Insira sua Chave de Licença VIP:",
    type="password"
)

gemini_api_key = st.sidebar.text_input(
    "Chave Gemini API (Grátis):",
    type="password"
)

# Validação da licença VIP
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
st.sidebar.markdown("[🔑 Obter chave API Gemini Grátis](https://aistudio.google.com/)")

# --- PAINEL PRINCIPAL ---
st.title("📈 DeepMarket AI — Enterprise v2.0")
st.caption("Suíte Autônoma de Engenharia de Mercado, Mapeamento Comercial e Geração de Dossiês")

st.write("")

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    nicho = st.text_input(
        "Nicho / Produto de Análise:",
        placeholder="Ex: Software de Gestão de Clínicas"
    )

with col2:
    publico = st.text_input(
        "Público-Alvo Prioritário:",
        placeholder="Ex: Médicos Donos de Consultórios Médios"
    )

with col3:
    ticket = st.selectbox(
        "Ticket da Oferta:",
        options=["R$ 100 - R$ 500", "R$ 500 - R$ 2.000", "R$ 2.000+ (High-Ticket)"],
        index=2
    )

# Execução do Pipeline
if st.button("🚀 EXECUTAR PIPELINE COMPLETO DE INTELIGÊNCIA"):
    if not is_authenticated:
        st.error("Por favor, insira uma Chave de Licença VIP válida na barra lateral para prosseguir.")
    elif not gemini_api_key:
        st.error("Por favor, insira sua Chave Gemini API na barra lateral.")
    elif not nicho or not publico:
        st.warning("Preencha o Nicho/Produto e o Público-Alvo antes de executar.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # ETAPA 1
            status_text.markdown("⚡ **Etapa 1/4:** Processando Métricas de Oportunidade e Saturação...")
            progress_bar.progress(25)
            prompt1 = f"""
            Atue como Engenheiro Estratégico de Mercado. Analise:
            - Nicho/Produto: {nicho}
            - Público-Alvo: {publico}
            - Ticket: {ticket}
            
            Gere uma análise profunda de: TAM/SAM/SOM estimado, Nível de Saturação Atual e Oportunidades não exploradas.
            """
            res1 = chamar_gemini(gemini_api_key, prompt1)
            
            # ETAPA 2
            status_text.markdown("⚡ **Etapa 2/4:** Mapeamento de Dores, Objeções e Desejos Profundos...")
            progress_bar.progress(50)
            prompt2 = f"""
            Com base em {nicho} para {publico}:
            1. 5 Dores Urgentes e Viscerais do público.
            2. 5 Maiores Objeções ao ticket {ticket}.
            3. Desejos de Status e Transformação Final buscados.
            """
            res2 = chamar_gemini(gemini_api_key, prompt2)
            
            # ETAPA 3
            status_text.markdown("⚡ **Etapa 3/4:** Engenharia de Posicionamento e Script Comercial...")
            progress_bar.progress(75)
            prompt3 = f"""
            Gere a estratégia comercial para {nicho}:
            1. Proposta Única de Valor (PUV) Irresistível.
            2. Script de Prospecção Direct/Cold Message High-Conversion.
            3. Quebra de Objeções Principais.
            """
            res3 = chamar_gemini(gemini_api_key, prompt3)
            
            # ETAPA 4
            status_text.markdown("⚡ **Etapa 4/4:** Compilando Dossiê Executivo e Relatório em PDF...")
            progress_bar.progress(100)
            
            dossie = f"""# DOSSIÊ EXECUTIVO - DEEPMARKET AI

**Nicho:** {nicho}  
**Público-Alvo:** {publico}  
**Ticket:** {ticket}  

---

## 1. MÉTRICAS DE OPORTUNIDADE E SATURAÇÃO
{res1}

---

## 2. DOSSIÊ PSICOGRÁFICO DO CLIENTE
{res2}

---

## 3. ENGENHARIA DE POSICIONAMENTO E SCRIPT COMERCIAL
{res3}
"""
            status_text.success("✅ Pipeline executado com sucesso!")
            
            st.markdown("---")
            st.markdown(dossie)
            
            # Gerar PDF
            pdf_bytes = gerar_pdf(dossie)
            
            st.download_button(
                label="📥 BAIXAR DOSSIÊ EXECUTIVO (PDF)",
                data=pdf_bytes,
                file_name=f"Dossie_DeepMarket_{nicho.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
            
        except Exception as e:
            status_text.empty()
            st.error(f"Falha na execução do pipeline: {str(e)}")
