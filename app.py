import streamlit as st
import time
import google.generativeai as genai

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FinnBot AI", page_icon="🏦", layout="centered")
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
local_css("style.css")
st.markdown('<div class="footer"><hr style="border: 0.5px solid #333; width: 80%; margin: auto; margin-bottom: 5px;">Developed by Felipe Silva.</div>', unsafe_allow_html=True)

# --- FUNÇÃO DE CONEXÃO ---
def get_model():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except Exception:
        st.error("❌ Erro: Chave de API não encontrada nos Secrets.")
        st.stop()

    modelos_para_tentar = [
        'gemini-2.5-flash', # Prioridade Gemini 2.5
        'gemini-2.0-flash',      
        'gemini-1.5-flash'
    ]

    for nome_modelo in modelos_para_tentar:
        try:
            model = genai.GenerativeModel(nome_modelo)
            return model, nome_modelo
        except Exception:
            continue
    
    st.error("⚠️ Não consegui conectar em nenhum modelo.")
    st.stop()

# --- INICIALIZAÇÃO DE DADOS ---
if 'saldo_conta' not in st.session_state:
    st.session_state.saldo_conta = 0.0
if 'saldo_cofrinho' not in st.session_state:
    st.session_state.saldo_cofrinho = 0.0
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou seu FinnBot. Como posso ajudar suas finanças?"}
    ]

model, nome_conectado = get_model()

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🏦 Meu Painel")
    st.success(f"⚡ Conectado: {nome_conectado}")
    
    st.metric("Saldo em Conta", f"R$ {st.session_state.saldo_conta:,.2f}")
    st.metric("No Cofrinho 🐷", f"R$ {st.session_state.saldo_cofrinho:,.2f}")
    
    st.divider()
    
    st.subheader("Depositar")
    valor_dep = st.number_input("Valor:", min_value=0.0, step=100.0, key="dep")
    if st.button("Confirmar Depósito"):
        st.session_state.saldo_conta += valor_dep
        st.rerun()

    st.divider()
    st.subheader("Cofrinho")
    valor_cofre = st.number_input("Operação cofrinho:", min_value=0.0, step=50.0, key="cof")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Guardar 📥"):
            if valor_cofre <= st.session_state.saldo_conta:
                st.session_state.saldo_conta -= valor_cofre
                st.session_state.saldo_cofrinho += valor_cofre
                st.rerun()
    with c2:
        if st.button("Resgatar 📤"):
            if valor_cofre <= st.session_state.saldo_cofrinho:
                st.session_state.saldo_cofrinho -= valor_cofre
                st.session_state.saldo_conta += valor_cofre
                st.rerun()

# --- CHAT PRINCIPAL ---
st.title("🤖 FinnBot: Assistente Financeiro")

# Container para as mensagens
chat_placeholder = st.container()

with chat_placeholder:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Entrada de pergunta
if prompt := st.chat_input("Como posso ajudar suas finanças hoje?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_placeholder.chat_message("user"):
        st.write(prompt)

    with chat_placeholder.chat_message("assistant"):
        if "saldo" in prompt.lower():
            resposta = f"💰 Conta: R$ {st.session_state.saldo_conta:,.2f} | 🐷 Cofrinho: R$ {st.session_state.saldo_cofrinho:,.2f}"
        else:
            with st.spinner(f"Processando com {nome_conectado}..."):
                try:
                    instrucoes = (
                        f"Você é o FinnBot. O usuário tem R$ {st.session_state.saldo_conta:.2f} disponível. "
                        "Responda de forma prática e motivadora."
                    )
                    history_gemini = []
                    for m in st.session_state.messages[-4:]:
                        role = "model" if m["role"] == "assistant" else "user"
                        history_gemini.append({"role": role, "parts": [m["content"]]})
                    
                    chat = model.start_chat(history=history_gemini[:-1])
                    response = chat.send_message(f"{instrucoes}\n\nPergunta: {prompt}")
                    resposta = response.text
                except Exception:
                    resposta = "Estou ajustando meus circuitos. Tente novamente."

        st.write(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})


