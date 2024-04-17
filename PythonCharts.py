import cohere
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

API_KEY = "qv7pDTi066ZRdBGIvSaeZJG6VCWspDbVLfkTJnRN"
PROMPT = "Please provide a JSON containing the specific columns like chart type, x-axis, y-axis, category, size, latitude, longitude, aggregator, title, as well as any relevant details which are missing for each suggested visualization based on the provided data:"

ALLOWED_EXTENSIONS = {'json'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        
        uploaded_file = request.files['file']

        if uploaded_file.filename == '':
            return jsonify({'error': 'No selected file'})

        if uploaded_file and allowed_file(uploaded_file.filename):
            file_path = os.path.join(os.getcwd(), uploaded_file.filename)
            uploaded_file.save(file_path)

            # Process the file (add your logic here)
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)

            # Perform analysis on the uploaded file
            analysis_result = analyze_json_with_cohere(data)

            return jsonify({'analysis_result': analysis_result})
        else:
            return jsonify({'error': 'Invalid file format'})
    except Exception as e:
        return jsonify({'error': str(e)})

def analyze_json_with_cohere(json_data):
    # Convert JSON data to DataFrame
    df = pd.DataFrame(json_data)

    # Perform analysis using Cohere
    data_str = df.to_string()
    co = cohere.Client(API_KEY)
    full_prompt = PROMPT + "\n\n" + data_str
    response = co.generate(
        model="command-xlarge-nightly",
        prompt=full_prompt,
        max_tokens=800,  # Adjust max_tokens based on the complexity of the analysis
        temperature=0.5,  # Experiment with temperature for generating diverse yet relevant responses
        k=3,   # k allows you to balance between diversity and quality in the generated text.
        p=0.9,   # Adjust k and p for better control over diversity and relevance
        frequency_penalty=0,  #parameter penalizes words that appear too frequently in the generated text
        presence_penalty=0,   #parameter penalizes repetition of similar phrases or concepts in the generated text
        stop_sequences=["--"],  #parameter specifies sequences of tokens that, when encountered in the generated text, signal the model to stop generating further text
        return_likelihoods='NONE'  #parameter specifies whether to return the likelihoods of each generated sequence
    )

    return response.generations[0].text

if __name__ == '__main__':
    app.run(debug=True, port=3000)
