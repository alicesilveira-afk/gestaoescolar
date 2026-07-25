from flask import Blueprint, render_template, request, redirect, url_for

bp_auth = Blueprint('auth', __name__)

@bp_auth.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        nome = request.form.get('nome')
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        # Lógica de gravação aqui...

        return redirect(url_for('index')) # ou url_for('auth.index')

    return render_template('cadastrar.html')