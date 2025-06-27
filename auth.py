import jwt
import datetime
from jwt.exceptions import ExpiredSignatureError

# 全局密钥
secret = '12asdffa2323'

# 生成token
def encode_func(user):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),  # 过期时间
        'iat': datetime.datetime.utcnow(),  # 签发时间
        'iss': 'cyz',  # 签发者
        'data': user
    }
    encoded = jwt.encode(payload, secret, algorithm='HS256')
    return encoded

# 解析token
def decode_func(token):
    if not token or token.count('.') != 2:
        raise ValueError("无效的Token格式，必须为三段结构")

    try:
        decoded = jwt.decode(token, secret, issuer='cyz', algorithms=['HS256'])
        print("JWT解析成功：", decoded)
        return decoded['data']
    except ExpiredSignatureError:
        raise ValueError("Token已过期，请重新登录")
    except Exception as e:
        raise ValueError(f"Token解析失败：{str(e)}")
