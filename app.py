import streamlit as st
import time
import google.generativeai as genai
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Erro na configuração da IA: {e}")
    st.stop()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FinnBot AI", page_icon="🏦", layout="centered")

# --- INICIALIZAÇÃO DE DADOS ---
if 'saldo_conta' not in st.session_state:
    st.session_state.saldo_conta = 0.0
if 'saldo_cofrinho' not in st.session_state:
    st.session_state.saldo_cofrinho = 0.0
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou seu FinnBot. Como posso ajudar suas finanças hoje?"}
    ]

# --- BARRA LATERAL (Painel Financeiro) ---
with st.sidebar:
    st.title("🏦 Meu Painel")
    st.metric("Saldo em Conta", f"R$ {st.session_state.saldo_conta:,.2f}")
    st.metric("No Cofrinho 🐷", f"R$ {st.session_state.saldo_cofrinho:,.2f}")
    
    st.divider()
    
    st.subheader("Depositar")
    valor_dep = st.number_input("Valor:", min_value=0.0, step=100.0, key="dep")
    if st.button("Confirmar Depósito"):
        st.session_state.saldo_conta += valor_dep
        st.success("Saldo atualizado!")
        time.sleep(0.5)
        st.rerun()

    st.divider()

    st.subheader("Cofrinho")
    valor_cofre = st.number_input("Valor da operação:", min_value=0.0, step=50.0, key="cof")
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

# --- LÓGICA DE RENDIMENTO ---
def calcular_rendimento(valor, meses):
    taxa = 0.0085 # 0.85% ao mês
    v_final = valor * (1 + taxa) ** meses
    return v_final, v_final - valor

# --- INTERFACE DE CHAT ---
st.title("🤖 FinnBot: Seu Assistente")

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Pergunte qualquer coisa!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        p_lower = prompt.lower()
        
        # 1. Respostas Rápidas (Lógica Local)
        if "saldo" in p_lower:
            resposta = f"Você tem R$ {st.session_state.saldo_conta:,.2f} na conta e R$ {st.session_state.saldo_cofrinho:,.2f} guardados."
        
        elif "render" in p_lower or "rendimento" in p_lower:
            nums = [float(s) for s in p_lower.replace(",", ".").split() if s.replace(".", "").isdigit()]
            if len(nums) >= 2:
                vf, lucro = calcular_rendimento(nums[0], nums[1])
                resposta = f"📈 Projeção: R$ {vf:,.2f} (Lucro de R$ {lucro:,.2f} em {nums[1]} meses)."
            else:
                resposta = "Informe o valor e os meses. Ex: 'Quanto rende 500 em 10 meses?'"
        
        # 2. Inteligência Artificial (Gemini)
        else:
            with st.spinner("Pensando..."):
                try:
                    # Configura as instruções de personalidade
                    contexto = (
                        f"Você é o FinnBot, um assistente financeiro amigável. "
                        f"O usuário tem R$ {st.session_state.saldo_conta:.2f} disponível. "
                        "Dê dicas curtas e úteis."
                    )
                    
                    # Prepara o histórico para o formato do Gemini
                    historico_ia = []
                    for m in st.session_state.messages[-6:]:
                        role_ia = "user" if m["role"] == "user" else "model"
                        historico_ia.append({"role": role_ia, "parts": [m["content"]]})
                    
                    # Inicia o chat com a memória
                    chat_session = model.start_chat(history=historico_ia[:-1])
                    response = chat_session.send_message(f"{contexto}\n\nPergunta: {prompt}")
                    resposta = response.text
                except Exception as e:
                    st.error(f"Erro na IA: {e}")
                    resposta = "Desculpe, tive um soluço técnico. Pode repetir?"

        st.write(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
