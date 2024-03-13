import os
import hashlib

import pytest

from tinymotion_backend.core.encryption import encrypt_file, decrypt_file
from tinymotion_backend.core.config import settings


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


@pytest.mark.parametrize("multiplier", [
    0.7,
    1.4,
    2.7,
])
def test_file_encryption_decryption_larger(tmp_path, multiplier):
    # create a tmp file with random contents of specified size
    tmp_file = tmp_path / "input.dat"
    tmp_file.write_bytes(os.urandom(int(multiplier * settings.FILE_CHUNK_SIZE_BYTES)))

    # compute the hash
    with tmp_file.open('rb') as fin:
        digest = hashlib.file_digest(fin, 'sha256')

    # encrypt the file
    enc_file = tmp_path / "encrypted.dat"
    with tmp_file.open('rb') as fin:
        orig_hash, enc_hash = encrypt_file(fin, enc_file)

    # compute hash of encrypted file
    with open(enc_file, 'rb') as fin:
        digest_enc = hashlib.file_digest(fin, 'sha256')

    assert digest_enc.hexdigest() == enc_hash
    assert digest.hexdigest() != digest_enc.hexdigest()

    # decrypt the file
    out_file = str(tmp_path / "output.dat")
    out_hash = decrypt_file(enc_file, out_file)
    assert os.path.exists(out_file)
    assert out_hash == orig_hash

    # check contents
    with open(out_file, 'rb') as fin:
        out_hash2 = hashlib.file_digest(fin, 'sha256').hexdigest()

    assert out_hash == out_hash2
