import mysql.connector
from config import DB_CONFIG


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id        INT AUTO_INCREMENT PRIMARY KEY,
            tipo      ENUM('ganho', 'gasto') NOT NULL,
            descricao VARCHAR(120) NOT NULL,
            valor     DECIMAL(12, 2) NOT NULL,
            mes       TINYINT  NOT NULL,
            ano       SMALLINT NOT NULL,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("✓ Banco inicializado.")


if __name__ == "__main__":
    init_db()
