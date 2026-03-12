from pathlib import Path
import sqlite3

# Caminho do banco de dados SQLite
DB_PATH = Path(__file__).resolve().parent / "tarefas.db"


def _conectar():
    # Estabelece conexão com o banco e permite acesso por nome de coluna
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def criar_tabela_regras_dados():
    # Cria a tabela de tarefas caso ainda nao exista
    with _conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                atividade TEXT NOT NULL,
                hora TEXT NOT NULL,
                status TEXT NOT NULL,
                descricao TEXT,
                data_criacao TEXT NOT NULL
            )
            """
        )
        conn.commit()


def inserir_tarefa(atividade, hora, status, descricao, data_criacao):
    # Insere uma nova tarefa e retorna o ID criado
    with _conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tarefas (atividade, hora, status, descricao, data_criacao)
            VALUES (?, ?, ?, ?, ?)
            """,
            (atividade, hora, status, descricao, data_criacao),
        )
        conn.commit()
        return cursor.lastrowid


def listar_tarefas():
    # Retorna todas as tarefas ordenadas do mais recente para o mais antigo
    with _conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tarefas ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]


def buscar_tarefa_por_id(tarefa_id):
    # Busca uma tarefa pelo ID e retorna None se nao existir
    with _conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tarefas WHERE id = ?", (tarefa_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def atualizar_tarefa(tarefa_id, atividade, hora, status, descricao, data_criacao):
    # Atualiza todos os campos de uma tarefa existente
    with _conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE tarefas
            SET atividade = ?, hora = ?, status = ?, descricao = ?, data_criacao = ?
            WHERE id = ?
            """,
            (atividade, hora, status, descricao, data_criacao, tarefa_id),
        )
        conn.commit()
        return cursor.rowcount > 0


def atualizar_status_tarefa(tarefa_id, status):
    # Atualiza apenas o status de uma tarefa
    with _conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tarefas SET status = ? WHERE id = ?",
            (status, tarefa_id),
        )
        conn.commit()
        return cursor.rowcount > 0


def excluir_tarefa(tarefa_id):
    # Exclui uma tarefa pelo ID
    with _conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
        conn.commit()
        return cursor.rowcount > 0


def buscar_tarefas_por_status(status):
    # Busca tarefas por status especifico
    with _conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tarefas WHERE LOWER(status) = LOWER(?) ORDER BY id DESC",
            (status,),
        )
        return [dict(row) for row in cursor.fetchall()]


def buscar_tarefas_por_data(data_criacao):
    # Busca tarefas por data de criacao especifica
    with _conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tarefas WHERE data_criacao = ? ORDER BY id DESC",
            (data_criacao,),
        )
        return [dict(row) for row in cursor.fetchall()]


def buscar_tarefas_por_atividade(atividade):
    # Busca tarefas que contenham o texto informado na atividade
    termo = f"%{atividade}%"
    with _conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tarefas WHERE atividade LIKE ? ORDER BY id DESC",
            (termo,),
        )
        return [dict(row) for row in cursor.fetchall()]


def buscar_tarefas(termo):
    # Busca geral em todos os campos da tarefa
    like = f"%{termo}%"
    with _conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM tarefas
            WHERE atividade LIKE ?
               OR descricao LIKE ?
               OR status LIKE ?
               OR data_criacao LIKE ?
            ORDER BY id DESC
            """,
            (like, like, like, like),
        )
        return [dict(row) for row in cursor.fetchall()]


def contar_tarefas():
    # Retorna o numero total de tarefas cadastradas
    with _conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM tarefas")
        row = cursor.fetchone()
        return int(row["total"])


def inicializar_banco():
    # Inicializa o banco de dados criando as tabelas necessarias
    criar_tabela_regras_dados()


if __name__ == "__main__":
    inicializar_banco()
    print(f"Banco pronto em: {DB_PATH}")
