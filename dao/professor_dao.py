from config import db
from modelos.professor import Professor
from modelos.nota import Nota


class ProfessorDAO:
    def salvar(self, professor):
        """Salva um novo professor no banco de dados."""
        existente = self.buscar_por_usuario(professor.usuario)
        if existente:
            return False, "Este nome de usuário já está cadastrado para outro professor."

        try:
            db.session.add(professor)
            db.session.commit()
            return True, "Professor cadastrado com sucesso!"
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao salvar professor: {str(e)}"

    def listar_todos(self):
        """Retorna todos os professores cadastrados em ordem alfabética."""
        return Professor.query.order_by(Professor.nome).all()

    def buscar_por_usuario(self, usuario):
        """Busca um professor pelo seu nome de usuário."""
        return Professor.query.filter_by(usuario=str(usuario).strip()).first()

    def lancar_nota_disciplina(self, matricula, disciplina, b1, b2, b3, b4):
        """
        Busca o registro de nota do aluno na disciplina informada.
        Se nenhuma nota for informada, cancela o salvamento.
        """
        def tratar_valor(v):
            if v is not None and str(v).strip() != '':
                try:
                    return float(v)
                except (ValueError, TypeError):
                    return None
            return None

        b1_val = tratar_valor(b1)
        b2_val = tratar_valor(b2)
        b3_val = tratar_valor(b3)
        b4_val = tratar_valor(b4)

        if all(v is None for v in [b1_val, b2_val, b3_val, b4_val]):
            return False, "Nenhuma nota foi informada. Preencha ao menos um bimestre."

        nota_obj = Nota.query.filter_by(
            matricula_aluno=str(matricula).strip(),
            disciplina=str(disciplina).strip()
        ).first()

        if not nota_obj:
            nota_obj = Nota(
                matricula_aluno=str(matricula).strip(),
                disciplina=str(disciplina).strip()
            )
            db.session.add(nota_obj)

        try:
            # Atualiza apenas as notas que foram fornecidas
            if b1_val is not None: nota_obj.b1 = b1_val
            if b2_val is not None: nota_obj.b2 = b2_val
            if b3_val is not None: nota_obj.b3 = b3_val
            if b4_val is not None: nota_obj.b4 = b4_val

            db.session.commit()
            return True, f"Notas da disciplina de {disciplina} atualizadas com sucesso!"
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao gravar no banco: {str(e)}"