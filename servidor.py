from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import db

# Importação dos Blueprints
from blueprints.bp_admin import bp_admin
from blueprints.bp_aluno import bp_aluno
from blueprints.bp_professor import bp_professor

# Importação das Models
from modelos.aluno import Aluno
from modelos.professor import Professor
from modelos.nota import Nota

from dao.aluno_dao import AlunoDAO
from dao.professor_dao import ProfessorDAO

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

    prof_dao = ProfessorDAO()
    professor = prof_dao.buscar_por_usuario(login_input)

    if professor and professor.senha == senha_input:
        session['usuario'] = professor.usuario
        session['nome'] = professor.nome
        session['perfil'] = 'Professor'
        session['disciplina'] = professor.disciplina
        return redirect(url_for('professor.dashboard'))

    aluno_dao = AlunoDAO()
    aluno = aluno_dao.buscar_por_matricula(login_input)

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
            disciplina = request.form.get('disciplina', '').strip()

            if not disciplina:
                return render_template('cadastrar.html', erro="Informe a disciplina do professor!")

            dao = ProfessorDAO()

            novo_prof = Professor(
                nome=usuario,
                usuario=usuario,
                senha=senha,
                disciplina=disciplina
            )
            sucesso, mensagem = dao.salvar(novo_prof)

            if sucesso:
                session['usuario'] = novo_prof.usuario
                session['nome'] = novo_prof.nome
                session['perfil'] = 'Professor'
                session['disciplina'] = disciplina
                return redirect(url_for('professor.dashboard'))
            else:
                return render_template('cadastrar.html', erro=mensagem)

    return render_template('cadastrar.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/listarusuarios')
def listarusuarios():
    dao = AlunoDAO()
    lista = dao.listar_todos()

    todas_notas = Nota.query.all()

    for aluno in lista:
        notas_aluno = [n for n in todas_notas if str(n.matricula_aluno).strip() == str(aluno.matricula).strip()]

        if notas_aluno:
            b1_list = [n.b1 for n in notas_aluno if n.b1 is not None]
            b2_list = [n.b2 for n in notas_aluno if n.b2 is not None]
            b3_list = [n.b3 for n in notas_aluno if n.b3 is not None]
            b4_list = [n.b4 for n in notas_aluno if n.b4 is not None]

            aluno.b1 = round(sum(b1_list) / len(b1_list), 1) if b1_list else None
            aluno.b2 = round(sum(b2_list) / len(b2_list), 1) if b2_list else None
            aluno.b3 = round(sum(b3_list) / len(b3_list), 1) if b3_list else None
            aluno.b4 = round(sum(b4_list) / len(b4_list), 1) if b4_list else None

            medias_disc = [n.media for n in notas_aluno if n.media is not None]
            aluno.media_calc = round(sum(medias_disc) / len(medias_disc), 1) if medias_disc else 0.0
        else:
            aluno.b1 = None
            aluno.b2 = None
            aluno.b3 = None
            aluno.b4 = None
            aluno.media_calc = 0.0

        aluno.situacao_calc = "Aprovado" if aluno.media_calc >= 7.0 else "Recuperação"

    return render_template('index.html', lista=lista)


if __name__ == '__main__':
    app.run(debug=True)