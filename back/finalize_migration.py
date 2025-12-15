"""
Script pour finaliser la migration - convertir les champs ID restants
"""

from database.database import engine
from sqlalchemy import text

def finalize_migration():
    print("=== Finalisation de la migration ===\n")
    
    try:
        with engine.connect() as connection:
            # 1. Renommer id_utilisateur en identifiant dans la table utilisateur
            print("1. Renommage de id_utilisateur en identifiant...")
            connection.execute(text("ALTER TABLE utilisateur RENAME COLUMN id_utilisateur TO identifiant"))
            print("   ✓ Renommage effectué")
            
            # 2. Convertir tous les autres champs ID de int en varchar(100)
            tables_and_columns = [
                ('formation', 'id_formation'),
                ('promotion', 'id_promotion'),
                ('etudiant', 'id_etudiant'),
                ('formateur', 'id_formateur'),
                ('espace_pedagogique', 'id_espace'),
                ('travail', 'id_travail'),
                ('groupe_etudiant', 'id_groupe'),
                ('assignation', 'id_assignation'),
                ('livraison', 'id_livraison')
            ]
            
            for table, column in tables_and_columns:
                print(f"2. Conversion de {table}.{column} en varchar(100)...")
                
                # Pour MySQL, on doit d'ajouter une nouvelle colonne, copier les données, puis supprimer l'ancienne
                # Étape 1: Ajouter la nouvelle colonne
                connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column}_temp VARCHAR(100)"))
                
                # Étape 2: Copier les données (conversion de int à varchar)
                connection.execute(text(f"UPDATE {table} SET {column}_temp = CAST({column} AS VARCHAR(100))"))
                
                # Étape 3: Supprimer l'ancienne colonne
                connection.execute(text(f"ALTER TABLE {table} DROP COLUMN {column}"))
                
                # Étape 4: Renommer la nouvelle colonne
                connection.execute(text(f"ALTER TABLE {table} RENAME COLUMN {column}_temp TO {column}"))
                
                print(f"   ✓ Conversion de {table}.{column} effectuée")
            
            # 3. Mettre à jour le DE existant pour marquer le mot de passe comme temporaire
            print("\n3. Mise à jour du compte DE...")
            connection.execute(text("""
                UPDATE utilisateur 
                SET mot_de_passe_temporaire = 1 
                WHERE email = 'de@genielogiciel.com'
            """))
            print("   ✓ Compte DE mis à jour")
            
            print("\n=== Migration finalisée avec succès ===")
            
    except Exception as e:
        print(f"Erreur lors de la finalisation: {e}")
        raise

if __name__ == "__main__":
    finalize_migration()