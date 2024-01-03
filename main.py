import vk_api
import datetime
from time import sleep
from random import choice
import telebot
import io
import requests
import os
import urllib.request
from dotenv import load_dotenv

bot = telebot.TeleBot(os.getenv('TOKENTGBOT'))

limit = datetime.timedelta(seconds=3)

import torch
import clip
from PIL import Image

#
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
#
# image = preprocess(Image.open("CLIP.png")).unsqueeze(0).to(device)
textNN = clip.tokenize(["fridge", "not firdge"]).to(device)


def pil_loader(path):
    # open path as file to avoid ResourceWarning (https://github.com/python-pillow/Pillow/issues/835)
    urllib.request.urlretrieve(path, "gfg.png")
    # # response = requests.get(url)
    # # image = Image.open(io.BytesIO(r.content))
    image = Image.open("gfg.png")

    # img = Image.open(f)

    return image.convert('RGB')


#
# with torch.no_grad():
#     image_features = model.encode_image(image)
#     text_features = model.encode_text(text)
#
#     logits_per_image, logits_per_text = model(image, text)
#     probs = logits_per_image.softmax(dim=-1).cpu().numpy()
#
# print("Label probs:", probs)  # prints: [[0.9927937  0.00421068 0.00299572]]


def getLatestPosts(groupsIds: list):
    comma = []
    for id in groupsIds:
        com = ['API.wall.get({', '})']
        com.insert(1, f'"owner_id": -{id}, "count": 2')
        comma.append(''.join(com))
    var=list()
    for l in comma:
        code = 'return {};'.format(l)
        s = api.execute(code=code.replace("'", ' '))
        var.append(s)
    # if len(groupsIds) != 1:
    #     # s = set()
    #     # for l in comma:
    #     #     s.add(l)
    #     # code = f"return {str(s)};"
    #     code = 'return {};'.format('; '.join(comma))
    # else:
    #     code = 'return {};'.format(comma)
    # print(code)
    latestPosts = []
    # var = api.execute(code=code.replace("'", ' '))
    # if len(groupsIds)==1:
    for group in var:
        try:
            group['items'][0]['is_pinned']
            postIndex = 1
        except KeyError:
            postIndex = 0

        post = group['items'][postIndex]
        latestPosts.append(
            (post['owner_id'], post['id'], post['date'], post['text'], post['comments'], post['attachments']))
    # else:
    #     for group in var['items']:
    #         try:
    #             group['is_pinned']
    #             postIndex = 1
    #         except KeyError:
    #             postIndex = 0
    #
    #         post = var['items'][postIndex]
    #         latestPosts.append(
    #             (post['owner_id'], post['id'], post['date'], post['text'], post['comments'], post['attachments']))
    return latestPosts


def main(groupsIds: list):
    while True:
        s = getLatestPosts(groupsIds)
        for owner_id, post_id, unix_date, text, comments, attachments in s:
            delta = (datetime.datetime.utcnow() - (datetime.datetime.utcfromtimestamp(unix_date)))
            if delta <= limit and comments['count'] < 1:
                t = text.lower()
                cond = [
                    'холодильник' in t or 'холодос' in t,
                    'куплю' not in t,
                    'не холодильник' not in t,
                ]
                if all(cond):
                    if len(attachments) > 0:
                        flag = False
                        for attach in attachments:
                            if 'photo' in attach:
                                url = attach['photo']['sizes'][5]['url']
                                img = pil_loader(url)
                                image = preprocess(img).unsqueeze(0).to(device)
                                with torch.no_grad():
                                    image_features = model.encode_image(image)
                                    text_features = model.encode_text(textNN)
                                    logits_per_image, logits_per_text = model(image, textNN)
                                    probs = logits_per_image.softmax(dim=-1).cpu().numpy()
                                if probs[0][0] > 0.9:
                                    flag = True
                                    break
                                else:
                                    continue
                        if flag:
                                # print("Label probs:", probs)  # prints: [[0.9927937  0.00421068 0.00299572]]

                            l = messages
                            api.wall.createComment(owner_id=owner_id,
                                                   post_id=post_id,
                                                   message=l)
                            tg_text = f"Бот ответил на пост https://vk.com/wall{owner_id}_{post_id}"
                            bot.send_message(os.getenv('TGCHATID'), tg_text)
                            print('[INFO] Бот ответил на пост https://vk.com/wall-{}_{}'.format(-owner_id, post_id, ))
        sleep(3)


if __name__ == "__main__":
    # print('\tПервонах бот. By WearyBread\nЕсли вы уже успешно заходили в аккаунт, можете ввести только логин')
    # groups = input('Введите ид групп через пробел(Пример: 195007647 195007647...): ').split()
    # groups = '36638733'.split()
    groups = os.getenv('GROUPS').split()
    # messages = input(
    #     'Введите сообщения через запятые (Пример: всем привет, спам, как дела?): ').split(
    #         ',')
    # login = input('Введите логин: ')
    # password = input('Введите пароль: ')
    messages = 'Холодос бронь'
    login = os.getenv('VKLOGIN')
    password = os.getenv('VKPASS')
    try:
        vk_session = vk_api.VkApi(login, password, app_id=2685278)
        vk_session.auth(token_only=True)
    except vk_api.exceptions.BadPassword as error:
        while True:
            print('Неправильный пароль, попробуйте ещё раз')
            login = input('Введите логин: ')
            password = input('Введите пароль: ')
            try:
                vk_session = vk_api.VkApi(login, password)
                vk_session.auth(token_only=True)
                break
            except vk_api.exceptions.BadPassword:
                pass
    api = vk_session.get_api()
    print(
        'Успешный запуск, чтобы остановить работу программы нажмите Ctrl + C или закройте консоль')
    main(groups)
# r = requests.get(url, stream=True)

# urllib.request.urlretrieve(url, "gfg.png")
# # response = requests.get(url)
# # image = Image.open(io.BytesIO(r.content))
# image = Image.open("gfg.png")
