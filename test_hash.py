#!/usr/bin/env python3
"""
测试密码哈希验证
"""
from passlib.context import CryptContext

# 密码上下文配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    if not plain_password or not hashed_password:
        return False

    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"密码验证失败: {e}")
        return False

def hash_password(password: str) -> str:
    """哈希密码"""
    if not password:
        raise ValueError("密码不能为空")

    try:
        return pwd_context.hash(password)
    except Exception as e:
        print(f"密码哈希失败: {e}")
        raise

if __name__ == "__main__":
    # 测试密码验证
    password = 'admin123'
    stored_hash = '$2b$12$Yzyq1aldxtXP0f2lxX2ewOim0XYHbmLkyaAcnCxTI.JaHy0oHsvWW'

    print(f'密码: {password}')
    print(f'存储的哈希: {stored_hash}')
    print(f'验证结果: {verify_password(password, stored_hash)}')

    # 生成新的哈希用于比较
    new_hash = hash_password(password)
    print(f'新生成的哈希: {new_hash}')
    print(f'新哈希验证: {verify_password(password, new_hash)}')

    # 测试其他可能的密码
    test_passwords = ['admin123', 'admin', '123456', 'password']
    print(f'\n测试不同密码与存储哈希的匹配:')
    for pwd in test_passwords:
        result = verify_password(pwd, stored_hash)
        print(f'  {pwd} -> {result}')
