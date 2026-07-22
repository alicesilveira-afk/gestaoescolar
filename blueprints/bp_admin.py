from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from modelos.aluno import Aluno
from dao.aluno_dao import AlunoDAO

bp_admin = Blueprint('admin', __name__)
dao = AlunoDAO()


@bp_admin.route('/admin')
def dashboard():
    if session.get('usuario') != 'Administrador':
        return redirect(url_for('index'))
    alunos = dao.listar_todos()
    return render_template('admin.html', alunos=alunos)


@bp_admin.route('/admin/cadastrar', methods=['POST'])
def cadastrar():
    if session.get('usuario') != 'Administrador':
        return redirect(url_for('index'))

    # === ACRESCENTADO: CAPTURA DAS NOTAS DOS 4 BIMESTRES ===
    # Convertemos para float para garantir o tipo numérico adequado no banco
    b1 = float(request.form.get('b1', 0.0))
    b2 = float(request.form.get('b2', 0.0))
    b3 = float(request.form.get('b3', 0.0))
    b4 = float(request.form.get('b4', 0.0))

    # MODIFICADO: Passando os parâmetros de b1 a b4 para o modelo Aluno
    novo_aluno = Aluno(
        nome=request.form.get('nome'),
        matricula=request.form.get('matricula'),
        email=request.form.get('email'),
        curso=request.form.get('curso'),
        data=request.form.get('data'),
        b1=b1,
        b2=b2,
        b3=b3,
        b4=b4
    )

    sucesso, mensaje = dao.salvar(novo_aluno)
    flash(mensaje, 'success' if sucesso else 'error')
    return redirect(url_for('admin.dashboard'))


@bp_admin.route('/admin/deletar/<matricula>')
def deletar(matricula):
    if session.get('usuario') != 'Administrador':
        return redirect(url_for('index'))
    dao.deletar(matricula)
    return redirect(url_for('admin.dashboard'))