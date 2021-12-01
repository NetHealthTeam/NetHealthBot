import joblib
from flask import jsonify
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import re
from datetime import datetime
from datetime import timedelta
import calendar

def make_vocab():
  months = "january|february|march|april|may|june|july|august|september|octember|november|december"
  months = months.split("|")
  vocab = ""
  time = 0
  while True:
    for month in months:
      if len(month)>=3:
        vocab = vocab + month + "|"
    for i in range(len(months)):
      if months[i] != "":
        months[i] = months[i][:-1]
      else: time +=1
    
    if time > 11:
      break
    else: time = 0
  return vocab


def find_month(x,vocab):
  m = re.match(r"\D*([0-9]{1,2}).*("+vocab[:-1]+")", x)
  if m:
    return m.group(1),m.group(2)
  else:
    m = re.match(r".*("+vocab[:-1]+")\D*([0-9]{1,2})", x)
    # print(m.group(2))
    if m: return m.group(2),m.group(1)
    else: return None,None

def find_day(x):
  m = re.match(r".*(today|tomorrow|yesterday|next day|nextday)", x)
  if m:
    return m.group(1)
  else: return None

def find_week_day(x):
  m = re.match(r".*(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", x)
  if m:
    return m.group(1)
  else: return None
  

def find_meal_time(x):
  m = re.match(r".*(lunch|dinner|supper|brunch|breakfast)", x)
  if m:
    return m.group(1)
  else: return None
  
def make_key_month(months):
  # print(months.items)
  new_dict = {}
  for key,value in months.items():
    word = key
    i = 0

    # print(word)
    while len(word) >= 3:
      
      new_dict[word] = value
      i += 1
      word = key[:-i]

      # print(new_dict)
  # print(new_dict)
  return new_dict



def find_date(X):
  months = {"january":1,"february":2,"march":3,"april":4,"may":5,"june":6,"july":7,"august":8,"september":9,"octember":10,"november":11,"december":12}
  days_not_digit = {"today":0,"tomorrow":1,"next day":1,"nextday":1}
  week_days = {"monday":1,"tuesday":2,"wednesday":3,"thursday":4,"friday":5,"saturday":6,"sunday":7}
  '''monday|tuesday|wednesday|thursday|friday|saturday|sunday'''
  week_days
  months = make_key_month(months)
  todays_date = datetime.now()
  day_type = {}
  vocab = make_vocab()
  # print(f"Vocab is\n{vocab}")
  # print(f"sentence:\n{X}")
  day, month = find_month(X,vocab)
  # if not day:
  day_not_digit = find_day(X)
  # if not day:
  week_day = find_week_day(X)
  # if not day:
  meal_time = find_meal_time(X)
  # print(day_not_digit)
    # print("Date is")
  if day and month:
    print("Day and month")
    my_string = str(todays_date.year)+"-"+str(months[month])+"-"+str(day)
    my_date = datetime.strptime(my_string, "%Y-%m-%d")  
    # print(my_date)
    # print(my_date.weekday())
  if day_not_digit:
    print("Days not digit")

    digit = days_not_digit[day_not_digit]
    date_diet = datetime.today() + timedelta(days=digit)
    my_string = str(date_diet.year)+"-"+str(date_diet.month)+"-"+str(date_diet.day)
    my_date = datetime.strptime(my_string, "%Y-%m-%d")  
    print(my_date)
  if week_day:
    print("Week day")

    distance = week_days[week_day] - week_days[str(calendar.day_name[todays_date.weekday()]).lower()]
    if distance < 0:
      distance += 7
    date_diet = datetime.today() + timedelta(days=distance)
    my_string = str(date_diet.year)+"-"+str(date_diet.month)+"-"+str(date_diet.day)
    my_date = datetime.strptime(my_string, "%Y-%m-%d")  
    print(my_date)
  return my_date.weekday(),meal_time

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
    # print(string)

    # string = [stemmer.lemmatize(word) for word in string]
    string = ' '.join(string)
    return string
def find_category(string):
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
        our_dict = {0:"workout",1:"diet for next days",2:"diet for today"}
        args = parser.parse_args()
        txt = args['text']
        txt = clean_str(txt)
        # print("\n\n\n\n\n\n\n")
        # print(txt)
        # print("\n\n\n\n\n\n\n")
        try:
            category  = find_category(txt)
        except:
            category = None
        
        # print("")
        # print(category)
        try:
            day_time, lunch_type = find_date(txt)
                    # print(our_dict[category],day_time,lunch_type)
            # print(day_time.weekday())
            return jsonify({'category': our_dict[category],"date":day_time,"lunch_type":lunch_type})
        except:
            day_time, lunch_type = None,None
            return jsonify({'category': our_dict[category],"date":day_time,"lunch_type":lunch_type})
        # print(our_dict[category],day_time,lunch_type)
        
        return jsonify({'category': our_dict[category],"date":day_time.weekday(),"lunch_type":lunch_type})

api.add_resource(predict_category, '/predict')

if __name__ == '__main__':
    app.run()