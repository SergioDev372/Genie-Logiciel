#!/usr/bin/env python3
"""
Script de test pour la nouvelle logique de création de comptes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.generators import generer_mot_de_passe_aleatoire
from core.jwt import get_password_hash, verify_password

def test_generation_mot_de_passe():
    """Test de génération de mots de passe simples"""
    print("=== Test génération mots de passe ===")
    
    for i in range(10):
        mdp = generer_mot_de_passe_aleatoire()
        print(f"Mot de passe {i+1}: {mdp}")
        
        # Vérifier que le mot de passe ne contient que A-Z et 0-9
        caracteres_valides = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        caracteres_mdp = set(mdp)
        
        if not caracteres_mdp.issubset(caracteres_valides):
            print(f"❌ ERREUR: Caractères invalides dans {mdp}")
            print(f"   Caractères trouvés: {caracteres_mdp}")
            print(f"   Caractères invalides: {caracteres_mdp - caracteres_valides}")
        else:
            print(f"✅ OK: Mot de passe valide")
    
    print()

def test_hashage_verification():
    """Test du hashage et de la vérification"""
    print("=== Test hashage et vérification ===")
    
    mots_de_passe_test = [
        "ABC123XY",
        "Z9Y8X7W6",
        "HELLO123",
        "TEST4567"
    ]
    
    for mdp in mots_de_passe_test:
        print(f"\nTest avec: {mdp}")
        hash_mdp = get_password_hash(mdp)
        print(f"Hash: {hash_mdp[:20]}...")
        
        # Test de vérification (sans debug pour plus de clarté)
        import core.jwt
        # Temporairement désactiver les prints de debug
        original_print = print
        def silent_print(*args, **kwargs):
            if not any("Debug:" in str(arg) for arg in args):
                original_print(*args, **kwargs)
        
        import builtins
        builtins.print = silent_print
        
        verification = verify_password(mdp, hash_mdp)
        
        builtins.print = original_print
        
        if verification:
            print("✅ Vérification réussie")
        else:
            print("❌ Vérification échouée")

if __name__ == "__main__":
    test_generation_mot_de_passe()
    test_hashage_verification()
    print("\n=== Tests terminés ===")