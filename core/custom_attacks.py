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
    
    def __init__(self, target_hash: str, wordlist_path: str, algorithm: str = "sha256"):
        self.target_hash = target_hash.lower()
        self.wordlist_path = wordlist_path
        self.algorithm = algorithm.lower()
        self.num_cores = multiprocessing.cpu_count()
        self.found_password = None
    
    @staticmethod
    def _hash_data(data: bytes, algo_name: str) -> str:
        """Hache les données en utilisant l'algorithme spécifié."""
        h = hashlib.new(algo_name)
        h.update(data)
        return h.hexdigest()

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
    def process_chunk(cls, word_chunk: list[str], target_hash: str, algorithm: str) -> tuple[bool, str | None, str | None]:
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
                        
                        if cls._hash_data(candidate, algorithm) == target_hash:
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
        Lecture de la wordlist par chunks pour optimiser la RAM.
        Retourne le mot de passe en clair s'il est trouvé.
        """
        import math
        
        try:
            # First pass: count lines safely to establish total progress
            with open(self.wordlist_path, 'rb') as f:
                total_words = 0
                while buf := f.read(1024 * 1024):
                    total_words += buf.count(b'\n')
        except FileNotFoundError:
            raise FileNotFoundError(f"La wordlist '{self.wordlist_path}' est introuvable.")

        if total_words == 0:
            return None

        # Determine chunk size: cap at 100,000 words per chunk to prevent memory bloat
        chunk_size = max(1000, min(100_000, total_words // (self.num_cores * 4)))
        total_chunks = math.ceil(total_words / chunk_size)
        
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
            
            task_id = progress.add_task("[cyan]Progression...", total=total_chunks)
            
            with concurrent.futures.ProcessPoolExecutor(max_workers=self.num_cores) as executor:
                futures = set()
                
                with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                    chunk = []
                    for line in f:
                        chunk.append(line)
                        if len(chunk) >= chunk_size:
                            # If queue is too large, wait for at least one to finish
                            while len(futures) >= self.num_cores * 4:
                                done, futures = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
                                for future in done:
                                    if self.found_password:
                                        break
                                    try:
                                        is_found, plaintext, error = future.result()
                                        if is_found:
                                            self.found_password = plaintext
                                    except Exception as exc:
                                        print(f"\n[!] Erreur dans un worker: {exc}")
                                    progress.update(task_id, advance=1)
                            
                            if self.found_password:
                                break
                            
                            future = executor.submit(self.process_chunk, chunk, self.target_hash, self.algorithm)
                            futures.add(future)
                            chunk = []
                            
                    # Submit the last chunk if any
                    if chunk and not self.found_password:
                        future = executor.submit(self.process_chunk, chunk, self.target_hash, self.algorithm)
                        futures.add(future)

                # Wait for remaining
                for future in concurrent.futures.as_completed(futures):
                    if self.found_password:
                        progress.update(task_id, advance=1)
                        continue
                        
                    try:
                        is_found, plaintext, error = future.result()
                        if is_found:
                            self.found_password = plaintext
                            for f in futures:
                                f.cancel()
                    except Exception as exc:
                        print(f"\n[!] Erreur dans un worker: {exc}")
                        
                    progress.update(task_id, advance=1)
                    
        return self.found_password
