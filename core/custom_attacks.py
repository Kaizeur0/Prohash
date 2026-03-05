import hashlib
import binascii
import concurrent.futures
import multiprocessing
import time
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn

class InjectedSaltAttack:
    """
    Module pour l'attaque Hybride par Injection de Sel.
    Fait glisser un sel (0-255) à l'intérieur de chaque mot d'une wordlist.
    """
    
    def __init__(self, target_hash: str, wordlist_path: str):
        self.target_hash = target_hash.lower()
        self.wordlist_path = wordlist_path
        self.num_cores = multiprocessing.cpu_count()
        self.found_password = None
    
    @staticmethod
    def _hash_sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _generate_salt_variations(salt_val: int) -> list[bytes]:
        """Génère les 3 variations de sel d'un octet pour une valeur donnée (0-255)"""
        # 1. Raw byte
        v1 = bytes([salt_val])
        # 2. Hex lowercase (ex: b"0a")
        hex_str_lower = f"{salt_val:02x}".encode('utf-8')
        # 3. Hex uppercase (ex: b"0A")
        hex_str_upper = f"{salt_val:02X}".encode('utf-8')
        
        return [v1, hex_str_lower, hex_str_upper]

    @classmethod
    def process_chunk(cls, word_chunk: list[str], target_hash: str) -> tuple[bool, str | None, str | None]:
        """
        Traite un sous-ensemble de mots.
        Retourne (is_found, plaintext_found, error_msg)
        """
        # Pré-générer toutes les variations de sels une seule fois pour optimiser
        all_salts = []
        for i in range(256):
            all_salts.extend(cls._generate_salt_variations(i))
            
        for base_word in word_chunk:
            base_word = base_word.strip()
            if not base_word:
                continue
                
            # Variations du mot
            words_to_test = [
                base_word,
                base_word.lower(),
                base_word.upper()
            ]
            
            for word in words_to_test:
                try:
                    word_bytes = word.encode('utf-8')
                except UnicodeEncodeError:
                    continue # Skip words that can't be encoded
                
                word_len = len(word_bytes)
                
                # Pour chaque sel pré-généré
                for salt in all_salts:
                    # Faire glisser le sel à chaque position possible
                    for i in range(word_len + 1):
                        candidate = word_bytes[:i] + salt + word_bytes[i:]
                        
                        if cls._hash_sha256(candidate) == target_hash:
                            # Essayer de décoder pour l'affichage, sinon fallback sur la représentation brute
                            try:
                                decoded_candidate = candidate.decode('utf-8')
                            except UnicodeDecodeError:
                                decoded_candidate = str(candidate)
                            return True, decoded_candidate, None
                            
        return False, None, None

    def execute(self) -> str | None:
        """
        Lance l'attaque en utilisant le multiprocessing.
        Retourne le mot de passe en clair s'il est trouvé.
        """
        try:
            with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                words = f.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"La wordlist '{self.wordlist_path}' est introuvable.")

        total_words = len(words)
        if total_words == 0:
            return None

        # Découper en chunks pour le multiprocessing
        chunk_size = max(1, total_words // (self.num_cores * 4)) # Over-provisioning factor of 4
        chunks = [words[i:i + chunk_size] for i in range(0, total_words, chunk_size)]
        
        print(f"\n[*] Préparation de l'attaque: {total_words:,} mots à tester")
        print(f"[*] Variations estimées: ~{total_words * 3 * 256 * 3 * 5:,} hashs à calculer") # Very rough estimate assuming avg length 5
        print(f"[*] Lancement sur {self.num_cores} cœurs CPU...\n")

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        ) as progress:
            
            task_id = progress.add_task("[cyan]Progression...", total=len(chunks))
            
            with concurrent.futures.ProcessPoolExecutor(max_workers=self.num_cores) as executor:
                # Soumettre tous les jobs
                future_to_chunk = {
                    executor.submit(self.process_chunk, chunk, self.target_hash): chunk 
                    for chunk in chunks
                }
                
                # Récupérer les résultats au fur et à mesure
                for future in concurrent.futures.as_completed(future_to_chunk):
                    if self.found_password: # Si on l'a déjà trouvé dans un autre processus, on skip
                        progress.update(task_id, advance=1)
                        continue
                        
                    try:
                        is_found, plaintext, error = future.result()
                        if is_found:
                            self.found_password = plaintext
                            # Annuler les futures en attente (optionnel mais bon pour les perfs)
                            for f in future_to_chunk:
                                f.cancel()
                    except Exception as exc:
                        print(f"\n[!] Erreur dans un worker: {exc}")
                        
                    progress.update(task_id, advance=1)
                    
        return self.found_password
