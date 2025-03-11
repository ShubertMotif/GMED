from app import app, db, Paziente  # Importiamo l'istanza dell'app e il modello Paziente

# Funzione per leggere il file e inserire i dati nel database
def carica_pazienti(file_path):
    with app.app_context():  # Aggiunto il contesto dell'app
        with open(file_path, "r") as file:
            for riga in file:
                dati = riga.strip().split(", ")

                # Gestione di nomi con più di due parole
                nome_completo = dati[0].split(" ")
                nome = " ".join(nome_completo[:-1])  # Tutte le parole tranne l'ultima
                cognome = nome_completo[-1]  # L'ultima parola come cognome

                eta = int(dati[1].split()[0])
                sesso = dati[2]
                peso = float(dati[3].split(": ")[1].split()[0])
                altezza = float(dati[4].split(": ")[1].split()[0])
                bmi = float(dati[5].split(": ")[1])
                dieta = dati[6].split(": ")[1]
                allergia = dati[7].split(": ")[1]
                patologia = dati[8].split(": ")[1]
                farmaco = dati[9].split(": ")[1]

                nuovo_paziente = Paziente(
                    nome=nome,
                    cognome=cognome,
                    data_nascita="1980-01-01",  # Placeholder
                    sesso=sesso,
                    note_mediche=f"Dieta: {dieta}, Allergia: {allergia}, Diagnosi: {patologia}, Farmaci: {farmaco}",
                    medico_id=1  # Assumiamo che l'admin sia il medico ID 1
                )

                db.session.add(nuovo_paziente)

        db.session.commit()
        print("✅ Pazienti caricati con successo!")

# Percorso del file dei pazienti simulati
file_path = "pazienti_simulati.txt"

# Esegui il caricamento
carica_pazienti(file_path)
