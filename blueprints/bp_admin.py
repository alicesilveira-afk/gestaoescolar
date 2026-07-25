from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from modelos.aluno import Aluno
from dao.aluno_dao import AlunoDAO

bp_admin = Blueprint('admin', __name__)
dao = AlunoDAO()


@bp_admin.route('/admin')
def dashboard():
    # Proteção da rota do Admin
    if session.get('usuario') != 'Administrador':
        return redirect(url_for('index'))

    # Traz todos os alunos cadastrados ordenados por nome via DAO
    alunos = dao.listar_todos()

    return render_template('admin.html', alunos=alunos)


@bp_admin.route('/admin/cadastrar', methods=['POST'])
def cadastrar():
    if session.get('usuario') != 'Administrador':
        return redirect(url_for('index'))

    # Captura e tratamento seguro de notas
    try:
        b1 = float(request.form.get('b1') or 0.0)
        b2 = float(request.form.get('b2') or 0.0)
        b3 = float(request.form.get('b3') or 0.0)
        b4 = float(request.form.get('b4') or 0.0)
    except ValueError:
        b1 = b2 = b3 = b4 = 0.0

    matricula = request.form.get('matricula')
    nome = request.form.get('nome')
    email = request.form.get('email') or f"{matricula}@escola.com"
    curso = request.form.get('curso') or 'Técnico em Informática'
    data = request.form.get('data') or '2026'

    novo_aluno = Aluno(
        nome=nome,
        matricula=matricula,
        senha='123',  # Senha padrão ao ser cadastrado pelo Admin
        email=email,
        curso=curso,
        data=data,
        b1=b1,
        b2=b2,
        b3=b3,
        b4=b4
    )

    sucesso, mensagem = dao.salvar(novo_aluno)
    flash(mensagem, 'success' if sucesso else 'error')
    return redirect(url_for('admin.dashboard'))


@bp_admin.route('/admin/deletar/<matricula>')
def deletar(matricula):
    if session.get('usuario') != 'Administrador':
        return redirect(url_for('index'))

    dao.deletar(matricula)
    return redirect(url_for('admin.dashboard'))