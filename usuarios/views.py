from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import auth, messages
from receitas.models import Receita

# TODO: Separar lógicas em use cases e services, conforme escopo

def cadastro(request):
    fica_em_cadastro = redirect('cadastro')
    vai_para_login = redirect('login')

    if request.method == 'POST':
        nome = request.POST['nome']
        email = request.POST['email']
        senha = request.POST['password']
        senha2 = request.POST['password2']


        if campo_vazio(nome):
            messages.error(request, 'O campo nome deve ser preenchido!')
            return fica_em_cadastro
        if campo_vazio(nome):
            messages.error(request, 'O campo email deve ser preenchido!')
            return fica_em_cadastro
        if senhas_nao_sao_iguais(senha, senha2):
            messages.error(
                request,
                'A confirmação da senha deve coincidir com a senha!'
            )
            return fica_em_cadastro
        if email_ja_cadastrado(email):
            messages.warning(
                request,
                'Usuário já cadastrado, favor fazer o login.'
            )
            return vai_para_login
        if nome_ja_cadastrado(nome):
            messages.warning(
                request,
                'Usuário já cadastrado, favor fazer o login.'
            )
            return vai_para_login

        user = User.objects.create_user(username=nome, email=email, password=senha)
        user.save()

        messages.success(request, 'Usuário cadastrado com sucesso!')
        return vai_para_login

    return render(request, 'usuarios/cadastro.html')


def login(request):
    fica_em_login = redirect('login')
    vai_para_dashboard = redirect('dashboard')

    if request.method == 'POST':
        email = request.POST['email']
        senha = request.POST['senha']

        if campo_vazio(email) or campo_vazio(senha):
            messages.error(
                request,
                'Os campos e-mail e senha são obrigatórios!'
            )
            return fica_em_login

        if email_ja_cadastrado(email):
            nome_usuario = User.objects.filter(
                email=email
            ).values_list('username', flat=True).get()

            user = auth.authenticate(
                request,
                username=nome_usuario,
                password=senha
            )

            if user is not None:
                auth.login(request, user)
                print(user)
                return vai_para_dashboard

        messages.error(
            request,
            'Usuário não encontrado, favor verifique o e-mail informado.'
        )

    return render(request, 'usuarios/login.html')


def dashboard(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        receitas = Receita.objects.order_by('-data_receita').filter(pessoa=user_id)

        dados = {
            'receitas': receitas
        }
        return render(request, 'usuarios/dashboard.html', dados)

    return redirect('login')


def logout(request):
    auth.logout(request)
    return redirect('index')


def cria_receita(request):
    if request.method == 'POST':
        nome_receita = request.POST['nome_receita']
        ingredientes = request.POST['ingredientes']
        modo_preparo = request.POST['modo_preparo']
        tempo_preparo = request.POST['tempo_preparo']
        rendimento = request.POST['rendimento']
        categoria = request.POST['categoria']
        foto = request.FILES['foto']

        user = get_object_or_404(User, pk=request.user.id)
        print(user)
        receita = Receita.objects.create(
            nome_receita=nome_receita,
            ingredientes=ingredientes,
            modo_preparo=modo_preparo,
            tempo_preparo=tempo_preparo,
            rendimento=rendimento,
            categoria=categoria,
            pessoa=user,
            foto=foto
        )
        receita.save()
        return redirect('dashboard')

    return render(request, 'usuarios/cria_receita.html')


def campo_vazio(campo):
    return not campo.strip()


def senhas_nao_sao_iguais(senha, senha2):
    return senha != senha2


def email_ja_cadastrado(email):
    return User.objects.filter(email=email).exists()


def nome_ja_cadastrado(nome):
    return User.objects.filter(username=nome).exists()
