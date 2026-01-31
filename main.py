import datetime

class FinBot:
    def __init__(self, nome_cliente):
        self.nome_cliente = nome_cliente
        # Simulação de Base de Dados
        self.dados_cliente = {
            "saldo": 4500.00,
            "limite_credito": 12000.00,
            "gastos_mes": 1350.50
        }
        # Persistência de Contexto (Memória da conversa)
        self.historico_conversa = []
        
    def _adicionar_ao_historico(self, autor, mensagem):
        timestamp = datetime.datetime.now().strftime("%H:%M")
        self.historico_conversa.append(f"[{timestamp}] {autor}: {mensagem}")

    def _formatar_moeda(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # --- Funcionalidades Específicas (Hard Skills: Python + Lógica) ---
    
    def consultar_saldo(self):
        saldo = self._formatar_moeda(self.dados_cliente['saldo'])
        return f"Seu saldo atual em conta corrente é de **{saldo}**."

    def simular_emprestimo(self, valor, meses):
        # Regra de negócio: Juros simples de 2.5% ao mês para exemplo
        taxa = 0.025
        if valor > self.dados_cliente['limite_credito']:
            return "⚠️ O valor solicitado está acima do seu limite pré-aprovado. Podemos analisar uma proposta personalizada no menu 'Gerente'."
        
        total_com_juros = valor * (1 + taxa * meses)
        parcela = total_com_juros / meses
        
        return (
            f"📊 **Simulação de Empréstimo**\n"
            f"- Valor solicitado: {self._formatar_moeda(valor)}\n"
            f"- Prazo: {meses} meses\n"
            f"- Parcela estimada: {self._formatar_moeda(parcela)}\n"
            f"- Total final: {self._formatar_moeda(total_com_juros)}\n"
            f"*(Nota: Taxas sujeitas a análise de crédito)*"
        )

    def explicar_produto(self, produto):
        # Base de Conhecimento (Knowledge Base)
        produtos = {
            "cdb": "O CDB (Certificado de Depósito Bancário) é um investimento de renda fixa onde você empresta dinheiro ao banco em troca de juros. É seguro e conta com garantia do FGC.",
            "lci": "A LCI (Letra de Crédito Imobiliário) é isenta de Imposto de Renda para pessoas físicas e ajuda a financiar o setor imobiliário.",
            "pix": "O Pix é o sistema de pagamentos instantâneos do Banco Central, funcionando 24/7 com liquidação em segundos."
        }
        return produtos.get(produto.lower(), "Desculpe, ainda não tenho informações detalhadas sobre este produto específico.")

    # --- Motor de IA Generativa (Simulação da Lógica de Intenção) ---
    
    def processar_mensagem(self, entrada_usuario):
        self._adicionar_ao_historico("Usuário", entrada_usuario)
        entrada_lower = entrada_usuario.lower()
        resposta = ""

        # Detecção de Intenção (NLU Simplificado)
        if "saldo" in entrada_lower or "quanto tenho" in entrada_lower:
            resposta = self.consultar_saldo()
        
        elif "simular" in entrada_lower or "emprestimo" in entrada_lower:
            # Tenta extrair números (exemplo simplificado de extração de entidades)
            try:
                numeros = [int(s) for s in entrada_lower.split() if s.isdigit()]
                if len(numeros) >= 2:
                    valor = numeros[0] if numeros[0] > 100 else numeros[1] # Heurística simples
                    meses = numeros[1] if numeros[0] > 100 else numeros[0]
                    resposta = self.simular_emprestimo(valor, meses)
                else:
                    resposta = "Para simular, preciso que você diga o valor e a quantidade de meses. Ex: 'Simular 5000 em 12 meses'."
            except:
                resposta = "Entendi que você quer simular um empréstimo. Por favor, informe o valor e o prazo."

        elif "o que é" in entrada_lower or "explica" in entrada_lower:
            termo = entrada_lower.split()[-1] # Pega a última palavra (ex: "o que é CDB")
            resposta = self.explicar_produto(termo)
            
        elif "obrigado" in entrada_lower or "tchau" in entrada_lower:
            resposta = f"Foi um prazer ajudar, {self.nome_cliente}! Conte sempre conosco para sua saúde financeira. 👋"

        else:
            # Fallback para IA Generativa (Aqui entraria a chamada da API OpenAI)
            resposta = (
                f"Entendi sua dúvida sobre '{entrada_usuario}'. "
                "Como sou um assistente focado em segurança, recomendo verificar essa informação específica "
                "no seu app ou falar com seu gerente. Posso ajudar com saldos, simulações ou explicar termos financeiros!"
            )

        self._adicionar_ao_historico("Bot", resposta)
        return resposta

# --- Interface de Execução (Console) ---

def iniciar_experiencia():
    print("--- 🏦 Bem-vindo ao NeoBank Assistant ---")
    print("Sou sua IA financeira pessoal. Segurança e clareza são nossa prioridade.")
    nome = input("Como gostaria de ser chamado? ")
    
    bot = FinBot(nome)
    print(f"\nOlá, {nome}! Posso ajudar com:\n1. Consultar Saldo\n2. Simular Empréstimos (Ex: 'Simular 1000 em 10x')\n3. Tirar dúvidas (Ex: 'O que é CDB?')\n(Digite 'sair' para encerrar)\n")
    
    while True:
        msg = input(f"{nome}: ")
        if msg.lower() in ["sair", "exit"]:
            print("Encerrando sessão segura...")
            break
        
        # Simulação de "typing" para UX
        import time
        print("Bot está digitando...", end="\r")
        time.sleep(0.8) 
        
        resposta = bot.processar_mensagem(msg)
        print(f"🤖 Bot: {resposta}\n")
        print("-" * 40)

if __name__ == "__main__":
    iniciar_experiencia()
