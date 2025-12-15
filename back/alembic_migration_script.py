"""
Migration script for adding mot_de_passe_temporaire field and tentative_connexion table
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Add mot_de_passe_temporaire column to utilisateur table
    op.add_column('utilisateur', 
        sa.Column('mot_de_passe_temporaire', sa.Boolean(), 
                  nullable=False, server_default='0')
    )
    
    # Create tentative_connexion table
    op.create_table('tentative_connexion',
        sa.Column('id_tentative', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=191), nullable=False),
        sa.Column('date_tentative', sa.DateTime(), nullable=False, 
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('succes', sa.Boolean(), nullable=False, 
                  server_default='0'),
        sa.PrimaryKeyConstraint('id_tentative')
    )
    
    # Update existing DE user to mark password as temporary
    op.execute("""
        UPDATE utilisateur 
        SET mot_de_passe_temporaire = TRUE 
        WHERE email = 'de@genielogiciel.com'
    """)


def downgrade():
    # Remove the mot_de_passe_temporaire column
    op.drop_column('utilisateur', 'mot_de_passe_temporaire')
    
    # Drop the tentative_connexion table
    op.drop_table('tentative_connexion')
    
    # Reset mot_de_passe_temporaire to FALSE for DE user (optional)
    op.execute("""
        UPDATE utilisateur 
        SET mot_de_passe_temporaire = FALSE 
        WHERE email = 'de@genielogiciel.com'
    """)