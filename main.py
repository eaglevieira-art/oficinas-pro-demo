import sqlite3
import webbrowser
import urllib.parse
from datetime import datetime
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


# ==============================================================================
# MÓDULO DE PAGAMENTOS (Integrado nativamente ao Streamlit)
# ==============================================================================
def abrir_tela_pagamento_streamlit(nome_cliente, whatsapp_cliente):
    st.markdown("### 💳 Área de Pagamento & Comprovante")
    st.info("Conclua o fechamento do serviço e envie o comprovante diretamente para o WhatsApp do cliente.")

    col1, col2 = st.columns(2)
    with col1:
        nome_pag = st.text_input("Confirmar Nome do Cliente:", value=nome_cliente, key="nome_pag")
        forma_pagamento = st.selectbox(
            "Selecione a Forma de Pagamento:",
            ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Pix", "QR Code", "Boleto Bancário"],
            key="forma_pag"
        )
    with col2:
        tel_limpo = "".join(filter(str.isdigit, whatsapp_cliente))
        if not tel_limpo.startswith("55"):
            tel_limpo = "55" + tel_limpo

        telefone_pag = st.text_input("Confirmar WhatsApp:", value=tel_limpo, key="tel_pag")
        valor_pag = st.text_input("Valor Total (R$):", value="150.00", key="val_pag")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Gerar Comprovante Oficial"):
        if nome_pag and telefone_pag and valor_pag:
            mensagem = (
                f"Olá, {nome_pag}! 👋\n\n"
                f"Aqui está o comprovante do seu serviço na *APPoficinas*:\n\n"
                f"💰 *Valor:* R$ {valor_pag}\n"
                f"💳 *Forma de Pagamento:* {forma_pagamento}\n\n"
                f"Obrigado pela preferência! 🚗🔧"
            )
            mensagem_codificada = urllib.parse.quote(mensagem)
            url_link = f"https://wa.me/{telefone_pag}?text={mensagem_codificada}"

            st.markdown(
                f'<a href="{url_link}" target="_blank" style="text-decoration: none;">'
                f'<div style="background-color: #25d366; color: white; padding: 15px 20px; '
                f'border-radius: 8px; font-weight: bold; text-align: center; margin-top: 10px; '
                f'cursor: pointer; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); font-size: 14pt;">'
                f'💬 Clique Aqui para Abrir e Enviar no WhatsApp'
                f'</div></a>',
                unsafe_allow_html=True
            )
            st.success("Link do comprovante gerado! Clique no botão verde acima para enviar.")
        else:
            st.error("⚠️ Por favor, preencha todos os campos da área de pagamento.")


# ==============================================================================
# CONFIGURAÇÃO E INTERFACE PRINCIPAL DO APP
# ==============================================================================

st.set_page_config(page_title="Oficina Pro", page_icon="🛠️", layout="wide")

# --- ESTILO CSS CUSTOMIZADO UNIFICADO ---
st.markdown("""
    <style>
        html, body, [class*="css"], p, label, input, select, textarea { font-size: 12pt !important; }

        /* Botões Padrão do Sistema */
        div.stButton > button {
            font-size: 12pt !important; border-radius: 8px !important;
            background-color: #3182ce !important; color: white !important;
            border: none !important; padding: 8px 20px !important;
            transition: all 0.3s ease !important; font-weight: bold !important;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1) !important;
        }
        div.stButton > button:hover {
            background-color: #2b6cb0 !important; transform: translateY(-2px) !important;
            box-shadow: 0px 6px 12px rgba(49, 130, 206, 0.3) !important;
        }

        /* --- PADRONIZAÇÃO COMPLETA DAS ABAS (TODAS AS TELAS) --- */
        button[data-baseweb="tab"] {
            background-color: #f0f4f8 !important;
            color: #4a5568 !important;
            border-radius: 8px 8px 0px 0px !important;
            padding: 10px 20px !important;
            margin-right: 6px !important;
            border: 1px solid #e2e8f0 !important;
            border-bottom: none !important;
            transition: all 0.2s ease-in-out !important;
            font-weight: 500 !important;
        }

        button[data-baseweb="tab"]:hover {
            background-color: #e2e8f0 !important;
            color: #2b6cb0 !important;
            cursor: pointer;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #ebf8ff !important;
            color: #2b6cb0 !important;
            font-weight: bold !important;
            border: 2px solid #bee3f8 !important;
            border-bottom: none !important;
        }
    </style>
""", unsafe_allow_html=True)


# --- BANCO DE DADOS ---
def conectar_banco():
    return sqlite3.connect('oficina.db')


def criar_banco_de_dados():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    # Adicionada a coluna criado_por para segurança de dados por usuário
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS clientes
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       nome
                       TEXT
                       NOT
                       NULL,
                       tipo_documento
                       TEXT,
                       documento
                       TEXT,
                       whatsapp
                       TEXT
                       NOT
                       NULL,
                       email
                       TEXT,
                       cidade
                       TEXT,
                       endereco
                       TEXT,
                       criado_por
                       TEXT
                       DEFAULT
                       'admin'
                   )
                   ''')

    # Atualização de segurança para bancos de dados já criados anteriormente
    try:
        cursor.execute("ALTER TABLE clientes ADD COLUMN criado_por TEXT DEFAULT 'admin'")
    except sqlite3.OperationalError:
        pass  # A coluna já existe

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS veiculos
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       cliente_id
                       INTEGER
                       NOT
                       NULL,
                       marca
                       TEXT
                       NOT
                       NULL,
                       modelo
                       TEXT
                       NOT
                       NULL,
                       placa
                       TEXT
                       NOT
                       NULL
                       UNIQUE,
                       ano_fabricacao
                       TEXT,
                       motorizacao
                       TEXT,
                       cor
                       TEXT,
                       km
                       INTEGER,
                       checklist_arranha
                       TEXT,
                       checklist_estepe
                       TEXT,
                       nivel_combustivel
                       TEXT,
                       FOREIGN
                       KEY
                   (
                       cliente_id
                   ) REFERENCES clientes
                   (
                       id
                   ))
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS ordens_servico
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       veiculo_id
                       INTEGER
                       NOT
                       NULL,
                       mecanico_responsavel
                       TEXT,
                       descricao_defeito
                       TEXT,
                       status
                       TEXT
                       NOT
                       NULL
                       DEFAULT
                       "Aguardando Orçamento",
                       data_inicio
                       TEXT,
                       data_fim
                       TEXT,
                       valor_total
                       REAL
                       DEFAULT
                       0.0,
                       FOREIGN
                       KEY
                   (
                       veiculo_id
                   ) REFERENCES veiculos
                   (
                       id
                   ))
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS itens_os
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       os_id
                       INTEGER
                       NOT
                       NULL,
                       tipo
                       TEXT
                       NOT
                       NULL,
                       descricao
                       TEXT
                       NOT
                       NULL,
                       quantidade
                       INTEGER
                       NOT
                       NULL
                       DEFAULT
                       1,
                       preco_unitario
                       REAL
                       NOT
                       NULL,
                       FOREIGN
                       KEY
                   (
                       os_id
                   ) REFERENCES ordens_servico
                   (
                       id
                   ))
                   ''')
    conexao.commit()
    conexao.close()


def listar_clientes(usuario_ativo):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    # Se for o usuário comum, ele só puxa os clientes que ele mesmo cadastrou
    if usuario_ativo == "usu":
        cursor.execute('SELECT id, nome FROM clientes WHERE criado_por = ?', (usuario_ativo,))
    else:
        cursor.execute('SELECT id, nome FROM clientes')
    dados = cursor.fetchall()
    conexao.close()
    return dados


def buscar_resumo_os(os_id):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute('''
                   SELECT os.id,
                          os.mecanico_responsavel,
                          os.descricao_defeito,
                          os.status,
                          os.data_inicio,
                          os.data_fim,
                          os.valor_total,
                          v.modelo,
                          v.placa,
                          c.nome,
                          c.whatsapp
                   FROM ordens_servico os
                            JOIN veiculos v ON os.veiculo_id = v.id
                            JOIN clientes c ON v.cliente_id = c.id
                   WHERE os.id = ?
                   ''', (os_id,))
    os_dados = cursor.fetchone()
    cursor.execute('SELECT tipo, descricao, quantidade, preco_unitario FROM itens_os WHERE os_id = ?', (os_id,))
    itens = cursor.fetchall()
    conexao.close()
    return os_dados, itens


def gerar_recibo_pdf(os_id):
    dados, itens = buscar_resumo_os(os_id)
    if not dados: return
    id_os, mecanico, defeito, status, dt_inicio, dt_fim, total, modelo, placa, cliente_nome, whatsapp = dados
    nome_arquivo = f"Recibo_OS_{id_os}.pdf"
    pdf = canvas.Canvas(nome_arquivo, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 750, "SISTEMA OFICINA PRO - RECIBO")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 730, f"Cliente: {cliente_nome} | Veículo: {modelo} ({placa})")
    pdf.drawString(50, 715, f"OS #: {id_os} | Status: {status} | Total: R$ {total:.2f}")
    pdf.save()


def enviar_whatsapp_tela(os_id, tipo_mensagem):
    dados, _ = buscar_resumo_os(os_id)
    if not dados: return
    id_os, _, defeito, _, _, _, total, modelo, placa, cliente_nome, whatsapp = dados
    telefone = "".join(filter(str.isdigit, whatsapp))
    if tipo_mensagem == "orcamento":
        texto = f"Olá *{cliente_nome}*! O orçamento do seu *{modelo}* ({placa}) ficou em *R$ {total:.2f}*. Pode aprovar?"
    else:
        texto = f"Olá *{cliente_nome}*! O seu *{modelo}* ({placa}) já está PRONTO! 🎉 Total: *R$ {total:.2f}*."
    texto_codificado = urllib.parse.quote(texto)
    link = f"https://api.whatsapp.com/send?phone=55{telefone}&text={texto_codificado}"
    webbrowser.open(link)


# --- SISTEMA DE AUTENTICAÇÃO (LOGIN) ---
def tela_login():
    st.markdown("<h2 style='text-align: center;'>🛠️ Login - Sistema Oficina Pro</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_login"):
            usuario = st.text_input("Usuário:")
            senha = st.text_input("Senha:", type="password")
            btn_entrar = st.form_submit_button("Entrar no Sistema")

            if btn_entrar:
                if usuario == "admin" and senha == "admin":
                    st.session_state['logado'] = True
                    st.session_state['usuario_ativo'] = "admin"
                    st.rerun()
                elif usuario == "usu" and senha == "usu":
                    st.session_state['logado'] = True
                    st.session_state['usuario_ativo'] = "usu"
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos.")


# --- DIRECIONAMENTO PRINCIPAL ---
def main():
    criar_banco_de_dados()

    # Gerencia o estado de Login do app
    if 'logado' not in st.session_state or not st.session_state['logado']:
        tela_login()
        return

    # Se estiver logado, carrega o painel correspondente
    user = st.session_state['usuario_ativo']

    # Barra lateral customizada com botão de Logout
    st.sidebar.markdown(f"👤 Conectado como: **{user.upper()}**")
    if st.sidebar.button("🚪 Sair (Logout)"):
        st.session_state['logado'] = False
        st.session_state.pop('cliente_atual_nome', None)
        st.session_state.pop('cliente_atual_whats', None)
        st.rerun()

    st.sidebar.markdown("---")

    # Definição de telas com base no tipo de usuário (usuário comum não vê Relatórios)
    opcoes_menu = ["👥 Cadastrar Cliente", "🚗 Entrada de Veículo", "📋 Painel de OS"]
    if user == "admin":
        opcoes_menu.append("📊 Relatório Excel")

    opcao = st.sidebar.radio("Escolha uma Tela:", opcoes_menu)

    # --- TELA 1: CADASTRO COMPLETO DO CLIENTE ---
    if opcao == "👥 Cadastrar Cliente":
        st.subheader("Gerenciamento de Clientes")

        aba_cadastro, aba_pagamento = st.tabs(["📝 Formulário de Cadastro", "💳 Fechamento & Pagamento"])

        with aba_cadastro:
            with st.form("form_cliente", clear_on_submit=False):
                salvar = st.form_submit_button("💾 Salvar Novo Cliente")
                st.markdown("<br>", unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    nome = st.text_input("Nome Completo / Razão Social *")
                    tipo_doc = st.selectbox("Tipo de Documento", ["CPF", "CNPJ"])
                    documento = st.text_input("Número do Documento (Apenas números)")
                    whatsapp = st.text_input("WhatsApp (com DDD, apenas números) *", placeholder="11999998888")
                with col2:
                    email = st.text_input("E-mail", placeholder="exemplo@email.com")
                    cidade = st.text_input("Cidade / Estado", placeholder="Ex: São Paulo - SP")
                    endereco = st.text_input("Endereço Completo (Rua, Nº, Bairro)")

            if salvar:
                if nome and whatsapp:
                    conexao = conectar_banco()
                    cursor = conexao.cursor()
                    # Salva identificando quem foi o usuário que criou o registro
                    cursor.execute('''
                                   INSERT INTO clientes (nome, tipo_documento, documento, whatsapp, email, cidade,
                                                         endereco, criado_por)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                   ''', (nome, tipo_doc, documento, whatsapp, email, cidade, endereco, user))
                    conexao.commit()
                    conexao.close()
                    st.success(
                        f"✅ Cliente '{nome}' cadastrado com sucesso! Mude para a aba 'Fechamento & Pagamento' no topo.")
                    st.session_state['cliente_atual_nome'] = nome
                    st.session_state['cliente_atual_whats'] = whatsapp
                else:
                    st.error("⚠️ Preencha os campos obrigatórios (Nome e WhatsApp).")

        with aba_pagamento:
            if 'cliente_atual_nome' in st.session_state:
                abrir_tela_pagamento_streamlit(st.session_state['cliente_atual_nome'],
                                               st.session_state['cliente_atual_whats'])
            else:
                st.info("ℹ️ Preencha e salve o cadastro na primeira aba para liberar o fechamento financeiro.")

    # --- TELA 2: ENTRADA DE VEÍCULO ---
    elif opcao == "🚗 Entrada de Veículo":
        st.subheader("Registro de Entrada de Veículo & Checklist")
        clientes = listar_clientes(user)  # Filtra conforme o nível do usuário
        if not clientes:
            st.warning("⚠️ Nossos registros não apontam clientes cadastrados por você para vincular a este veículo.")
        else:
            lista_clientes_formatada = {c[1]: c[0] for c in clientes}
            cliente_selecionado = st.selectbox("Selecione o Dono do Veículo:", list(lista_clientes_formatada.keys()))

            with st.form("form_veiculo", clear_on_submit=True):
                btn_salvar_veiculo = st.form_submit_button("⚙️ Registrar Entrada e Abrir OS")
                st.markdown("<br>", unsafe_allow_html=True)

                aba_ficha, aba_checklist, aba_triagem = st.tabs(
                    ["🚘 Ficha Técnica", "📋 Checklist de Inspeção", "🔧 Triagem Inicial"])

                with aba_ficha:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        marca = st.text_input("Marca (Ex: Fiat, Volkswagen) *")
                        modelo = st.text_input("Modelo do Carro (Ex: Uno, Gol) *")
                    with col2:
                        placa = st.text_input("Placa *").upper()
                        ano_fabricacao = st.text_input("Ano de Fabricação (Ex: 2018/2019) *")
                    with col3:
                        motorizacao = st.text_input("Motorização (Ex: 1.0, 1.6, 2.0 Turbo)")
                        cor = st.text_input("Cor do Veículo")
                    km = st.number_input("Quilometragem (KM) Atual:", min_value=0, step=1)

                with aba_checklist:
                    col_ch1, col_ch2, col_ch3 = st.columns(3)
                    with col_ch1:
                        checklist_arranha = st.selectbox("Possui Arranhões ou Amassados?",
                                                         ["Não", "Sim (Descrever na triagem)"])
                    with col_ch2:
                        checklist_estepe = st.selectbox("O Estepe está no veículo?", ["Sim", "Não"])
                    with col_ch3:
                        nivel_combustivel = st.selectbox("Nível do Combustível:",
                                                         ["Vazio", "1/4", "1/2", "3/4", "Cheio"])

                with aba_triagem:
                    defeito = st.text_area("Reclamação / Defeito Relatado pelo Cliente *")
                    mecanico = st.text_input("Mecânico Responsável pela Triagem")

            if btn_salvar_veiculo:
                if marca and modelo and placa and ano_fabricacao and defeito:
                    id_cliente = lista_clientes_formatada[cliente_selecionado]
                    conexao = conectar_banco()
                    cursor = conexao.cursor()
                    cursor.execute('''
                                   INSERT INTO veiculos (cliente_id, marca, modelo, placa, ano_fabricacao,
                                                         motorizacao, cor, km, checklist_arranha, checklist_estepe,
                                                         nivel_combustivel)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                   ''', (id_cliente, marca, modelo, placa, ano_fabricacao, motorizacao, cor, km,
                                         checklist_arranha, checklist_estepe, nivel_combustivel))
                    id_veiculo = cursor.lastrowid
                    cursor.execute(
                        'INSERT INTO ordens_servico (veiculo_id, descricao_defeito, mecanico_responsavel, data_inicio) VALUES (?, ?, ?, ?)',
                        (id_veiculo, defeito, mecanico, datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
                    conexao.commit()
                    conexao.close()
                    st.success(f"🚗 {marca} {modelo} ({placa}) registrado e OS aberta com sucesso!")
                else:
                    st.error("⚠️ Preencha todos os campos obrigatórios.")

    # --- TELA 3: PAINEL DE OS ---
    elif opcao == "📋 Painel de OS":
        st.subheader("Gerenciamento de Ordens de Serviço (OS)")
        conexao = conectar_banco()
        cursor = conexao.cursor()

        # Filtro de segurança: 'usu' só visualiza ordens vinculadas aos clientes dele
        if user == "usu":
            cursor.execute('''
                           SELECT os.id, c.nome, v.modelo, os.status, os.valor_total
                           FROM ordens_servico os
                                    JOIN veiculos v ON os.veiculo_id = v.id
                                    JOIN clientes c ON v.cliente_id = c.id
                           WHERE c.criado_por = ?
                           ''', (user,))
        else:
            cursor.execute('''
                           SELECT os.id, c.nome, v.modelo, os.status, os.valor_total
                           FROM ordens_servico os
                                    JOIN veiculos v ON os.veiculo_id = v.id
                                    JOIN clientes c ON v.cliente_id = c.id
                           ''')

        todas_os = cursor.fetchall()
        conexao.close()

        if todas_os:
            lista_os_formatada = {f"OS #{o[0]} - {o[1]} ({o[2]})": o[0] for o in todas_os}
            os_selecionada = st.selectbox("Selecione uma OS para Gerenciar:", list(lista_os_formatada.keys()))
            id_os_atual = lista_os_formatada[os_selecionada]

            st.markdown("#### ⚡ Ações Rápidas da OS")
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button("🏁 Fechar OS e Gerar PDF", use_container_width=True):
                    conexao = conectar_banco()
                    cursor = conexao.cursor()
                    cursor.execute('SELECT SUM(quantidade * preco_unitario) FROM itens_os WHERE os_id = ?',
                                   (id_os_atual,))
                    total = cursor.fetchone()[0] or 0.0
                    cursor.execute(
                        'UPDATE ordens_servico SET status = "Concluído", data_fim = ?, valor_total = ? WHERE id = ?',
                        (datetime.now().strftime('%d/%m/%Y %H:%M:%S'), total, id_os_atual))
                    conexao.commit()
                    conexao.close()
                    gerar_recibo_pdf(id_os_atual)
                    st.success(f"🏁 OS #{id_os_atual} Concluída!")
            with col_btn2:
                if st.button("💬 Enviar Orçamento WhatsApp", use_container_width=True):
                    enviar_whatsapp_tela(id_os_atual, "orcamento")
            with col_btn3:
                if st.button("🎉 Avisar Carro Pronto WhatsApp", use_container_width=True):
                    enviar_whatsapp_tela(id_os_atual, "pronto")

            st.markdown("---")

            aba_lancar, aba_resumo = st.tabs(["🛠️ Adicionar Peças/Serviços", "📄 Visualizar Resumo Atual"])

            with aba_lancar:
                with st.form("form_itens"):
                    col_it1, col_it2, col_it3, col_it4 = st.columns([2, 4, 2, 2])
                    with col_it1:
                        tipo_item = st.selectbox("Tipo:", ["PECA", "SERVICO"])
                    with col_it2:
                        desc_item = st.text_input("Descrição do Item:")
                    with col_it3:
                        qtd_item = st.number_input("Qtd:", min_value=1, value=1)
                    with col_it4:
                        preco_item = st.number_input("Preço (R$):", min_value=0.0, value=0.0)

                    add_item = st.form_submit_button("➕ Incluir Item na Ordem")

                if add_item and desc_item:
                    conexao = conectar_banco()
                    cursor = conexao.cursor()
                    cursor.execute(
                        'INSERT INTO itens_os (os_id, tipo, descricao, database, quantidade, preco_unitario) VALUES (?, ?, ?, ?, ?)'
                        if False else 'INSERT INTO itens_os (os_id, tipo, descricao, quantidade, preco_unitario) VALUES (?, ?, ?, ?, ?)',
                        (id_os_atual, tipo_item, desc_item, qtd_item, preco_item))
                    conexao.commit()
                    conexao.close()
                    st.success("✅ Item adicionado!")

            with aba_resumo:
                os_dados, itens = buscar_resumo_os(id_os_atual)
                if os_dados:
                    st.markdown(f"**Cliente:** {os_dados[9]} | **Veículo:** {os_dados[7]} ({os_dados[8]})")
                    st.markdown(f"**Situação Atual:** `{os_dados[3]}`")
                    if itens:
                        import pandas as pd
                        df_itens = pd.DataFrame(itens, columns=["Tipo", "Descrição", "Qtd", "Preço Unitário"])
                        st.table(df_itens)
                    else:
                        st.info("Nenhum item adicionado a esta OS ainda.")
        else:
            st.info("Nenhuma Ordem de Serviço encontrada para o seu nível de acesso.")

    # --- TELA 4: RELATÓRIOS (EXCLUSIVA ADMIN) ---
    elif opcao == "📊 Relatório Excel" and user == "admin":
        st.subheader("Exportar Relatório de Caixa e OS (Restrito: Administrador)")

        conexao = conectar_banco()
        cursor = conexao.cursor()
        cursor.execute(
            'SELECT os.id, c.nome, v.modelo, os.status, os.valor_total, os.data_inicio FROM ordens_servico os JOIN veiculos v ON os.veiculo_id = v.id JOIN clientes c ON v.cliente_id = c.id')
        dados = cursor.fetchall()
        conexao.close()

        import pandas as pd
        df = pd.DataFrame(dados, columns=["Numero_OS", "Cliente", "Veiculo", "Status", "Valor_Total_R$", "Data_Inicio"])
        csv = df.to_csv(index=False, sep=";").encode('utf-8-sig')

        st.download_button(label="📥 Baixar Planilha para Excel", data=csv, file_name="relatorio_oficina.csv",
                           mime="text/csv")
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("#### 📋 Pré-visualização dos Dados Correntes")
        st.dataframe(df, use_container_width=True)


if __name__ == "__main__":
    main()