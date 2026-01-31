import streamlit as st
import datetime
import time

# --- CLASSE ORIGINAL ADAPTADA ---
class FinBot:
    def __init__(self, nome_cliente):
        self.nome_cliente = nome_cliente
        # Simulação de Base de Dados
        self.dados_cliente = {
            "saldo": 4500.00,
            "limite_credito": 12000.00,
            "gastos_mes": 1350.50
        }
        
    def _formatar_moeda(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def consultar_saldo(self):
        saldo = self._formatar_moeda(self.dados_cliente['saldo'])
        return f"Seu saldo atual em conta corrente é de **{saldo}**."

    def simular_emprestimo(self, valor, meses):
        taxa = 0.025
        if valor > self.dados_cliente['limite_credito']:
            return "⚠️ O valor solicitado está acima do seu limite pré-aprovado. Podemos analisar uma proposta personalizada no menu 'Gerente'."
        
        total_com_juros = valor * (1 + taxa * meses)
        parcela = total_com_juros / meses
        
        return (
            f"📊 **Simulação de Empréstimo**\n\n"
            f"- Valor solicitado: {self._formatar_moeda(valor)}\n"
            f"- Prazo: {meses} meses\n"
            f"- Parcela estimada: {self._formatar_moeda(parcela)}\n"
            f"- Total final: {self._formatar_moeda(total_com_juros)}\n\n"
            f"*(Nota: Taxas sujeitas a análise de crédito)*"
        )

    def explicar_produto(self, produto):
        produtos = {
            "cdb": "O CDB (Certificado de Depósito Bancário) é um investimento de renda fixa onde você empresta dinheiro ao banco em troca de juros. É seguro e conta com garantia do FGC.",
            "lci": "A LCI (Letra de Crédito Imobiliário) é isenta de Imposto de Renda para pessoas físicas e ajuda a financiar o setor imobiliário.",
            "pix": "O Pix é o sistema de pagamentos instantâneos do Banco Central, funcionando 24/7 com liquidação em segundos."
        }
        return produtos.get(produto.lower(), "Desculpe, ainda não tenho informações detalhadas sobre este produto específico.")

    def processar_mensagem(self, entrada_usuario):
        entrada_lower = entrada_usuario.lower()
        
        if "saldo" in entrada_lower or "quanto tenho" in entrada_lower:
            return self.consultar_saldo()
        
        elif "simular" in entrada_lower or "emprestimo" in entrada_lower:
            try:
                numeros = [int(s) for s in entrada_lower.split() if s.isdigit()]
                if len(numeros) >= 2:
                    valor = numeros[0] if numeros[0] > 100 else numeros[1]
                    meses = numeros[1] if numeros[0] > 100 else numeros[0]
                    return self.simular_emprestimo(valor, meses)
                else:
                    return "Para simular, preciso que você diga o valor e a quantidade de meses. Ex: 'Simular 5000 em 12 meses'."
            except:
                return "Entendi que você quer simular um empréstimo. Por favor, informe o valor e o prazo."

        elif "o que é" in entrada_lower or "explica" in entrada_lower:
            termo = entrada_lower.split()[-1].replace("?", "")
            return self.explicar_produto(termo)
            
        elif "obrigado" in entrada_lower or "tchau" in entrada_lower:
            return f"Foi um prazer ajudar, {self.nome_cliente}! Conte sempre conosco. 👋"

        else:
            return f"Entendi sua dúvida sobre '{entrada_usuario}'. Como sou um assistente focado em segurança, recomendo verificar no app ou falar com seu gerente!"

# --- INTERFACE STREAMLIT ---

st.set_page_config(page_title="FinnBot AI", page_icon="🏦")

st.title("🏦 FinnBot Assistant")
st.caption("Sua inteligência financeira personalizada")

# Inicialização do Bot e Histórico na Sessão
if "bot" not in st.session_state:
    st.session_state.bot = FinBot("Usuário")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou sua IA financeira. Como posso ajudar você hoje?"}
    ]

# Exibição do histórico de mensagens
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Entrada de Chat
if prompt := st.chat_input("Ex: Qual meu saldo? ou Simular 5000 em 12 meses"):
    # Adiciona mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Processamento da Resposta
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            time.sleep(0.6) # Simula o "typing" que você tinha no console
            resposta = st.session_state.bot.processar_mensagem(prompt)
            st.write(resposta)
            st.session_state.messages.append({"role": "assistant", "content": resposta})




