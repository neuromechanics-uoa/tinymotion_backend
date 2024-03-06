import os
import hashlib

from tinymotion_backend.core.encryption import encrypt_file, decrypt_file


def test_file_encryption_decryption(tmp_path):
    # write some contents to a temporary file
    tmp_file = tmp_path / "myfile.txt"
    tmp_file.write_text("hello")

    # compute the hash
    with tmp_file.open('rb') as fin:
        digest = hashlib.file_digest(fin, 'sha256')

    # encrypt the file
    enc_file = tmp_path / "myfile.txt.enc"
    with tmp_file.open('rb') as fin:
        orig_hash, enc_hash = encrypt_file(fin, enc_file)

    assert os.path.exists(enc_file)
    assert digest.hexdigest() == orig_hash

    with open(enc_file, 'rb') as fin:
        digest_enc = hashlib.file_digest(fin, 'sha256')

    assert digest_enc.hexdigest() == enc_hash
    assert digest.hexdigest() != digest_enc.hexdigest()

    # decrypt the file
    out_file = str(tmp_path / "myfile2.txt")
    orig_hash2 = decrypt_file(enc_file, out_file)
    assert os.path.exists(out_file)
    assert orig_hash2 == orig_hash

    # check contents
    with open(out_file, 'r') as fin:
        content = fin.read()

    assert content == "hello"
