from datetime import datetime
import calendar


def obter_data_atual():
    # Dicionario para traduzir dias da semana para portugues
    dias_semana_portugues = {
        "Monday": "Seg",
        "Tuesday": "Ter",
        "Wednesday": "Qua",
        "Thursday": "Qui",
        "Friday": "Sex",
        "Saturday": "Sáb",
        "Sunday": "Dom",
    }

    # Dicionario para traduzir meses para portugues
    meses_semana_portugues = {
        "January": "JAN",
        "February": "FEV",
        "March": "MAR",
        "April": "ABR",
        "May": "MAI",
        "June": "JUN",
        "July": "JUL",
        "August": "AGO",
        "September": "SET",
        "October": "OUT",
        "November": "NOV",
        "December": "DEZ",
    }

    # Obtem data e hora atual
    agora = datetime.now()

    # Extrai nome do dia, mes e numero do dia
    dia_nome = calendar.day_name[agora.weekday()]
    mes_nome = calendar.month_name[agora.month]
    dia_data = agora.day

    # Formata data em portugues
    data_portugues = (
        dias_semana_portugues.get(dia_nome)
        + f", {dia_data} {meses_semana_portugues.get(mes_nome)}"
    )

    return data_portugues
