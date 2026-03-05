import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib
from core.custom_attacks import InjectedSaltAttack

def test_attack_sha256():
    word = "Password123"
    salt = b"0a" # Hex lowercase for 10
    
    word_bytes = word.encode('utf-8')
    injected_bytes = word_bytes[:5] + salt + word_bytes[5:]
    target_hash = hashlib.sha256(injected_bytes).hexdigest()
    
    wordlist_path = "test_wordlist_sha256.txt"
    with open(wordlist_path, "w") as f:
        f.write("wrongword\n")
        f.write(f"{word}\n")
        
    attack = InjectedSaltAttack(target_hash=target_hash, wordlist_path=wordlist_path, algorithm="sha256")
    result = attack.execute()
    
    assert result == "Passw0aord123"
    os.remove(wordlist_path)

def test_attack_md5():
    word = "admin"
    salt = b"\n" # Raw byte for \x0a
    
    word_bytes = word.encode('utf-8')
    injected_bytes = word_bytes[:2] + salt + word_bytes[2:] # "ad\nmin"
    target_hash = hashlib.md5(injected_bytes).hexdigest()
    
    wordlist_path = "test_wordlist_md5.txt"
    with open(wordlist_path, "w") as f:
        f.write("foo\n")
        f.write(f"{word}\n")
        
    attack = InjectedSaltAttack(target_hash=target_hash, wordlist_path=wordlist_path, algorithm="md5")
    result = attack.execute()
    
    assert result == "ad\nmin"
    os.remove(wordlist_path)

if __name__ == "__main__":
    test_attack_sha256()
    test_attack_md5()
