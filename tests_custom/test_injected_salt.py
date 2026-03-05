import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib
from core.custom_attacks import InjectedSaltAttack

def test_attack():
    # Setup
    word = "Password123"
    salt = b"0a" # Hex lowercase for 10
    
    # Inject salt at index 5: "Passw" + "0a" + "ord123"
    word_bytes = word.encode('utf-8')
    injected_bytes = word_bytes[:5] + salt + word_bytes[5:]
    target_hash = hashlib.sha256(injected_bytes).hexdigest()
    
    print(f"Test Word: {word}")
    print(f"Injected Bytes: {injected_bytes}")
    print(f"Target Hash: {target_hash}")
    
    # Create wordlist
    wordlist_path = "test_wordlist.txt"
    with open(wordlist_path, "w") as f:
        f.write("wrongword\n")
        f.write(f"{word}\n")
        f.write("anotherwrongword\n")
        
    print("\nRunning attack...")
    attack = InjectedSaltAttack(target_hash=target_hash, wordlist_path=wordlist_path)
    result = attack.execute()
    
    if result:
        print(f"\n[OK] Found matching password: {result}")
        assert result == "Passw0aord123"
        # Clean up
        os.remove(wordlist_path)
    else:
        print(f"\n[FAIL] Could not find the password!")
        # Clean up
        os.remove(wordlist_path)
        assert False, "Could not find the password"

if __name__ == "__main__":
    test_attack()
