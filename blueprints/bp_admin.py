from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from config import db
from modelos.aluno import Aluno
from modelos.professor import Professor
from modelos.nota import Nota
from dao.aluno_dao import AlunoDAO
from dao.professor_dao import ProfessorDAO

bp_admin = Blueprint('admin', __name__)
aluno_dao = AlunoDAO()
prof_dao = ProfessorDAO()


@bp_admin.route('/admin')
def dashboard():
    # Proteção da rota do Admin
    if session.get('usuario') != 'Administrador':
        return redirect(url_for('index'))

    alunos = aluno_dao.listar_todos()
    professores = prof_dao.listar_todos()
    todas_notas = Nota.query.all()

    return render_template(
        'admin.html',
        alunos=alunos,
        professores=professores,
        todas_notas=todas_notas
    )


@bp_admin.route('/admin/cadastrar', methods=['POST'])
def cadastrar():
    if session.get('usuario') != 'Administrador':
        return redirect(url_for('index'))

    def extrair_nota(campo):
        val = request.form.get(campo)
        if val is not None and str(val).strip() != '':
            try:
                return float(val)
            except (ValueError, TypeError):
                return None
        return None

    b1 = extrair_nota('b1')
    b2 = extrair_nota('b2')
    b3 = extrair_nota('b3')
    b4 = extrair_nota('b4')

    matricula = request.form.get('matricula')
    nome = request.form.get('nome')
    email = request.form.get('email') or f"{matricula}@escola.com"
    curso = request.form.get('curso') or 'Técnico em Informática'
    data = request.form.get('data') or '2026'

    novo_aluno = Aluno(
        nome=nome,
        matricula=matricula,
        senha='123',
        email=email,
        curso=curso,
        data=data,
        b1=b1,
        b2=b2,
        b3=b3,
        b4=b4
    )

    sucesso, mensagem = aluno_dao.salvar(novo_aluno)
    flash(mensagem, 'success' if sucesso else 'error')
    return redirect(url_for('admin.dashboard'))


@bp_admin.route('/admin/deletar/<matricula>')
def deletar(matricula):
    if session.get('usuario') != 'Administrador':
        return redirect(url_for('index'))

    aluno = Aluno.query.filter_by(matricula=str(matricula).strip()).first()

    if aluno:
        try:
            db.session.delete(aluno)
            db.session.commit()
            flash("Aluno e todas as suas notas associadas foram removidos!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao remover aluno: {str(e)}", "error")
    else:
        flash("Aluno não encontrado.", "error")

    return redirect(url_for('admin.dashboard'))


@bp_admin.route('/admin/deletar_professor/<int:id>')
def deletar_professor(id):
    if session.get('usuario') != 'Administrador':
        return redirect(url_for('index'))

    professor = Professor.query.get(id)
    if professor:
        try:
            db.session.delete(professor)
            db.session.commit()
            flash(f"Professor(a) {professor.nome} removido(a) com sucesso!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao remover professor: {str(e)}", "error")
    else:
        flash("Professor não encontrado.", "error")

    return redirect(url_for('admin.dashboard'))