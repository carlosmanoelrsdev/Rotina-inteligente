import os
from typing import List, Dict

from groq import Groq
from dotenv import load_dotenv


class ChatAtividadesService:
    # Servico de chat para assistencia em atividades usando Groq API com Llama

    def __init__(self, atividade_base: str):
        # Garante que a chave do arquivo .env tenha prioridade sobre variaveis globais.
        load_dotenv(override=True)
        self.atividade_base = (atividade_base or "").strip()
        self.historico: List[Dict[str, str]] = []

        # Inicializa cliente Groq
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise ValueError("Configure GROQ_API_KEY no .env para ativar o chat.")

        self.client = Groq(api_key=api_key)

    def mensagem_inicial(self) -> str:
        # Retorna mensagem de boas-vindas com a atividade selecionada
        atividade = self.atividade_base or "sua atividade"
        return (
            "Oi, eu sou o chat de atividades. "
            f"Vou te ajudar com foco em '{atividade}'. "
            "Posso sugerir planejamento, passos práticos e revisão."
        )

    def enviar_mensagem(self, mensagem_usuario: str) -> str:
        # Valida mensagem do usuario
        texto = (mensagem_usuario or "").strip()
        if not texto:
            return "Digite uma mensagem para eu te ajudar na atividade."

        if not self.atividade_base:
            return "Selecione uma atividade base antes de conversar."

        # Define regras de comportamento do assistente
        prompt_sistema = (
            "Você é um assistente focado somente em atividades pessoais, estudos e produtividade. "
            "Regras obrigatórias: "
            "1) Responda apenas assuntos relacionados a atividade base do usuário. "
            "2) Recuse qualquer tema sensível, perigoso, ilegal, sexual, ódio ou violência. "
            "3) Respostas objetivas, práticas e curtas em português do Brasil."
        )

        try:
            # Chamada para a API da Groq
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {
                        "role": "user",
                        "content": (
                            f"Atividade base: {self.atividade_base}\n"
                            f"Mensagem: {texto}"
                        ),
                    },
                ],
                temperature=0.7,
                max_tokens=1024,
            )

            # Extrai resposta do modelo
            resposta = completion.choices[0].message.content.strip()

            if not resposta:
                return "Não consegui gerar resposta agora. Tente novamente."

            # Armazena no historico e retorna
            self.historico.append({"usuario": texto, "assistente": resposta})
            return resposta

        except Exception as e:
            # Tratamento de erros da API Groq
            erro_str = str(e).lower()

            if "authentication" in erro_str or "invalid api key" in erro_str:
                return "Chave Groq inválida ou sem permissão. Verifique GROQ_API_KEY no .env."
            elif "rate limit" in erro_str or "quota" in erro_str:
                return "Limite de uso da Groq atingido. Tente novamente mais tarde."
            elif "timeout" in erro_str:
                return "Tempo de resposta da Groq excedido. Tente novamente."
            elif "connection" in erro_str or "network" in erro_str:
                return "Sem conexão com internet para acessar Groq."
            else:
                return f"Erro ao conectar com o chat: {str(e)}"
