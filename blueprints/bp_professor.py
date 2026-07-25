from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session
from dao.aluno_dao import AlunoDAO
from config import db

bp_professor = Blueprint('professor', __name__)
dao = AlunoDAO()

# Lista temporária em memória para armazenar os avisos
# (Você pode depois substituir por uma tabela no banco de dados se preferir)
avisos_db = [
    {
        "autor": "Prof. Carlos",
        "mensagem": "Lembrete: Entrega do trabalho de informática até sexta-feira!",
        "data": "22/07/2026"
    }
]


@bp_professor.route('/professor')
def dashboard():
    if session.get('usuario') != 'Professor':
        return redirect(url_for('index'))

    alunos = dao.listar_todos()

    # --- Cálculo de Estatísticas da Turma ---
    total_alunos = len(alunos)
    aprovados = 0
    recuperacao = 0
    reprovados = 0
    soma_medias = 0.0
    qtd_com_media = 0

    for aluno in alunos:
        situacao = getattr(aluno, 'situacao', '')
        if situacao == 'Aprovado':
            aprovados += 1
        elif situacao == 'Recuperação':
            recuperacao += 1
        else:
            reprovados += 1

        try:
            m = float(aluno.media)
            soma_medias += m
            qtd_com_media += 1
        except (ValueError, TypeError):
            pass

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

    return render_template('professor.html', alunos=alunos, stats=stats)


@bp_professor.route('/professor/notas', methods=['POST'])
def lancar_notas():
    if session.get('usuario') != 'Professor':
        return redirect(url_for('index'))

    matricula = request.form.get('matricula')
    b1 = request.form.get('b1')
    b2 = request.form.get('b2')
    b3 = request.form.get('b3')
    b4 = request.form.get('b4')

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


@bp_professor.route('/avisos')
def ver_avisos():
    """
    Exibe a tela do quadro de avisos.
    Lê a lista 'avisos_db' compartilhada.
    """
    # Garante que só usuários logados entrem (seja Aluno ou Professor)
    if not session.get('usuario'):
        return redirect(url_for('login'))

    return render_template('avisos.html', avisos=avisos_db)


@bp_professor.route('/professor/publicar_aviso', methods=['POST'])
def publicar_aviso():
    """
    Apenas o PROFESSOR pode cadastrar recados novos.
    """
    if session.get('usuario') != 'Professor':
        return redirect(url_for('login'))

    mensagem = request.form.get('mensagem')

    if mensagem:
        data_atual = datetime.now().strftime("%d/%m/%Y")
        novo_aviso = {
            "autor": "Prof. Carlos",  # Nome do professor que postou
            "mensagem": mensagem,
            "data": data_atual
        }
        # Coloca o aviso novo sempre no TOPO da lista
        avisos_db.insert(0, novo_aviso)

    return redirect(url_for('professor.ver_avisos'))