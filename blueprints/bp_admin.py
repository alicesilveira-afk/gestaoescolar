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
    if session.get('usuario') != 'Administrador':
        return redirect(url_for('index'))

    alunos = aluno_dao.listar_todos()
    professores = prof_dao.listar_todos()
    todas_notas = Nota.query.all()

    for aluno in alunos:
        notas_aluno = [n for n in todas_notas if str(n.matricula_aluno).strip() == str(aluno.matricula).strip()]

        if notas_aluno:

            b1_list = [n.b1 for n in notas_aluno if n.b1 is not None]
            b2_list = [n.b2 for n in notas_aluno if n.b2 is not None]
            b3_list = [n.b3 for n in notas_aluno if n.b3 is not None]
            b4_list = [n.b4 for n in notas_aluno if n.b4 is not None]


            aluno.b1_geral = round(sum(b1_list) / len(b1_list), 1) if b1_list else None
            aluno.b2_geral = round(sum(b2_list) / len(b2_list), 1) if b2_list else None
            aluno.b3_geral = round(sum(b3_list) / len(b3_list), 1) if b3_list else None
            aluno.b4_geral = round(sum(b4_list) / len(b4_list), 1) if b4_list else None


            medias_disciplinas = [n.media for n in notas_aluno if n.media is not None]
            aluno.media_geral = round(sum(medias_disciplinas) / len(medias_disciplinas), 1) if medias_disciplinas else 0.0
        else:

            aluno.b1_geral = None
            aluno.b2_geral = None
            aluno.b3_geral = None
            aluno.b4_geral = None
            aluno.media_geral = 0.0

        # Situação unificada considerando a Média Geral
        aluno.situacao_geral = "Aprovado" if aluno.media_geral >= 7.0 else "Recuperação"

    return render_template(
        'admin.html',
        alunos=alunos,
        lista=alunos,
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