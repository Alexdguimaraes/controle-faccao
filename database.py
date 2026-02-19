"""
Banco de dados para mobile.
"""
import os
import sqlite3
from kivy.utils import platform

DB_NAME = "faccao_mobile.db"


def get_db_path():
    """Retorna o caminho do banco de dados."""
    if platform == 'android':
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), DB_NAME)
    else:
        return DB_NAME


def init_db():
    """Inicializa o banco de dados."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Clientes (
            id_cliente TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            telefone TEXT,
            email TEXT,
            banco_preferencial TEXT DEFAULT 'Caixa'
        )
    ''')
    
    # Modelos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Modelos (
            modelo TEXT PRIMARY KEY,
            custo_unitario REAL NOT NULL
        )
    ''')
    
    # Remessas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Remessas (
            id_remessa TEXT PRIMARY KEY,
            id_cliente TEXT NOT NULL,
            modelo TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            custo_unitario REAL NOT NULL,
            saldo_montar INTEGER DEFAULT 0,
            entregue INTEGER DEFAULT 0,
            prazo_dias INTEGER DEFAULT 30,
            data_criacao TEXT NOT NULL,
            cliente_destino TEXT,
            data_prevista TEXT,
            status TEXT DEFAULT 'Em Aberto'
        )
    ''')
    
    # Financeiro
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Financeiro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_remessa TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            valor_receber REAL NOT NULL,
            data_entrega TEXT NOT NULL,
            data_vencimento TEXT,
            status TEXT DEFAULT 'Pendente',
            banco TEXT,
            data_recebimento TEXT
        )
    ''')
    
    # Configurações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT
        )
    ''')
    
    # Inserir contador de OP
    cursor.execute('''
        INSERT OR IGNORE INTO Configuracoes (chave, valor) VALUES ('ultimo_id_remessa', '0')
    ''')
    
    # Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL
        )
    ''')
    
    # Usuário padrão (senha: admin)
    cursor.execute('''
        INSERT OR IGNORE INTO Usuarios (usuario, senha_hash) 
        VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G')
    ''')
    
    # Bancos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Bancos (
            nome TEXT PRIMARY KEY,
            limite_mensal REAL DEFAULT 5000
        )
    ''')
    
    bancos = ['Caixa', 'Banco do Brasil', 'Itaú', 'Bradesco', 'Nubank']
    for b in bancos:
        cursor.execute('INSERT OR IGNORE INTO Bancos (nome) VALUES (?)', (b,))
    
    conn.commit()
    conn.close()


def get_connection():
    """Retorna uma conexão com o banco."""
    return sqlite3.connect(get_db_path())
