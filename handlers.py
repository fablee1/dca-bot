import datetime

from aiogram.types import ParseMode
from aiogram.utils.emoji import emojize

import keyboards
from aiogram import types
from load_all import dp, _
from database import DBCommands
from qr import read_qr

db = DBCommands()

num_emojis = [':zero:', ':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:']
number_emojis = []
for x in num_emojis:
    number_emojis.append(emojize(x))


async def num_to_emoji(num):
    digits = list(str(num))
    num = ''
    for digit in digits:
        num += number_emojis[int(digit)]
    return num


async def generate_quest(call, page, q_count=3, is_call=True):
    quests = await db.last_quests()
    if not quests:
        msg = _('No quests to display.')
        if not is_call:
            await call.answer(msg)
        else:
            await call.message.answer(msg)
        return
    last_quests = quests[(page - 1) * q_count:page * q_count]
    num_q = len(quests)
    num = (page - 1) * q_count
    q_str = _('Quest from')
    lang = db.get_lang()
    for x in last_quests:
        num += 1
        is_next_page = False
        if num == page * q_count:
            if num_q > page * q_count:
                is_next_page = True
        date_str = '*[{q_str} {d}\.{m}\.{y}]({url})*'.format(d=x.date.day,
                                                             m=x.date.month,
                                                             y=x.date.year,
                                                             url=x.url,
                                                             q_str=q_str)
        solved_str = _('Quest not solved\! 🕐')
        if x.solved:
            solved_str = _('Quest is solved\! ✅')
        msg_q = _('{num} {date_str}'
                  '\nDifficulty: {diff}/100'
                  '\n{sol}').format(num=await num_to_emoji(num), date_str=date_str, diff=x.diff, sol=solved_str)
        if not is_call:
            await call.answer(msg_q, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True,
                              reply_markup=await keyboards.hint_kb(x.date, page, lang=lang, next_page=is_next_page))
        else:
            await call.message.answer(msg_q, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True,
                                      reply_markup=await keyboards.hint_kb(x.date, page, lang=lang,
                                                                           next_page=is_next_page))


async def generate_news(call, page, n_count=5, is_call=True):
    news = await db.last_news()
    if not news:
        msg = _('No news to display')
        if not is_call:
            await call.answer(msg)
        else:
            await call.message.answer(msg)
        return
    last_news = news[(page - 1) * n_count:page * n_count]
    num_n = len(news)
    num = (page - 1) * n_count
    n_str = _('News')
    msg = emojize(':newspaper: *{n_str}*\n'.format(n_str=n_str))
    if page > 1:
        msg = ''
    for x in last_news:
        num += 1
        url = x.url
        desc = x.desc
        if await db.get_lang() == 'ru':
            if x.url_ru is not None:
                url = x.url_ru
            if x.desc_ru is not None:
                desc = x.desc_ru
        date = '{d}\.{m}\.{y}'.format(d=x.date.day, m=x.date.month, y=x.date.year)
        msg += '\n\n{num} {desc} \({date}\)' \
               '\n{url}'.format(date=date, num=await num_to_emoji(num), desc=desc, url=url.replace('.', '\.').replace('-', '\-'))
    if num_n > page * n_count:
        if not is_call:
            await call.answer(msg, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=await keyboards.more_news(page),
                              disable_web_page_preview=True)
        else:
            await call.message.answer(msg, parse_mode=ParseMode.MARKDOWN_V2,
                                      reply_markup=await keyboards.more_news(page),
                                      disable_web_page_preview=True)
    else:
        if not is_call:
            await call.answer(msg, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
        else:
            await call.message.answer(msg, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)


@dp.message_handler(text=['🌐 Website', '🌐 Вебсайт'])
async def cmd_site(message: types.Message):
    msg = _('Stay tuned!'
            '\nComing soon...')
    await message.answer(msg)


@dp.callback_query_handler(keyboards.quest_cb.filter(action='hint'))
async def show_hint(call: types.CallbackQuery, callback_data: dict):
    data = callback_data['text']
    quest_date = datetime.datetime.strptime(callback_data['date'], '%Y-%m-%d %H:%M:%S')
    hints = await db.get_hints(quest_date)
    hint_n = data[0]
    lang = data[-2:]
    hint_text = 'error'
    if lang == 'en':
        if hint_n == '1':
            hint_text = hints.hint1
        elif hint_n == '2':
            hint_text = hints.hint2
        elif hint_n == '3':
            hint_text = hints.hint3
        elif hint_n == '4':
            hint_text = hints.hint4
    else:
        if hint_n == '1':
            hint_text = hints.hint1_ru
        elif hint_n == '2':
            hint_text = hints.hint2_ru
        elif hint_n == '3':
            hint_text = hints.hint3_ru
        elif hint_n == '4':
            hint_text = hints.hint4_ru
    await call.answer(text=hint_text, show_alert=True)


@dp.message_handler(text=['📱 Apps', '📱 Приложения'])
async def cmd_apps(message: types.Message):
    msg = _('Here you can find our apps!'
            '\n\nDownload them to make the most from our quests.')
    await message.answer(msg, reply_markup=await keyboards.app_kb())


@dp.message_handler(text=['⚙️ Language', '⚙️ Язык'])
async def lang(message: types.Message):
    msg = _('Choose your language:')
    await message.answer(msg, reply_markup=await keyboards.lang_kb())


@dp.callback_query_handler(text='RU')
async def lang_ru(call: types.CallbackQuery):
    await db.set_language('ru')
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=await keyboards.lang_conf_kb())


@dp.callback_query_handler(text='lang_confirm')
async def lang_confirm(call: types.CallbackQuery):
    msg = _('🇬🇧 Your language is now english! 🇬🇧')
    await call.answer()
    await call.message.edit_reply_markup()
    await call.message.answer(msg, reply_markup=await keyboards.main_kb())


@dp.callback_query_handler(text='EN')
async def lang_ru(call: types.CallbackQuery):
    await db.set_language('en')
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=await keyboards.lang_conf_kb())


@dp.message_handler(text=['🗞 News', '🗞 Новости'])
async def cmd_news(message: types.Message):
    await generate_news(message, 1, is_call=False)


@dp.message_handler(text=['🔍 Quests', '🔍 Квесты'])
async def cmd_quests(message: types.Message):
    await generate_quest(message, 1, is_call=False)


@dp.message_handler(commands=['start', 'help'])
async def cmd_start(message: types.Message):
    msg = _(':wave: Welcome to the DCA quest bot.\n\n'
            ':rocket: DCA - Digital Crypto Art is a project dedicated to make interesting quests '
            'by testing your skills and knowledge. In our quests you can win big and small depending '
            'on the difficulty of the quests. The prize can be in any cryptocurrency.\n\n'
            ':information_source: Here you can find our latest news, as well as our latest quests.\n\n')
    await db.add_new_user()
    await message.answer(emojize(msg), reply_markup=await keyboards.main_kb())


@dp.callback_query_handler(keyboards.quest_cb.filter(action='more_quests'))
async def more_quests(call: types.CallbackQuery, callback_data: dict):
    page = int(callback_data['text'])
    await call.answer()
    await call.message.edit_reply_markup()
    await generate_quest(call, page, is_call=True)


@dp.callback_query_handler(text='app_not_exists')
async def app_not_exists(call: types.CallbackQuery):
    await call.answer(_('App for this platform is coming soon.'
                        '\nPlease stay updated!'))


@dp.message_handler(text=['💽 Scan QR', '💽 Отсканировать QR'])
async def scan_qr(message: types.Message):
    msg = _('Send me your qr code.')
    await message.answer(msg)


@dp.message_handler(content_types=['photo', 'document'])
async def handle_qr(message: types.Message):
    qr_data = await read_qr(message)
    msg = _('No qr found, try again!')
    if qr_data is not None:
        msg = qr_data
    await message.answer(msg)


@dp.callback_query_handler(keyboards.more_news_cb.filter())
async def more_news(call: types.CallbackQuery, callback_data: dict):
    page = int(callback_data['page'])
    await call.answer()
    await call.message.edit_reply_markup()
    await generate_news(call, page)
