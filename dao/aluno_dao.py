from config import db
from modelos.aluno import Aluno


class AlunoDAO:
    def salvar(self, aluno):
        existente = self.buscar_por_matricula(aluno.matricula)
        if existente:
            return False, "Esta matrícula já está cadastrada no sistema."

        try:
            db.session.add(aluno)
            db.session.commit()
            return True, "Aluno cadastrado com absoluto sucesso!"
        except Exception as e:
            db.session.rollback()
            return False, f"Erro interno ao salvar: {str(e)}"

    def listar_todos(self):
        return Aluno.query.order_by(Aluno.nome).all()

    def buscar_por_matricula(self, matricula):
        return Aluno.query.filter_by(matricula=str(matricula).strip()).first()

    def atualizar_notas(self, matricula, b1, b2, b3, b4):
        aluno = self.buscar_por_matricula(matricula)
        if aluno:
            try:
                aluno.b1 = float(b1) if b1 else 0.0
                aluno.b2 = float(b2) if b2 else 0.0
                aluno.b3 = float(b3) if b3 else 0.0
                aluno.b4 = float(b4) if b4 else 0.0
                db.session.commit()
                return True
            except (ValueError, TypeError):
                db.session.rollback()
                return False
        return False

    def deletar(self, matricula):
        aluno = self.buscar_por_matricula(matricula)
        if aluno:
            try:
                db.session.delete(aluno)
                db.session.commit()
                return True
            except Exception:
                db.session.rollback()
                return False
        return False