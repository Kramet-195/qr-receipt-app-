from flask import Flask, request, jsonify, send_file
import qrcode
from io import BytesIO
from cryptography.fernet import Fernet
import base64
import os

app = Flask(__name__)

# Get the Fernet key from Railway environment variables
STATIC_KEY = os.environ.get("STATIC_KEY")

if not STATIC_KEY:
    raise ValueError("STATIC_KEY environment variable is not set!")

try:
    cipher = Fernet(STATIC_KEY.encode())  # Ensure it's in the correct format
except Exception:
    raise ValueError("Invalid STATIC_KEY! Ensure it is a 32-byte base64-encoded string.")

BASE_URL = "https://www.linktospin.com/?order_id="

def encrypt_order_id(order_id):
    """Encrypt order ID and return a URL-safe encoded string."""
    encrypted_id = cipher.encrypt(order_id.encode())
    return base64.urlsafe_b64encode(encrypted_id).decode()

def decrypt_order_id(encrypted_id):
    """Decrypt the encoded order ID."""
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_id)
    return cipher.decrypt(encrypted_bytes).decode()

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
