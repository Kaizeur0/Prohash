import base64
import json
from utils.logger import log_info, log_error

class JWTExtractor:
    """Module pour extraire les informations d'un JSON Web Token et le préparer pour Hashcat."""

    @staticmethod
    def is_jwt(token: str) -> bool:
        """Vérifie sommairement si une chaîne ressemble à un JWT."""
        parts = token.split('.')
        return len(parts) == 3

    @staticmethod
    def _decode_base64url(data: str) -> bytes:
        """Décode une chaîne Base64URL en ajoutant le padding nécessaire."""
        padding = '=' * (4 - (len(data) % 4))
        return base64.urlsafe_b64decode(data + padding)

    def extract(self, token: str) -> dict | None:
        """
        Extrait le header, le payload et prépare le format Hashcat.
        Retourne un dictionnaire avec les infos ou None si erreur.
        """
        token = token.strip()
        
        if not self.is_jwt(token):
            log_error("Le hash fourni ne ressemble pas à un JWT valide (doit contenir 3 parties séparées par des points).")
            return None

        parts = token.split('.')
        
        try:
            header_json = json.loads(self._decode_base64url(parts[0]).decode('utf-8'))
            payload_json = json.loads(self._decode_base64url(parts[1]).decode('utf-8'))
            
            # Format attendu par Hashcat pour le mode 16500 : le token JWT complet
            # C'est Hashcat lui-même qui gère la séparation en interne pour HMAC-SHA256,
            # mais on le valide ici pour être sûr qu'il est utilisable.
            
            alg = header_json.get('alg', 'Inconnu')
            if alg.upper() != 'HS256':
                log_info(f"[!] Attention : L'algorithme du token est {alg}. Hashcat (mode 16500) est optimisé pour HS256 (HMAC-SHA256).")

            log_info(f"[+] JWT détecté. Algorithme: {alg}")
            
            return {
                "header": header_json,
                "payload": payload_json,
                "token": token,
                "hashcat_mode": 16500
            }
            
        except Exception as e:
            log_error(f"Impossible de décoder le JWT : {e}")
            return None

if __name__ == '__main__':
    # Exemple de test rapide
    sample_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    extractor = JWTExtractor()
    result = extractor.extract(sample_jwt)
    if result:
        print("Header :", result['header'])
        print("Format Hashcat prêt :", result['token'])
