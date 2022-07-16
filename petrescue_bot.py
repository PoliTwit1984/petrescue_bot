import random
import shutil

import petpy
import petpy as pf
import requests
import tweepy
from PIL import Image, ImageDraw, ImageFont
from random_address import real_random_address

import config

client = tweepy.Client(config.bearer_token, config.consumer_key,
                       config.consumer_secret, config.access_token,
                       config.access_token_secret)


auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)

auth.set_access_token(config.access_token, config.access_token_secret)

api = tweepy.API(auth)


states_names = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
                "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}

# find right size for font based on image size


def find_font_size(text, font, image, target_width_ratio):
    image_name = Image.open(image)
    tested_font_size = 100
    tested_font = ImageFont.truetype(font, tested_font_size)
    observed_width, observed_height = get_text_size(
        text, image_name, tested_font)
    estimated_font_size = tested_font_size / \
        (observed_width / image_name.width) * target_width_ratio
    return round(estimated_font_size)


def get_text_size(text, image, font):
    im = Image.new('RGB', (image.width, image.height))
    draw = ImageDraw.Draw(im)
    return draw.textsize(text, font)


add = real_random_address()
zip_code = add.get("postalCode")
pf = petpy.Petfinder(key=config.petfinder_key, secret=config.petfinder_secret)
animals = pf.animals(animal_type='dog', status='adoptable', location=zip_code,
                     distance=500, breed="Dachshund", results_per_page=100, pages=1)
animal_ids = []
for i in animals['animals']:
    animal_ids.append(i['id'])

animal_id = random.choice(animal_ids)

animal = pf.animals(animal_id=animal_id)
name = animal.get('animals').get('name')
full_pic = animal.get('animals').get('photos')[0]['full']
url = animal.get('animals').get('url')
state_name = animal.get('animals').get('contact')
temp_state_name = (state_name.get('address').get('state'))
final_state_name = temp_state_name.strip()
temp_state_name = states_names[temp_state_name]

hashtag1 = f"#{temp_state_name}"
hashtag2 = f"#{final_state_name}"

r = requests.get(full_pic, stream=True)
filename = "a_pic.jpg"

# Check if the image was retrieved successfully
if r.status_code == 200:
    # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
    r.raw.decode_content = True

    # Open a local file with wb ( write binary ) permission.
    with open(filename, 'wb') as f:
        shutil.copyfileobj(r.raw, f)

else:
    print("Image Couldn't be retreived")

font = "AllerDisplay.ttf"

image = Image.open(filename)
text = f"{name} in {final_state_name} needs a home. Please Retweet."
width = image.width
height = image.height
font_name = "AllerDisplay.ttf"
fs = find_font_size(text, font_name, filename, .85)
print(fs)
font = ImageFont.truetype(r'AllerDisplay.ttf', int(fs))
draw = ImageDraw.Draw(image)
draw.text((width/2, height/2), text=text, font=font, fill="black", anchor="mm")
draw.text((int(width/2.02), int(height/2.02)), text=text,
          font=font, fill="white", anchor="mm")  # creates shadow and starts text in middle of image
image.save('a_pic.jpg')


media = api.media_upload(filename)
tweet = f"{name} needs a home near {hashtag1} {hashtag2} @petfinder\nLet's put politics aside for a few minutes and do a good deed.\nPlease Retweet.\nMore information - {url}"

# Post tweet with image

api.update_status(status=tweet, media_ids=[media.media_id])
