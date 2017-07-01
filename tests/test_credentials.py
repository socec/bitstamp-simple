from bitstamp_simple.credentials import Credentials, Cryptography

def test_data_encrypt_decrypt():
    password = 'pass'
    plaintext = 'foobar'
    encrypted = Cryptography.data_encrypt(password, plaintext)
    decrypted = Cryptography.data_decrypt(password, encrypted)
    assert decrypted == plaintext
