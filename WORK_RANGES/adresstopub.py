import ecdsa
import hashlib
from bitcoin import privkey_to_address
from base58 import b58decode
import binascii
import multiprocessing
from itertools import product


def find_public_key_and_private_key_from_address(args):
    hash_address, lower_range, upper_range, keys_scanned = args
    count = 0
    for i in range(lower_range, upper_range):
        count += 1
        private_key_hex = format(i, '064x')
        private_key = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex), curve=ecdsa.SECP256k1)
        public_key = private_key.get_verifying_key()
        public_key_compressed = b'\x02' + public_key.to_string()[:32] if public_key.to_string()[32] % 2 == 0 else b'\x03' + public_key.to_string()[:32]
        current_address = privkey_to_address(private_key_hex, magicbyte=0x00)
        current_address_compressed = privkey_to_address(private_key_hex, magicbyte=0x6f)
        keys_scanned.append(1)
        if count % 10000 == 0:
            print(f"Public Key: {binascii.hexlify(public_key_compressed).decode()}")
            print(f"Private Key: {private_key_hex}")
            print(f"Address: {current_address}")
            print(f"Compressed Address: {current_address_compressed}")
        if current_address == hash_address or current_address_compressed == hash_address:
            return public_key_compressed, private_key_hex
    return None, None


def address_to_hash(address):
    decoded_address = b58decode(address)
    hash_address = binascii.hexlify(decoded_address).decode('utf-8')
    return hash_address[2:-8]


def print_keys_scanned(keys_scanned):
    while True:
        print(f"Scanned keys: {len(keys_scanned)}", end='\r')


def main():
    address = '13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so'
    hash_address = address_to_hash(address)
    lower_range = 0x20000000000000000
    upper_range = 0x3ffffffffffffffff

    # Divide the search range into smaller ranges for multiprocessing
    num_processes = int(multiprocessing.cpu_count() * 0.9)  # 90% of available CPUs
    step = (upper_range - lower_range) // num_processes
    ranges = [(lower_range + i * step, lower_range + (i + 1) * step) for i in range(num_processes)]

    with multiprocessing.Manager() as manager:
        keys_scanned = manager.list()
        pool = multiprocessing.Pool(num_processes)
        pool.apply_async(print_keys_scanned, args=(keys_scanned,))
        public_key, private_key_hex = next((pk, sk) for pk, sk in pool.map(find_public_key_and_private_key_from_address, [(hash_address, lr, ur, keys_scanned) for lr, ur in ranges]) if pk is not None), (None, None)

    print(f"Address: {address}")
    print(f"Hash160: {hash_address}")

    if public_key:
        print(f"Public Key: {binascii.hexlify(public_key).decode()}")
        print(f"Private Key: {private_key_hex}")
        with open('found_keys.txt', 'w') as f:
            f.write(f"Address: {address}\n")
            f.write(f"Public Key: {binascii.hexlify(public_key).decode()}\n")
            f.write(f"Private Key: {private_key_hex}\n")
    else:
        print("Public Key not found in the specified range.")


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
