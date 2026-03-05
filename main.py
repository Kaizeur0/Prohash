import sys
import argparse
from ui.cli_interface import start_cli
from core.custom_attacks import InjectedSaltAttack

def main():
    """Point d'entrée principal de ProHash."""
    parser = argparse.ArgumentParser(description="ProHash - L'Assistant Hashcat Intelligent")
    parser.add_argument("--mode", type=str, choices=["injected-salt"], help="Mode d'attaque spécifique")
    parser.add_argument("--hash", type=str, help="Le hash cible")
    parser.add_argument("--wordlist", type=str, help="Chemin vers la wordlist")
    
    args = parser.parse_args()

    try:
        if args.mode == "injected-salt":
            if not args.hash or not args.wordlist:
                print("[!] Erreur: Les arguments --hash et --wordlist sont requis pour ce mode.")
                sys.exit(1)
                
            print(f"\n[*] Démarrage de l'attaque Injected Salt sur le hash: {args.hash}")
            attack = InjectedSaltAttack(target_hash=args.hash, wordlist_path=args.wordlist)
            
            # Record start time
            import time
            start_time = time.time()
            
            result = attack.execute()
            
            elapsed = time.time() - start_time
            print(f"[*] Attaque terminée en {elapsed:.2f} secondes.")
            
            if result:
                print(f"\n[+] SUCCESS: Le mot de passe est -> {result}")
            else:
                print("\n[-] ECHEC: Mot de passe non trouvé dans la wordlist.")
            sys.exit(0)
            
        else:
            # Mode interactif par défaut
            start_cli()
            
    except KeyboardInterrupt:
        print("\n\n[!] Interruption détectée. Fermeture de ProHash.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Une erreur inattendue s'est produite : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
