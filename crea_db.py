from app import db, app

# Crea il database e le tabelle
with app.app_context():
    db.create_all()
    print("Database creato con successo!")
