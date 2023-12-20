from flask import Flask, request, jsonify
import os
import magic
import uuid
from werkzeug.utils import secure_filename
from pydub import AudioSegment

app = Flask(__name__)

# Set the secure upload folder and maximum content length
app.config['UPLOAD_FOLDER'] = '/path/to/secure/upload/folder'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Function to check if the file type is allowed
def allowed_file(filename):
    mime = magic.Magic()
    file_type = mime.from_file(filename)
    return file_type.startswith('audio/') or file_type.startswith('video/')

# Function to generate a unique filename
def generate_unique_filename(original_filename):
    filename = secure_filename(original_filename)
    base, extension = os.path.splitext(filename)
    unique_filename = f"{base}_{uuid.uuid4().hex}{extension}"
    return unique_filename

# Function to sanitize filenames
def sanitize_filename(filename):
    return secure_filename(filename)

@app.route('/api/convert-to-text', methods=['POST'])
def convert_to_text():
    try:
        # Get the uploaded file
        audio_file = request.files['audio']

        # Check if the file is allowed
        if not allowed_file(audio_file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        # Generate a unique filename
        filename = generate_unique_filename(audio_file.filename)
        
        # Save the file securely
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(file_path)

        # Convert the audio file to wav format
        sound = AudioSegment.from_file(file_path)
        sound.export(file_path, format="wav")

        # Use SpeechRecognition to transcribe the audio
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)

        text_result = recognizer.recognize_google(audio_data)

        # Return the transcribed text
        return jsonify({'text': text_result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
