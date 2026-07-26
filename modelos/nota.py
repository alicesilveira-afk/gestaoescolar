from config import db


class Nota(db.Model):
    __tablename__ = 'notas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    matricula_aluno = db.Column(db.String(50), db.ForeignKey('alunos.matricula'), nullable=False)
    disciplina = db.Column(db.String(100), nullable=False)

    b1 = db.Column(db.Float, nullable=True, default=None)
    b2 = db.Column(db.Float, nullable=True, default=None)
    b3 = db.Column(db.Float, nullable=True, default=None)
    b4 = db.Column(db.Float, nullable=True, default=None)

    @property
    def media(self):
        notas_lancadas = [n for n in [self.b1, self.b2, self.b3, self.b4] if n is not None]
        if not notas_lancadas:
            return 0.0
        return round(sum(notas_lancadas) / len(notas_lancadas), 1)

    @property
    def situacao(self):
        notas_lancadas = [n for n in [self.b1, self.b2, self.b3, self.b4] if n is not None]
        if not notas_lancadas:
            return "Em Aberto"
        return "Aprovado" if self.media >= 7.0 else "Recuperação"