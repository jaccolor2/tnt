from flask import Flask, request, send_file
import base64
import tempfile

app = Flask(__name__)

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    request_data = request.json  # Assuming JSON input
    base64_pdf_string = request_data.get('base64_pdf', None)

    if not base64_pdf_string:
        return "Error: Base64 PDF string not provided", 400

    try:
        # Decode the Base64 string
        pdf_data = base64.b64decode(base64_pdf_string)

        # Save the PDF to a temporary file
        temp_pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_pdf_file.write(pdf_data)
        temp_pdf_file.close()

        # Send the PDF file back to the client
        return send_file(temp_pdf_file.name, as_attachment=True, attachment_filename='generated.pdf')

    except Exception as e:
        return f"Error generating PDF: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
