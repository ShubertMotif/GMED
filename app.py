from flask import Flask, render_template, request
import pubchempy as pcp

app = Flask(__name__)

def get_structure_image(compound_name):
    compounds = pcp.get_compounds(compound_name, 'name')
    if compounds:
        cid = compounds[0].cid
        return f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG'
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    if query:
        results = pcp.get_compounds(query, 'name')
        if results:
            image_url = get_structure_image(query)
            return render_template('results.html', query=query, results=results, image_url=image_url)
    return render_template('index.html', error="Farmaco non trovato.")

@app.route('/processo')
def processo():
    return render_template('processo.html')

@app.route('/calcoli')
def calcoli():
    return render_template('calcoli.html')

@app.route('/aggiungi_farmaco', methods=['GET', 'POST'])
def aggiungi_farmaco():
    return render_template('aggiungi_farmaco.html')

@app.route('/contatti')
def contatti():
    return render_template('contatti.html')

if __name__ == '__main__':
    app.run(debug=True)
