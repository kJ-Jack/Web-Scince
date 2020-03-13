import pymongo
import json
import pandas as pd
import spacy
import enchant

DB_connect = "mongodb://localhost:27017/"
DB_name = 'web_science'
DB_table = 'tweets'
path = './class'
emotion_class = {'excitement':['#excitement'],
                 'happy':['#happy'],
                 'pleasant':['#pleasant'], 
                 'surprise':['#surprise'],
                 'fear':['#fear'],
                 'angry':['#angry'],}

def read_file(emotion): 
    tweet_list = []
    file_Object = open(path +'/' + emotion +'.json', 'r').readlines() 
    for inf in file_Object:
        tweet_list.append(json.loads(inf)['text'])
    return  tweet_list

tweets = pd.DataFrame()
for key in emotion_class.keys():
    tweets_emotion = pd.DataFrame(read_file(key), columns=['text'])
    tweets_emotion['emotion'] = key
    tweets = tweets.append(tweets_emotion)

tweets = tweets.drop_duplicates(subset='text').reset_index(drop=True)
#print(tweets)

nlp = spacy.load('en_core_web_sm', disable=['ner'])
nlp.remove_pipe('tagger')
nlp.remove_pipe('parser')

def spacy_tokenize(string):
  tokens = list()
  doc = nlp(string)
  for token in doc:
    tokens.append(token)
  return tokens

def isEmoji(content):
    if not content:
        return False
    if u"\U0001F600" <= content and content <= u"\U0001F64F":
        return True
    elif u"\U0001F300" <= content and content <= u"\U0001F5FF":
        return True
    elif u"\U0001F680" <= content and content <= u"\U0001F6FF":
        return True
    elif u"\U0001F1E0" <= content and content <= u"\U0001F1FF":
        return True
    else:
        return False

def normalize(tokens):
  normalized_tokens = ''
  diction = enchant.Dict("en_UK")
  for token in tokens:
    if ((token.is_alpha and diction.check(token.text)) or isEmoji(token.text)):#and diction.check(diction.suggest(token.text)[0])
      normalized = token.text.lower() + ' '
      normalized_tokens += normalized 
  return normalized_tokens

def tokenize_normalize(string):
  return normalize(spacy_tokenize(string))

myclient = pymongo.MongoClient(DB_connect)
mydb = myclient[DB_name]
mycol = mydb[DB_table]
for i in range(len(tweets)):
  inf = {'id': i+1, 'text':tokenize_normalize(tweets['text'][i]), 'emotion':tokenize_normalize(tweets['emotion'][i])}
  print (inf)
  x = mycol.insert_one(inf) 

