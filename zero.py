import sqlite3

# Chemin de la base de données SQLite
DATABASE_PATH = "images.db"

def reset_shown_values():
    """Réinitialise la colonne 'shown' pour tous les enregistrements à zéro."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE images SET shown = 0")
    conn.commit()
    print("All 'shown' values have been reset to 0.")
    conn.close()

if __name__ == "__main__":
    reset_shown_values()
