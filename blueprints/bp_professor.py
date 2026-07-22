from flask import Blueprint, render_template, request, redirect, url_for, session
from dao.aluno_dao import AlunoDAO
from config import db

bp_professor = Blueprint('professor', __name__)
dao = AlunoDAO()


@bp_professor.route('/professor')
def dashboard():
    if session.get('usuario') != 'Professor':
        return redirect(url_for('index'))
    alunos = dao.listar_todos()
    return render_template('professor.html', alunos=alunos)


@bp_professor.route('/professor/notas', methods=['POST'])
def lancar_notas():
    if session.get('usuario') != 'Professor':
        return redirect(url_for('index'))

    # Coleta a matrícula e as 4 notas vindas do professor.html
    matricula = request.form.get('matricula')
    b1 = request.form.get('b1')
    b2 = request.form.get('b2')
    b3 = request.form.get('b3')
    b4 = request.form.get('b4')

    # Atualiza o banco de dados passando os 4 bimestres
    dao.atualizar_notas(matricula, b1, b2, b3, b4)
    return redirect(url_for('professor.dashboard'))


@bp_professor.route('/professor/chamada')
def chamada():
    if session.get('usuario') != 'Professor':
        return redirect(url_for('index'))

    alunos = dao.listar_todos()
    return render_template('chamada.html', alunos=alunos)


@bp_professor.route('/professor/registrar_presenca', methods=['POST'])
def registrar_presenca():
    if session.get('usuario') != 'Professor':
        return redirect(url_for('index'))

    Presenca = db.Model.registry._class_registry.get('Presenca')
    if not Presenca:
        from modelos.aluno import Presenca

    dados_formulario = request.form

    try:
        alunos = dao.listar_todos()

        for aluno in alunos:
            status = dados_formulario.get(str(aluno.matricula))

            if status:
                nova_presenca = Presenca(
                    matricula_aluno=str(aluno.matricula),
                    status=str(status)
                )
                db.session.add(nova_presenca)

        db.session.commit()
        print("-> CHAMADA SALVA NO BANCO DE DADOS COM SUCESSO! <-")

    except Exception as e:
        db.session.rollback()
        print(f"ERRO AO GRAVAR NO BANCO: {e}")

    return redirect(url_for('professor.dashboard'))