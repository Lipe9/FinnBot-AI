import streamlit as st
import time
import google.generativeai as genai
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FinnBot AI Pro", page_icon="🏦", layout="wide")

# --- FUNÇÃO DE CONEXÃO ---
def get_model():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except Exception:
        st.error("❌ Erro: Chave de API não encontrada.")
        st.stop()
    
    modelos = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-flash-latest']
    for nome in modelos:
        try:
            return genai.GenerativeModel(nome), nome
        except: continue
    st.stop()

# --- INICIALIZAÇÃO DE ESTADO ---
if 'saldo_conta' not in st.session_state: st.session_state.saldo_conta = 0.0
if 'saldo_cofrinho' not in st.session_state: st.session_state.saldo_cofrinho = 0.0
if 'extrato' not in st.session_state: st.session_state.extrato = []
if 'nome_meta' not in st.session_state: st.session_state.nome_meta = "Minha Meta"
if 'valor_meta' not in st.session_state: st.session_state.valor_meta = 0.0
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou seu FinnBot Pro. Pronto para gerenciar suas metas?"}]
if 'historico_conversas' not in st.session_state: st.session_state.historico_conversas = []

model, nome_conectado = get_model()

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🏦 FinnBot Dashboard")
    st.caption(f"Status: {nome_conectado}")

    # --- NOVO CHAT / LIMPAR ---
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ Novo", use_container_width=True):
            if len(st.session_state.messages) > 1:
                st.session_state.historico_conversas.append({
                    "label": f"🕒 {time.strftime('%H:%M')} - {st.session_state.messages[1]['content'][:15]}",
                    "chats": list(st.session_state.messages)
                })
            st.session_state.messages = [{"role": "assistant", "content": "Novo chat! Como posso ajudar?"}]
            st.rerun()
    with c2:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.session_state.historico_conversas = []
            st.rerun()

    with st.expander("📜 Histórico de Chats"):
        for i, conversa in enumerate(reversed(st.session_state.historico_conversas)):
            if st.button(conversa["label"], key=f"h_{i}", use_container_width=True):
                st.session_state.messages = list(conversa["chats"])
                st.rerun()

    st.divider()

    # --- FINANCEIRO ---
    st.metric("Conta Corrente", f"R$ {st.session_state.saldo_conta:,.2f}")
    st.metric("Cofrinho 🐷", f"R$ {st.session_state.saldo_cofrinho:,.2f}")

    # GRÁFICO DE COMPOSIÇÃO
    if st.session_state.saldo_conta > 0 or st.session_state.saldo_cofrinho > 0:
        df_pizza = pd.DataFrame({
            "Categoria": ["Disponível", "Guardado"],
            "Valor": [st.session_state.saldo_conta, st.session_state.saldo_cofrinho]
        })
        st.write("📊 **Composição do Patrimônio**")
        st.bar_chart(df_pizza.set_index("Categoria"))

    st.divider()
    
    # TRANSAÇÕES
    st.subheader("💳 Movimentar")
    valor_op = st.number_input("Valor (R$):", min_value=0.0, step=50.0)
    
    if st.button("💰 Depositar na Conta", use_container_width=True):
        st.session_state.saldo_conta += valor_op
        st.session_state.extrato.append(f"🟢 +R$ {valor_op:.2f} (Depósito)")
        st.rerun()

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("📥 Guardar", use_container_width=True):
            if valor_op <= st.session_state.saldo_conta:
                st.session_state.saldo_conta -= valor_op
                st.session_state.saldo_cofrinho += valor_op
                st.session_state.extrato.append(f"📥 -R$ {valor_op:.2f} (Cofrinho)")
                st.rerun()
    with col_t2:
        if st.button("📤 Resgatar", use_container_width=True):
            if valor_op <= st.session_state.saldo_cofrinho:
                st.session_state.saldo_cofrinho -= valor_op
                st.session_state.saldo_conta += valor_op
                st.session_state.extrato.append(f"📤 +R$ {valor_op:.2f} (Resgate)")
                st.rerun()

# --- ÁREA PRINCIPAL ---
col_main, col_info = st.columns([2, 1])

with col_info:
    # SEÇÃO DE METAS
    st.subheader("🎯 Metas")
    with st.expander("⚙️ Configurar Meta"):
        st.session_state.nome_meta = st.text_input("Nome da Meta:", value=st.session_state.nome_meta)
        st.session_state.valor_meta = st.number_input("Valor Alvo:", min_value=0.0, value=st.session_state.valor_meta)
    
    if st.session_state.valor_meta > 0:
        progresso = min(st.session_state.saldo_cofrinho / st.session_state.valor_meta, 1.0)
        st.write(f"**{st.session_state.nome_meta}**")
        st.progress(progresso)
        st.caption(f"{progresso*100:.1f}% concluído")
    
    st.divider()
    
    # EXTRATO
    st.subheader("📄 Extrato")
    if not st.session_state.extrato:
        st.caption("Nenhuma transação.")
    else:
        for item in reversed(st.session_state.extrato[-5:]): # Mostra as últimas 5
            st.caption(item)

    # BOTÃO ANÁLISE IA
    st.divider()
    if st.button("🧠 Pedir Análise da IA", use_container_width=True):
        analise_prompt = (f"Analise minhas finanças: Tenho R$ {st.session_state.saldo_conta} na conta e R$ {st.session_state.saldo_cofrinho} no cofrinho. "
                         f"Minha meta é '{st.session_state.nome_meta}' de R$ {st.session_state.valor_meta}. Me dê uma dica prática.")
        st.session_state.messages.append({"role": "user", "content": analise_prompt})
        st.rerun()

with col_main:
    st.title("🤖 FinnBot Assistente")
    
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Ex: Como economizar para minha meta?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analisando dados..."):
                try:
                    ctx = (f"Você é o FinnBot. Saldo: R$ {st.session_state.saldo_conta:.2f}. "
                           f"Cofrinho: R$ {st.session_state.saldo_cofrinho:.2f}. "
                           f"Meta: {st.session_state.nome_meta} (R$ {st.session_state.valor_meta:.2f}). "
                           "Seja curto, direto e use emojis.")
                    
                    hist = []
                    for m in st.session_state.messages[-6:]:
                        r = "model" if m["role"] == "assistant" else "user"
                        hist.append({"role": r, "parts": [m["content"]]})
                    
                    chat = model.start_chat(history=hist[:-1])
                    response = chat.send_message(f"{ctx}\n\nPergunta: {prompt}")
                    st.write(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except:
                    st.write("Erro na conexão. Tente novamente.")
