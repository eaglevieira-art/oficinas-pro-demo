import streamlit as st
from datetime import datetime
import sqlite3
import urllib.parse
import shutil  # Para realizar o backup do banco de dados
import os

# --- CONFIGURAÇÃO DA DATA DE INÍCIO DO TESTE ---
DATA_INICIO_TESTE = "24/06/2026"  # Formato: DD/MM/AAAA


# ==========================================
# FUNÇÕES DE INFRAESTRUTURA, BACKUP E LICENÇA
# ==========================================

def gerenciar_temas():
    """Cria um seletor na barra lateral e aplica as variações de temas via CSS"""
    st.sidebar.markdown("<p style='font-weight: bold; margin-bottom: 5px; color: #4a5568;'>🎨 Aparência do Sistema:</p>",
                        unsafe_allow_html=True)

    # Inicializa o tema padrão caso não exista na sessão
    if 'tema_selecionado' not in st.session_state:
        st.session_state['tema_selecionado'] = "Azul Suave"

    tema = st.sidebar.selectbox(
        "Escolha o Tema",
        ["Azul Suave", "Tema Dark", "Padrão Streamlit"],
        label_visibility="collapsed"
    )
    st.session_state['tema_selecionado'] = tema

    # CSS Global para remover a barra branca do topo em qualquer tema customizado
    st.markdown("""
        <style>
            header[data-testid="stHeader"] {
                background: rgba(0,0,0,0) !important;
                background-color: transparent !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Aplicação dos estilos CSS baseados na escolha
    if tema == "Azul Suave":
        st.markdown("""
            <style>
                .stApp { background-color: #F0F4F8; }
                [data-testid="stSidebar"] { background-color: #D9E2EC; }
                .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
                    background-color: #FFFFFF !important; color: #102A43 !important;
                }
                .stExpander {
                    background-color: #FFFFFF !important; border: 1px solid #BCCCDC !important;
                    border-radius: 6px; margin-bottom: 8px;
                }
                h1, h2, h3, p, label, span, .stMarkdown { color: #102A43; }
                /* Garante texto legível no botão Sair */
                [data-testid="stSidebar"] .stButton>button {
                    color: #102A43 !important;
                }
            </style>
        """, unsafe_allow_html=True)

    elif tema == "Tema Dark":
        st.markdown("""
            <style>
                .stApp { background-color: #0E1117; }
                [data-testid="stSidebar"] { background-color: #1E222B; }
                .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
                    background-color: #262730 !important; color: #FAFAFA !important;
                    border: 1px solid #4A5568 !important;
                }
                .stExpander {
                    background-color: #1E222B !important; border: 1px solid #4A5568 !important;
                    border-radius: 6px; margin-bottom: 8px;
                }
                h1, h2, h3, p, label, span, .stMarkdown { color: #FAFAFA; }
                div[data-testid="stMetricValue"] { color: #1E90FF !important; }
                /* Corrige o texto branco sobre botão branco no menu Dark */
                [data-testid="stSidebar"] .stButton>button {
                    color: #0E1117 !important;
                    font-weight: bold;
                }
            </style>
        """, unsafe_allow_html=True)

    elif tema == "Padrão Streamlit":
        pass


def gerenciar_banco_nuvem():
    """Painel lateral para baixar e restaurar o banco de dados na nuvem"""
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<p style='font-weight: bold; margin-bottom: 5px; color: #4a5568;'>💾 Gestão de Dados (Nuvem):</p>",
        unsafe_allow_html=True)

    # 1. Botão para Baixar o Banco de Dados Atual
    if os.path.exists("oficina.db"):
        with open("oficina.db", "rb") as f:
            st.sidebar.download_button(
                label="📥 Baixar Cópia do Banco (.db)",
                data=f,
                file_name="oficina.db",
                mime="application/x-sqlite3",
                use_container_width=True
            )

    # 2. Campo para Restaurar o Banco de Dados (Upload)
    arquivo_enviado = st.sidebar.file_uploader("Restaurar Banco de Dados", type=["db"], label_visibility="collapsed")
    if arquivo_enviado is not None:
        try:
            with open("oficina.db", "wb") as f:
                f.write(arquivo_enviado.getbuffer())
            st.sidebar.success("✅ Banco restaurado! Atualizando...")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Erro ao restaurar: {e}")


def criar_banco_de_dados():
    """Cria o banco de dados e as tabelas se não existirem"""
    conn = sqlite3.connect("oficina.db")
    cursor = conn.cursor()

    # 1. Tabela de usuários (Login)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            senha TEXT
        )
    """)

    # Inserir o usuário padrão se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES ('admin', 'admin')")

    # 2. Tabela de Veículos e Clientes integrada
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT UNIQUE,
            marca TEXT,
            modelo TEXT,
            ano TEXT,
            cor TEXT,
            combustivel TEXT,
            km_atual INTEGER,
            nome_cliente TEXT,
            whatsapp TEXT,
            cpf TEXT,
            endereco TEXT,
            observacoes TEXT,
            data_cadastro TEXT
        )
    """)

    # 3. Tabela de Ordens de Serviço (O.S.)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_veiculo INTEGER,
            defeito_reclamado TEXT,
            servico_realizado TEXT,
            pecas_utilizadas TEXT,
            valor_mao_obra REAL,
            valor_pecas REAL,
            valor_total REAL,
            status TEXT,
            data_abertura TEXT,
            forma_pagamento TEXT,
            status_pagamento TEXT,
            data_pagamento TEXT,
            FOREIGN KEY(id_veiculo) REFERENCES veiculos(id)
        )
    """)

    # 4. Tabela: Estoque de Peças
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_barras TEXT UNIQUE,
            nome_peca TEXT,
            quantidade_estoque INTEGER,
            preco_venda REAL,
            foto_peca BLOB,
            data_cadastro TEXT
        )
    """)

    # Verificação de segurança para colunas financeiras
    try:
        cursor.execute("ALTER TABLE ordens_servico ADD COLUMN forma_pagamento TEXT")
        cursor.execute("ALTER TABLE ordens_servico ADD COLUMN status_pagamento TEXT")
        cursor.execute("ALTER TABLE ordens_servico ADD COLUMN data_pagamento TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


def realizar_backup():
    """Gera uma cópia de segurança do banco de dados na pasta 'backups'"""
    try:
        if not os.path.exists("oficina.db"):
            return None

        if not os.path.exists("backups"):
            os.makedirs("backups")

        data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_backup = f"backups/oficina_backup_{data_hora}.db"
        shutil.copy2("oficina.db", nome_backup)
        return nome_backup
    except Exception as e:
        st.error(f"⚠️ Falha ao gerar backup: {e}")
        return None


def verificar_licenca():
    """Retorna (bloqueado, dias_restantes)"""
    try:
        data_inicio = datetime.strptime(DATA_INICIO_TESTE, "%d/%m/%Y")
        data_atual = datetime.now()
        dias_passados = (data_atual - data_inicio).days
        dias_restantes = 30 - dias_passados

        if dias_restantes <= 0:
            return True, 0
        return False, dias_restantes
    except Exception:
        return True, 0


def tela_login():
    """Exibe o formulário de login"""
    st.subheader("🔑 Acesso ao Sistema")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar", use_container_width=True):
        conn = sqlite3.connect("oficina.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
        user_exists = cursor.fetchone()
        conn.close()

        if user_exists:
            st.session_state['logado'] = True
            st.session_state['usuario_ativo'] = usuario
            st.success("Logado com sucesso!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")


def formatar_real(valor):
    """Auxiliar para formatar floats no padrão R$ 1.234,56"""
    if valor is None:
        valor = 0.0
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ==========================================
# DIRECIONAMENTO PRINCIPAL (MAIN)
# ==========================================

def main():
    criar_banco_de_dados()

    bloqueado, dias_restantes = verificar_licenca()

    if bloqueado:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.error("❌ **PERÍODO DE AVALIAÇÃO EXPIRADO**")
        st.markdown("""
            <div style='text-align: center; padding: 20px; border: 2px solid #fc8181; border-radius: 8px; background-color: #fff5f5;'>
                <h3 style='color: #c53030;'>O período de 30 dias de demonstração deste aplicativo chegou ao fim.</h3>
                <p style='font-size: 13pt;'>Para liberar o acesso definitivo ao sistema entre em contato.</p>
                <br>
                <a href='https://wa.me/5513922028978' target='_blank' style='text-decoration: none;'>
                    <div style='background-color: #25d366; color: white; padding: 12px 25px; border-radius: 8px; font-weight: bold; display: inline-block;'>
                        💬 Chamar no WhatsApp para Ativar Licença
                    </div>
                </a>
            </div>
        """, unsafe_allow_html=True)
        return

    if 'logado' not in st.session_state or not st.session_state['logado']:
        gerenciar_temas()
        st.sidebar.markdown("---")
        tela_login()
        return

    user = st.session_state['usuario_ativo']

    # Barra lateral fixa - Identificação e Temas
    st.sidebar.markdown(f"👤 Operador: **{user.upper()}**")
    st.sidebar.info(f"⏳ Teste Demo: **{dias_restantes} dias restantes**")

    # Chama o gerenciador de visual na barra lateral
    gerenciar_temas()

    if st.sidebar.button("🚪 Sair (Logout)", use_container_width=True):
        st.session_state['logado'] = False
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("<p style='font-weight: bold; margin-bottom: 5px; color: #4a5568;'>Menu Principal:</p>",
                        unsafe_allow_html=True)

    if 'menu_ativo' not in st.session_state:
        st.session_state['menu_ativo'] = "📋 Ordens de Serviço"

    if st.sidebar.button("📋 Ordens de Serviço", use_container_width=True,
                         type="secondary" if st.session_state['menu_ativo'] != "📋 Ordens de Serviço" else "primary"):
        st.session_state['menu_ativo'] = "📋 Ordens de Serviço"
        st.rerun()

    if st.sidebar.button("🚗 Cadastrar Veículo", use_container_width=True,
                         type="secondary" if st.session_state['menu_ativo'] != "🚗 Cadastrar Veículo" else "primary"):
        st.session_state['menu_ativo'] = "🚗 Cadastrar Veículo"
        st.rerun()

    if st.sidebar.button("📦 Estoque de Peças", use_container_width=True,
                         type="secondary" if st.session_state['menu_ativo'] != "📦 Estoque de Peças" else "primary"):
        st.session_state['menu_ativo'] = "📦 Estoque de Peças"
        st.rerun()

    if st.sidebar.button("💰 Efetivar Pagamento", use_container_width=True,
                         type="secondary" if st.session_state['menu_ativo'] != "💰 Efetivar Pagamento" else "primary"):
        st.session_state['menu_ativo'] = "💰 Efetivar Pagamento"
        st.rerun()

    if st.sidebar.button("📊 Relatórios & Caixa", use_container_width=True,
                         type="secondary" if st.session_state['menu_ativo'] != "📊 Relatórios" else "primary"):
        st.session_state['menu_ativo'] = "📊 Relatórios"
        st.rerun()

    # Chama o painel de segurança de dados na nuvem logo abaixo do menu principal
    gerenciar_banco_nuvem()

    menu = st.session_state['menu_ativo']

    # ==========================================
    # ABA: GERENCIAMENTO DE ORDENS DE SERVIÇO
    # ==========================================
    if menu == "📋 Ordens de Serviço":
        st.title("📋 Abertura de Ordens de Serviço")
        termo_busca = st.text_input("🔍 Buscar veículo por Placa ou Cliente").strip().upper()
        veiculo_selecioncionado = None

        if termo_busca:
            conn = sqlite3.connect("oficina.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, placa, marca, modelo, nome_cliente, whatsapp FROM veiculos WHERE placa LIKE ? OR nome_cliente LIKE ?",
                (f"%{termo_busca}%", f"%{termo_busca}%"))
            resultados = cursor.fetchall()
            conn.close()

            if resultados:
                opcoes_veiculos = {f"{r[1]} - {r[2]} {r[3]} (Dono: {r[4]})": r for r in resultados}
                escolha = st.selectbox("Selecione o veículo:", list(opcoes_veiculos.keys()))
                veiculo_selecioncionado = opcoes_veiculos[escolha]

        if veiculo_selecioncionado:
            id_veiculo, placa_v, marca_v, modelo_v, cliente_v, whats_v = veiculo_selecioncionado
            st.info(f"🚗 **Veículo:** {marca_v} {modelo_v} ({placa_v}) | **Cliente:** {cliente_v}")

            with st.form("form_nova_os"):
                defeito = st.text_area("Defeito Reclamado")
                servico = st.text_area("Serviço a ser Realizado")
                pecas = st.text_area("Peças Necessárias")
                col_v1, col_v2, col_v3 = st.columns(3)
                with col_v1:
                    v_mao_obra = st.number_input("Mão de Obra (R$)", min_value=0.0, format="%.2f")
                with col_v2:
                    v_pecas = st.number_input("Total Peças (R$)", min_value=0.0, format="%.2f")
                with col_v3:
                    status_os = st.selectbox("Status", ["Orçamento", "Em Andamento", "Pronto"])

                if st.form_submit_button("🛠️ Salvar Ordem de Serviço", use_container_width=True):
                    if defeito:
                        conn = sqlite3.connect("oficina.db")
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO ordens_servico (id_veiculo, defeito_reclamado, servico_realizado, pecas_utilizadas, valor_mao_obra, valor_pecas, valor_total, status, data_abertura, status_pagamento)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pendente')
                        """, (id_veiculo, defeito, servico, pecas, v_mao_obra, v_pecas, (v_mao_obra + v_pecas),
                              status_os, datetime.now().strftime("%d/%m/%Y %H:%M")))
                        conn.commit()
                        conn.close()
                        st.success("✅ Ordem de Serviço cadastrada com sucesso!")


    # ==========================================
    # ABA: CADASTRAR VEÍCULO
    # ==========================================
    elif menu == "🚗 Cadastrar Veículo":
        st.title("🚗 Cadastro de Veículos e Clientes")
        with st.form("form_cadastro_veiculo", clear_on_submit=True):
            placa = st.text_input("Placa").upper().strip()
            marca = st.selectbox("Marca",
                                 ["Chevrolet", "Fiat", "Ford", "Volkswagen", "Toyota", "Honda", "Hyundai", "Renault",
                                  "Outra"])
            modelo = st.text_input("Modelo")
            nome_cliente = st.text_input("Nome do Cliente")
            whatsapp = st.text_input("WhatsApp (com DDD)")

            if st.form_submit_button("💾 Salvar Cadastro", use_container_width=True):
                if placa and modelo and nome_cliente:
                    try:
                        conn = sqlite3.connect("oficina.db")
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO veiculos (placa, marca, modelo, nome_cliente, whatsapp, data_cadastro)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (placa, marca, modelo, nome_cliente, whatsapp, datetime.now().strftime("%d/%m/%Y")))
                        conn.commit()
                        conn.close()
                        st.success("✅ Cliente e veículo registrados!")
                    except sqlite3.IntegrityError:
                        st.error("❌ Placa já cadastrada.")


    # ==========================================
    # ABA: ESTOQUE DE PEÇAS
    # ==========================================
    elif menu == "📦 Estoque de Peças":
        st.title("📦 Controle de Estoque")
        with st.form("form_peca", clear_on_submit=True):
            c_barras = st.text_input("Código de Barras")
            n_peca = st.text_input("Nome da Peça")
            qtd = st.number_input("Quantidade", min_value=1)
            preco = st.number_input("Preço de Venda (R$)", min_value=0.0, format="%.2f")
            if st.form_submit_button("📥 Cadastrar Peça"):
                if c_barras and n_peca:
                    conn = sqlite3.connect("oficina.db")
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO pecas (codigo_barras, nome_peca, quantidade_estoque, preco_venda, data_cadastro) VALUES (?, ?, ?, ?, ?)",
                        (c_barras, n_peca, qtd, preco, datetime.now().strftime("%d/%m/%Y")))
                    conn.commit()
                    conn.close()
                    st.success("Peça cadastrada!")


    # ==========================================
    # ABA: 💰 EFETIVAR PAGAMENTO E ENVIAR WHATSAPP
    # ==========================================
    elif menu == "💰 Efetivar Pagamento":
        st.title("💰 Terminal de Efetivação Expressa")
        st.write(
            "Selecione uma ordem pendente para aplicar o pagamento, realizar o backup automático e enviar o recibo no WhatsApp.")

        conn = sqlite3.connect("oficina.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT os.id, v.placa, v.nome_cliente, os.valor_total, v.whatsapp, v.modelo, os.valor_mao_obra, os.valor_pecas
            FROM ordens_servico os
            JOIN veiculos v ON os.id_veiculo = v.id
            WHERE os.status_pagamento != 'Pago' OR os.status_pagamento IS NULL
            ORDER BY os.id DESC
        """)
        pendentes = cursor.fetchall()
        conn.close()

        if not pendentes and 'pagamento_sucesso' not in st.session_state:
            st.success("🎉 Todas as ordens de serviço encontram-se pagas!")
        else:
            if 'pagamento_sucesso' not in st.session_state:
                opcoes_pendentes = {
                    f"O.S. N° {p[0]} | {p[1]} - {p[2]} (Valor: {formatar_real(p[3])})": p
                    for p in pendentes
                }

                escolha_os = st.selectbox("Selecione a O.S. para Baixa Financeira:", list(opcoes_pendentes.keys()))
                os_sel = opcoes_pendentes[escolha_os]
                id_os, placa, cliente, valor_total, whats_cliente, modelo_v, m_obra, v_pecas = os_sel

                st.markdown("---")

                with st.form("form_fechamento"):
                    st.markdown(f"📋 **Cliente:** {cliente} | **Veículo:** {modelo_v} ({placa})")
                    st.markdown(
                        f"💰 **Total a Receber:** <span style='font-size:18pt; color:#2f855a; font-weight:bold;'>{formatar_real(valor_total)}</span>",
                        unsafe_allow_html=True)

                    forma_pagto = st.selectbox("Forma de Recebimento:",
                                               ["Pix", "Dinheiro", "Cartão de Débito", "Cartão de Crédito"])

                    confirmar_baixa = st.form_submit_button("✅ Efetivar e Atualizar Caixa (Gera Backup)",
                                                            use_container_width=True)

                    if confirmar_baixa:
                        arquivo_bkp = realizar_backup()

                        conn = sqlite3.connect("oficina.db")
                        cursor = conn.cursor()
                        data_pago = datetime.now().strftime("%d/%m/%Y %H:%M")
                        cursor.execute("""
                            UPDATE ordens_servico 
                            SET status = 'Finalizado', forma_pagamento = ?, status_pagamento = 'Pago', data_pagamento = ? 
                            WHERE id = ?
                        """, (forma_pagto, data_pago, id_os))
                        conn.commit()
                        conn.close()

                        st.session_state['pagamento_sucesso'] = {
                            "id_os": id_os, "cliente": cliente, "placa": placa, "modelo": modelo_v,
                            "m_obra": m_obra, "v_pecas": v_pecas, "total": valor_total, "forma": forma_pagto,
                            "whats": whats_cliente, "backup": arquivo_bkp
                        }
                        st.rerun()

            if 'pagamento_sucesso' in st.session_state:
                dados = st.session_state['pagamento_sucesso']

                st.success(f"✅ O.S. N° {dados['id_os']} marcada como PAGA! Caixa Alimentado com sucesso.")
                if dados['backup']:
                    st.toast(f"💾 Cópia de Segurança salva em: {dados['backup']}", icon="💾")

                mensagem_recibo = (
                    f"🧾 *COMPROVANTE DE PAGAMENTO - OFICINA PRO*\n\n"
                    f"Prezado(a) *{dados['cliente']}*, seu pagamento foi processado com sucesso!\n\n"
                    f"📌 *DETALHES DA ORDEM N° {dados['id_os']}*\n"
                    f"🚗 Veículo: {dados['modelo']} (Placa: {dados['placa']})\n"
                    f"🔧 Mão de Obra: {formatar_real(dados['m_obra'])}\n"
                    f"📦 Peças Aplicadas: {formatar_real(dados['v_pecas'])}\n"
                    f"----------------------------------\n"
                    f"💰 *VALOR TOTAL RECEBIDO: {formatar_real(dados['total'])}*\n"
                    f"💳 Forma de Pagamento: *{dados['forma']}*\n\n"
                    f"Obrigado pela preferência e confiança! 👍"
                )

                fone_limpo = "".join([c for c in str(dados['whats']) if c.isdigit()])
                if fone_limpo and not fone_limpo.startswith("55") and len(fone_limpo) >= 10:
                    fone_limpo = "55" + fone_limpo

                texto_codificado = urllib.parse.quote(mensagem_recibo)
                link_whatsapp = f"https://wa.me/{fone_limpo}?text={texto_codificado}"

                st.markdown("### 🔑 Enviar Comprovante ao Cliente:")

                st.markdown(f"""
                    <a href="{link_whatsapp}" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #25d366; color: white; padding: 12px 20px; border-radius: 6px; font-weight: bold; text-align: center; font-size: 13pt; margin-bottom: 15px;">
                            💬 Enviar Recibo e Resumo por WhatsApp ({dados['whats']})
                        </div>
                    </a>
                """, unsafe_allow_html=True)

                if st.button("📊 Finalizar e Ir Para o Caixa", use_container_width=True, type="primary"):
                    st.session_state.pop('pagamento_sucesso', None)
                    st.session_state['menu_ativo'] = "📊 Relatórios"
                    st.rerun()


    # ==========================================
    # ABA: PAINEL DE CONTROLE E RELATÓRIOS
    # ==========================================
    elif menu == "📊 Relatórios":
        st.title("📊 Fluxo de Caixa & Relatórios Gerenciais")

        conn = sqlite3.connect("oficina.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT os.id, v.placa, v.nome_cliente, os.defeito_reclamado, os.valor_total, 
                   os.status, os.data_abertura, os.forma_pagamento, os.status_pagamento
            FROM ordens_servico os
            JOIN veiculos v ON os.id_veiculo = v.id
            ORDER BY os.id DESC
        """)
        todas_os = cursor.fetchall()
        conn.close()

        # Faturamento Real por Caixa (Apenas o que está pago)
        t_pix = sum(o[4] for o in todas_os if o[8] == "Pago" and o[7] == "Pix")
        t_dinheiro = sum(o[4] for o in todas_os if o[8] == "Pago" and o[7] == "Dinheiro")
        t_debito = sum(o[4] for o in todas_os if o[8] == "Pago" and o[7] == "Cartão de Débito")
        t_credito = sum(o[4] for o in todas_os if o[8] == "Pago" and o[7] == "Cartão de Crédito")
        t_geral = t_pix + t_dinheiro + t_debito + t_credito

        f1, f2, f3, f4, f5 = st.columns(5)
        with f1:
            st.metric(label="💎 Pix", value=formatar_real(t_pix))
        with f2:
            st.metric(label="💵 Dinheiro", value=formatar_real(t_dinheiro))
        with f3:
            st.metric(label="💳 Débito", value=formatar_real(t_debito))
        with f4:
            st.metric(label="💳 Crédito", value=formatar_real(t_credito))
        with f5:
            st.metric(label="📈 Total Geral", value=formatar_real(t_geral))

        st.markdown("<br>", unsafe_allow_html=True)
        st.write("### 🔍 Histórico de Atendimentos Cadastrados")

        for os_item in todas_os:
            id_os, placa, cliente, defeito, total, status, data, f_pag, s_pag = os_item
            tag_f = f" [{f_pag}]" if f_pag else ""
            with st.expander(f"🛠️ O.S. N° {id_os} | {placa} - {cliente} | Pago: {s_pag}{tag_f}"):
                st.write(f"**Data Abertura:** {data}")
                st.write(f"**Defeito Reclamado:** {defeito}")
                st.write(f"**Valor total:** {formatar_real(total)}")
                st.write(f"**Status Operacional:** {status}")


if __name__ == "__main__":
    main()
