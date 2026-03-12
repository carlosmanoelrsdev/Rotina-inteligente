from interface.Main import Interface
from notificacao.notificacao import iniciar_monitoramento_background

# executa o programa
if __name__ == "__main__":
    # Inicia o monitoramento de notificações em background
    iniciar_monitoramento_background()

    # Inicia a interface gráfica
    programa = Interface()
    programa.mainloop()
