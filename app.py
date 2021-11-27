import joblib
from flask import jsonify
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import re


def clean_str(string):
    # string = re.sub(r'\W', ' ', str(X[sen]))
    
    # remove all single characters
    string = re.sub(r'\s+[a-zA-Z]\s+', ' ', string)
    
    # Remove single characters from the start
    string = re.sub(r'\^[a-zA-Z]\s+', ' ', string) 
    
    # Substituting multiple spaces with single space
    string = re.sub(r'\s+', ' ', string, flags=re.I)
    
    # Removing prefixed 'b'
    string = re.sub(r'^b\s+', '', string)
    
    # Converting to Lowercase
    string = string.lower()
    
    # Lemmatization
    string = string.split()
    print(string)

    # string = [stemmer.lemmatize(word) for word in string]
    string = ' '.join(string)
    return string
def find_category(string):
    string = clean_str(string)
    classifier = joblib.load("./random_forest.joblib")
    vectorizer = joblib.load("./vectorizer.joblib")
    tfidfconverter = joblib.load("./tfidfconverter.joblib")
    
    # print(type(vectorizer))
    docs_new = [string]
    X_new_counts = vectorizer.transform(docs_new)
    X_new_tfidf = tfidfconverter.transform(X_new_counts)

    predicted = classifier.predict(X_new_tfidf)
    return int(predicted[0])




app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()  # used to parse incoming requests
parser.add_argument('text', required=True,
                    help='Text cannot be blank!')

class predict_category(Resource):
    def post(self):
        args = parser.parse_args()
        txt = args['text']
        print("\n\n\n\n\n\n\n")
        print(txt)
        print("\n\n\n\n\n\n\n")
        category  = find_category(txt)
        print(category)
        return jsonify({'category': category})

api.add_resource(predict_category, '/predict')

if __name__ == '__main__':
    app.run()