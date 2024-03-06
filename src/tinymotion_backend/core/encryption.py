import logging
import hashlib
import struct

from cryptography.fernet import Fernet

from tinymotion_backend.core.config import settings


logger = logging.getLogger(__name__)


def encrypt_file(input_file_handle, output_file_path):
    """
    Encrypts the given file using Fernet.

    Returns the SHA256 checksum of the unencrypted content and the encrypted
    content.

    """
    # create Fernet object for encrypting the video
    fernet = Fernet(settings.VIDEO_SECRET_KEY)

    # sha256 objects for calculating the hashes
    hash_orig = hashlib.sha256()
    hash_enc = hashlib.sha256()

    # next we store the video file to disk
    with open(output_file_path, "wb") as out_file:
        while content := input_file_handle.read(settings.FILE_CHUNK_SIZE_BYTES):
            # apply encryption
            enc_content = fernet.encrypt(content)

            # write the size of the encrypted chunk, which isn't the same as the unencrypted chunk
            # to help with reading back in later
            enc_content_len = struct.pack("<I", len(enc_content))
            out_file.write(enc_content_len)

            # write the encrypted content to file
            out_file.write(enc_content)

            # computing the hash of the unencrypted content
            hash_orig.update(content)

            # computing the hash of the encrypted content
            hash_enc.update(enc_content_len)
            hash_enc.update(enc_content)

    return hash_orig.hexdigest(), hash_enc.hexdigest()


def decrypt_file(input_file_path, output_file_path):
    """
    Decrypts the input file and stores it at the given output file path.

    Returns the sha256 checksum of the decrypted file.

    """
    # Fernet object for decrypting the video
    fernet = Fernet(settings.VIDEO_SECRET_KEY)

    # sha256 object for calculating the hash
    hash_decrypted = hashlib.sha256()

    # open the files and do the decryption
    with open(input_file_path, 'rb') as fin, open(output_file_path, 'wb') as fout:
        while True:
            size_data = fin.read(4)
            if len(size_data) == 0:
                break
            chunk_enc = fin.read(struct.unpack("<I", size_data)[0])
            chunk_dec = fernet.decrypt(chunk_enc)
            hash_decrypted.update(chunk_dec)
            fout.write(chunk_dec)

    return hash_decrypted.hexdigest()
