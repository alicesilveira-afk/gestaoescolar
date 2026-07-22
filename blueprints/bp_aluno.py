from flask import Blueprint, render_template, session, redirect, url_for
from dao.aluno_dao import AlunoDAO
from config import db

bp_aluno = Blueprint('aluno', __name__, url_prefix='/aluno')


@bp_aluno.route('/dashboard')
def dashboard():
    if 'usuario' not in session or 'matricula' not in session:
        return redirect(url_for('index'))

    matricula_logada = str(session['matricula']).strip()

    dao = AlunoDAO()
    aluno = dao.buscar_por_matricula(matricula_logada)

    if not aluno:
        try:
            aluno = dao.buscar_por_matricula(int(matricula_logada))
        except ValueError:
            pass

    if not aluno:
        return redirect(url_for('index'))

    # Busca a classe Presenca dinamicamente para evitar importação circular
    Presenca = db.Model.registry._class_registry.get('Presenca')
    if not Presenca:
        from modelos.aluno import Presenca

    historico_presencas = Presenca.query.filter_by(matricula_aluno=str(aluno.matricula)).all()

    total_presencas = sum(1 for p in historico_presencas if p.status == 'Presente')
    total_faltas = sum(1 for p in historico_presencas if p.status == 'Ausente')

    # === CORRIGIDO ===
    # Removemos os cálculos manuais e os sinais de "=" que travavam o sistema.
    # O modelo Aluno agora faz toda a mágica sozinho usando as @property!

    return render_template(
        'aluno.html',
        aluno=aluno,
        presencas=historico_presencas,
        total_presencas=total_presencas,
        total_faltas=total_faltas
    )