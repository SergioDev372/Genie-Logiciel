"""
Migration script corrigée pour:
1. Ajout du champ mot_de_passe_temporaire
2. Création de la table tentative_connexion
3. Conversion des champs ID de Integer à String (avec les bons noms de colonnes)
"""

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    # 1. Ajouter le champ mot_de_passe_temporaire à la table utilisateur
    op.add_column('utilisateur', 
        sa.Column('mot_de_passe_temporaire', sa.Boolean(), 
                  nullable=False, server_default='0')
    )
    
    # 2. Créer la table tentative_connexion
    op.create_table('tentative_connexion',
        sa.Column('id_tentative', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=191), nullable=False),
        sa.Column('date_tentative', sa.DateTime(), nullable=False, 
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('succes', sa.Boolean(), nullable=False, 
                  server_default='0'),
        sa.PrimaryKeyConstraint('id_tentative')
    )
    
    # 3. Conversion des champs ID de Integer à String (avec les bons noms)
    
    # Pour la table utilisateur (id_utilisateur -> identifiant)
    op.alter_column('utilisateur', 'id_utilisateur',
        existing_type=sa.Integer(),
        type_=sa.String(100),
        nullable=False,
        primary_key=True
    )
    
    # Renommer la colonne id_utilisateur en identifiant
    op.execute('ALTER TABLE utilisateur RENAME COLUMN id_utilisateur TO identifiant')
    
    # Pour la table formation
    op.alter_column('formation', 'id_formation',
        existing_type=sa.Integer(),
        type_=sa.String(100),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table promotion
    op.alter_column('promotion', 'id_promotion',
        existing_type=sa.Integer(),
        type_=sa.String(100),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table etudiant
    op.alter_column('etudiant', 'id_etudiant',
        existing_type=sa.Integer(),
        type_=sa.String(100),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table formateur
    op.alter_column('formateur', 'id_formateur',
        existing_type=sa.Integer(),
        type_=sa.String(100),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table espace_pedagogique
    op.alter_column('espace_pedagogique', 'id_espace',
        existing_type=sa.Integer(),
        type_=sa.String(100),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table travail
    op.alter_column('travail', 'id_travail',
        existing_type=sa.Integer(),
        type_=sa.String(100),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table groupe_etudiant
    op.alter_column('groupe_etudiant', 'id_groupe',
        existing_type=sa.Integer(),
        type_=sa.String(100),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table assignation
    op.alter_column('assignation', 'id_assignation',
        existing_type=sa.Integer(),
        type_=sa.String(100),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table livraison
    op.alter_column('livraison', 'id_livraison',
        existing_type=sa.Integer(),
        type_=sa.String(100),
        nullable=False,
        primary_key=True
    )
    
    # 4. Mettre à jour le DE existant pour marquer le mot de passe comme temporaire
    op.execute("""
        UPDATE utilisateur 
        SET mot_de_passe_temporaire = TRUE 
        WHERE email = 'de@genielogiciel.com'
    """)


def downgrade() -> None:
    # 1. Remettre les champs ID en Integer
    
    # Pour la table livraison
    op.alter_column('livraison', 'id_livraison',
        existing_type=sa.String(100),
        type_=sa.Integer(),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table assignation
    op.alter_column('assignation', 'id_assignation',
        existing_type=sa.String(100),
        type_=sa.Integer(),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table groupe_etudiant
    op.alter_column('groupe_etudiant', 'id_groupe',
        existing_type=sa.String(100),
        type_=sa.Integer(),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table travail
    op.alter_column('travail', 'id_travail',
        existing_type=sa.String(100),
        type_=sa.Integer(),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table espace_pedagogique
    op.alter_column('espace_pedagogique', 'id_espace',
        existing_type=sa.String(100),
        type_=sa.Integer(),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table formateur
    op.alter_column('formateur', 'id_formateur',
        existing_type=sa.String(100),
        type_=sa.Integer(),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table etudiant
    op.alter_column('etudiant', 'id_etudiant',
        existing_type=sa.String(100),
        type_=sa.Integer(),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table promotion
    op.alter_column('promotion', 'id_promotion',
        existing_type=sa.String(100),
        type_=sa.Integer(),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table formation
    op.alter_column('formation', 'id_formation',
        existing_type=sa.String(100),
        type_=sa.Integer(),
        nullable=False,
        primary_key=True
    )
    
    # Pour la table utilisateur (renommer en id_utilisateur)
    op.execute('ALTER TABLE utilisateur RENAME COLUMN identifiant TO id_utilisateur')
    
    op.alter_column('utilisateur', 'id_utilisateur',
        existing_type=sa.String(100),
        type_=sa.Integer(),
        nullable=False,
        primary_key=True
    )
    
    # 2. Supprimer la table tentative_connexion
    op.drop_table('tentative_connexion')
    
    # 3. Supprimer le champ mot_de_passe_temporaire
    op.drop_column('utilisateur', 'mot_de_passe_temporaire')
    
    # 4. Remettre à FALSE pour le DE (optionnel)
    op.execute("""
        UPDATE utilisateur 
        SET mot_de_passe_temporaire = FALSE 
        WHERE email = 'de@genielogiciel.com'
    """)