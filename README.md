# 🏦 FinBot AI: Assistente Financeiro Inteligente

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange)
![Status](https://img.shields.io/badge/Status-Funcional-brightgreen)

O **FinBot** é uma aplicação web de inteligência artificial voltada para o setor de finanças pessoais. Ele une a precisão de um painel de controle bancário com a flexibilidade da IA Generativa (Google Gemini) para oferecer uma experiência de autoatendimento fluida, educativa e segura.

## 🎯 Objetivo
Democratizar o entendimento financeiro. O FinBot preenche a lacuna entre planilhas complexas e o usuário final, utilizando uma interface visual intuitiva e um chat inteligente para fornecer suporte, cálculos de rendimento e educação financeira em tempo real.

## 🚀 Funcionalidades Principais

### 🖥️ Interface Interativa (Streamlit)
- **Painel Financeiro (Sidebar):** Controle visual de saldo em conta corrente e "Cofrinho".
- **Gestão de Ativos:** Botões rápidos para depositar, guardar dinheiro no cofrinho ou resgatar valores.
- **Feedback Visual:** Indicadores de sucesso e atualizações de saldo em tempo real.

### 🤖 Inteligência Híbrida
- **Lógica Determinística:** Cálculos exatos para transações (saques, depósitos) e projeções matemáticas de juros compostos.
- **IA Generativa (Gemini 1.5/2.5):** Um "cérebro" treinado com contexto financeiro para responder dúvidas como "Como juntar 3 mil reais?" ou explicar termos como CDB e LCI.
- **Memória de Contexto:** O bot "lembra" do saldo atual do usuário durante a conversa para dar conselhos personalizados.

### 🛡️ UX & Segurança
- **Validação de Erros:** Impede saques maiores que o saldo ou entradas inválidas.
- **Conexão Blindada:** Sistema de reconexão automática que alterna entre modelos de IA (Flash/Pro) para garantir que o chat nunca fique fora do ar.

## 🛠️ Tecnologias Utilizadas

* **[Python 3.x](https://www.python.org/):** Linguagem base para toda a lógica de backend.
* **[Streamlit](https://streamlit.io/):** Framework para criação da interface web interativa e responsiva.
* **[Google Generative AI](https://ai.google.dev/):** Integração com modelos LLM (Gemini 1.5 Flash / 2.5) para processamento de linguagem natural.
* **Session State:** Gerenciamento de persistência de dados (saldo e histórico de chat) durante a sessão do usuário.

## 📂 Estrutura do Projeto

```text
📁 finbot/
│
├── app.py                # Código principal (Frontend + Backend + Lógica IA)
├── requirements.txt      # Dependências (streamlit, google-generativeai)
├── .streamlit/
│   └── secrets.toml      # (Local) Onde fica a API Key do Google
└── README.md             # Documentação do projeto
