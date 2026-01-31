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
        st.error("❌ Erro: Chave de API não encontrada nos Secrets.")
        st.stop()
    
    # Modelos disponíveis na sua conta (conforme lista anterior)
    modelos = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-flash-latest']
    for nome in modelos:
        try:
            m = genai.GenerativeModel(nome)
            # Teste simples de conexão
            return m, nome
        except: continue
    st.stop()

# --- INICIALIZAÇÃO DE ESTADO (Session State) ---
if 'saldo_conta' not in st.session_state: st.session_state.saldo_conta = 0.0
if 'saldo_cofrinho' not in st.session_state: st.session_state.saldo_cofrinho = 0.0
if 'extrato' not in st.session_state: st.session_state.extrato = []
if 'nome_meta' not in st.session_state: st.session_state.nome_meta = "Minha Meta"
if 'valor_meta' not in st.session_state: st.session_state.valor_meta = 0.0
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou seu FinnBot Pro. Vamos organizar suas finanças?"}]
if 'historico_conversas' not in st.session_state: st.session_state.historico_conversas = []

model, nome_conectado = get_model()

# --- BARRA LATERAL (Sidebar) ---
with st.sidebar:
    st.title("🏦 FinnBot Dashboard")
    st.caption(f"Status: {nome_conectado}")

    # --- NOVO CHAT / LIMPAR ---
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ Novo Chat", use_container_width=True):
            if len(st.session_state.messages) > 1:
                st.session_state.historico_conversas.append({
                    "label": f"🕒 {time.strftime('%H:%M')} - {st.session_state.messages[1]['content'][:15]}...",
                    "chats": list(st.session_state.messages)
                })
            st.session_state.messages = [{"role": "assistant", "content": "Novo chat iniciado! Como posso ajudar?"}]
            st.rerun()
    with c2:
        if st.button("🗑️ Limpar Hist.", use_container_width=True):
            st.session_state.historico_conversas = []
            st.rerun()

    with st.expander("📜 Conversas Anteriores"):
        for i, conversa in enumerate(reversed(st.session_state.historico_conversas)):
            if st.button(conversa["label"], key=f"h_{i}", use_container_width=True):
                st.session_state.messages = list(conversa["chats"])
                st.rerun()

    st.divider()

    # --- FINANCEIRO ---
    st.metric("Conta Corrente", f"R$ {st.session_state.saldo_conta:,.2f}")
    st.metric("Cofrinho 🐷", f"R$ {st.session_state.saldo_cofrinho:,.2f}")

    # Gráfico de Barras de Composição
    if st.session_state.saldo_conta > 0 or st.session_state.saldo_cofrinho > 0:
        df_pizza = pd.DataFrame({
            "Categoria": ["Disponível", "Guardado"],
            "Valor": [st.session_state.saldo_conta, st.session_state.saldo_cofrinho]
        })
        st.write("📊 **Distribuição**")
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
                st.session_state.extrato.append(f"📥 -R$ {valor_op:.2f} (Para Cofrinho)")
                st.rerun()
            else: st.error("Saldo insuficiente")
    with col_t2:
        if st.button("📤 Resgatar", use_container_width=True):
            if valor_op <= st.session_state.saldo_cofrinho:
                st.session_state.saldo_cofrinho -= valor_op
                st.session_state.saldo_conta += valor_op
                st.session_state.extrato.append(f"📤 +R$ {valor_op:.2f} (Do Cofrinho)")
                st.rerun()
            else: st.error("Cofrinho vazio")

# --- ÁREA PRINCIPAL ---
col_main, col_info = st.columns([2, 1])

with col_info:
    # SEÇÃO DE METAS
    st.subheader("🎯 Metas")
    with st.expander("⚙️ Configurar Meta"):
        st.session_state.nome_meta = st.text_input("
