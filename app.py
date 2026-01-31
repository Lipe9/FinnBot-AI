import streamlit as st
import time
import google.generativeai as genai
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Erro: Chave de API não configurada. Verifique os Secrets do Streamlit.")
    st.stop()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FinnBot AI", page_icon="🏦")

# --- INICIALIZAÇÃO DE DADOS (Persistência no Navegador) ---
if 'saldo_conta' not in st.session_state:
    st.session_state.saldo_conta = 0.0
if 'saldo_cofrinho' not in st.session_state:
    st.session_state.saldo_cofrinho = 0.0
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou seu FinnBot, turbinado com IA. Como posso ajudar suas finanças hoje?"}
    ]

# --- BARRA LATERAL (Painel Financeiro) ---
with st.sidebar:
    st.title("🏦 Meu Painel")
    st.metric("Saldo em Conta", f"R$ {st.session_state.saldo_conta:,.2f}")
    st.metric("Guardado no Cofrinho 🐷", f"R$ {st.session_state.saldo_cofrinho:,.2f}")
    
    st.divider()
    
    st.subheader("Receber Saldo")
    valor_input_conta = st.number_input("Quanto deseja depositar?", min_value=0.0, step=100.0, key="add_conta")
    if st.button("Depositar na Conta"):
        st.session_state.saldo_conta += valor_input_conta
        st.success("Saldo atualizado!")
        time.sleep(1)
        st.rerun()

    st.divider()

    st.subheader("Gerenciar Cofrinho")
    valor_cofrinho = st.number_input("Valor da operação:", min_value=0.0, step=50.0, key="val_cofrinho")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Guardar 📥"):
            if valor_cofrinho <= st.session_state.saldo_conta:
                st.session_state.saldo_conta -= valor_cofrinho
                st.session_state.saldo_cofrinho += valor_cofrinho
                st.rerun()
            else:
                st.error("Saldo insuficiente.")
    with col2:
        if st.button("Resgatar 📤"):
            if valor_cofrinho <= st.session_state.saldo_cofrinho:
                st.session_state.saldo_cofrinho -= valor_cofrinho
                st.session_state.saldo_conta += valor_cofrinho
                st.rerun()
            else:
                st.error("Valor insuficiente no cofrinho.")

# --- LÓGICA DE RENDIMENTO ---
def calcular_rendimento(valor, meses):
    taxa_mensal = 0.0085  # Aproximadamente 100% do CDI
    valor_final = valor * (1 + taxa_mensal) ** meses
    lucro = valor_final - valor
    return valor_final, lucro

# --- INTERFACE DE CHAT ---
st.title("🤖 FinnBot: Assistente & Cofrinho")

# Exibir histórico de mensagens
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Entrada do usuário
if prompt := st.chat_input("Pergunte sobre saldo, rendimento ou dicas financeiras!"):
    # Adiciona mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        p_lower = prompt.lower()
        
        # 1. Verificação de Comandos Locais (Ações Rápidas)
        if "saldo" in p_lower:
            resposta = f"Seu saldo atual é de R$ {st.session_state.saldo_conta:,.2f} em conta e R$ {st.session_state.saldo_cofrinho:,.2f} no cofrinho."
        
        elif "render" in p_lower or "rendimento" in p_lower:
            nums = [float(s) for s in p_lower.replace(",", ".").split() if s.replace(".", "").isdigit()]
            if len(nums) >= 2:
                v_final, v_lucro = calcular_rendimento(nums[0], nums[1])
                resposta = (f"📈 **Projeção de Rendimento:**\n\n"
                            f"Valor final: **R$ {v_final:,.2f}**\n"
                            f"Lucro estimado: **R$ {v_lucro:,.2f}**")
            else:
                resposta = "Para calcular, informe o valor e o tempo. Ex: 'Quanto rende 1000 em 12 meses?'"
    # 2. IA Generativa com Memória de Contexto
        else:
            with st.spinner("Analisando com IA..."):
                try:
                    instrucoes_ia = (
                        f"Você é o FinnBot. Saldo conta: R$ {st.session_state.saldo_conta:.2f}. "
                        f"No cofrinho: R$ {st.session_state.saldo_cofrinho:.2f}."
                    )
                    
                    history = []
                    for m in st.session_state.messages[-5:]:
                        # Corrigindo: Gemini exige 'user' e 'model'
                        role = "user" if m["role"] == "user" else "model"
                        history.append({"role": role, "parts": [m["content"]]})
                    
                    chat = model.start_chat(history=history[:-1])
                    response = chat.send_message(f"{instrucoes_ia}\n\nPergunta: {prompt}")
                    resposta = response.text
                except Exception as e:
                    # ISSO VAI MOSTRAR O ERRO REAL NO SITE
                    st.error(f"Erro na API: {e}")
                    resposta = "Não consegui falar com meu cérebro de IA agora."
                    
                    # Criamos o histórico formatado para o Gemini
                    history = []
                    for m in st.session_state.messages[-5:]: # Pegamos as últimas 5 mensagens para dar contexto
                        role = "user" if m["role"] == "user" else "model"
                        history.append({"role": role, "parts": [m["content"]]})
                    
                    # Iniciamos o chat com memória
                    chat = model.start_chat(history=history[:-1]) # O histórico antigo
                    response = chat.send_message(f"{instrucoes_ia}\n\nPergunta atual: {prompt}")
                    resposta = response.text
                except Exception as e:
                    resposta = "Desculpe, tive um problema técnico ao processar sua pergunta. Tente novamente em instantes!"

        st.write(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})

