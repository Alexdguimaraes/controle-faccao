"""
Utilitários para mobile.
"""


def format_currency(value: float) -> str:
    """Formata valor como moeda."""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_date(date_str: str) -> str:
    """Formata data."""
    if not date_str:
        return ""
    try:
        from datetime import datetime
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%d/%m/%Y')
    except:
        return date_str


class Logger:
    """Logger simples."""
    
    @staticmethod
    def info(msg: str):
        print(f"[INFO] {msg}")
    
    @staticmethod
    def error(msg: str):
        print(f"[ERROR] {msg}")
