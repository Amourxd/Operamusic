import os
import re
import textwrap

import aiofiles
import aiohttp
import numpy as np
import random

from PIL import Image, ImageChops, ImageOps, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch

from SankiMusic import bot
from SankiMusic.utilities.config import OWNER_ID, YOUTUBE_IMG_URL



def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


def add_corners(im):
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, im.split()[-1])
    im.putalpha(mask)


async def gen_thumb(videoid, user_id):
    try:
        os.remove(f"cache/thumb{videoid}.png")
        os.remove(f"cache/{videoid}_{user_id}.png")
    except:
        pass
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()


        bot_prof = await bot.get_profile_photos(bot.id)
        bot_pic = await bot.download_media(bot_prof[0]['file_id'], file_name=f'bot_{bot.id}.jpg')
        bot_img = Image.open(bot_pic)
        bot_img_new = Image.new('L', [640, 640], 0)
        bot_img_draw = ImageDraw.Draw(bot_img_new)
        bot_img_draw.pieslice([(0, 0), (640,640)], 0, 360, fill = 255, outline = "white")
        bot_img_array = np.array(bot_img)
        bot_img_new_array = np.array(bot_img_new)
        bot_de_img = np.dstack((bot_img_array, bot_img_new_array))
        bot_pic_final = Image.fromarray(bot_de_img)
        bot_img_final = bot_pic_final.resize((165, 165))

        try:
            user_prof = await bot.get_profile_photos(user_id)
            user_pic = await bot.download_media(user_prof[0]['file_id'], file_name=f'user_{user_id}.jpg')
        except:
            user_prof = await bot.get_profile_photos(bot.id)
            user_pic = await bot.download_media(user_prof[0]['file_id'], file_name=f'user_{bot.id}.jpg')
        user_img = Image.open(user_pic)
        user_img_new = Image.new('L', [640, 640], 0)
        user_img_draw = ImageDraw.Draw(user_img_new)
        user_img_draw.pieslice([(0, 0), (640,640)], 0, 360, fill = 255, outline = "white")
        user_img_array = np.array(user_img)
        user_img_new_array = np.array(user_img_new)
        user_de_img = np.dstack((user_img_array, user_img_new_array))
        user_pic_final = Image.fromarray(user_de_img)
        user_img_final = user_pic_final.resize((165, 165))

        

        youtube = Image.open(f"cache/thumb{videoid}.png")
        cover = Image.open(f"SankiMusic/resource/logo.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        enhancer = ImageEnhance.Brightness(image2.filter(filter=ImageFilter.BoxBlur(30)))
        img = enhancer.enhance(1.2)
        img_new = ImageOps.expand(img, border=13, fill=f"white")
        background = changeImageSize(1280, 720, img_new)
        logo = changeImageSize(800, 450, youtube)
        logo_bright = ImageEnhance.Brightness(logo)
        logo = logo_bright.enhance(1.2)
        logo_contra = ImageEnhance.Contrast(logo)
        logo = logo_contra.enhance(1.2)
        logo.thumbnail((800, 450), Image.ANTIALIAS)
        logo = ImageOps.expand(logo, border=7, fill="white")
        background.paste(logo, (234, 132))
        background.paste(bot_img_final, (40, 40), mask=bot_img_final)
        background.paste(user_img_final, (1075, 40), mask=user_img_final)
        background.paste(user_img_final, (40, 515), mask=user_img_final)
        background.paste(bot_img_final, (1075, 515), mask=bot_img_final)
        background.paste(cover, (0, 0), mask=cover)
        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("SankiMusic/resource/font.ttf", 80)
        font2 = ImageFont.truetype("SankiMusic/resource/font2.ttf", 50)
        para = textwrap.wrap(title, width=20)
        try:
            draw.text(
                (310, 25),
                f"NOW PLAYING",
                fill="white",
                stroke_width=3,
                stroke_fill="black",
                font=font,
            )
            if para[0]:
                text_w, text_h = draw.textsize(f"{para[0]}", font=font2)
                draw.text(
                    ((1280 - text_w) / 2, 600),
                    f"{para[0]}",
                    fill="white",
                    stroke_width=3,
                    stroke_fill="black",
                    font=font2,
                )
            if para[1]:
                text_w, text_h = draw.textsize(f"{para[1]}", font=font2)
                draw.text(
                    ((1280 - text_w) / 2, 650),
                    f"{para[1]}",
                    fill="white",
                    stroke_width=3,
                    stroke_fill="black",
                    font=font2,
                )
        except:
            pass
        try:
            os.remove(f"cache/thumb{videoid}_{user_id}.png")
        except:
            pass
        background.save(f"cache/{videoid}_{user_id}.png")
        return f"cache/{videoid}_{user_id}.png"
    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL



async def que_thumb(videoid, user_id):
    try:
        os.remove(f"cache/que_thumb{videoid}.png")
        os.remove(f"cache/que_{videoid}_{user_id}.png")
    except:
        pass
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/que_thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()


        bot_prof = await bot.get_profile_photos(bot.id)
        bot_pic = await bot.download_media(bot_prof[0]['file_id'], file_name=f'bot_{bot.id}.jpg')
        bot_img = Image.open(bot_pic)
        bot_img_new = Image.new('L', [640, 640], 0)
        bot_img_draw = ImageDraw.Draw(bot_img_new)
        bot_img_draw.pieslice([(0, 0), (640,640)], 0, 360, fill = 255, outline = "white")
        bot_img_array = np.array(bot_img)
        bot_img_new_array = np.array(bot_img_new)
        bot_de_img = np.dstack((bot_img_array, bot_img_new_array))
        bot_pic_final = Image.fromarray(bot_de_img)
        bot_img_final = bot_pic_final.resize((165, 165))

        try:
            user_prof = await bot.get_profile_photos(user_id)
            user_pic = await bot.download_media(user_prof[0]['file_id'], file_name=f'user_{user_id}.jpg')
        except:
            user_prof = await bot.get_profile_photos(bot.id)
            user_pic = await bot.download_media(user_prof[0]['file_id'], file_name=f'user_{bot.id}.jpg')
        user_img = Image.open(user_pic)
        user_img_new = Image.new('L', [640, 640], 0)
        user_img_draw = ImageDraw.Draw(user_img_new)
        user_img_draw.pieslice([(0, 0), (640,640)], 0, 360, fill = 255, outline = "white")
        user_img_array = np.array(user_img)
        user_img_new_array = np.array(user_img_new)
        user_de_img = np.dstack((user_img_array, user_img_new_array))
        user_pic_final = Image.fromarray(user_de_img)
        user_img_final = user_pic_final.resize((165, 165))

        

        youtube = Image.open(f"cache/que_thumb{videoid}.png")
        cover = Image.open(f"SankiMusic/resource/logo.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        enhancer = ImageEnhance.Brightness(image2.filter(filter=ImageFilter.BoxBlur(30)))
        img = enhancer.enhance(1.2)
        img_new = ImageOps.expand(img, border=13, fill=f"white")
        background = changeImageSize(1280, 720, img_new)
        logo = changeImageSize(800, 450, youtube)
        logo_bright = ImageEnhance.Brightness(logo)
        logo = logo_bright.enhance(1.2)
        logo_contra = ImageEnhance.Contrast(logo)
        logo = logo_contra.enhance(1.2)
        logo.thumbnail((800, 450), Image.ANTIALIAS)
        logo = ImageOps.expand(logo, border=7, fill="white")
        background.paste(logo, (234, 132))
        background.paste(bot_img_final, (40, 40), mask=bot_img_final)
        background.paste(user_img_final, (1075, 40), mask=user_img_final)
        background.paste(user_img_final, (40, 515), mask=user_img_final)
        background.paste(bot_img_final, (1075, 515), mask=bot_img_final)
        background.paste(cover, (0, 0), mask=cover)
        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("SankiMusic/resource/font.ttf", 80)
        font2 = ImageFont.truetype("SankiMusic/resource/font2.ttf", 50)
        para = textwrap.wrap(title, width=20)
        try:
            draw.text(
                (300, 25),
                f"SONG QUEUED",
                fill="white",
                stroke_width=3,
                stroke_fill="black",
                font=font,
            )
            if para[0]:
                text_w, text_h = draw.textsize(f"{para[0]}", font=font2)
                draw.text(
                    ((1280 - text_w) / 2, 600),
                    f"{para[0]}",
                    fill="white",
                    stroke_width=3,
                    stroke_fill="black",
                    font=font2,
                )
            if para[1]:
                text_w, text_h = draw.textsize(f"{para[1]}", font=font2)
                draw.text(
                    ((1280 - text_w) / 2, 650),
                    f"{para[1]}",
                    fill="white",
                    stroke_width=3,
                    stroke_fill="black",
                    font=font2,
                )
        except:
            pass
        try:
            os.remove(f"cache/que_thumb{videoid}_{user_id}.png")
        except:
            pass
        background.save(f"cache/que_{videoid}_{user_id}.png")
        return f"cache/que_{videoid}_{user_id}.png"
    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
