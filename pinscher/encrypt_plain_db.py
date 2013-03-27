import sys
import StringIO as io
from Crypto.Cipher import AES
from Keyfile import Keyfile


if __name__ == '__main__':
    db_from = sys.argv[1]
    db_to = sys.argv[2]
    keyfile = Keyfile('default', sys.argv[3], 60)
    cipher = AES.new(keyfile.key, AES.MODE_CFB, keyfile.iv)
    output = io.StringIO()
    with open(db_from, 'r') as in_f:
        with open(db_to, 'wb') as out_f:
            out_f.write(cipher.encrypt(in_f.read().encode('utf-8')))
