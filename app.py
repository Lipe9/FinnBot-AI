import streamlit as st
import time

# --- CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="FinnBot Cofrinho", page_icon="🏦")

# --- INICIALIZAÇÃO DE DADOS (Persistência no Navegador) ---
if 'saldo_conta' not in st.session_state:
    st.session_state.saldo_conta = 0.0
if 'saldo_cofrinho' not in st.session_state:
    st.session_state.saldo_cofrinho = 0.0
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou seu FinBot. Vamos organizar suas economias hoje?"}]

# --- BARRA LATERAL (UX: Resumo Financeiro) ---
# --- BARRA LATERAL (UX: Resumo Financeiro) ---
with st.sidebar:
    st.title("🏦 Meu Painel")
    st.metric("Saldo em Conta", f"R$ {st.session_state.saldo_conta:,.2f}")
    st.metric("Guardado no Cofrinho 🐷", f"R$ {st.session_state.saldo_cofrinho:,.2f}")
    
    st.divider()
    
    # --- NOVO: ADICIONAR SALDO À CONTA ---
    st.subheader("Receber Saldo")
    valor_input_conta = st.number_input("Quanto deseja depositar na conta?", min_value=0.0, step=100.0, key="add_conta")
    if st.button("Depositar na Conta"):
        st.session_state.saldo_conta += valor_input_conta
        st.success(f"R$ {valor_input_conta:,.2f} adicionados à conta!")
        time.sleep(1) # Pausa curta para o usuário ler a mensagem
        st.rerun()

    st.divider()

    # --- AJUSTAR COFRINHO (GUARDAR) ---
    st.subheader("Gerenciar Cofrinho")
    valor_cofrinho = st.number_input("Valor da operação (Cofrinho):", min_value=0.0, step=50.0, key="val_cofrinho")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Guardar 📥"):
            if valor_cofrinho <= st.session_state.saldo_conta:
                st.session_state.saldo_conta -= valor_cofrinho
                st.session_state.saldo_cofrinho += valor_cofrinho
                st.success("Guardado!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Saldo insuficiente.")

    with col2:
        # --- NOVO: RESGATAR DO COFRINHO ---
        if st.button("Resgatar 📤"):
            if valor_cofrinho <= st.session_state.saldo_cofrinho:
                st.session_state.saldo_cofrinho -= valor_cofrinho
                st.session_state.saldo_conta += valor_cofrinho
                st.success("Resgatado!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Não há esse valor no cofrinho.")

# --- LÓGICA DE RENDIMENTO ---
def calcular_rendimento(valor, meses):
    taxa_mensal = 0.0085
    valor_final = valor * (1 + taxa_mensal) ** meses
    lucro = valor_final - valor
    return valor_final, lucro
# --- INTERFACE DE CHAT ---
st.title("🤖 FinnBot: Assistente & Cofrinho")

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ex: 'Quanto vai render 1000 em 12 meses?'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        p_lower = prompt.lower()

        if "render" in p_lower or "rendimento" in p_lower:
            numeros = [float(s) for s in p_lower.replace(",", ".").split() if s.replace(".", "").isdigit()]
            
            if len(numeros) >= 2:
                valor_sim = numeros[0]
                meses_sim = int(numeros[1])
                v_final, v_lucro = calcular_rendimento(valor_sim, meses_sim)
                
                resposta = (f"📈 **Projeção de Rendimento (CDB 100% CDI):**\n\n"
                            f"Se você guardar **R$ {valor_sim:,.2f}** por **{meses_sim} meses**:\n"
                            f"- Você terá um total de: **R$ {v_final:,.2f}**\n"
                            f"- Seu dinheiro rendeu: **R$ {v_lucro:,.2f}**")
            else:
                resposta = "Para calcular o rendimento, diga o valor e o tempo. Ex: 'Quanto rende 500 em 6 meses?'"
        
        elif "saldo" in p_lower:
            resposta = f"Você tem R$ {st.session_state.saldo_conta:,.2f} na conta e R$ {st.session_state.saldo_cofrinho:,.2f} no cofrinho."
        
        else:
            resposta = "Posso te ajudar a calcular rendimentos ou gerenciar seu cofrinho na barra lateral!"

        st.write(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})


