# PROJETO PREMIADO!
# 1º lugar no desafio "50 Dias de Código", realizado em parceria com a Rocketseat.

# Rotina Inteligente - Agenda com Clima, IA e Notificações

**Projeto desenvolvido para auxilio de rotina**

Aplicativo desktop para organização de rotina com login, cadastro de tarefas, consulta de clima em tempo real, notificações locais e assistente de IA focado em produtividade.

https://github.com/user-attachments/assets/10696910-66f4-4c79-b97f-8ab116ab8502

---

## Sobre o Projeto

O **Rotina Inteligente** é a evolução de um projeto prático para fechamento da jornada do desafio. A aplicação resolve um problema real: centralizar planejamento diário, contexto de clima e apoio de IA em uma interface única.

### Objetivo

Entregar uma aplicação funcional, clara e executável que ajude no planejamento diário com:

- Gestão de tarefas (CRUD)
- Clima atual por cidade
- Notificações de lembrete
- Assistente IA contextual por atividade

---

## Funcionalidades

### Funcionalidades Principais

1. **Login e contexto inicial**
- Validação de usuário/senha
- Captura da cidade no login para uso no dashboard

2. **Dashboard de tarefas**
- Listagem de tarefas em cards
- Busca/filtro por atividade, descrição e status
- Painel lateral com detalhes da tarefa selecionada
- Atualização de clima com botão de refresh

3. **CRUD completo de tarefas**
- Criar tarefa com atividade, hora, status e descrição
- Editar tarefa existente
- Excluir tarefa com confirmação
- Persistência local em SQLite

4. **Assistente IA para produtividade**
- Seleção de atividade base
- Chat com respostas práticas focadas na atividade selecionada
- Integração com API da Groq (modelo Llama)

5. **Notificações locais no Windows**
- Agendamento automático de lembretes
- Antecedência configurável (15, 30 ou 60 minutos)
- Notificações nativas usando `winotify`

### Extras Implementados

- Interface gráfica moderna com `CustomTkinter`
- Navegação entre telas (Dashboard, Nova Tarefa, Assistente IA)
- Validação de hora no formato `HH:MM`
- Tratamento de erros de API (clima e IA)
- Código organizado em módulos por responsabilidade

---

## Tecnologias Utilizadas

| Tecnologia | Uso |
|------------|-----|
| Python 3.10+ | Linguagem principal |
| CustomTkinter | Interface gráfica desktop |
| SQLite3 | Persistência local de tarefas |
| Requests | Requisições HTTP (OpenWeatherMap) |
| python-dotenv | Variáveis de ambiente |
| Groq SDK | Chat IA para assistente |
| Winotify | Notificações no Windows |

---

## Estrutura do Projeto

```text
app.py
interface/Main.py                  # Interface principal e navegação
login/regras_login.py              # Regras de autenticação
database/regrasDados.py            # CRUD e banco SQLite
clima/climarequisicoes.py          # Integração com OpenWeatherMap
chat_ai/definicoeschat.py          # Integração com Groq
notificacao/notificacao.py         # Motor de notificações
calendario_climatico/calendario_dia.py
```

---

## Instalacao

### Pré-requisitos

- Python 3.10 ou superior
- Sistema operacional Windows (para notificações com `winotify`)
- Chave de API da OpenWeatherMap
- Chave de API da Groq

### Passo a Passo

1. **Clone o repositório**

```bash
git clone https://github.com/carlosmanoelrsdev/50-dias-de-codigo
cd "Desafio semanal/Desafio semana 6/Rotina Inteligente"
```

2. **Crie e ative o ambiente virtual**

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure variáveis de ambiente no arquivo `.env`**

```env
API_KEY=sua_chave_openweathermap
GROQ_API_KEY=sua_chave_groq
```

---

## Como Executar

```bash
python app.py
```

### Fluxo de uso

1. Faça login (`admin` / `1234`) e informe uma cidade.
2. No dashboard, veja tarefas e clima atual.
3. Cadastre tarefas na aba **Nova Tarefa**.
4. Abra **Assistente IA**, selecione uma atividade e converse.
5. Receba lembretes locais conforme horário das tarefas.

---

## Arquitetura e Destaques Técnicos

- **Apresentação**: `interface/Main.py` com classes de tela e componentes CustomTkinter.
- **Dados**: `database/regrasDados.py` com funções de persistência SQLite.
- **Serviços externos**:
	- `clima/climarequisicoes.py` para OpenWeatherMap.
	- `chat_ai/definicoeschat.py` para Groq.
- **Automação local**: `notificacao/notificacao.py` com thread em background e timers.

Pontos de destaque:

- Separação modular por domínio
- CRUD completo com validações
- Integração de múltiplos serviços externos
- UX com navegação simples e feedback visual

---

## Melhorias Futuras

- Sistema de cadastro real de usuários
- Testes automatizados para serviços e regras de negócio
- Exportação/importação de tarefas
- Relatórios de produtividade

---

## Autor

**Carlos Manoel**  
Contato: Carlosmanoeldev@outlook.com

