from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime

# 秘密鍵を生成
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
)

# 証明書を作成
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"JP"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Tokyo"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Tokyo"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Test"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
])

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
    datetime.datetime.utcnow() + datetime.timedelta(days=365)
).add_extension(
    x509.SubjectAlternativeName([
        x509.DNSName(u"localhost"),
    ]),
    critical=False,
).sign(private_key, hashes.SHA256())

# ファイルに保存
with open("cert.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

with open("key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

print("証明書が生成されました: cert.pem, key.pem")
