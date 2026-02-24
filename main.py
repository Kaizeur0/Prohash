import sys
from ui.cli_interface import start_cli

def main():
    """Point d'entrée principal de ProHash."""
    try:
        start_cli()
    except KeyboardInterrupt:
        print("\n\n[!] Interruption détectée. Fermeture de ProHash.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Une erreur inattendue s'est produite : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
