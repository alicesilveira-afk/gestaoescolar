from flask import Blueprint, render_template, session, redirect, url_for
from dao.aluno_dao import AlunoDAO
from modelos.aluno import Presenca
from modelos.nota import Nota

bp_aluno = Blueprint('aluno', __name__, url_prefix='/aluno')


@bp_aluno.route('/dashboard')
def dashboard():

    if 'usuario' not in session or 'matricula' not in session or session.get('perfil') != 'Aluno':
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
        session.clear()
        return redirect(url_for('index'))


    historico_presencas = Presenca.query.filter_by(matricula_aluno=str(aluno.matricula)).all()

    total_presencas = sum(1 for p in historico_presencas if p.status == 'Presente')
    total_faltas = sum(1 for p in historico_presencas if p.status in ['Falta', 'Ausente'])

    notas_disciplinas = Nota.query.filter_by(matricula_aluno=str(aluno.matricula)).all()

    return render_template(
        'aluno.html',
        aluno=aluno,
        presencas=historico_presencas,
        total_presencas=total_presencas,
        total_faltas=total_faltas,
        notas_disciplinas=notas_disciplinas
    )