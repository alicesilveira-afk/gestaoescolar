from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from dao.aluno_dao import AlunoDAO
from dao.professor_dao import ProfessorDAO
from modelos.aluno import Presenca
from modelos.nota import Nota
from config import db

bp_professor = Blueprint('professor', __name__)
aluno_dao = AlunoDAO()
prof_dao = ProfessorDAO()

avisos_db = [
    {
        "autor": "Prof. Carlos (Informática)",
        "mensagem": "Lembrete: Entrega do trabalho de informática até sexta-feira!",
        "data": "22/07/2026"
    }
]


@bp_professor.route('/professor')
def dashboard():

    if session.get('perfil') != 'Professor':
        return redirect(url_for('index'))

    alunos = aluno_dao.listar_todos()
    disciplina_professor = session.get('disciplina') or 'Geral'

    for aluno in alunos:
        nota_obj = Nota.query.filter_by(
            matricula_aluno=str(aluno.matricula).strip(),
            disciplina=str(disciplina_professor).strip()
        ).first()

        if nota_obj:
            aluno.b1_disc = nota_obj.b1
            aluno.b2_disc = nota_obj.b2
            aluno.b3_disc = nota_obj.b3
            aluno.b4_disc = nota_obj.b4
            aluno.media_disc = nota_obj.media
            aluno.situacao_disc = nota_obj.situacao
        else:
            aluno.b1_disc = None
            aluno.b2_disc = None
            aluno.b3_disc = None
            aluno.b4_disc = None
            aluno.media_disc = 0.0
            aluno.situacao_disc = 'Em Aberto'

    total_alunos = len(alunos)
    aprovados = 0
    recuperacao = 0
    reprovados = 0
    soma_medias = 0.0
    qtd_com_media = 0

    for aluno in alunos:
        if aluno.situacao_disc == 'Aprovado':
            aprovados += 1
        elif aluno.situacao_disc == 'Recuperação':
            recuperacao += 1

        if aluno.media_disc > 0:
            soma_medias += aluno.media_disc
            qtd_com_media += 1

    media_geral = round(soma_medias / qtd_com_media, 1) if qtd_com_media > 0 else 0.0
    taxa_aprovacao = round((aprovados / total_alunos) * 100, 1) if total_alunos > 0 else 0.0

    stats = {
        'total': total_alunos,
        'media_geral': media_geral,
        'taxa_aprovacao': taxa_aprovacao,
        'aprovados': aprovados,
        'recuperacao': recuperacao,
        'reprovados': reprovados
    }

    return render_template(
        'professor.html',
        alunos=alunos,
        stats=stats,
        disciplina=disciplina_professor
    )


@bp_professor.route('/professor/notas', methods=['POST'])
def lancar_notas():
    if session.get('perfil') != 'Professor':
        return redirect(url_for('index'))

    matricula = request.form.get('matricula')
    disciplina = session.get('disciplina') or request.form.get('disciplina') or 'Geral'

    b1 = request.form.get('b1')
    b2 = request.form.get('b2')
    b3 = request.form.get('b3')
    b4 = request.form.get('b4')

    if not matricula:
        flash("Matrícula não informada.", "error")
        return redirect(url_for('professor.dashboard'))

    # Salva/Atualiza no banco via DAO
    sucesso, mensagem = prof_dao.lancar_nota_disciplina(
        matricula=matricula,
        disciplina=disciplina,
        b1=b1,
        b2=b2,
        b3=b3,
        b4=b4
    )

    flash(mensagem, 'success' if sucesso else 'error')
    return redirect(url_for('professor.dashboard'))


@bp_professor.route('/professor/chamada')
def chamada():
    if session.get('perfil') != 'Professor':
        return redirect(url_for('index'))

    alunos = aluno_dao.listar_todos()
    return render_template('chamada.html', alunos=alunos)


@bp_professor.route('/professor/registrar_presenca', methods=['POST'])
def registrar_presenca():
    if session.get('perfil') != 'Professor':
        return redirect(url_for('index'))

    dados_formulario = request.form

    try:
        alunos = aluno_dao.listar_todos()

        for aluno in alunos:
            status = dados_formulario.get(str(aluno.matricula))

            if status:
                nova_presenca = Presenca(
                    matricula_aluno=str(aluno.matricula),
                    status=str(status)
                )
                db.session.add(nova_presenca)

        db.session.commit()
        flash("Chamada registrada com sucesso!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao registrar chamada: {str(e)}", "error")

    return redirect(url_for('professor.dashboard'))


@bp_professor.route('/avisos')
def ver_avisos():
    """Exibe a tela do quadro de avisos para qualquer usuário autenticado."""
    if not session.get('usuario'):
        return redirect(url_for('index'))

    return render_template('avisos.html', avisos=avisos_db)


@bp_professor.route('/professor/publicar_aviso', methods=['POST'])
def publicar_aviso():
    """Permite que qualquer PROFESSOR cadastrado publique recados novos no quadro."""
    if session.get('perfil') != 'Professor':
        flash("Apenas professores possuem permissão para publicar avisos.", "error")
        return redirect(url_for('index'))

    mensagem = request.form.get('mensagem')

    if mensagem and mensagem.strip():
        data_atual = datetime.now().strftime("%d/%m/%Y")

        nome_professor = session.get('nome') or session.get('usuario') or 'Professor'
        disciplina_professor = session.get('disciplina')

        if disciplina_professor:
            autor_formatado = f"Prof. {nome_professor} ({disciplina_professor})"
        else:
            autor_formatado = f"Prof. {nome_professor}"

        novo_aviso = {
            "autor": autor_formatado,
            "mensagem": mensagem.strip(),
            "data": data_atual
        }
        avisos_db.insert(0, novo_aviso)
        flash("Aviso publicado com sucesso no quadro!", "success")

    return redirect(url_for('professor.ver_avisos'))