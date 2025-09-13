from flask import Flask, render_template, jsonify
import json
from core.hash_chain import HashChain
from core.digital_signature import generate_keys, sign_data, verify_signature

app = Flask(__name__)

# デモ用JSONデータの読み込み
# with open(\'app/demo_karte.json\', \'r\', encoding=\'utf-8\') as f:
#     patient_data = json.load(f)

@app.route(\'/\')
def index():
    return render_template(\'index.html\')

@app.route(\'/patient_data\')
def get_patient_data():
    with open(\'app/demo_karte.json\', \'r\', encoding=\'utf-8\') as f:
        data = json.load(f)
    return jsonify(data)

# 以下はハッシュチェーンと電子署名のデモ用エンドポイント（必要に応じて追加）
@app.route(\'/hash_chain_demo\')
def hash_chain_demo():
    hash_chain = HashChain()
    hash_chain.add_block({\"patient_id\": \"P001\", \"event\": \"診察開始\"})
    hash_chain.add_block({\"patient_id\": \"P001\", \"event\": \"処方箋発行\"})
    return jsonify({\"chain_valid\": hash_chain.is_valid(), \"chain\": hash_chain.chain})

@app.route(\'/digital_signature_demo\')
def digital_signature_demo():
    private_key, public_key = generate_keys()
    message = \"これは署名されるメッセージです。\"
    signature = sign_data(private_key, message)
    is_valid = verify_signature(public_key, message, signature)
    return jsonify({\"message\": message, \"signature_valid\": is_valid})

if __name__ == \'__main__\':
    # cert.pem と key.pem はFlaskアプリケーションと同じディレクトリに配置
    # 開発環境でのみ使用し、本番環境ではNginxなどのリバースプロキシでHTTPSを構成することを推奨
    app.run(debug=True, ssl_context=(\'app/cert.pem\', \'app/key.pem\'))
