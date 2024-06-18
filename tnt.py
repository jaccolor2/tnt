from flask import Flask, request, send_file
import base64
import tempfile
import os
import requests
from fpdf import FPDF
from PIL import Image

app = Flask(__name__)

@app.route('/', methods=['POST'])
def generate_pdf():
    request_data = request.json  # Assuming JSON input
    base64_zpl_string = request_data.get('base64_zpl', None)

    if not base64_zpl_string:
        return "Error: Base64 ZPL string not provided", 400

    try:
        # Decode the Base64 string
        zpl_data = base64.b64decode(base64_zpl_string).decode('utf-8')

        # Convert ZPL to PNG using Labelary
        files = {'file': ('label.zpl', zpl_data)}
        response = requests.post('http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/', files=files, headers={'Accept': 'application/pdf'})
        
        if response.status_code != 200:
            return f"Error converting ZPL to image: {response.text}", 500

        # Save the PNG to a temporary file
        temp_image_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_image_file.write(response.content)
        temp_image_file.close()

        # Convert the PNG to PDF using Pillow and FPDF
        image = Image.open(temp_image_file.name)
        pdf = FPDF()
        pdf.add_page()
        pdf.image(temp_image_file.name, x=10, y=8, w=pdf.w - 20)
        temp_pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_pdf_file.name)
        
        # Send the PDF file back to the client
        return send_file(temp_pdf_file.name, as_attachment=True)

    except Exception as e:
        return f"Error generating PDF: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
