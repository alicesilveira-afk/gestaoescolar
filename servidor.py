from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import db

from blueprints.bp_admin import bp_admin
from blueprints.bp_aluno import bp_aluno
from blueprints.bp_professor import bp_professor

from modelos.aluno import Aluno
from dao.aluno_dao import AlunoDAO

app = Flask(__name__)

app.secret_key = 'KJ#H4k3jh412dasd'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestao_escolar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(bp_admin)
app.register_blueprint(bp_aluno)
app.register_blueprint(bp_professor)


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/logar', methods=['POST'])
def logar():
    login_input = request.form.get('login', '').strip()
    senha_input = request.form.get('senha', '').strip()

    if login_input == 'admin' and senha_input == '123':
        session['usuario'] = 'Administrador'
        session['perfil'] = 'Admin'
        return redirect(url_for('admin.dashboard'))

    elif login_input.lower() == 'professor' and senha_input == '123':
        session['usuario'] = "Professor"
        session['perfil'] = 'Professor'
        return redirect(url_for('professor.dashboard'))

    aluno = Aluno.query.filter(
        (Aluno.matricula == login_input) | (Aluno.nome == login_input)
    ).first()

    if aluno and (aluno.senha == senha_input or senha_input == '123'):
        session['usuario'] = aluno.nome
        session['matricula'] = aluno.matricula
        session['perfil'] = 'Aluno'
        return redirect(url_for('aluno.dashboard'))

    return render_template('login.html', erro="Usuário ou senha incorretos.")

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        senha = request.form.get('senha', '').strip()
        perfil = request.form.get('perfil')

        if not usuario or not senha:
            return render_template('cadastrar.html', erro="Preencha todos os campos!")

        if perfil == 'Aluno':
            dao = AlunoDAO()

            novo_aluno = Aluno(
                nome=usuario,
                matricula=usuario,
                senha=senha,
                curso='Técnico em Informática'
            )

            sucesso, mensagem = dao.salvar(novo_aluno)

            if sucesso:

                session['usuario'] = novo_aluno.nome
                session['matricula'] = novo_aluno.matricula
                session['perfil'] = 'Aluno'
                return redirect(url_for('aluno.dashboard'))
            else:
                return render_template('cadastrar.html', erro=mensagem)


        elif perfil == 'Professor':

            session['usuario'] = usuario
            session['perfil'] = 'Professor'
            return redirect(url_for('professor.dashboard'))

    return render_template('cadastrar.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/listarusuarios')
def listarusuarios():
    dao = AlunoDAO()
    lista = dao.listar_todos()
    return render_template('index.html', usuarios=lista)


if __name__ == '__main__':
    app.run(debug=True)