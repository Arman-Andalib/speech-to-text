import os
from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
import google.generativeai as genai
from pydub import AudioSegment

app = Flask(__name__)

# Configure the Google Generative AI with your API key
genai.configure(api_key="AIzaSyDVrw35-dZ-xRF3DpcZaoSiV38l6SfRDXw")
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize the recognizer
recognizer = sr.Recognizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    # Retrieve the audio file from the request
    audio_file = request.files['audio']
    temp_audio_path = 'temp_audio.webm'
    audio_file.save(temp_audio_path)
    
    audio_segment = AudioSegment.from_file(temp_audio_path)
    wav_path = 'audio.wav'
    audio_segment.export(wav_path, format='wav')

    # Recognize speech from the audio file
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio, language="fa-IR,en-US")
            print(f"Transcribed Text: {text}")
            
            # Get response from the Gemini model
            gemini_response = model.generate_content(text).text
            print(f"Gemini AI Response: {gemini_response}")
            
            # Return both the transcribed text and the Gemini AI response as JSON
            return jsonify({
                'transcribed_text': text,
                'gemini_response': gemini_response
            })
        
        except sr.UnknownValueError:
            return jsonify({'error': 'Could not understand audio'}), 400
        except sr.RequestError as e:
            return jsonify({'error': f'Speech Recognition error: {e}'}), 500
        except Exception as e:
            return jsonify({'error': f'Processing error: {e}'}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True)
if __name__ == '__main__':
    app.run(ssl_context=('https.crt', 'https.key'), host='0.0.0.0', port=443)