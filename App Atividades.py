from datetime import datetime, timedelta
import json
import random

# Nome do app Terminal Activity

ARQUIVO_TAREFAS = "arq_atividades_app_v1.0.json"
ARQUIVO_USUARIOS = "arq_usuarios_app_v1.0.json"

def inicializar_arquivo_tarefas():
    global data_do_sistema
    try:
        with open(ARQUIVO_TAREFAS, "r") as arquivo:
            dados = json.load(arquivo)
            if "ultima_verificacao" not in dados or "atividades" not in dados:
                raise ValueError("Estrutura do arquivo inválida.")
    except (FileNotFoundError, ValueError):
        dados = {
            "ultima_verificacao": data_do_sistema,  # Usa a variável global corretamente inicializada
            "atividades": []
        }
        with open(ARQUIVO_TAREFAS, "w") as arquivo:
            json.dump(dados, arquivo, indent=4)



class Usuario:
    def __init__(self, nome, id, senha, bio, data_criacao):
        self.nome = nome
        self.id = id
        self.senha = senha
        self.bio = bio
        self.data_criacao = datetime.strptime(data_criacao, "%d/%m/%y").date()
        self.atividades = []

    def salvar_usuario(self):
        try:
            usuarios = Usuario.carregar_usuarios()
        except FileNotFoundError:
            usuarios = []

        usuario_dict = {
            "nome": self.nome,
            "id": self.id,
            "senha": self.senha,
            "bio": self.bio,
            "data_criacao": self.data_criacao.strftime("%d/%m/%y"),
            "atividades": self.atividades,
        }

        usuarios.append(usuario_dict)

        with open(ARQUIVO_USUARIOS, "w") as arquivo:
            json.dump(usuarios, arquivo, indent=4)
            return usuario_dict

    @staticmethod
    def carregar_usuarios():
        try:
            with open(ARQUIVO_USUARIOS, "r") as arquivo:
                return json.load(arquivo)
        except FileNotFoundError:
            return []
     
    @staticmethod
    def listar_usuarios():
        usuarios = Usuario.carregar_usuarios()
        if not usuarios:
            print("Nenhum usuário encontrado.")
            return

        print("\nLista de Usuários:")
        for i, usuario in enumerate(usuarios, start=1):
            print(f"{i}. Nome: {usuario['nome']}")
            print(f"   ID: {usuario['id']}")
            print(f"   Biografia: {usuario['bio']}")
            print(f"   Data de Criação: {usuario['data_criacao']}")
            print("-" * 30)

    @staticmethod
    def criar_usuario():
        global data_do_sistema
        usuarios = Usuario.carregar_usuarios()

        while True:
            nome = input("\nDigite o nome do usuário\nOu digite 0 para voltar: ")
            
            if nome == "0":
                print("\nVoltando...")
                break
            
            elif any(usuario["nome"] == nome for usuario in usuarios):
                print("Já existe um usuário com esse nome, tente novamente.\n")
            
            else:
                while True:
                    senha = input("Crie uma senha\na senha não pode ser o número 0: ")
                    if senha == "0":
                        print("\nA senha não pode ser 0, escolha outra senha.")
                        continue
                    verificar_senha = input("Digite novamente sua senha: ")
                    if senha == verificar_senha:
                        break
                    else:
                        print("Senha diferente, tente novamente.")

                bio = input("Digite a sua biografia: ")

                # Geração de ID único
                ids_existentes = {usuario["id"] for usuario in Usuario.carregar_usuarios()}
                while True:
                    id = random.randint(1, 1000)
                    if id not in ids_existentes:
                        break  # Gera um ID único e sai do loop
                
                data_criacao = data_do_sistema.strftime("%d/%m/%y")

                novo_usuario = Usuario(nome, id, senha, bio, data_criacao)
                novo_usuario.salvar_usuario()
                print(f"Usuário criado com sucesso! ID: {id}")
                return novo_usuario

    @staticmethod
    def remover_usuario(nome):  # Remove o usuário e todas as atividades relacionadas a ele
        usuarios = Usuario.carregar_usuarios()
        usuario_encontrado = None

        for usuario in usuarios:
            if usuario["nome"] == nome:
                usuario_encontrado = usuario
                break  # Interrompe o loop assim que encontra o usuário

        if not usuario_encontrado:
            print(f"Erro: Nenhum usuário encontrado com o nome '{nome}'.")
            return

        # Remove o usuário da lista
        usuarios.remove(usuario_encontrado)

        # Atualiza o arquivo JSON dos usuários
        with open(ARQUIVO_USUARIOS, "w") as arquivo:
            json.dump(usuarios, arquivo, indent=4)

        # Remover atividades vinculadas ao usuário
        atividades = Atividade.carregar_atividades()
        atividades = [atividade for atividade in atividades if atividade.get("usuario") != nome]

        with open(ARQUIVO_TAREFAS, "w") as arquivo:
            json.dump(atividades, arquivo, indent=4)

        print(f"Usuário '{nome}' e suas atividades foram removidos com sucesso.")

    @staticmethod
    def modificar_usuario(usuario_logado):

        usuarios = Usuario.carregar_usuarios()

        while True:
            print("\nO que deseja modificar?")
            print("1. Nome")
            print("2. Biografia")
            print("3. Senha")
            print("0. Voltar")

            opcao = input("\nEscolha uma opção: ")

            if opcao == "1":  # Modificar nome
                novo_nome = input("Digite o novo nome\nOu 0 para cancelar: ")
                if any(u["nome"] == novo_nome for u in usuarios):
                    print("Erro: Já existe um usuário com este nome.")
                
                elif novo_nome == "0":
                    pass

                else:
                    for usuario in usuarios:
                        if usuario["id"] == usuario_logado["id"]:  # Localiza pelo ID único
                            usuario["nome"] = novo_nome
                            usuario_logado["nome"] = novo_nome  # Atualiza também na sessão do usuário logado
                            print("Nome atualizado com sucesso!")

            elif opcao == "2":  # Modificar biografia
                nova_bio = input("Digite a nova biografia\nOu digite 0 para cancelar: ")
                if nova_bio == "0":
                    pass
                    
                for usuario in usuarios:
                    if usuario["id"] == usuario_logado["id"]:
                        usuario["bio"] = nova_bio
                        usuario_logado["bio"] = nova_bio
                        print("\nBiografia atualizada com sucesso!\n")

            elif opcao == "3":  # Modificar senha
                while True:
                    nova_senha = input("Digite a nova senha\nOu digite 0 para cancelar: ")

                    if nova_senha == "0":
                        pass

                    else:
                        confirmar_senha = input("Confirme a nova senha: ")
                        if nova_senha == confirmar_senha:
                            for usuario in usuarios:
                                if usuario["id"] == usuario_logado["id"]:
                                    usuario["senha"] = nova_senha
                                    usuario_logado["senha"] = nova_senha
                                    print("Senha atualizada com sucesso!")
                                    break
                            break
                        else:
                            print("As senhas não coincidem. Tente novamente.")

            elif opcao == "0":  # Voltar
                print("Voltando...")
                break

            else:
                print("Opção inválida. Tente novamente.")

        # Salva as alterações no arquivo JSON
        with open(ARQUIVO_USUARIOS, "w") as arquivo:
            json.dump(usuarios, arquivo, indent=4)
        print("Alterações salvas com sucesso!")

        
class Atividade:
    def __init__(self, nome, descricao, data_criacao, id):
        self.nome = nome
        self.descricao = descricao
        self.data_criacao = datetime.strptime(data_criacao, "%d/%m/%y").date()
        self.concluido = False
        self.data_conclusao = None
        self.id = id
    
    @staticmethod
    def modificar(id):  # Pesquisa o nome de uma atividade e, se encontrar, modifica a atividade
        global data_do_sistema
        try:
            # Carrega o arquivo completo, não apenas a lista de atividades
            with open(ARQUIVO_TAREFAS, "r") as arquivo:
                dados = json.load(arquivo)

            atividades = dados.get("atividades", [])
            if not atividades:
                print("Nenhuma atividade cadastrada.")
                return

            nome = input("Digite o nome da atividade que deseja modificar: ")
            for atividade in atividades:
                if atividade['nome'] == nome and atividade['id'] == id:
                    print("1. Alterar nome")
                    print("2. Alterar descrição")
                    print("3. Marcar como concluída")
                    opcao = input("Escolha uma opção: ")

                    if opcao == "1":
                        novo_nome = input("Digite o novo nome: ")
                        atividade['nome'] = novo_nome
                    elif opcao == "2":
                        nova_descricao = input("Digite a nova descrição: ")
                        atividade['descricao'] = nova_descricao
                    elif opcao == "3":
                        atividade['concluido'] = True
                        atividade['data_conclusao'] = data_do_sistema.strftime("%d/%m/%y")
                    else:
                        print("Opção inválida.")
                        return

                    # Atualiza o arquivo JSON mantendo a estrutura global
                    dados["atividades"] = atividades
                    with open(ARQUIVO_TAREFAS, "w") as arquivo:
                        json.dump(dados, arquivo, indent=4)

                    print("Atividade modificada com sucesso!")
                    return

            print("Atividade não encontrada.")

        except FileNotFoundError:
            print("Arquivo de tarefas não encontrado. Inicializando...")
            inicializar_arquivo_tarefas()
     
    def salvar_atividade(self):
        global data_do_sistema
        try:
            with open(ARQUIVO_TAREFAS, "r") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            dados = {
                "ultima_verificacao": data_do_sistema.strftime("%d/%m/%y"),
                "atividades": []
            }

        # Impedir duplicatas
        for atividade in dados["atividades"]:
            if atividade["nome"] == self.nome and atividade["id"] == self.id:
                print("Erro: Uma atividade com o mesmo nome já existe para este usuário.")
                return
        
        # Atributos comuns a todas as atividades
        atividade_dict = {
            "nome": self.nome,
            "descricao": self.descricao,
            "data_criacao": self.data_criacao.strftime("%d/%m/%y"),
            "concluido": self.concluido,
            "data_conclusao": self.data_conclusao.strftime("%d/%m/%y") if self.data_conclusao else None,
            "id": self.id
        }

        # Atributos específicos para Tarefa
        if isinstance(self, Tarefa):
            atividade_dict["data_limite"] = self.data_limite.strftime("%d/%m/%y")
            atividade_dict["atrasada"] = self.atrasada

        # Atributos específicos para Hábito
        elif isinstance(self, Habito):
            atividade_dict["periodo_repeticao"] = self.periodo_repeticao
        

        dados["atividades"].append(atividade_dict)

        with open(ARQUIVO_TAREFAS, "w") as arquivo:
            json.dump(dados, arquivo, indent=4)
        print("Atividade salva com sucesso!")

    @staticmethod
    def carregar_atividades():
        try:
            with open(ARQUIVO_TAREFAS, "r") as arquivo:
                dados = json.load(arquivo)

                # Valida a estrutura do arquivo
                if not isinstance(dados, dict) or "ultima_verificacao" not in dados or "atividades" not in dados:
                    raise ValueError("Estrutura inválida. Inicializando arquivo de tarefas.")

                Atividade.verificar_validade()  # Chama a validação global
                return dados.get("atividades", [])
        except (FileNotFoundError, ValueError):
            print("Arquivo inválido ou não encontrado. Inicializando...")
            inicializar_arquivo_tarefas()
            return []

    @staticmethod
    def remover_atividade(nome, id):  # Remove uma atividade pelo nome e ID do usuário
        try:
            # Carregar o arquivo completo
            with open(ARQUIVO_TAREFAS, "r") as arquivo:
                dados = json.load(arquivo)

            atividades = dados.get("atividades", [])
            atividade_encontrada = False
            atividades_filtradas = []

            for atividade in atividades:
                if atividade["nome"] == nome and atividade["id"] == id:
                    atividade_encontrada = True
                else:
                    atividades_filtradas.append(atividade)

            if not atividade_encontrada:
                print(f"Erro: Nenhuma atividade encontrada com o nome '{nome}' para o usuário '{id}'.")
                return

            # Atualizar a lista de atividades no dicionário de dados
            dados["atividades"] = atividades_filtradas

            # Salvar as alterações no arquivo, preservando a estrutura global
            with open(ARQUIVO_TAREFAS, "w") as arquivo:
                json.dump(dados, arquivo, indent=4)

            print(f"Atividade '{nome}' removida com sucesso para o usuário '{id}'.")

        except FileNotFoundError:
            print("Nenhuma atividade encontrada para remover.")

        
    @staticmethod
    def listar_atividades(id):
        atividades = Atividade.carregar_atividades()
        print(" ")
        atividades_id = [atividade for atividade in atividades if atividade.get("id") == id]
        if not atividades_id:
            print("Nenhuma atividade cadastrada para este usuário.")
        else:
            for i, atividade in enumerate(atividades_id, start=1):
                if not "periodo_repeticao" in atividade:
                    print(f"{i}. Tarefa:\nNome: {atividade['nome']}\nDescrição: {atividade['descricao']}\nData Limite: {atividade.get('data_limite', 'N/A')}\nData de Criação: {atividade['data_criacao']}\nStatus: {'Concluído em ' + atividade['data_conclusao'] if atividade['concluido'] else 'Não concluído'}\nAtrasada: {'Sim' if atividade.get('atrasada', False) else 'Não'}\n")
                else:
                    print(f"{i}. Hábito:\nNome: {atividade['nome']}\nDescrição: {atividade['descricao']}\nData de Criação: {atividade['data_criacao']}\nPeríodo: {atividade['periodo_repeticao']}\nStatus: {'Concluído em ' + atividade['data_conclusao'] if atividade['concluido'] else 'Não concluído'}\n")


    def verificar_validade():
        global data_do_sistema
        print("Verificando validade...")

        try:
            with open(ARQUIVO_TAREFAS, "r") as arquivo:
                dados = json.load(arquivo)

            # Garantir que `dados` tenha a estrutura correta
            if not isinstance(dados, dict) or "ultima_verificacao" not in dados or "atividades" not in dados:
                raise ValueError("Estrutura do arquivo de tarefas inválida. Recriando...")

        except (FileNotFoundError, ValueError):
            # Inicializa a estrutura correta do arquivo
            dados = {
                "ultima_verificacao": data_do_sistema.strftime("%d/%m/%y"),
                "atividades": []
            }
            with open(ARQUIVO_TAREFAS, "w") as arquivo:
                json.dump(dados, arquivo, indent=4)
            print("Arquivo de tarefas inicializado com sucesso.")
            return  # Não há o que verificar em um arquivo recém-criado

        # Pegar a última verificação global
        ultima_verificacao_global = datetime.strptime(dados["ultima_verificacao"], "%d/%m/%y").date()

        atividades = dados.get("atividades", [])

        for atividade in atividades:
            if "data_limite" in atividade:  # Verificar se é uma tarefa
                data_limite = datetime.strptime(atividade["data_limite"], "%d/%m/%y").date()

                if not atividade["concluido"] and data_limite < data_do_sistema:
                    atividade["atrasada"] = True
                else:
                    atividade["atrasada"] = False

            elif "periodo_repeticao" in atividade:  # Verificar se é um hábito
                if atividade["periodo_repeticao"] == "diário":  # Reseta o hábito
                    if ultima_verificacao_global != data_do_sistema:
                        atividade["concluido"] = False

                elif atividade["periodo_repeticao"] == "semanal":  # Reseta o hábito
                    ultimo_sabado = ultima_verificacao_global - timedelta(days=ultima_verificacao_global.weekday() + 2)
                    if (ultimo_sabado + timedelta(days=7)) < data_do_sistema:
                        atividade["concluido"] = False

                elif atividade["periodo_repeticao"] == "mensal":  # Reseta o hábito
                    if ultima_verificacao_global.month != data_do_sistema.month or ultima_verificacao_global.year != data_do_sistema.year:
                        atividade["concluido"] = False

        # Atualizar a data de última verificação no cabeçalho
        dados["ultima_verificacao"] = data_do_sistema.strftime("%d/%m/%y")

        # Salvar as alterações no arquivo
        with open(ARQUIVO_TAREFAS, "w") as arquivo:
            json.dump(dados, arquivo, indent=4)

        print("Validade das atividades verificada e atualizada.")


class Tarefa(Atividade):
    def __init__(self, nome, descricao, data_criacao, data_limite, id): # Inicializa uma tarefa com nome, descrição, data de criação e data limite
        super().__init__(nome, descricao, data_criacao, id)
        self.data_limite = datetime.strptime(data_limite, "%d/%m/%y").date()
        self.atrasada = False

    @staticmethod
    def criar_tarefa(id):
        global data_do_sistema
        nome = input("Digite o nome da tarefa: ")
        descricao = input("Digite a descrição da tarefa: ")

        # Coleta e valida a data limite
        while True:
            datalimite_input = input("Digite a data limite no formato DD/MM/YY: ")
            try:
                datalimite = datetime.strptime(datalimite_input, "%d/%m/%y").date()
                if datalimite < data_do_sistema:
                    print("Data limite inválida! A data não pode ser anterior à data atual.")
                else:
                    break
            except ValueError:
                print("Data inválida! Por favor, insira no formato DD/MM/YY.")

        nova_tarefa = Tarefa(nome, descricao, data_do_sistema.strftime("%d/%m/%y"), datalimite.strftime("%d/%m/%y"), id)
        print("Tarefa criada com sucesso!")
        return nova_tarefa


class Habito(Atividade):
    def __init__(self, nome, descricao, data_criacao, periodo_repeticao, id): # Inicializa um hábito com nome, descrição, data de criação e período de repetição
        super().__init__(nome, descricao, data_criacao, id)
        self.periodo_repeticao = periodo_repeticao


    @staticmethod
    def criar_habito(id): # Cria um novo hábito com validação das entradas
        global data_do_sistema
        nome = input("Digite o nome do hábito: ")
        descricao = input("Digite a descrição do hábito: ")

        print("1. Diário")
        print("2. Semanal")
        print("3. Mensal")
        opcao = input("Escolha uma opção ")

        if opcao == "1":
            periodo_repeticao = "diário"
            
        elif opcao =="2":
            periodo_repeticao = "semanal"

        elif opcao == "3":
            periodo_repeticao = "mensal"

        else:
            print("Opção invalida")

        novo_habito = Habito(nome, descricao, data_do_sistema.strftime("%d/%m/%y"), periodo_repeticao, id)
        print("Hábito criado com sucesso!")
        return novo_habito


def menu_de_login():  # Exibe o menu de opções para manipular atividades
    global xdias, data_do_sistema
    xdias = 0  # Número de dias a adicionar
    data_do_sistema = datetime.now().date() + timedelta(days=xdias)

    while True:
        print("\nBem vindo ao gerenciador de Atividades\n")
        print("1.Criar usuario")
        print("2.Entrar")
        print("3.Listar Usuarios")
        print("0.Sair do app")
        opcao = input("\nEscolha uma opção ")

        if opcao == "0":
            print("Saindo do app...")
            exit()

        elif opcao == "1":
            Usuario.criar_usuario()

        elif opcao == "2":
            if not Usuario.carregar_usuarios():
                print("Nenhum usuário encontrado")
                
            
            else:
                while True:
                    opcao = input("\nDigite o nome do seu usuário\nOu digite 0 para voltar: ")
                    usuarios = Usuario.carregar_usuarios()

                    usuario_encontrado = next((usuario for usuario in usuarios if usuario["nome"] == opcao), None)
                    if opcao == "0":
                        print("Voltando...")
                        break

                    elif usuario_encontrado:
                        print("Usuário " + opcao + " encontrado")

                        while True:
                            opcaosenha = input("\nDigite sua senha para entrar\nOu digite 0 para voltar: ")

                            if opcaosenha == "0":
                                print("Voltando...")
                                break

                            elif opcaosenha == usuario_encontrado["senha"]:
                                print("Senha correta")
                                print("Bem vindo(a) " + opcao)
                                menu_de_atividades(usuario_encontrado)
                                return
                            else:
                                print("Senha errada")
                    else:
                        print("Não existe um usuário com o nome " + opcao)
                        break
            
        elif opcao == "3":
            Usuario.listar_usuarios()

        else:
            print("Opção inválida")


def menu_de_atividades(usuario_logado):
    while True:
        print("\nMenu de Atividades")
        print("1. Menu de usuario")
        print("2. Menu de atividades")
        print("3. Alterar Dias do Sistema")
        print("0. Sair")

        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1": # Menu usuario
            while True:
                print("\n\nMenu de usuario")
                print("1. Modificar dados do usuario")
                print("2. Sair")
                print("3. Excluir usuario")
                print("0. Voltar")

                opcao_usuario = input("\nEscolha uma opção: ")

                if opcao_usuario == "0":
                    break

                elif opcao_usuario == "1":
                    Usuario.modificar_usuario(usuario_logado)
                    
                elif opcao_usuario == "2":
                    print("Saindo...")
                    menu_de_login()
                    return

                elif opcao_usuario == "3":
                    confirmar = input(f"\nTem certeza que deseja excluir o usuário '{usuario_logado['nome']}'? (s/n): ").lower()
                    if confirmar == "s":
                        Usuario.remover_usuario(usuario_logado["nome"])
                        menu_de_login()
                        return  # Sai do menu após exclusão
                    elif confirmar == "n":
                        print("Ação de exclusão cancelada.")
                    else:
                        print("Opção inválida. Tente novamente.")
                else:
                    print("Opção inválida. Tente novamente.")

        elif opcao == "2":  # Menu de atividades
            while True:
                print("\n\nMenu de Atividades")
                print("1. Criar Atividade")
                print("2. Listar Atividades")
                print("3. Modificar Atividade")
                print("4. Excluir Atividade")
                print("0. Voltar")

                opcao_atividade = input("\nEscolha uma opção: ")

                if opcao_atividade == "0":
                    print("Voltando...")
                    break

                elif opcao_atividade == "1":
                    print("1. Criar Tarefa")
                    print("2. Criar Hábito")
                    tipo_atividade = input("Escolha uma opção: ")

                    if tipo_atividade == "1":
                        nova_tarefa = Tarefa.criar_tarefa(usuario_logado["id"])
                        nova_tarefa.salvar_atividade()
                    elif tipo_atividade == "2":
                        novo_habito = Habito.criar_habito(usuario_logado["id"])
                        novo_habito.salvar_atividade()
                    else:
                        print("Opção inválida.")

                elif opcao_atividade == "2":
                    Atividade.listar_atividades(usuario_logado["id"])

                elif opcao_atividade == "3":
                    Atividade.modificar(usuario_logado["id"])

                elif opcao_atividade == "4":
                    nome_atividade = input("Digite o nome da atividade que deseja excluir: ")
                    Atividade.remover_atividade(nome_atividade, usuario_logado["id"])
                else:
                    print("Opção inválida. Tente novamente.")

        elif opcao == "3":  # Alterar dias do sistema
            try:
                dias = int(input("Digite o número de dias para avançar ou retroceder no sistema (use valores negativos para retroceder): "))
                global data_do_sistema
                data_do_sistema += timedelta(days=dias)
                print(f"A data do sistema agora é {data_do_sistema.strftime('%d/%m/%Y')}.")
            except ValueError:
                print("Entrada inválida. Insira um número inteiro.")

        elif opcao == "0":  # Sair
            menu_de_login()
        

        else:
            print("Opção inválida. Tente novamente.")

data_do_sistema = datetime.now().strftime("%d/%m/%y")  # Define a data inicial do sistema

inicializar_arquivo_tarefas()

menu_de_login()


