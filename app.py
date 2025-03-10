from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import pubchempy as pcp

# Configurazione dell'app Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'DATA', 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersegreto'

# Inizializzazione database e autenticazione
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# =======================
# 📌 Modelli del Database
# =======================

class Medico(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    pazienti = db.relationship('Paziente', backref='medico', lazy=True)

class Paziente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100), nullable=False)
    data_nascita = db.Column(db.String(10), nullable=False)  # Formato YYYY-MM-DD
    sesso = db.Column(db.String(10), nullable=False)
    note_mediche = db.Column(db.Text, nullable=True)
    farmaci = db.relationship('Farmaco', backref='paziente', lazy=True)
    medico_id = db.Column(db.Integer, db.ForeignKey('medico.id'), nullable=False)

class Farmaco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    principio_attivo = db.Column(db.String(255), nullable=False)
    dose = db.Column(db.String(50), nullable=True)
    effetti_collaterali = db.Column(db.Text, nullable=True)
    paziente_id = db.Column(db.Integer, db.ForeignKey('paziente.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Medico, int(user_id))


# =======================
# 📌 ROUTE PRINCIPALI
# =======================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Permette ai medici di registrarsi solo con username e password"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')

        if Medico.query.filter_by(username=username).first():
            flash("Username già in uso!", "danger")
            return redirect(url_for('register'))

        nuovo_medico = Medico(username=username, password=password)
        db.session.add(nuovo_medico)
        db.session.commit()
        flash("Registrazione completata! Ora puoi accedere.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Gestisce il login del medico usando solo username e password"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        medico = Medico.query.filter_by(username=username).first()

        if medico and bcrypt.check_password_hash(medico.password, password):
            login_user(medico)
            flash("Accesso effettuato con successo!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Username o password errati!", "danger")

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Sei uscito dal sistema.", "info")
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard del medico con i pazienti"""
    pazienti = Paziente.query.filter_by(medico_id=current_user.id).all()
    return render_template('dashboard.html', pazienti=pazienti)

@app.route('/aggiungi_paziente', methods=['GET', 'POST'])
@login_required
def aggiungi_paziente():
    """Aggiunta di un nuovo paziente"""
    if request.method == 'POST':
        nome = request.form.get('nome')
        cognome = request.form.get('cognome')
        data_nascita = request.form.get('data_nascita')
        sesso = request.form.get('sesso')
        note_mediche = request.form.get('note_mediche')

        nuovo_paziente = Paziente(
            nome=nome, cognome=cognome, data_nascita=data_nascita,
            sesso=sesso, note_mediche=note_mediche, medico_id=current_user.id
        )
        db.session.add(nuovo_paziente)
        db.session.commit()
        flash("Paziente aggiunto con successo!", "success")
        return redirect(url_for('dashboard'))

    return render_template('aggiungi_paziente.html')

@app.route('/aggiungi_farmaco', methods=['GET', 'POST'])
@login_required
def aggiungi_farmaco():
    """Registra un nuovo farmaco e lo assegna a un paziente"""

    # Ottieni i pazienti del medico loggato per il menu a tendina
    pazienti = Paziente.query.filter_by(medico_id=current_user.id).all()

    if request.method == 'POST':
        nome = request.form.get('nome')
        principio_attivo = request.form.get('principio_attivo')
        dose = request.form.get('dose')
        effetti_collaterali = request.form.get('effetti_collaterali')
        paziente_id = request.form.get('paziente_id')

        # Controllo che il paziente esista
        paziente = Paziente.query.get(paziente_id)
        if not paziente or paziente.medico_id != current_user.id:
            flash("Paziente non valido!", "danger")
            return redirect(url_for('aggiungi_farmaco'))

        # Creazione del nuovo farmaco
        nuovo_farmaco = Farmaco(
            nome=nome,
            principio_attivo=principio_attivo,
            dose=dose,
            effetti_collaterali=effetti_collaterali,
            paziente_id=paziente_id
        )
        db.session.add(nuovo_farmaco)
        db.session.commit()
        flash("Farmaco registrato con successo!", "success")
        return redirect(url_for('dashboard'))

    return render_template('aggiungi_farmaco.html', pazienti=pazienti)


@app.route('/database')
@login_required
def database():
    """Mostra tutti i farmaci salvati in una tabella"""
    farmaci = Farmaco.query.all()
    return render_template('database.html', farmaci=farmaci)

@app.route('/contatti')
def contatti():
    """Pagina dei contatti"""
    return render_template('contatti.html')


@app.route('/search', methods=['POST'])
def search():
    """Cerca un farmaco nel database interno e mostra i risultati"""
    query = request.form.get('query')

    if not query:
        flash("Inserisci un nome di farmaco valido!", "warning")
        return redirect(url_for('index'))

    # Cerca il farmaco nel database
    farmaco = Farmaco.query.filter(Farmaco.nome.ilike(f"%{query}%")).first()

    if farmaco:
        return render_template('results.html', query=query, farmaco=farmaco)
    else:
        flash("Nessun farmaco trovato nel database!", "warning")
        return redirect(url_for('index'))



@app.route('/save', methods=['POST'])
def save():
    """Salva un farmaco nel database con le note personalizzate."""
    nome = request.form.get('nome')
    formula = request.form.get('formula')
    peso_molecolare = request.form.get('peso_molecolare')
    note = request.form.get('note')

    if nome:
        nuovo_farmaco = Farmaco(nome=nome, formula=formula, peso_molecolare=peso_molecolare, note=note)
        db.session.add(nuovo_farmaco)
        db.session.commit()

    return redirect(url_for('saved_farmaci'))

@app.route('/saved')
def saved_farmaci():
    """Mostra tutti i farmaci salvati nel database."""
    farmaci = Farmaco.query.all()
    return render_template('saved.html', farmaci=farmaci)



# =======================
# 📌 AVVIO SERVER
# =======================
if __name__ == '__main__':
    app.run(debug=True)
