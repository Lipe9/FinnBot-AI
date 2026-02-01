import streamlit as st
import time
import google.generativeai as genai

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FinnBot AI", page_icon="🏦", layout="centered")

# --- FUNÇÃO DE CONEXÃO ---
def get_model():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except Exception:
        st.error("❌ Erro: Chave de API não encontrada nos Secrets do Streamlit.")
        st.stop()

    # Lista de modelos para tentativa de conexão
    modelos_para_tentar = [
        'gemini-2.0-flash',      
        'gemini-1.5-flash',   
        'gemini-1.5-pro'
    ]

    for nome_modelo in modelos_para_tentar:
        try:
            model = genai.GenerativeModel(nome_modelo)
            # Teste rápido para ver se o modelo responde
            return model, nome_modelo
        except Exception:
            continue
    
    st.error("⚠️ Não consegui conectar em nenhum modelo. Verifique sua cota ou chave.")
    st.stop()

# --- INICIALIZAÇÃO DE DADOS (SESSION STATE) ---
if 'saldo_conta' not in st.session_state:
    st.session_state.saldo_conta = 0.0
if 'saldo_cofrinho' not in st.session_state:
    st.session_state.saldo_cofrinho = 0.0
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou seu FinnBot. Pergunte sobre suas finanças ou peça dicas de economia!"}
    ]

# --- TENTA CONECTAR AO MODELO ---
model, nome_conectado = get_model()

# --- BARRA LATERAL (OPCIONAL/ATIVADA) ---
with st.sidebar:
    st.title("🏦 Meu Painel")
    st.info(f"Modelo: {nome_conectado}")
    
    st.metric("Saldo em Conta", f"R$ {st.session_state.saldo_conta:,.2f}")
    st.metric("No Cofrinho 🐷", f"R$ {st.session_state.saldo_cofrinho:,.2f}")
    
    st.divider()
    
    st.subheader("Depositar")
    valor_dep = st.number_input("Valor para depositar:", min_value=0.0, step=10.0, key="dep")
    if st.button("Confirmar Depósito"):
        st.session_state.saldo_conta += valor_dep
        st.success("Saldo atualizado!")
        time.sleep(1)
        st.rerun()

    st.divider()

    st.subheader("Cofrinho")
    valor_cofre = st.number_input("Valor da operação:", min_value=0.0, step=10.0, key="cof")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Guardar 📥"):
            if valor_cofre <= st.session_state.saldo_conta:
                st.session_state.saldo_conta -= valor_cofre
                st.session_state.saldo_cofrinho += valor_cofre
                st.rerun()
            else:
                st.error("Saldo insuficiente!")
    with c2:
        if st.button("Resgatar 📤"):
            if valor_cofre <= st.session_state.saldo_cofrinho:
                st.session_state.saldo_cofrinho -= valor_cofre
                st.session_state.saldo_conta += valor_cofre
                st.rerun()
            else:
                st.error("Cofrinho vazio!")

# --- CORPO PRINCIPAL (CHAT) ---
st.title("🤖 FinnBot: Assistente Financeiro")

# Exibe o histórico de mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Entrada do usuário
if prompt := st.chat_input("Como posso ajudar suas finanças hoje?"):
    # Adiciona mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Gera resposta do Assistente
    with st.chat_message("assistant"):
        # Lógica Rápida Local (Saldo)
        if "saldo" in prompt.lower():
            resposta = f"Seu saldo atual é:\n\n💰 **Conta:** R$ {st.session_state.saldo_conta:,.2f}\n🐷 **Cofrinho:** R$ {st.session_state.saldo_cofrinho:,.2f}"
        
        # Lógica IA
        else:
            with st.spinner("Pensando..."):
                try:
                    instrucoes = (
                        f"Você é o FinnBot, um assistente financeiro amigável. "
                        f"O usuário tem R$ {st.session_state.saldo_conta:.2f} na conta e "
                        f"R$ {st.session_state.saldo_cofrinho:.2f} guardados no cofrinho. "
                        "Seja objetivo, use emojis e motive o usuário a economizar."
                    )
                    
                    # Formata histórico para o padrão do Gemini
                    history_gemini = []
                    for m in st.session_state.messages[-6:]: # Pega as últimas 6 mensagens
                        role = "model" if m["role"] == "assistant" else "user"
                        history_gemini.append({"role": role, "parts": [m["content"]]})
                    
                    chat = model.start_chat(history=history_gemini[:-1])
                    response = chat.send_message(f"{instrucoes}\n\nPergunta do usuário: {prompt}")
                    resposta = response.text
                    
                except Exception as e:
                    # Fallback caso o chat com histórico falhe
                    try:
                        fallback_resp = model.generate_content(f"{instrucoes}\n\n{prompt}")
                        resposta = fallback_resp.text
                    except Exception as e2:
                        resposta = "Ops, tive um probleminha técnico. Pode repetir?"
        
        st.write(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})

# --- RODAPÉ ---
st.write("---")
st.caption("Developed by Felipe Silva.")
