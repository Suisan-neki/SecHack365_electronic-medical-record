#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SecHack365 患者中心の医療DXプロジェクト
SSL証明書生成スクリプト（モノレポ対応版）
"""

import os
import argparse
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime

def generate_self_signed_cert(cert_dir="certs", common_name="localhost"):
    """
    自己署名証明書を生成する
    
    Args:
        cert_dir (str): 証明書を保存するディレクトリ
        common_name (str): 証明書のコモンネーム
    """
    
    # 出力ディレクトリが存在しない場合は作成
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
        print(f"[INFO] 証明書ディレクトリを作成しました: {cert_dir}")
    
    print("[INFO] SSL証明書を生成中...")
    
    # 秘密鍵を生成（セキュリティ強化のため4096bit）
    print("[INFO] RSA秘密鍵を生成中（4096bit）...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    
    # 証明書の主体情報を設定
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"JP"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Tokyo"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Tokyo"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"SecHack365 Medical DX Project"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u"Development"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])
    
    # 証明書を作成
    print("[INFO] X.509証明書を生成中...")
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        # 開発用として1年間有効
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(common_name),
            x509.DNSName("127.0.0.1"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]),
        critical=False,
    ).add_extension(
        x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            content_commitment=False,
            data_encipherment=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    ).add_extension(
        x509.ExtendedKeyUsage([
            x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
        ]),
        critical=True,
    ).sign(private_key, hashes.SHA256())
    
    # ファイルパスを設定
    cert_path = os.path.join(cert_dir, "cert.pem")
    key_path = os.path.join(cert_dir, "key.pem")
    
    # 証明書をファイルに保存
    print(f"[INFO] 証明書を保存中: {cert_path}")
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    # 秘密鍵をファイルに保存
    print(f"[INFO] 秘密鍵を保存中: {key_path}")
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    print("[SUCCESS] SSL証明書の生成が完了しました")
    print(f"[INFO] 証明書: {cert_path}")
    print(f"[INFO] 秘密鍵: {key_path}")
    print("[WARNING] この証明書は開発用の自己署名証明書です")
    print("[WARNING] 本番環境では信頼できるCA発行の証明書を使用してください")
    
    return cert_path, key_path

if __name__ == "__main__":
    import ipaddress
    
    parser = argparse.ArgumentParser(
        description="SecHack365 医療DXプロジェクト用SSL証明書生成ツール"
    )
    parser.add_argument(
        '--cert-dir', 
        default='certs', 
        help='証明書を保存するディレクトリ (デフォルト: certs)'
    )
    parser.add_argument(
        '--common-name', 
        default='localhost', 
        help='証明書のコモンネーム (デフォルト: localhost)'
    )
    
    args = parser.parse_args()
    
    try:
        generate_self_signed_cert(
            cert_dir=args.cert_dir,
            common_name=args.common_name
        )
    except Exception as e:
        print(f"[ERROR] 証明書生成エラー: {e}")
        exit(1)
