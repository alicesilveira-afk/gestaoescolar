from flask import Blueprint, render_template, session, redirect, url_for
from dao.aluno_dao import AlunoDAO
from config import db
from modelos.aluno import Presenca  # Importação direta limpa a verificação manual

bp_aluno = Blueprint('aluno', __name__, url_prefix='/aluno')


@bp_aluno.route('/dashboard')
def dashboard():
    # 1. Verifica se o aluno está logado
    if 'usuario' not in session or 'matricula' not in session:
        return redirect(url_for('index'))

    matricula_logada = str(session['matricula']).strip()

    # 2. Busca os dados do aluno no DAO
    dao = AlunoDAO()
    aluno = dao.buscar_por_matricula(matricula_logada)

    if not aluno:
        try:
            aluno = dao.buscar_por_matricula(int(matricula_logada))
        except ValueError:
            pass

    # Se a matrícula da sessão não existir no banco, volta para o login
    if not aluno:
        session.clear()
        return redirect(url_for('index'))

    # 3. Busca o histórico de presenças do aluno
    historico_presencas = Presenca.query.filter_by(matricula_aluno=str(aluno.matricula)).all()

    # Contagem de presença e falta
    total_presencas = sum(1 for p in historico_presencas if p.status == 'Presente')
    total_faltas = sum(1 for p in historico_presencas if p.status in ['Falta', 'Ausente'])

    return render_template(
        'aluno.html',
        aluno=aluno,
        presencas=historico_presencas,
        total_presencas=total_presencas,
        total_faltas=total_faltas
    )