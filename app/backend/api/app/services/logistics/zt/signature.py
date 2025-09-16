import base64
import hashlib


def md5_base64_byte(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    # 二进制数据字符串值
    md5_str = m.digest()
    b64_str = base64.b64encode(md5_str)
    return b64_str.decode('utf-8')


def signature(string):
    return md5_base64_byte(string)
