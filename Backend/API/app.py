from flask import Flask, jsonify, request
from flask_restx import Resource, Api
from flask_cors import CORS
import collections
import joblib
import pandas as pd
import re
import csv

app = Flask(__name__)
CORS(app)
api = Api(app)

model = joblib.load('phishing_classifier.joblib')
calibrator = joblib.load('phishing_model_calibrator.joblib')
data = pd.read_csv('emails.csv').drop('Email No.', axis=1)

with open('suspicious_words.csv', 'r') as file:
    reader = csv.reader(file)
    top_phishing_words = list(reader)[0]


def preprocess(email):
    def count_words(email):
        # Tokenize the email into words using a regular expression
        words = email.split()
        # Count the frequency of each word
        word_count = collections.Counter(words)
        return word_count

    # Count the words in the email
    email_word_count = count_words(email)

    data.columns = data.columns.astype(str)

    # Create a new dataframe row with the same columns, initialized to 0
    new_email = pd.DataFrame([0]*(len(data.columns) - 1), index=data.drop(['Prediction'], axis=1).columns).transpose()

    # Update the counts in the new row using the email word count
    for word, count in email_word_count.items():
        if word in new_email.columns:
            new_email.loc[0, word] = count

    return new_email


@api.route('/highlight-phishing-indicators')
class HighlightIndicators(Resource):
    def get(self):
        highlighted_email = request.args.get('email')
        
        for feature in top_phishing_words:
            # Use re.escape to escape any special characters in the feature string
            feature_escaped = re.escape(feature)
            # Replace the feature with a highlighted version
            highlighted_email = re.sub(
                f"({feature_escaped})", 
                r"<span class='highlight'>\1</span>", 
                highlighted_email, 
                flags=re.IGNORECASE
            )

        return jsonify({'highlighted_email': highlighted_email})


@api.route('/predict')
class Predict(Resource):
    def get(self):
        # Get the email string from the query parameter
        email_body = request.args.get('email')  

        # Preprocess email_body to match the model input format
        feature_vector = preprocess(email_body)

        # Make a prediction
        prediction = model.predict(feature_vector)

        # Determine probability of prediction being correct
        probability = calibrator.predict_proba(feature_vector)
        
        # Return the result as JSON
        return jsonify({
            'is_phishing': bool(prediction[0]),
            'probability': str(round(float(max(probability[0])) * 100, 2)) + '%',
        })
    

if __name__ == '__main__':
    app.run(debug=True)