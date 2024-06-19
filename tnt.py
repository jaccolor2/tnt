from flask import Flask, request, send_file, jsonify
import requests
import shutil
import base64
import tempfile
import os

app = Flask(__name__)

def convert_base64_to_pdf(base64_zpl, output_file='label.pdf', label_size='5x6', density='8dpmm'):
    try:
        # Decode base64 ZPL to raw ZPL string
        zpl = base64.b64decode(base64_zpl).decode('utf-8')

        # Construct URL with label size and density parameters
        url = f'http://api.labelary.com/v1/printers/{density}/labels/{label_size}/0/'
        
        # Set headers to accept PDF
        headers = {'Accept': 'application/pdf'}  # Change to 'image/png' for PNG images

        # Make POST request to Labelary API
        response = requests.post(url, headers=headers, data=zpl, stream=True)

        # Check if request was successful
        if response.status_code == 200:
            # Save the PDF response to a file
            with open(output_file, 'wb') as out_file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, out_file)
            return True, None  # Success
        else:
            return False, f"Error: {response.status_code} - {response.text}"  # Failure
    except Exception as e:
        return False, f"Error: {str(e)}"

@app.route('/', methods=['POST'])
def generate_pdf():
    request_data = request.json  # Assuming JSON input
    base64_zpl_string = request_data.get('base64_zpl', None)

    if not base64_zpl_string:
        return jsonify({"error": "Base64 ZPL string not provided"}), 400

    try:
        # Create a temporary file to save the PDF
        temp_pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_pdf_file.close()
        
        # Convert the base64 ZPL to PDF
        success, error_message = convert_base64_to_pdf(base64_zpl_string, output_file=temp_pdf_file.name)

        if success:
            # Send the PDF file back to the client
            return send_file(temp_pdf_file.name, as_attachment=True)
        else:
            return jsonify({"error": error_message}), 500

    except Exception as e:
        return jsonify({"error": f"Error generating PDF: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
