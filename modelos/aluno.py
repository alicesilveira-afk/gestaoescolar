from config import db
from datetime import datetime


class Aluno(db.Model):
    __tablename__ = 'alunos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    matricula = db.Column(db.String(20), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False, default='123')
    email = db.Column(db.String(100), unique=False, nullable=True)
    curso = db.Column(db.String(100), nullable=False, default='Técnico em Informática')
    data = db.Column(db.String(20), nullable=False, default='2026')


    b1 = db.Column(db.Float, nullable=True, default=None)
    b2 = db.Column(db.Float, nullable=True, default=None)
    b3 = db.Column(db.Float, nullable=True, default=None)
    b4 = db.Column(db.Float, nullable=True, default=None)


    presencas = db.relationship(
        'Presenca',
        backref='aluno',
        cascade='all, delete-orphan',
        lazy=True
    )

    notas_disciplinas = db.relationship(
        'Nota',
        backref='aluno_rel',
        cascade='all, delete-orphan',
        lazy=True
    )

    def __init__(self, nome, matricula, senha='123', email=None, curso='Técnico em Informática', data='2026', b1=None, b2=None, b3=None, b4=None):
        self.nome = nome
        self.matricula = matricula
        self.senha = senha
        self.email = email or f"{matricula}@escola.com"
        self.curso = curso
        self.data = data
        self.b1 = float(b1) if b1 is not None and str(b1).strip() != '' else None
        self.b2 = float(b2) if b2 is not None and str(b2).strip() != '' else None
        self.b3 = float(b3) if b3 is not None and str(b3).strip() != '' else None
        self.b4 = float(b4) if b4 is not None and str(b4).strip() != '' else None

    @property
    def media(self):
        notas_validas = [n for n in [self.b1, self.b2, self.b3, self.b4] if n is not None]
        if not notas_validas:
            return 0.0
        return round(sum(notas_validas) / len(notas_validas), 1)

    @property
    def frequencia(self):
        total_aulas = len(self.presencas)
        if total_aulas == 0:
            return 100.0
        presencas_contadas = sum(1 for p in self.presencas if p.status == 'Presente')
        return round((presencas_contadas / total_aulas) * 100, 1)

    @property
    def situacao(self):
        if self.frequencia < 75.0:
            return "Reprovado por Falta"

        m = self.media
        if m >= 7.0:
            return "Aprovado"
        else:
            return "Recuperação"


class Presenca(db.Model):
    __tablename__ = 'presencas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    matricula_aluno = db.Column(db.String(20), db.ForeignKey('alunos.matricula'), nullable=False)
    data = db.Column(db.Date, default=lambda: datetime.now().date(), nullable=False)
    status = db.Column(db.String(10), nullable=False)