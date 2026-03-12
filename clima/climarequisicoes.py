# Módulos para requisições HTTP, variáveis de ambiente e manipulação de datas
import requests
import os
from dotenv import load_dotenv
from datetime import datetime


def buscar_clima(cidade):
    load_dotenv()
    API_KEY = os.getenv("API_KEY")

    # Constrói URL com parâmetros: cidade, chave API e idioma português
    link_clima_atual = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KEY}&lang=pt_br"

    # Requisita dados à API
    requisicao_atual = requests.get(link_clima_atual)
    requisicao_dic_atual = requisicao_atual.json()
    cod = requisicao_dic_atual.get("cod")

    # Tratamento de códigos de resposta HTTP
    if cod == 200:
        # Sucesso: extrai dados climáticos
        descricao_clima = requisicao_dic_atual["weather"][0]["description"]
        # Converte temperatura de Kelvin (padrão da API) para Celsius
        temperatura_clima = requisicao_dic_atual["main"]["temp"] - 273.15

        dados = {
            "cidade": cidade,
            "temperatura": f"{temperatura_clima:.1f}",
            "descricao": descricao_clima,
        }

    elif cod == "404":
        # Erro: cidade não encontrada
        dados = {
            "cidade": cidade,
            "temperatura": "N/A",
            "descricao": "Cidade não encontrada",
        }

    elif cod == 401:
        # Erro: chave API inválida ou expirada
        dados = {
            "cidade": cidade,
            "temperatura": "N/A",
            "descricao": "API KEY inválida",
        }

    elif cod == 429:
        # Erro: limite de requisições excedido
        dados = {
            "cidade": cidade,
            "temperatura": "N/A",
            "descricao": "Muitas requisições — tente novamente mais tarde",
        }

    else:
        # Erro: resposta inesperada da API
        dados = {
            "cidade": cidade,
            "temperatura": "N/A",
            "descricao": f"Erro desconhecido (cod {cod})",
        }

    return dados
