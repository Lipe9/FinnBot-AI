import streamlit as st
import time
import google.generativeai as genai

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FinnBot AI", page_icon="🏦")
def get_model():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except Exception:
        st.error("❌ Erro: Chave de API não encontrada nos Secrets.")
        st.stop()
    modelos_para_tentar = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-001',
        'gemini-1.5-flash-latest',
        'gemini-pro'
    ]

    for nome_modelo in modelos_para_tentar:
        try:
            model = genai.GenerativeModel(nome_modelo)
            # Teste rápido para ver se conecta (gera 1 token)
            model.generate_content("Oi")
            return model, nome_modelo
        except Exception:
            continue # Se falhar, tenta o próximo da lista
    
    # Se chegou aqui, nenhum funcionou. Vamos listar o que existe.
    st.error("⚠️ Nenhum modelo padrão funcionou. Listando modelos disponíveis para sua chave:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                st.code(m.name) # Mostra o nome correto na tela
    except Exception as e:
        st.error(f"Erro fatal ao listar modelos: {e}")
    st.stop()

# --- INICIALIZAÇÃO DE DADOS ---
if 'saldo_conta' not in st.session_state:
    st.session_state.saldo_conta = 0.0
if 'saldo_cofrinho' not in st.session_state:
    st.session_state.saldo_cofrinho = 0.0
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou seu FinnBot. Como posso ajudar suas finanças hoje?"}
    ]

# --- TENTA CONECTAR AO INICIAR ---
model, nome_conectado = get_model()

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🏦 Meu Painel")
    # Pequeno indicador de qual modelo conectou (para debug)
    st.caption(f"🟢 Conectado via: {nome_conectado}")
    
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

# --- CHAT ---
st.title("🤖 FinnBot: Seu Assistente")

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Pergunte sobre seus investimentos..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        # Lógica Local (Saldo)
        if "saldo" in prompt.lower():
            resposta = f"💰 Conta: R$ {st.session_state.saldo_conta:,.2f} | 🐷 Cofrinho: R$ {st.session_state.saldo_cofrinho:,.2f}"
        
        # Lógica IA (Gemini)
        else:
            with st.spinner("Analisando..."):
                try:
                    instrucoes = (
                        f"Você é o FinnBot. O usuário tem R$ {st.session_state.saldo_conta:.2f}. "
                        "Responda de forma breve e direta."
                    )
                    
                    # Prepara histórico (convertendo assistant -> model)
                    history_gemini = []
                    for m in st.session_state.messages[-4:]:
                        role = "model" if m["role"] == "assistant" else "user"
                        history_gemini.append({"role": role, "parts": [m["content"]]})
                    
                    # Tenta chat com memória
                    chat = model.start_chat(history=history_gemini[:-1])
                    response = chat.send_message(f"{instrucoes}\n\nPergunta: {prompt}")
                    resposta = response.text
                    
                except Exception as e:
                    # Fallback para resposta sem memória se der erro
                    try:
                        resposta = model.generate_content(f"{instrucoes}\n\n{prompt}").text
                    except Exception as e2:
                        st.error(f"Erro final: {e2}")
                        resposta = "Não consegui responder agora."

        st.write(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
