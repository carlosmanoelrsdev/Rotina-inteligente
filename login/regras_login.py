def validar_login(usuario, senha):
    # Verifica se os campos foram preenchidos
    if not usuario or not senha:
        return False, "Por favor, preencha todos os campos."

    # Valida credenciais de login
    if usuario == "admin" and senha == "1234":
        return True, "Login bem-sucedido!"
    else:
        return False, "Usuário ou senha incorretos."
