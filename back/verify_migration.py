"""
Script pour vérifier si les modifications ont été appliquées à la base de données
"""

from database.database import engine
from sqlalchemy import text

def check_database_structure():
    print("=== Vérification de la structure de la base de données ===\n")
    
    try:
        with engine.connect() as connection:
            # Vérifier la table utilisateur
            print("1. Vérification de la table utilisateur:")
            result = connection.execute(text("DESCRIBE utilisateur"))
            utilisateur_columns = result.fetchall()
            
            for col in utilisateur_columns:
                print(f"   - {col[0]}: {col[1]} {'(NOT NULL)' if col[2] == 'NO' else ''} {col[3] if col[3] else ''}")
            
            # Vérifier si le champ mot_de_passe_temporaire existe
            mot_de_passe_temp_exists = any(col[0] == 'mot_de_passe_temporaire' for col in utilisateur_columns)
            print(f"   ✓ Champ 'mot_de_passe_temporaire': {'EXISTE' if mot_de_passe_temp_exists else 'N\'EXISTE PAS'}")
            
            # Vérifier si le champ identifiant existe (au lieu de id_utilisateur)
            identifiant_exists = any(col[0] == 'identifiant' for col in utilisateur_columns)
            id_utilisateur_exists = any(col[0] == 'id_utilisateur' for col in utilisateur_columns)
            print(f"   ✓ Champ 'identifiant': {'EXISTE' if identifiant_exists else 'N\'EXISTE PAS'}")
            print(f"   ✓ Champ 'id_utilisateur': {'EXISTE' if id_utilisateur_exists else 'N\'EXISTE PAS'}")
            
            print("\n2. Vérification de la table tentative_connexion:")
            result = connection.execute(text("SHOW TABLES LIKE 'tentative_connexion'"))
            table_exists = result.fetchone() is not None
            print(f"   ✓ Table 'tentative_connexion': {'EXISTE' if table_exists else 'N\'EXISTE PAS'}")
            
            if table_exists:
                result = connection.execute(text("DESCRIBE tentative_connexion"))
                tentative_columns = result.fetchall()
                for col in tentative_columns:
                    print(f"   - {col[0]}: {col[1]} {'(NOT NULL)' if col[2] == 'NO' else ''} {col[3] if col[3] else ''}")
            
            print("\n3. Vérification des autres tables:")
            tables_to_check = ['formation', 'promotion', 'etudiant', 'formateur', 'espace_pedagogique', 'travail', 'groupe_etudiant', 'assignation', 'livraison']
            
            for table in tables_to_check:
                result = connection.execute(text(f"DESCRIBE {table}"))
                columns = result.fetchall()
                
                # Vérifier si le champ ID est en String ou Integer
                id_column = next((col for col in columns if col[0].startswith('id_') or col[0] == 'identifiant'), None)
                if id_column:
                    id_name = id_column[0]
                    id_type = id_column[1]
                    print(f"   ✓ {table}.{id_name}: {id_type}")
            
            print("\n=== Vérification terminée ===")
            
    except Exception as e:
        print(f"Erreur lors de la vérification: {e}")

if __name__ == "__main__":
    check_database_structure()