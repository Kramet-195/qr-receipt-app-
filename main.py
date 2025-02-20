from flask import Flask, render_template, send_file
import qrcode
import random
import io

app = Flask(__name__)

# List to store unique 8-digit codes
codes = [str(random.randint(10000000, 99999999)) for _ in range(1000)]


# Function to generate a QR code for the link
def generate_qr_code(url):
    img = qrcode.make(url)
    byte_io = io.BytesIO()
    img.save(byte_io, 'PNG')
    byte_io.seek(0)
    return byte_io


@app.route('/')
def index():
    # Get a random code from the list
    if codes:
        code = codes.pop(random.randint(0, len(codes) - 1))  # Pop a random code
        url = f"https://www.linktospin.com/{code}"  # The URL with the code

        # Generate the QR code
        qr_code_image = generate_qr_code(url)

        # Return the receipt with QR code and the used code
        return render_template('receipt.html', qr_code_image=qr_code_image, code=code)
    else:
        return "No codes available", 404


if __name__ == '__main__':
    app.run(debug=True)
