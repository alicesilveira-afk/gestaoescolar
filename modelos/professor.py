from config import db


class Professor(db.Model):
    __tablename__ = 'professores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    disciplina = db.Column(db.String(100), nullable=False)

    def __init__(self, nome, usuario, senha, disciplina):
        self.nome = nome
        self.usuario = usuario
        self.senha = senha
        self.disciplina = disciplina