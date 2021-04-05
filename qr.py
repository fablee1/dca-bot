from aiogram import types

from pyzbar.pyzbar import decode
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

qr_img = 0


async def file_name():
    global qr_img
    file_name = 'file_' + str(qr_img) + '.jpg'
    if qr_img == 3:
        qr_img = 0
    qr_img += 1
    return file_name


async def read_qr(message: types.Message):
    path = './photos/' + await file_name()
    try:
        await message.photo[-1].download(path)
    except:
        await message.document.download(path)
    try:
        qr_data = decode(Image.open(path))
    except:
        return None
    if qr_data:
        data = qr_data[0][0].decode()
        return data
    else:
        return None
