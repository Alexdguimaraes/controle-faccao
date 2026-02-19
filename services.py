"""
Services para mobile.
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from app.database import get_connection
from app.models import Cliente, Remessa, Financeiro


class ClienteService:
    """Service de clientes."""
    
    @staticmethod
    def listar_todos() -> List[Cliente]:
        """Lista todos os clientes."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Clientes ORDER BY nome')
        
        clientes = []
        for row in cursor.fetchall():
            clientes.append(Cliente(
                id_cliente=row[0],
                nome=row[1],
                telefone=row[2],
                email=row[3],
                banco_preferencial=row[4] or "Caixa"
            ))
        
        conn.close()
        return clientes
    
    @staticmethod
    def buscar_por_id(id_cliente: str) -> Optional[Cliente]:
        """Busca cliente por ID."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Clientes WHERE id_cliente = ?', (id_cliente,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Cliente(
                id_cliente=row[0],
                nome=row[1],
                telefone=row[2],
                email=row[3],
                banco_preferencial=row[4] or "Caixa"
            )
        return None
    
    @staticmethod
    def cadastrar(dados: Dict) -> Dict:
        """Cadastra um cliente."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO Clientes (id_cliente, nome, telefone, email, banco_preferencial)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                dados['id_cliente'].upper(),
                dados['nome'],
                dados.get('telefone'),
                dados.get('email'),
                dados.get('banco_preferencial', 'Caixa')
            ))
            
            conn.commit()
            conn.close()
            
            return {'sucesso': True, 'mensagem': 'Cliente cadastrado!'}
            
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def get_resumo() -> Dict:
        """Retorna resumo de clientes."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM Clientes')
        total = cursor.fetchone()[0]
        conn.close()
        
        return {'total': total}


class RemessaService:
    """Service de remessas."""
    
    @staticmethod
    def listar_todos(id_cliente: str = None, status: str = None) -> List[Remessa]:
        """Lista remessas."""
        conn = get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM Remessas WHERE 1=1'
        params = []
        
        if id_cliente:
            query += ' AND id_cliente = ?'
            params.append(id_cliente)
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        query += ' ORDER BY data_criacao DESC'
        
        cursor.execute(query, params)
        
        remessas = []
        for row in cursor.fetchall():
            remessas.append(Remessa(
                id_remessa=row[0],
                id_cliente=row[1],
                modelo=row[2],
                quantidade=row[3],
                custo_unitario=row[4],
                saldo_montar=row[5],
                entregue=row[6],
                prazo_dias=row[7],
                data_criacao=row[8],
                cliente_destino=row[9],
                data_prevista=row[10],
                status=row[11]
            ))
        
        conn.close()
        return remessas
    
    @staticmethod
    def get_overdue() -> List[Remessa]:
        """Retorna remessas atrasadas."""
        hoje = datetime.now().strftime('%Y-%m-%d')
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM Remessas 
            WHERE data_prevista < ? AND saldo_montar > 0 AND status != 'Entregue'
            ORDER BY data_prevista
        ''', (hoje,))
        
        remessas = []
        for row in cursor.fetchall():
            remessas.append(Remessa(
                id_remessa=row[0],
                id_cliente=row[1],
                modelo=row[2],
                quantidade=row[3],
                custo_unitario=row[4],
                saldo_montar=row[5],
                entregue=row[6],
                prazo_dias=row[7],
                data_criacao=row[8],
                cliente_destino=row[9],
                data_prevista=row[10],
                status=row[11]
            ))
        
        conn.close()
        return remessas
    
    @staticmethod
    def criar(dados: Dict) -> Dict:
        """Cria uma nova remessa."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Gerar ID
            cursor.execute("SELECT valor FROM Configuracoes WHERE chave = 'ultimo_id_remessa'")
            ultimo = int(cursor.fetchone()[0])
            novo_id = ultimo + 1
            id_remessa = f"OP-{novo_id:04d}"
            
            # Calcular data prevista
            prazo = dados.get('prazo_dias', 30)
            data_prevista = (datetime.now() + timedelta(days=prazo)).strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT INTO Remessas 
                (id_remessa, id_cliente, modelo, quantidade, custo_unitario, 
                 saldo_montar, data_criacao, data_prevista, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                id_remessa,
                dados['id_cliente'],
                dados['modelo'],
                dados['quantidade'],
                dados['custo_unitario'],
                dados['quantidade'],
                datetime.now().strftime('%Y-%m-%d'),
                data_prevista,
                'Em Aberto'
            ))
            
            # Atualizar contador
            cursor.execute(
                "UPDATE Configuracoes SET valor = ? WHERE chave = 'ultimo_id_remessa'",
                (str(novo_id),)
            )
            
            conn.commit()
            conn.close()
            
            return {'sucesso': True, 'mensagem': f'OP {id_remessa} criada!', 'id': id_remessa}
            
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def registrar_entrega(id_remessa: str, quantidade: int) -> Dict:
        """Registra uma entrega."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Buscar remessa
            cursor.execute('SELECT * FROM Remessas WHERE id_remessa = ?', (id_remessa,))
            row = cursor.fetchone()
            
            if not row:
                return {'sucesso': False, 'mensagem': 'OP não encontrada'}
            
            saldo_atual = row[5]
            entregue_atual = row[6]
            custo = row[4]
            
            if quantidade > saldo_atual:
                quantidade = saldo_atual
            
            novo_saldo = saldo_atual - quantidade
            novo_entregue = entregue_atual + quantidade
            status = 'Entregue' if novo_saldo == 0 else 'Em Aberto'
            
            # Atualizar remessa
            cursor.execute('''
                UPDATE Remessas 
                SET saldo_montar = ?, entregue = ?, status = ?
                WHERE id_remessa = ?
            ''', (novo_saldo, novo_entregue, status, id_remessa))
            
            # Criar financeiro
            data_entrega = datetime.now().strftime('%Y-%m-%d')
            data_venc = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT INTO Financeiro 
                (id_remessa, quantidade, valor_receber, data_entrega, data_vencimento, status)
                VALUES (?, ?, ?, ?, ?, 'Pendente')
            ''', (id_remessa, quantidade, quantidade * custo, data_entrega, data_venc))
            
            conn.commit()
            conn.close()
            
            return {
                'sucesso': True, 
                'mensagem': f'Entrega de {quantidade} unidades registrada!',
                'finalizada': novo_saldo == 0
            }
            
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def get_estatisticas() -> Dict:
        """Retorna estatísticas."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*), SUM(saldo_montar), SUM(saldo_montar * custo_unitario)
            FROM Remessas WHERE saldo_montar > 0
        ''')
        row = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_ops': row[0] or 0,
            'total_saldo': row[1] or 0,
            'valor_saldo': row[2] or 0
        }


class FinanceiroService:
    """Service financeiro."""
    
    @staticmethod
    def get_all(id_cliente: str = None, status: str = None) -> List[Dict]:
        """Lista títulos financeiros."""
        conn = get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT f.*, c.nome as cliente_nome
            FROM Financeiro f
            LEFT JOIN Remessas r ON r.id_remessa = f.id_remessa
            LEFT JOIN Clientes c ON c.id_cliente = r.id_cliente
            WHERE 1=1
        '''
        params = []
        
        if id_cliente:
            query += ' AND r.id_cliente = ?'
            params.append(id_cliente)
        
        if status:
            query += ' AND f.status = ?'
            params.append(status)
        
        query += ' ORDER BY f.data_vencimento ASC'
        
        cursor.execute(query, params)
        
        titulos = []
        for row in cursor.fetchall():
            titulos.append({
                'id': row[0],
                'id_remessa': row[1],
                'quantidade': row[2],
                'valor_receber': row[3],
                'data_entrega': row[4],
                'data_vencimento': row[5],
                'status': row[6],
                'banco': row[7],
                'data_recebimento': row[8],
                'cliente_nome': row[9] if len(row) > 9 else ''
            })
        
        conn.close()
        return titulos
    
    @staticmethod
    def get_totais(id_cliente: str = None) -> Dict:
        """Retorna totais."""
        conn = get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                SUM(CASE WHEN f.status = 'Pendente' THEN f.valor_receber ELSE 0 END) as pendente,
                SUM(CASE WHEN f.status = 'Recebido' THEN f.valor_receber ELSE 0 END) as recebido
            FROM Financeiro f
            LEFT JOIN Remessas r ON r.id_remessa = f.id_remessa
            WHERE 1=1
        '''
        params = []
        
        if id_cliente:
            query += ' AND r.id_cliente = ?'
            params.append(id_cliente)
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        
        return {
            'pendente': row[0] or 0,
            'recebido': row[1] or 0
        }
    
    @staticmethod
    def get_monthly_received(banco: str, year: int, month: int) -> float:
        """Retorna total recebido no mês."""
        conn = get_connection()
        cursor = conn.cursor()
        
        start = f"{year}-{month:02d}-01"
        if month == 12:
            end = f"{year + 1}-01-01"
        else:
            end = f"{year}-{month + 1:02d}-01"
        
        cursor.execute('''
            SELECT SUM(valor_receber) 
            FROM Financeiro 
            WHERE status = 'Recebido' AND banco = ? AND data_recebimento >= ? AND data_recebimento < ?
        ''', (banco, start, end))
        
        result = cursor.fetchone()[0] or 0
        conn.close()
        return result
    
    @staticmethod
    def liquidar(fin_id: int, banco: str) -> str:
        """Liquida um título."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            data_receb = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('''
                UPDATE Financeiro 
                SET status = 'Recebido', banco = ?, data_recebimento = ?
                WHERE id = ?
            ''', (banco, data_receb, fin_id))
            
            conn.commit()
            conn.close()
            
            return "OK"
            
        except Exception as e:
            return str(e)


class BackupService:
    """Service de backup."""
    
    @staticmethod
    def backup() -> Dict:
        """Realiza backup."""
        try:
            import shutil
            from app.database import get_db_path
            
            src = get_db_path()
            dst = src.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
            
            shutil.copy2(src, dst)
            
            return {'sucesso': True, 'mensagem': f'Backup: {dst}'}
            
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
