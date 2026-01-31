import streamlit as st
import time
import google.generativeai as genai

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FinnBot AI", page_icon="🏦")

# --- FUNÇÃO DE CONEXÃO AJUSTADA PARA SUA CONTA ---
def get_model():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except Exception:
        st.error("❌ Erro: Chave de API não encontrada nos Secrets.")
        st.stop()

    # Atualizado com base na SUA lista de modelos disponíveis
    modelos_para_tentar = [
        'gemini-2.5-flash',      # Prioridade 1: O mais novo e rápido
        'gemini-2.0-flash',      # Prioridade 2
        'gemini-flash-latest',   # Prioridade 3: Genérico
        'gemini-pro-latest'      # Prioridade 4
    ]

    for nome_modelo in modelos_para_tentar:
        try:
            # Tenta conectar (algumas versões exigem o prefixo models/, outras não, o SDK costuma lidar)
            model = genai.GenerativeModel(nome_modelo)
            return model, nome_modelo
        except Exception:
            continue
    
    st.error("⚠️ Não consegui conectar em nenhum modelo, mesmo com a lista atualizada.")
    st.stop()

# --- INICIALIZAÇÃO DE DADOS ---
if 'saldo_conta' not in st.session_state:
    st.session_state.saldo_conta = 0.0
if 'saldo_cofrinho' not in st.session_state:
    st.session_state.saldo_cofrinho = 0.0
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou seu FinnBot. Pergunte sobre suas finanças."}
    ]

# --- TENTA CONECTAR ---
model, nome_conectado = get_model()

# --- BARRA LATERAL ---
# with st.sidebar:
#    st.title("🏦 Meu Painel")
#    st.success(f"⚡ Conectado: {nome_conectado}") # Mostra que funcionou!
#    
#   st.metric("Saldo em Conta", f"R$ {st.session_state.saldo_conta:,.2f}")
#   st.metric("No Cofrinho 🐷", f"R$ {st.session_state.saldo_cofrinho:,.2f}")
#   
#   st.divider()
#   
#   st.subheader("Depositar")
#   valor_dep = st.number_input("Valor:", min_value=0.0, step=100.0, key="dep")
#   if st.button("Confirmar Depósito"):
#       st.session_state.saldo_conta += valor_dep
#       st.success("Saldo atualizado!")
#        time.sleep(0.5)
#       st.rerun()
#
#   st.divider()
#
#   st.subheader("Cofrinho")
#   valor_cofre = st.number_input("Operação cofrinho:", min_value=0.0, step=50.0, key="cof")
#   c1, c2 = st.columns(2)
#   with c1:
#       if st.button("Guardar 📥"):
#           if valor_cofre <= st.session_state.saldo_conta:
#               st.session_state.saldo_conta -= valor_cofre
#               st.session_state.saldo_cofrinho += valor_cofre
#               st.rerun()
#   with c2:
#       if st.button("Resgatar 📤"):
#           if valor_cofre <= st.session_state.saldo_cofrinho:
 #               st.session_state.saldo_cofrinho -= valor_cofre
  #              st.session_state.saldo_conta += valor_cofre
   #             st.rerun()

# --- CHAT ---
st.title("🤖 FinnBot: Assistente Financeiro")

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Como posso ajudar suas finanças hoje?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        # Lógica Local
        if "saldo" in prompt.lower():
            resposta = f"💰 Conta: R$ {st.session_state.saldo_conta:,.2f} | 🐷 Cofrinho: R$ {st.session_state.saldo_cofrinho:,.2f}"
        
        # Lógica IA (Gemini 2.5)
        else:
            with st.spinner(f"Processando com {nome_conectado}..."):
                try:
                    instrucoes = (
                        f"Você é o FinnBot. O usuário tem R$ {st.session_state.saldo_conta:.2f} disponível. "
                        "Responda de forma prática e motivadora."
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
                    # Fallback
                    try:
                        resposta = model.generate_content(f"{instrucoes}\n\n{prompt}").text
                    except Exception as e2:
                        st.error(f"Erro: {e2}")
                        resposta = "Estou ajustando meus circuitos. Tente novamente."

        st.write(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})

