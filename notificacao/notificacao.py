import sys
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time
from winotify import Notification, audio

# Adiciona o diretório pai ao caminho de busca
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.regrasDados import listar_tarefas

# Configurações
TEMPO_ANTECEDENCIA_MINUTOS = 15  # Tempo padrão inicial de 15 minutos
notificacoes_agendadas = {}


def definir_tempo_antecedencia(minutos):
    """Permite alterar o tempo de antecedência das notificações"""
    global TEMPO_ANTECEDENCIA_MINUTOS
    TEMPO_ANTECEDENCIA_MINUTOS = minutos


def obter_tempo_antecedencia():
    """Retorna o tempo atual de antecedência em minutos"""
    return TEMPO_ANTECEDENCIA_MINUTOS


def enviar_notificacao(titulo, mensagem):
    """Envia uma notificação usando winotify"""
    try:
        notificacao = Notification(
            app_id="Rotina inteligente", title=titulo, msg=mensagem, duration="short"
        )
        notificacao.set_audio(audio.LoopingAlarm4, loop=False)
        notificacao.show()
    except Exception:
        pass


def agendar_notificacoes():
    """Verifica tarefas e agenda notificações com base no tempo de antecedência configurado"""
    global notificacoes_agendadas

    try:
        tarefas = listar_tarefas()
    except Exception:
        return

    if not tarefas:
        return

    agora = datetime.now()

    for tarefa in tarefas:
        if not tarefa.get("hora"):
            continue

        try:
            tarefa_id = tarefa.get("id")
            hora_tarefa = datetime.strptime(tarefa["hora"], "%H:%M").time()
            horario_tarefa = datetime.combine(agora.date(), hora_tarefa)

            # Se a tarefa já passou hoje, agenda para amanhã
            if horario_tarefa <= agora:
                horario_tarefa += timedelta(days=1)

            # Calcula o tempo de antecedência configurado
            tempo_notificacao = horario_tarefa - timedelta(
                minutes=TEMPO_ANTECEDENCIA_MINUTOS
            )
            tempo_espera = (tempo_notificacao - agora).total_seconds()

            # Se não foi agendada ainda e o tempo é positivo, agenda
            if tarefa_id not in notificacoes_agendadas and tempo_espera > 0:
                timer = threading.Timer(
                    tempo_espera,
                    enviar_notificacao,
                    args=[
                        f"Lembrete: {tarefa['atividade']}",
                        f"Sua tarefa '{tarefa['atividade']}' começará em {TEMPO_ANTECEDENCIA_MINUTOS} minutos às {tarefa['hora']}",
                    ],
                )
                timer.daemon = True
                timer.start()
                notificacoes_agendadas[tarefa_id] = True

        except ValueError:
            pass


def monitorar_notificacoes():
    """Loop contínuo que verifica tarefas a cada minuto"""
    global notificacoes_agendadas
    tempo_anterior = TEMPO_ANTECEDENCIA_MINUTOS

    while True:
        # Se o tempo de antecedência mudou, limpa e reagenda todas as notificações
        if tempo_anterior != TEMPO_ANTECEDENCIA_MINUTOS:
            notificacoes_agendadas.clear()
            tempo_anterior = TEMPO_ANTECEDENCIA_MINUTOS

        agendar_notificacoes()
        time.sleep(60)  # Verifica a cada 60 segundos


def iniciar_monitoramento_background():
    """Inicia o monitoramento em uma thread separada"""
    thread_notificacoes = threading.Thread(target=monitorar_notificacoes, daemon=True)
    thread_notificacoes.start()


if __name__ == "__main__":
    monitorar_notificacoes()
