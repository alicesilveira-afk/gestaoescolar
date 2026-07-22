from flask import Flask, render_template, request, redirect, url_for, session
from config import db

from blueprints.bp_admin import bp_admin
from blueprints.bp_aluno import bp_aluno
from blueprints.bp_professor import bp_professor
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
    login = request.form.get('login')
    senha = request.form.get('senha')


    if login == 'admin' and senha == '123':
        session['usuario'] = 'Administrador'
        return redirect(url_for('admin.dashboard'))


    elif login == 'professor' and senha == '123':
        session['usuario'] = "Professor"
        return redirect(url_for('professor.dashboard'))

    elif login and login.isdigit() and senha == '123':
        dao = AlunoDAO()


        try:
            aluno_encontrado = dao.buscar_por_matricula(int(login))
        except (ValueError, TypeError):
            aluno_encontrado = dao.buscar_por_matricula(login)


        if aluno_encontrado:
            session['usuario'] = aluno_encontrado.nome
            session['matricula'] = aluno_encontrado.matricula
            return redirect(url_for('aluno.dashboard'))

        return render_template('login.html')

    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html')

@app.route('/listarusuarios')
def listarusuarios():
    class Usuario:
        def __init__(self, nome, matricula, curso, email, b1, b2, b3, b4):
            self.nome = nome
            self.matricula = matricula
            self.curso = curso
            self.email = email
            # Notas dos 4 Bimestres
            self.b1 = float(b1)
            self.b2 = float(b2)
            self.b3 = float(b3)
            self.b4 = float(b4)
            # Cálculo automático da média anual
            self.media = round((self.b1 + self.b2 + self.b3 + self.b4) / 4, 1)
            # Regra de negócio automatizada para a situação
            self.situacao = "Aprovado" if self.media >= 7.0 else "Recuperação"


    us1 = Usuario('Alice Batista da Silveira', '202418660018', 'Informática', 'silveiraalice002@gmail.com', 8.0, 7.5,
                  9.0, 8.5)
    us2 = Usuario('Francisco David', '202418660022', 'Informática', 'franciscodavid@gmail.com', 6.0, 5.5, 7.0, 6.5)
    us3 = Usuario('rene', '202418660035', 'Meio Ambiente', 'mirela@gmail.com', 9.0, 8.5, 9.5, 9.0)
    us4 = Usuario('junior', '202418660040', 'Edificações', 'junior@gmail.com', 5.0, 6.0, 5.5, 5.0)

    lista = [us1, us2, us3, us4]
    return render_template('index.html', usuarios=lista)


if __name__ == '__main__':
    app.run(debug=True)