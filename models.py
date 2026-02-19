"""
Models simplificados para mobile.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Cliente:
    id_cliente: str
    nome: str
    telefone: Optional[str] = None
    email: Optional[str] = None
    banco_preferencial: str = "Caixa"


@dataclass
class Modelo:
    modelo: str
    custo_unitario: float


@dataclass
class Remessa:
    id_remessa: str
    id_cliente: str
    modelo: str
    quantidade: int
    custo_unitario: float
    saldo_montar: int = 0
    entregue: int = 0
    prazo_dias: int = 30
    data_criacao: str = ""
    cliente_destino: Optional[str] = None
    data_prevista: Optional[str] = None
    status: str = "Em Aberto"
    
    def __post_init__(self):
        if not self.data_criacao:
            self.data_criacao = datetime.now().strftime('%Y-%m-%d')
        if self.saldo_montar == 0:
            self.saldo_montar = self.quantidade
    
    def calcular_valor_total(self) -> float:
        return self.quantidade * self.custo_unitario
    
    def calcular_saldo_valor(self) -> float:
        return self.saldo_montar * self.custo_unitario


@dataclass
class Financeiro:
    id: int
    id_remessa: str
    quantidade: int
    valor_receber: float
    data_entrega: str
    data_vencimento: Optional[str] = None
    status: str = "Pendente"
    banco: Optional[str] = None
    data_recebimento: Optional[str] = None


@dataclass
class Usuario:
    id: int
    usuario: str
    senha_hash: str
