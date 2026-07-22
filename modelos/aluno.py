from config import db
from datetime import datetime


class Aluno(db.Model):
    __tablename__ = 'alunos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    matricula = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    curso = db.Column(db.String(100), nullable=False)
    data = db.Column(db.String(20), nullable=False)

    # 1. MODIFICADO: Agora com colunas para os 4 bimestres
    b1 = db.Column(db.Float, default=0.0)
    b2 = db.Column(db.Float, default=0.0)
    b3 = db.Column(db.Float, default=0.0)
    b4 = db.Column(db.Float, default=0.0)

    # 2. MODIFICADO: Construtor atualizado para receber os 4 bimestres
    def __init__(self, nome, matricula, email, curso, data, b1=0.0, b2=0.0, b3=0.0, b4=0.0):
        self.nome = nome
        self.matricula = matricula
        self.email = email
        self.curso = curso
        self.data = data
        self.b1 = float(b1)
        self.b2 = float(b2)
        self.b3 = float(b3)
        self.b4 = float(b4)

    # 3. MODIFICADO: Média calculada dividindo por 4
    @property
    def media(self):
        return round((self.b1 + self.b2 + self.b3 + self.b4) / 4, 1)

    # 4. ACRESCENTADO: % de Frequência calculado direto no modelo
    @property
    def frequencia(self):
        total_aulas = len(self.presencas)
        if total_aulas == 0:
            return 100.0
        presencas_contadas = sum(1 for p in self.presencas if p.status == 'Presente')
        return round((presencas_contadas / total_aulas) * 100, 1)

    # 5. MODIFICADO: Situação validando nota E frequência (menos de 75% reprova!)
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
    data = db.Column(db.Date, default=datetime.utcnow().date, nullable=False)
    status = db.Column(db.String(10), nullable=False)

    aluno = db.relationship('Aluno', backref=db.backref('presencas', cascade='all, delete-orphan'))