from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
from stego import Steganography
from werkzeug.utils import secure_filename
from flask import session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Add this near the top of your file

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode_page')
def encode_page():
    return render_template('encode.html')

@app.route('/decode_page')
def decode_page():
    # Clear any existing decoded message when loading the page
    session.pop('decoded_message', None)
    return render_template('decode.html', decoded_message=None)

@app.route('/download_message')
def download_message():
    message = session.get('decoded_message')
    if message:
        # Create a text file with the message
        message_path = os.path.join(app.config['UPLOAD_FOLDER'], 'decoded_message.txt')
        with open(message_path, 'w') as f:
            f.write(message)
        return send_file(message_path, as_attachment=True, download_name='decoded_message.txt')
    return redirect(url_for('decode_page'))

@app.route('/encode', methods=['POST'])
def encode():
    if 'file' not in request.files:
        flash('No file uploaded')
        return render_template('index.html')
    
    file = request.files['file']
    message = request.form.get('message', '')
    
    if file.filename == '' or not allowed_file(file.filename):
        flash('Invalid file type. Please upload a PNG image.')
        return render_template('index.html')
    
    try:
        # Save uploaded file
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input.png')
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.png')
        file.save(input_path)
        
        # Encode message
        stego = Steganography()
        stego.encode(input_path, message, output_path)
        
        # Return the encoded image
        return send_file(output_path, as_attachment=True, download_name='output.png')
    
    except Exception as e:
        flash(f'Error: {str(e)}')
        return render_template('index.html')

@app.route('/decode', methods=['POST'])
def decode():
    if 'file' not in request.files:
        flash('No file uploaded')
        return redirect(url_for('decode_page'))
    
    file = request.files['file']
    
    if file.filename == '' or not allowed_file(file.filename):
        flash('Invalid file type. Please upload a PNG image.')
        return redirect(url_for('decode_page'))
    
    try:
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], 'decode_input.png')
        file.save(input_path)
        
        stego = Steganography()
        message = stego.decode(input_path)
        
        if message:
            # Store message in session for download and display
            session['decoded_message'] = message
            return render_template('decode.html', decoded_message=message)
        else:
            flash('No message found in the image')
            
    except Exception as e:
        flash(f'Error: {str(e)}')
    
    return redirect(url_for('decode_page'))

if __name__ == '__main__':
    app.run(debug=True)