from fastapi import FastAPI
from firebase_admin import credentials, initialize_app, storage, firestore
from gtts import gTTS
from dotenv import load_dotenv
import os
import random
import string

api = FastAPI()
load_dotenv()

cred = credentials.Certificate(os.environ.get('firebase_cred_path'))
initialize_app(cred, {'storageBucket': 'with-touch.appspot.com'})

def random_file_name():
    _LENGTH = 16
    string_pool = string.ascii_letters
    random_file = ""
    
    for i in range(_LENGTH):
        random_file += random.choice(string_pool)
    
    return random_file

@api.get('/upload')
def upload(name, description):
    random_file = random_file_name()

    tts = gTTS(
        text=name + " " + description,
        lang='ko', slow=False
    )
    tts.save(random_file+'.mp3')

    bucket = storage.bucket()
    blob = bucket.blob(random_file+'.mp3')
    blob.upload_from_filename(random_file+'.mp3')

    blob.make_public()

    os.remove(random_file+'.mp3')

    return blob.public_url

@api.get('/upload_food')
def upload_food(barcode, name, description, price, what, kcal, sodium, carbohydrates, sugars, fats, trans_fat, saturated_fat, cholesterol, proteins, calcium):

    file_name = barcode

    tts = gTTS(
        text=f"{name}은 {description} 가격은 {price}입니다. 영양 정보는 칼로리는 {kcal}칼로리이며 나트륨은 {sodium}미리그람, 탄수화물은 {carbohydrates}그람, 당류는 {sugars}그람, 지방은 {fats}그람, 트랜스 지방은 {trans_fat}그람, 포화지방은 {saturated_fat}그람, 콜리스테롤은 {cholesterol}, 단백질은 {proteins}그람이며 칼슘은 {calcium}미리그람입니다.",
        lang='ko', slow=False
    )
    tts.save(file_name+'.mp3')

    bucket = storage.bucket()
    blob = bucket.blob(file_name+'.mp3')
    blob.upload_from_filename(file_name+'.mp3')

    blob.make_public()

    os.remove(file_name+'.mp3')

    db = firestore.client()
    doc_ref = db.collection(u'foods').document(barcode)
    doc_ref.set({
        u'name': name,
        u'description': description,
        u'price' : price,
        u'whatisthing': what,
        u'kcal': kcal+"kcal",
        u'sodium': sodium+"mg",
        u'carbohydrates' : carbohydrates+"g",
        u'sugars': sugars+"g",
        u'fats': fats+"g",
        u'trans_fats': trans_fat+"g",
        u'saturated_fat' : saturated_fat+"g",
        u'cholesterol': cholesterol+"mg",
        u'proteins' : proteins+"g",
        u'calcium' : calcium+"mg"
    })
    url = 'http://see-by-sound.netlify.app/food/'+ barcode
    return url