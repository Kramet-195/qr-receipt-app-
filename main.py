from flask import Flask, request, jsonify, send_file
import qrcode
from io import BytesIO
from cryptography.fernet import Fernet
import base64

app = Flask(__name__)

# Hardcoding the new secret key
SECRET_KEY = b'y5YIl8WAa9DaehnWfffIV5OMsPB1ro30y1ACzCvlHfI='
cipher = Fernet(SECRET_KEY)

BASE_URL = "https://www.linktospin.com/?order_id="

def encrypt_order_id(order_id):
    """Encrypt order ID and return a URL-safe string."""
    encrypted = cipher.encrypt(order_id.encode()).decode()
    return encrypted.rstrip('=')


def decrypt_order_id(encrypted_id):
    """Decrypt the encoded order ID."""
    padding = 4 - (len(encrypted_id) % 4)
    if padding != 4:
        encrypted_id = encrypted_id + ('=' * padding)

    return cipher.decrypt(encrypted_id.encode()).decode()

def generate_qr(encrypted_order_id):
    """Generate a QR code and return it as a PNG byte stream."""
    qr_url = BASE_URL + encrypted_order_id
    qr = qrcode.make(qr_url)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer

@app.route('/generate_qr', methods=['GET'])
def get_qr():
    """API endpoint to generate and return a QR code for an encrypted order ID."""
    order_id = request.args.get('order_id')

    if not order_id:
        return jsonify({"error": "Missing order_id"}), 400

    encrypted_order_id = encrypt_order_id(order_id)
    buffer = generate_qr(encrypted_order_id)

    return send_file(buffer, mimetype='image/png')

@app.route('/decrypt', methods=['GET'])
def decrypt_qr():
    """API to decrypt an order ID from a QR code URL."""
    encrypted_id = request.args.get('order_id')

    if not encrypted_id:
        return jsonify({"error": "Missing encrypted order_id"}), 400

    try:
        decrypted_order_id = decrypt_order_id(encrypted_id)
        return jsonify({"order_id": decrypted_order_id})
    except Exception:
        return jsonify({"error": "Invalid encrypted ID"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
