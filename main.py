from my_token import TOKEN
from my_token import TOKEN_VK
import requests
import yadisk
from progress.bar import IncrementalBar
import os

URL = 'https://api.vk.com/method/photos.get'

# user_id = input ('Введите ID пользователя VK: ')
# TOKEN = input ('Введите токен ЯндексДиска: ')

params = {
'access_token' : TOKEN_VK,
'user_id' : '1687630',
 # 'user_id' : user_id,   
'album_id' : 'profile',
'extended' : '1',
'v':'5.131'
    }
# for i in tqdm(range(100)):
res = requests.get(URL, params=params).json()
if "This profile is private" in str(res):
    quit("Это - закрытый профиль")
    
lenth = res['response']['count']

# Преобразуем likes и сортируем по ним 

def sort (dictionary, param) :
    photos_ = sorted(dictionary, key=lambda d: d[param], reverse=True)
    return photos_
    
for i_count in range (lenth):
    res['response']['items'][i_count]['likes'] =  int(res['response']['items'][i_count]['likes']['count'])

# photos_sorted = sorted(res['response']['items'], key=lambda d: d['likes'], reverse=True)
photos_sorted = sort (res['response']['items'], 'likes') 

ynd = yadisk.YaDisk(token=TOKEN)
if ynd.check_token():
    if not ynd.is_dir("/Your-Photos"):
        ynd.mkdir("/Your-Photos")


# y.upload(file_name, file_disk)

if lenth > 5 :
    lenth = 5
bar = IncrementalBar('Countdown', max = lenth)
likes_previous = 0
list_photos = []

for i_phot in range (lenth):
    bar.next()
    like = int (photos_sorted[i_phot]['likes'])
    if like != likes_previous :
        file_name = str(like) + '.jpg'
    else :
        file_name = str(like) + str (photos_sorted[i_phot]['date']) + '.jpg'

    likes_previous = like
    by_width = sort(photos_sorted[i_phot]['sizes'], 'width')
    i_count = 0

    if by_width[0]['width'] == 0 :
        for i_width in by_width :
            i_count += 1
        photo_url = by_width[i_count-1]['url']
        photo_size = '0x0'
    else :
        photo_url = by_width[0]['url']
        photo_size = str(by_width[0]['width']) + 'x' + str(by_width[0]['height'])
    
    file_path = '/Your-Photos/' + file_name
    
    photo_data = dict(file_name=file_name, size=photo_size)
    list_photos.append (photo_data)
    photo_get = requests.get(photo_url)

    with open(file_name, 'wb') as f:
        f.write(photo_get.content)
    if ynd.is_file(file_path):
        ynd.remove(file_path, permanently=False)
    ynd.upload(file_name, file_path)
    os.remove(file_name)

    # bar.finish()

with open('photos_list.txt', 'w') as photo_list:
    photo_list.write(str (list_photos))
print('\nВаши фотографии в папке: "Your-Photos"')

