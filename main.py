"""
G.A. Facção - Sistema Mobile para Android
Versão 2.0 Mobile - Kivy
"""
import os
import sys
from pathlib import Path

# Configurar path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.clock import Clock
from kivy.utils import platform

# KivyMD
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.chip import MDChip
from kivymd.uix.badge import MDBadge
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.chip import MDChip
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem
from kivymd.icon_definitions import md_icons
from kivymd.font_definitions import theme_font_styles
from kivymd.theming import ThemableBehavior
from kivymd.color_definitions import colors

# Importar lógica do sistema
from app.database import init_db, get_db_path
from app.models import Cliente, Remessa, Financeiro
from app.services import ClienteService, RemessaService, FinanceiroService, BackupService
from app.utils import Logger, format_currency, format_date

# Cores do tema
PRIMARY_COLOR = [0.129, 0.588, 0.953, 1]  # #2196F3
SUCCESS_COLOR = [0.298, 0.686, 0.314, 1]  # #4CAF50
WARNING_COLOR = [1, 0.596, 0, 1]          # #FF9800
DANGER_COLOR = [0.957, 0.263, 0.212, 1]   # #F44336


class LoginScreen(MDScreen):
    """Tela de login."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Espaçamento superior
        layout.add_widget(MDBoxLayout(size_hint_y=0.3))
        
        # Logo/Título
        layout.add_widget(MDLabel(
            text="G.A. Facção",
            halign='center',
            font_style='H3',
            theme_text_color='Primary'
        ))
        
        layout.add_widget(MDLabel(
            text="Sistema de Controle",
            halign='center',
            font_style='Subtitle1',
            theme_text_color='Secondary'
        ))
        
        layout.add_widget(MDBoxLayout(size_hint_y=0.1))
        
        # Card de login
        card = MDCard(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15),
            size_hint=(1, None),
            height=dp(280),
            elevation=4
        )
        
        # Usuário
        self.txt_usuario = MDTextField(
            hint_text="Usuário",
            icon_right="account",
            mode="rectangle"
        )
        card.add_widget(self.txt_usuario)
        
        # Senha
        self.txt_senha = MDTextField(
            hint_text="Senha",
            icon_right="lock",
            password=True,
            mode="rectangle"
        )
        card.add_widget(self.txt_senha)
        
        # Botão login
        btn_login = MDRaisedButton(
            text="ENTRAR",
            size_hint=(1, None),
            height=dp(50),
            md_bg_color=SUCCESS_COLOR,
            on_release=self.do_login
        )
        card.add_widget(btn_login)
        
        layout.add_widget(card)
        layout.add_widget(MDBoxLayout(size_hint_y=0.3))
        
        self.add_widget(layout)
    
    def do_login(self, instance):
        usuario = self.txt_usuario.text.strip()
        senha = self.txt_senha.text
        
        if not usuario or not senha:
            self.show_error("Preencha usuário e senha")
            return
        
        # Simular login (integrar com UsuarioService)
        if usuario == "admin" and senha == "admin":
            self.manager.current = 'main'
            self.manager.transition = SlideTransition(direction='left')
        else:
            self.show_error("Usuário ou senha incorretos")
    
    def show_error(self, message):
        Snackbar(text=message, bg_color=DANGER_COLOR).open()


class DashboardScreen(MDScreen):
    """Tela principal com dashboard."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        Clock.schedule_once(self.load_data, 0.5)
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Visão Geral",
            elevation=4,
            left_action_items=[["menu", lambda x: self.open_menu()]],
            right_action_items=[["refresh", lambda x: self.load_data()]]
        )
        layout.add_widget(toolbar)
        
        # Conteúdo scrollável
        scroll = MDScrollView()
        content = MDBoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Cards de KPI
        self.kpi_layout = MDGridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(220))
        
        self.card_clientes = self.create_kpi_card("Clientes", "0", "account-group", PRIMARY_COLOR)
        self.card_producao = self.create_kpi_card("Em Produção", "0", "factory", WARNING_COLOR)
        self.card_receber = self.create_kpi_card("A Receber", "R$ 0,00", "cash-remove", DANGER_COLOR)
        self.card_faturamento = self.create_kpi_card("Faturamento", "R$ 0,00", "chart-line", SUCCESS_COLOR)
        
        self.kpi_layout.add_widget(self.card_clientes)
        self.kpi_layout.add_widget(self.card_producao)
        self.kpi_layout.add_widget(self.card_receber)
        self.kpi_layout.add_widget(self.card_faturamento)
        
        content.add_widget(self.kpi_layout)
        
        # Ações rápidas
        content.add_widget(MDLabel(text="Ações Rápidas", font_style='H6', size_hint_y=None, height=dp(40)))
        
        actions = MDGridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(120))
        
        actions.add_widget(MDRaisedButton(
            text="Nova OP",
            icon="plus",
            size_hint=(1, 1),
            on_release=lambda x: self.go_to_screen('producao')
        ))
        
        actions.add_widget(MDRaisedButton(
            text="Registrar Entrega",
            icon="truck-delivery",
            size_hint=(1, 1),
            on_release=lambda x: self.go_to_screen('producao')
        ))
        
        actions.add_widget(MDRaisedButton(
            text="Liquidar",
            icon="cash-check",
            size_hint=(1, 1),
            on_release=lambda x: self.go_to_screen('financeiro')
        ))
        
        actions.add_widget(MDRaisedButton(
            text="Novo Cliente",
            icon="account-plus",
            size_hint=(1, 1),
            on_release=lambda x: self.go_to_screen('clientes')
        ))
        
        content.add_widget(actions)
        
        # Alertas
        content.add_widget(MDLabel(text="Alertas", font_style='H6', size_hint_y=None, height=dp(40)))
        
        self.alerts_layout = MDBoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        self.alerts_layout.bind(minimum_height=self.alerts_layout.setter('height'))
        content.add_widget(self.alerts_layout)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def create_kpi_card(self, title, value, icon, color):
        """Cria um card de KPI."""
        card = MDCard(orientation='vertical', padding=dp(10), elevation=2, size_hint_y=None, height=dp(100))
        
        icon_widget = MDIconButton(icon=icon, theme_text_color="Custom", text_color=color)
        card.add_widget(icon_widget)
        
        lbl_value = MDLabel(text=value, font_style='H4', halign='center')
        lbl_value.theme_text_color = 'Custom'
        lbl_value.text_color = color
        card.add_widget(lbl_value)
        
        card.add_widget(MDLabel(text=title, font_style='Caption', halign='center', theme_text_color='Secondary'))
        
        # Guardar referência ao label de valor
        card.value_label = lbl_value
        
        return card
    
    def load_data(self, *args):
        """Carrega dados do dashboard."""
        try:
            # Clientes
            from app.services import ClienteService
            resumo = ClienteService.get_resumo()
            self.card_clientes.value_label.text = str(resumo.get('total', 0))
            
            # Produção
            from app.services import RemessaService
            stats = RemessaService.get_estatisticas()
            self.card_producao.value_label.text = str(stats.get('total_saldo', 0))
            
            # A receber
            from app.services import FinanceiroService
            totais = FinanceiroService.get_totais()
            self.card_receber.value_label.text = f"R$ {totais.get('pendente', 0):,.2f}"
            
            # Faturamento
            from datetime import date
            hoje = date.today()
            recebido = FinanceiroService.get_monthly_received("Caixa", hoje.year, hoje.month)
            self.card_faturamento.value_label.text = f"R$ {recebido:,.2f}"
            
            # Alertas
            self.load_alerts()
            
        except Exception as e:
            print(f"Erro ao carregar dashboard: {e}")
    
    def load_alerts(self):
        """Carrega alertas."""
        self.alerts_layout.clear_widgets()
        
        # Verificar remessas atrasadas
        from app.dao import RemessaDAO
        atrasadas = RemessaDAO.get_overdue()
        
        if atrasadas:
            for r in atrasadas[:3]:  # Mostrar apenas 3
                item = OneLineListItem(
                    text=f"⚠️ OP {r.id_remessa} atrasada",
                    theme_text_color='Custom',
                    text_color=DANGER_COLOR
                )
                self.alerts_layout.add_widget(item)
        else:
            self.alerts_layout.add_widget(MDLabel(
                text="Nenhum alerta",
                theme_text_color='Secondary',
                halign='center'
            ))
    
    def open_menu(self):
        """Abre menu lateral."""
        pass  # Implementar drawer
    
    def go_to_screen(self, screen_name):
        """Navega para outra tela."""
        self.manager.current = screen_name


class ClientesScreen(MDScreen):
    """Tela de clientes."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Clientes",
            elevation=4,
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["plus", lambda x: self.add_cliente()]]
        )
        layout.add_widget(toolbar)
        
        # Busca
        self.txt_busca = MDTextField(
            hint_text="Buscar cliente...",
            icon_right="magnify",
            mode="rectangle",
            size_hint_y=None,
            height=dp(50)
        )
        self.txt_busca.bind(on_text_validate=self.search)
        layout.add_widget(self.txt_busca)
        
        # Lista
        scroll = MDScrollView()
        self.lista = MDList()
        scroll.add_widget(self.lista)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        Clock.schedule_once(self.load_clientes, 0.5)
    
    def load_clientes(self, *args):
        """Carrega lista de clientes."""
        self.lista.clear_widgets()
        
        try:
            from app.services import ClienteService
            clientes = ClienteService.listar_todos()
            
            for c in clientes:
                item = TwoLineListItem(
                    text=c.nome,
                    secondary_text=f"{c.id_cliente} | {c.telefone or 'Sem telefone'}",
                    on_release=lambda x, cid=c.id_cliente: self.view_cliente(cid)
                )
                self.lista.add_widget(item)
                
        except Exception as e:
            self.lista.add_widget(OneLineListItem(text=f"Erro: {e}"))
    
    def search(self, instance):
        """Busca clientes."""
        termo = instance.text
        # Implementar busca
        pass
    
    def add_cliente(self):
        """Abre formulário de novo cliente."""
        pass
    
    def view_cliente(self, cliente_id):
        """Visualiza detalhes do cliente."""
        pass
    
    def go_back(self):
        """Volta para tela anterior."""
        self.manager.current = 'main'


class ProducaoScreen(MDScreen):
    """Tela de produção."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(
            title="Produção",
            elevation=4,
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["plus", lambda x: self.nova_op()]]
        )
        layout.add_widget(toolbar)
        
        # Tabs
        tabs = MDTabs()
        
        tab_abertas = TabProducaoAbertas(title="Em Aberto")
        tab_entregues = TabProducaoEntregues(title="Entregues")
        
        tabs.add_widget(tab_abertas)
        tabs.add_widget(tab_entregues)
        
        layout.add_widget(tabs)
        self.add_widget(layout)
    
    def nova_op(self):
        """Cria nova OP."""
        pass
    
    def go_back(self):
        self.manager.current = 'main'


class TabProducaoAbertas(MDFloatLayout, MDTabsBase):
    """Tab de OPs em aberto."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)
    
    def build_ui(self, *args):
        scroll = MDScrollView()
        self.lista = MDList()
        scroll.add_widget(self.lista)
        self.add_widget(scroll)
        self.load_ops()
    
    def load_ops(self):
        """Carrega OPs em aberto."""
        try:
            from app.dao import RemessaDAO
            remessas = RemessaDAO.get_all()
            
            for r in remessas:
                if r.saldo_montar > 0:
                    item = TwoLineListItem(
                        text=f"{r.id_remessa} - {r.modelo}",
                        secondary_text=f"Saldo: {r.saldo_montar} | Cliente: {r.id_cliente}",
                        on_release=lambda x, rid=r.id_remessa: self.registrar_entrega(rid)
                    )
                    self.lista.add_widget(item)
        except Exception as e:
            self.lista.add_widget(OneLineListItem(text=f"Erro: {e}"))
    
    def registrar_entrega(self, op_id):
        """Registra entrega da OP."""
        pass


class TabProducaoEntregues(MDFloatLayout, MDTabsBase):
    """Tab de OPs entregues."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)
    
    def build_ui(self, *args):
        scroll = MDScrollView()
        self.lista = MDList()
        scroll.add_widget(self.lista)
        self.add_widget(scroll)


class FinanceiroScreen(MDScreen):
    """Tela financeira."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(
            title="Financeiro",
            elevation=4,
            left_action_items=[["arrow-left", lambda x: self.go_back()]]
        )
        layout.add_widget(toolbar)
        
        # Resumo
        card = MDCard(orientation='vertical', padding=dp(15), elevation=2)
        card.add_widget(MDLabel(text="Resumo", font_style='H6'))
        
        self.lbl_pendente = MDLabel(text="A Receber: R$ 0,00", theme_text_color='Custom', text_color=WARNING_COLOR)
        self.lbl_vencido = MDLabel(text="Vencido: R$ 0,00", theme_text_color='Custom', text_color=DANGER_COLOR)
        self.lbl_recebido = MDLabel(text="Recebido: R$ 0,00", theme_text_color='Custom', text_color=SUCCESS_COLOR)
        
        card.add_widget(self.lbl_pendente)
        card.add_widget(self.lbl_vencido)
        card.add_widget(self.lbl_recebido)
        
        layout.add_widget(card)
        
        # Lista
        scroll = MDScrollView()
        self.lista = MDList()
        scroll.add_widget(self.lista)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        Clock.schedule_once(self.load_data, 0.5)
    
    def load_data(self, *args):
        """Carrega dados financeiros."""
        try:
            from app.services import FinanceiroService
            totais = FinanceiroService.get_totais()
            
            self.lbl_pendente.text = f"A Receber: R$ {totais.get('pendente', 0):,.2f}"
            self.lbl_recebido.text = f"Recebido: R$ {totais.get('recebido', 0):,.2f}"
            
            # Carregar títulos
            from app.dao import FinanceiroDAO
            titulos = FinanceiroDAO.get_all()
            
            for t in titulos:
                if t['status'] == 'Pendente':
                    item = TwoLineListItem(
                        text=f"R$ {t['valor_receber']:,.2f} - {t.get('cliente_nome', 'N/A')}",
                        secondary_text=f"Venc: {t['data_vencimento']}",
                        on_release=lambda x, tid=t['id']: self.liquidar(tid)
                    )
                    self.lista.add_widget(item)
                    
        except Exception as e:
            print(f"Erro: {e}")
    
    def liquidar(self, fin_id):
        """Liquida título."""
        pass
    
    def go_back(self):
        self.manager.current = 'main'


class MainScreen(MDScreen):
    """Tela principal com navegação inferior."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical')
        
        # Bottom Navigation
        bottom_nav = MDBottomNavigation()
        
        # Aba Dashboard
        dash_item = MDBottomNavigationItem(
            name='dash',
            text='Início',
            icon='home'
        )
        dash_item.add_widget(DashboardContent())
        bottom_nav.add_widget(dash_item)
        
        # Aba Clientes
        cli_item = MDBottomNavigationItem(
            name='clientes',
            text='Clientes',
            icon='account-group'
        )
        cli_item.add_widget(ClientesContent())
        bottom_nav.add_widget(cli_item)
        
        # Aba Produção
        prod_item = MDBottomNavigationItem(
            name='producao',
            text='Produção',
            icon='factory'
        )
        prod_item.add_widget(ProducaoContent())
        bottom_nav.add_widget(prod_item)
        
        # Aba Financeiro
        fin_item = MDBottomNavigationItem(
            name='financeiro',
            text='Financeiro',
            icon='cash-multiple'
        )
        fin_item.add_widget(FinanceiroContent())
        bottom_nav.add_widget(fin_item)
        
        # Aba Mais
        mais_item = MDBottomNavigationItem(
            name='mais',
            text='Mais',
            icon='dots-horizontal'
        )
        mais_item.add_widget(MaisContent())
        bottom_nav.add_widget(mais_item)
        
        layout.add_widget(bottom_nav)
        self.add_widget(layout)


class DashboardContent(MDBoxLayout):
    """Conteúdo da aba Dashboard."""
    
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        Clock.schedule_once(self.build_ui, 0)
    
    def build_ui(self, *args):
        scroll = MDScrollView()
        content = MDBoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # KPIs
        kpi_grid = MDGridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(200))
        
        kpi_grid.add_widget(self.create_kpi_card("Clientes", "0", "account-group", PRIMARY_COLOR))
        kpi_grid.add_widget(self.create_kpi_card("Produção", "0", "package-variant", WARNING_COLOR))
        kpi_grid.add_widget(self.create_kpi_card("A Receber", "R$ 0", "cash-remove", DANGER_COLOR))
        kpi_grid.add_widget(self.create_kpi_card("Faturamento", "R$ 0", "trending-up", SUCCESS_COLOR))
        
        content.add_widget(kpi_grid)
        
        # Ações rápidas
        content.add_widget(MDLabel(text="Ações Rápidas", font_style='H6', size_hint_y=None, height=dp(40)))
        
        actions = MDGridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(150))
        actions.add_widget(self.create_action_btn("Nova OP", "plus", 'producao'))
        actions.add_widget(self.create_action_btn("Entrega", "truck-delivery", 'producao'))
        actions.add_widget(self.create_action_btn("Liquidar", "cash-check", 'financeiro'))
        actions.add_widget(self.create_action_btn("Cliente", "account-plus", 'clientes'))
        
        content.add_widget(actions)
        
        scroll.add_widget(content)
        self.add_widget(scroll)
    
    def create_kpi_card(self, title, value, icon, color):
        card = MDCard(orientation='vertical', padding=dp(10), elevation=2, size_hint_y=None, height=dp(90))
        card.md_bg_color = [0.98, 0.98, 0.98, 1]
        
        box = MDBoxLayout(orientation='horizontal')
        box.add_widget(MDIconButton(icon=icon, theme_text_color='Custom', text_color=color))
        
        vbox = MDBoxLayout(orientation='vertical')
        vbox.add_widget(MDLabel(text=value, font_style='H5', theme_text_color='Primary'))
        vbox.add_widget(MDLabel(text=title, font_style='Caption', theme_text_color='Secondary'))
        box.add_widget(vbox)
        
        card.add_widget(box)
        return card
    
    def create_action_btn(self, text, icon, screen):
        return MDRaisedButton(
            text=text,
            icon=icon,
            size_hint=(1, 1),
            on_release=lambda x: self.change_screen(screen)
        )
    
    def change_screen(self, screen):
        """Muda para tela específica."""
        # Navegar para tela
        pass


class ClientesContent(MDBoxLayout):
    """Conteúdo da aba Clientes."""
    
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        Clock.schedule_once(self.build_ui, 0)
    
    def build_ui(self, *args):
        # Busca
        self.txt_busca = MDTextField(
            hint_text="Buscar cliente...",
            icon_right="magnify",
            mode="rectangle",
            size_hint_y=None
        )
        self.add_widget(self.txt_busca)
        
        # Lista
        scroll = MDScrollView()
        self.lista = MDList()
        scroll.add_widget(self.lista)
        self.add_widget(scroll)
        
        # FAB
        fab = MDFloatingActionButton(
            icon="plus",
            pos_hint={'right': 0.95, 'y': 0.05},
            on_release=lambda x: self.novo_cliente()
        )
        self.add_widget(fab)
        
        self.load_clientes()
    
    def load_clientes(self):
        """Carrega clientes."""
        try:
            from app.services import ClienteService
            clientes = ClienteService.listar_todos()
            
            for c in clientes:
                item = TwoLineListItem(
                    text=c.nome,
                    secondary_text=c.id_cliente
                )
                self.lista.add_widget(item)
        except Exception as e:
            self.lista.add_widget(OneLineListItem(text=f"Erro: {e}"))
    
    def novo_cliente(self):
        """Abre formulário."""
        pass


class ProducaoContent(MDBoxLayout):
    """Conteúdo da aba Produção."""
    
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        Clock.schedule_once(self.build_ui, 0)
    
    def build_ui(self, *args):
        tabs = MDTabs()
        tabs.add_widget(TabAbertas(title="Em Aberto"))
        tabs.add_widget(TabEntregues(title="Entregues"))
        self.add_widget(tabs)


class TabAbertas(MDFloatLayout, MDTabsBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.load, 0)
    
    def load(self, *args):
        scroll = MDScrollView()
        self.lista = MDList()
        scroll.add_widget(self.lista)
        self.add_widget(scroll)


class TabEntregues(MDFloatLayout, MDTabsBase):
    pass


class FinanceiroContent(MDBoxLayout):
    """Conteúdo da aba Financeiro."""
    
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        Clock.schedule_once(self.build_ui, 0)
    
    def build_ui(self, *args):
        # Resumo
        card = MDCard(orientation='vertical', padding=dp(15), elevation=2, size_hint_y=None, height=dp(150))
        card.add_widget(MDLabel(text="Resumo do Mês", font_style='H6'))
        
        grid = MDGridLayout(cols=3)
        grid.add_widget(self.create_resumo_item("A Receber", "R$ 0", WARNING_COLOR))
        grid.add_widget(self.create_resumo_item("Vencido", "R$ 0", DANGER_COLOR))
        grid.add_widget(self.create_resumo_item("Recebido", "R$ 0", SUCCESS_COLOR))
        card.add_widget(grid)
        
        self.add_widget(card)
        
        # Lista
        scroll = MDScrollView()
        self.lista = MDList()
        scroll.add_widget(self.lista)
        self.add_widget(scroll)
    
    def create_resumo_item(self, label, value, color):
        box = MDBoxLayout(orientation='vertical')
        box.add_widget(MDLabel(text=value, halign='center', theme_text_color='Custom', text_color=color))
        box.add_widget(MDLabel(text=label, halign='center', font_style='Caption'))
        return box


class MaisContent(MDBoxLayout):
    """Conteúdo da aba Mais."""
    
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=dp(10), **kwargs)
        Clock.schedule_once(self.build_ui, 0)
    
    def build_ui(self, *args):
        scroll = MDScrollView()
        lista = MDList()
        
        items = [
            ("Estoque", "package-variant", 'estoque'),
            ("Despesas", "cash-minus", 'despesas'),
            ("Relatórios", "chart-bar", 'relatorios'),
            ("Backup", "cloud-upload", 'backup'),
            ("Configurações", "cog", 'config'),
            ("Sobre", "information", 'sobre'),
            ("Sair", "logout", 'sair'),
        ]
        
        for text, icon, action in items:
            item = OneLineListItem(
                text=text,
                on_release=lambda x, a=action: self.on_item_click(a)
            )
            lista.add_widget(item)
        
        scroll.add_widget(lista)
        self.add_widget(scroll)
    
    def on_item_click(self, action):
        """Trata clique no item."""
        if action == 'sair':
            App.get_running_app().stop()


class FaccaoApp(MDApp):
    """App principal."""
    
    def build(self):
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.accent_palette = 'Green'
        self.theme_cls.theme_style = 'Light'
        
        # Inicializar banco
        self.init_database()
        
        # Criar screen manager
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ClientesScreen(name='clientes'))
        sm.add_widget(ProducaoScreen(name='producao'))
        sm.add_widget(FinanceiroScreen(name='financeiro'))
        
        return sm
    
    def init_database(self):
        """Inicializa banco de dados."""
        try:
            init_db()
        except Exception as e:
            print(f"Erro ao inicializar DB: {e}")


if __name__ == '__main__':
    FaccaoApp().run()
