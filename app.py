from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pubchempy as pcp

app = Flask(__name__)

# Configura SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farmaci.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modello per i farmaci salvati
class Farmaco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    formula = db.Column(db.String(50), nullable=True)
    peso_molecolare = db.Column(db.Float, nullable=True)
    note = db.Column(db.String(255), nullable=True)

# Creazione del database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """Cerca un farmaco su PubChem e mostra i risultati."""
    query = request.form.get('query')
    if query:
        # Ricerca su PubChem
        results = pcp.get_compounds(query, 'name')

        # Se troviamo dei risultati, passiamo i dati alla pagina dei risultati
        if results:
            compound = results[0]  # Prendiamo il primo risultato (puoi modificarlo per gestire più risultati)
            return render_template('results.html', query=query, compound=compound)

    # Se non trova nulla, mostriamo un errore nella pagina
    return render_template('index.html', error="Farmaco non trovato.")


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

@app.route('/database')
def database():
    """Mostra tutti i farmaci salvati in una tabella"""
    farmaci = Farmaco.query.all()
    """Pagina per calcoli sulle interazioni farmacologiche"""
    return render_template('database.html')

@app.route('/aggiungi_farmaco')
def aggiungi_farmaco():
    """Pagina dei contatti"""
    return render_template('aggiungi_farmaco.html')

@app.route('/contatti')
def contatti():
    """Pagina dei contatti"""
    return render_template('contatti.html')


if __name__ == '__main__':
    app.run(debug=True)
