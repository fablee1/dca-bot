from aiogram.types import ContentType, ParseMode
from aiogram.utils.emoji import emojize

import keyboards
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Filter
from aiogram import types
from load_all import dp, _
from database import DBCommands, Quests, Hints, News
from states import AddQuest, AddHints, EditQuest, AddApp, AddNews, EditNews
import datetime

db = DBCommands()


class IsAdmin(Filter):
    key = 'is_admin'

    async def check(self, message: types.Message):
        return await db.is_admin()


async def generate_admin_quests(call, page, q_count=1, gen_new=True, is_call=True, quest_d=None):
    quests = await db.last_quests()
    if not quests:
        msg = _('No quests to display.')
        if not is_call:
            await call.answer(msg)
        else:
            await call.message.answer(msg)
        return
    page = int(page)
    if quest_d is not None:
        for n, q in enumerate(quests):
            if quest_d == q.date:
                page = int(n + 1)
    last_quests = quests[(page - 1) * q_count:page * q_count]
    num_q = len(quests)
    num = (page - 1) * q_count
    for x in last_quests:
        num += 1
        is_next_page = False
        is_prev_page = False
        if num_q > page * q_count:
            is_next_page = True
        if page * q_count > 1:
            is_prev_page = True
        q_from_str = _('Quest from')
        date_str = '[{q_str} {d}.{m}.{y}]({url})'.format(d=x.date.day,
                                                         m=x.date.month,
                                                         y=x.date.year,
                                                         url=x.url,
                                                         q_str=q_from_str)
        solved_str = _('Quest not solved! 🕐')
        if x.solved:
            solved_str = _('Quest is solved! ✅')
        dif_str = _('Difficulty')
        msg_q = '{num} {date_str}' \
                '\n{dif_s}: {diff}/100' \
                '\n{sol}'.format(dif_s=dif_str, num=num, date_str=date_str, diff=x.diff, sol=solved_str)
        if gen_new:
            if not is_call:
                await call.answer(msg_q, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
                                  reply_markup=await keyboards.edit_quest_kb(x, page, is_next_page, is_prev_page))
            else:
                await call.message.answer(msg_q, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
                                          reply_markup=await keyboards.edit_quest_kb(x, page, is_next_page,
                                                                                     is_prev_page))
        else:
            if not is_call:
                await call.edit_text(msg_q, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                await call.edit_reply_markup(
                    reply_markup=await keyboards.edit_quest_kb(x, page, is_next_page, is_prev_page))
            else:
                await call.message.edit_text(msg_q, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                await call.message.edit_reply_markup(
                    reply_markup=await keyboards.edit_quest_kb(x, page, is_next_page, is_prev_page))


async def generate_admin_news(call, page, q_count=1, gen_new=True, is_call=True, news_d=None):
    news = await db.last_news()
    if not news:
        msg = _('No news to display.')
        if not is_call:
            await call.answer(msg)
        else:
            await call.message.answer(msg)
        return
    page = int(page)
    if news_d is not None:
        for n, q in enumerate(news):
            if news_d == q.date:
                page = int(n + 1)
    last_quests = news[(page - 1) * q_count:page * q_count]
    num_q = len(news)
    num = (page - 1) * q_count
    for x in last_quests:
        num += 1
        is_next_page = False
        is_prev_page = False
        if num_q > page * q_count:
            is_next_page = True
        if page * q_count > 1:
            is_prev_page = True
        news_from_str = _('News from')
        date_str = '{n_str} {d}.{m}.{y}'.format(d=x.date.day,
                                                m=x.date.month,
                                                y=x.date.year,
                                                n_str=news_from_str)
        t_d_str_en = _('Title/desc english')
        t_d_str_ru = _('Title/desc russian')
        url_str_en = _('English url')
        url_str_ru = _('Russian url')
        msg_q = '{num}. <b>{date_str}</b>' \
                '\n<b>{t_d_str_en}</b>: {desc_en}' \
                '\n<b>{t_d_str_ru}</b>: {desc_ru}' \
                '\n<b>{url_str_en}</b>: {url_en}' \
                '\n<b>{url_str_ru}</b>: {url_ru}'.format(t_d_str_en=t_d_str_en, t_d_str_ru=t_d_str_ru, desc_ru=x.desc_ru,
                                                  num=num, date_str=date_str, desc_en=x.desc, url_str_en=url_str_en,
                                                  url_str_ru=url_str_ru, url_en=x.url, url_ru=x.url_ru)
        if gen_new:
            if not is_call:
                await call.answer(msg_q, parse_mode=ParseMode.HTML, disable_web_page_preview=True,
                                  reply_markup=await keyboards.edit_news_kb(x, page, is_next_page, is_prev_page))
            else:
                await call.message.answer(msg_q, parse_mode=ParseMode.HTML, disable_web_page_preview=True,
                                          reply_markup=await keyboards.edit_news_kb(x, page, is_next_page,
                                                                                    is_prev_page))
        else:
            if not is_call:
                await call.edit_text(msg_q, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
                await call.edit_reply_markup(
                    reply_markup=await keyboards.edit_news_kb(x, page, is_next_page, is_prev_page))
            else:
                await call.message.edit_text(msg_q, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
                await call.message.edit_reply_markup(
                    reply_markup=await keyboards.edit_news_kb(x, page, is_next_page, is_prev_page))


@dp.callback_query_handler(IsAdmin(), text='admin_quests')
async def quest_menu(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=await keyboards.admin_quest_menu())


@dp.message_handler(IsAdmin(), commands=['cancel'], state=AddQuest)
async def cancel_quest(message: types.Message, state: FSMContext):
    await message.answer('Admin menu.', reply_markup=await keyboards.admin_quest_menu())
    await state.reset_state()


@dp.message_handler(IsAdmin(), commands=['cancel'], state=AddNews)
async def cancel_news(message: types.Message, state: FSMContext):
    await message.answer('Admin menu.', reply_markup=await keyboards.admin_news_menu())
    await state.reset_state()


@dp.message_handler(IsAdmin(), commands=['cancel'], state=AddApp)
async def cancel_app(message: types.Message, state: FSMContext):
    await message.answer('Admin menu.', reply_markup=await keyboards.admin_news_menu())
    await state.reset_state()


@dp.message_handler(IsAdmin(), commands=['admin'])
async def admin_panel(message: types.Message):
    msg = _('This is your admin panel.\n\n'
            'Using the buttons below, you can '
            'manage quests, news, apps '
            'and look for stats.')
    await message.answer(msg, reply_markup=await keyboards.admin_kb())


@dp.message_handler(IsAdmin(), commands=['set_admin'])
async def set_admin(message: types.Message):
    msg = _('Incorrect username format. Please use /set_admin @username')
    args = message.get_args()
    if args != '' and len(args.split(' ')) == 1 and args[0] == '@':
        username = args.strip('@')
        user = await db.get_user_username(username)
        if user is not None:
            await user.update(is_admin=True).apply()
            msg = _('This person is admin now!')
        else:
            msg = _('This user is not in the database, please ask him to start the bot first!')
    await message.reply(msg)


@dp.message_handler(IsAdmin(), commands=['del_admin'])
async def del_admin(message: types.Message):
    msg = _('Incorrect username format. Please use /del_admin @username')
    args = message.get_args()
    if args != '' and len(args.split(' ')) == 1 and args[0] == '@':
        username = args.strip('@')
        user = await db.get_user_username(username)
        if user is not None:
            await user.update(is_admin=False).apply()
            msg = _('This person is no more an admin!')
        else:
            msg = _('This user is not in the database, please ask him to start the bot first!')
    await message.reply(msg)


@dp.callback_query_handler(IsAdmin(), text='add_quest')
async def add_quest(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer(_("Enter quest date in format DD-MM-YYYY "
                                "or type '-' to assign today's date, or press /cancel"))
    await AddQuest.EnterDate.set()


@dp.message_handler(IsAdmin(), state=AddQuest.EnterDate)
async def enter_quest_date(message: types.Message, state: FSMContext):
    if message.text == '-':
        date = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    else:
        try:
            date = datetime.datetime.strptime(message.text, '%d-%m-%Y')
        except:
            await message.answer(_('Incorrect date format. Try again.'))
            return
    quest = Quests()
    quest.date = date
    await message.answer(_('Quest date is: {date}'
                           '\nNow enter quest url or press /cancel').format(date=date))
    await AddQuest.EnterUrl.set()
    await state.update_data(quest=quest)


@dp.message_handler(IsAdmin(), state=AddQuest.EnterUrl)
async def enter_quest_date(message: types.Message, state: FSMContext):
    url = message.text
    data = await state.get_data()
    quest: Quests = data.get('quest')
    quest.url = url
    msg = _('Quest url is: [{url}]({url})'
            '\nNow enter quest difficulty from 0 to 100 or press /cancel').format(url=url)
    await message.answer(msg, disable_web_page_preview=True, parse_mode=types.ParseMode.MARKDOWN)
    await AddQuest.EnterDiff.set()
    await state.update_data(quest=quest)


@dp.message_handler(IsAdmin(), state=AddQuest.EnterDiff)
async def enter_quest_date(message: types.Message, state: FSMContext):
    diff = message.text
    if diff.isnumeric() and 0 <= int(diff) <= 100:
        data = await state.get_data()
        quest: Quests = data.get('quest')
        quest.diff = int(diff)
        await message.answer(_('Quest difficulty is: {diff}'
                               '\n\nNow check quest:'
                               '\nDate: {date}'
                               '\nUrl: [{url}]({url})'
                               '\nDifficulty: {diff}'
                               '\n\nIf everything is correct press confirm or press /cancel').format(
            diff=diff, date=quest.date, url=quest.url),
            parse_mode=types.ParseMode.MARKDOWN, reply_markup=await keyboards.confirm_kb())
        await AddQuest.Confirm.set()
        await state.update_data(quest=quest)
    else:
        await message.answer(_('Error, this must be a number between 0 and 100. Try again.'))


@dp.callback_query_handler(IsAdmin(), text='confirm', state=AddQuest.Confirm)
async def confirm_quest(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    quest: Quests = data.get('quest')
    hint = Hints()
    hint.date = quest.date
    await hint.create()
    await quest.create()
    await call.message.answer(_('Admin menu.'), reply_markup=await keyboards.admin_quest_menu())
    await state.reset_state()


@dp.callback_query_handler(IsAdmin(), text='start_again', state=AddQuest.Confirm)
async def start_again(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer(_("Enter quest date in format DD-MM-YYYY "
                                "or type '-' to assign today's date, or press /cancel"))
    await AddQuest.EnterDate.set()


@dp.callback_query_handler(IsAdmin(), keyboards.edit_quest_cb.filter(action='edit_date'))
async def date(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    quest_date = datetime.datetime.strptime(callback_data['quest'], '%Y-%m-%d %H:%M:%S')
    page = callback_data['data']
    msg = _('Enter new date in format DD-MM-YYYY:')
    await call.answer()
    mess = await call.message.answer(msg)
    await call.message.delete()
    await EditQuest.ConfirmDate.set()
    await state.update_data(q_date=quest_date, page=page, mess=mess)


@dp.message_handler(IsAdmin(), state=EditQuest.ConfirmDate)
async def confirm_date(message: types.Message, state: FSMContext):
    date_t = message.text
    if date_t == '-':
        date_n = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    elif len(message.text.split('-')) == 3:
        date_n = datetime.datetime.strptime(date_t, '%d-%m-%Y')
    else:
        await message.answer(_('Incorrect date format. Try again.'))
        return
    data = await state.get_data()
    date = data.get('q_date')
    page = data.get('page')
    mess = data.get('mess')
    quest = await db.get_quest(date)
    hint = await db.get_hints(date)
    await quest.update(date=date_n).apply()
    await hint.update(date=date_n).apply()
    await mess.delete()
    await generate_admin_quests(message, page, is_call=False, quest_d=date_n)
    await state.reset_state()


@dp.callback_query_handler(IsAdmin(), keyboards.edit_quest_cb.filter(action='edit_url'))
async def url(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    quest_date = datetime.datetime.strptime(callback_data['quest'], '%Y-%m-%d %H:%M:%S')
    page = callback_data['data']
    msg = _('Enter new url:')
    await call.answer()
    mess = await call.message.answer(msg)
    await call.message.delete()
    await EditQuest.ConfirmUrl.set()
    await state.update_data(q_date=quest_date, page=page, mess=mess)


@dp.message_handler(IsAdmin(), state=EditQuest.ConfirmUrl)
async def confirm_url(message: types.Message, state: FSMContext):
    url = message.text
    data = await state.get_data()
    date = data.get('q_date')
    page = data.get('page')
    mess = data.get('mess')
    quest = await db.get_quest(date)
    await quest.update(url=url).apply()
    await mess.delete()
    await generate_admin_quests(message, page, is_call=False)
    await state.reset_state()


@dp.callback_query_handler(IsAdmin(), keyboards.edit_quest_cb.filter(action='edit_diff'))
async def diff(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    quest_date = datetime.datetime.strptime(callback_data['quest'], '%Y-%m-%d %H:%M:%S')
    page = callback_data['data']
    msg = _('Enter new difficulty from 0 to 100:')
    await call.answer()
    mess = await call.message.answer(msg)
    await call.message.delete()
    await EditQuest.ConfirmDiff.set()
    await state.update_data(q_date=quest_date, page=page, mess=mess)


@dp.message_handler(IsAdmin(), state=EditQuest.ConfirmDiff)
async def confirm_diff(message: types.Message, state: FSMContext):
    diff = message.text
    if diff.isnumeric() and 0 <= int(diff) <= 100:
        data = await state.get_data()
        date = data.get('q_date')
        page = data.get('page')
        mess = data.get('mess')
        quest = await db.get_quest(date)
        await quest.update(diff=int(diff)).apply()
        await mess.delete()
        await generate_admin_quests(message, page, is_call=False)
        await state.reset_state()
    else:
        await message.answer(_('Should be number between 0 and 100'))


@dp.callback_query_handler(IsAdmin(), keyboards.edit_quest_cb.filter(action='edit_hints'), state=AddHints.ChooseLang)
async def hints(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    quest_date = datetime.datetime.strptime(callback_data['quest'], '%Y-%m-%d %H:%M:%S')
    page = callback_data['data']
    await call.answer()
    await state.reset_state()
    await call.message.edit_text(_('Choose hint:'))
    await call.message.edit_reply_markup(reply_markup=await keyboards.admin_hints_kb(quest_date, page))


@dp.callback_query_handler(IsAdmin(), keyboards.edit_quest_cb.filter(action='edit_hints'))
async def hints(call: types.CallbackQuery, callback_data: dict):
    quest_date = datetime.datetime.strptime(callback_data['quest'], '%Y-%m-%d %H:%M:%S')
    page = callback_data['data']
    await call.answer()
    await call.message.edit_text(_('Choose hint:'))
    await call.message.edit_reply_markup(reply_markup=await keyboards.admin_hints_kb(quest_date, page))


@dp.callback_query_handler(IsAdmin(), keyboards.admin_hint_cb.filter())
async def choose_hint_lang(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    hint_n = callback_data['hint_n']
    page = callback_data['page']
    q_date = callback_data['q_date']
    await call.answer()
    await call.message.edit_text(_('Choose hint language:'))
    await call.message.edit_reply_markup(reply_markup=await keyboards.hint_lang())
    await AddHints.ChooseLang.set()
    await state.update_data(hint_n=hint_n, page=page, q_date=q_date)


@dp.callback_query_handler(IsAdmin(), keyboards.del_hint_cb.filter(), state=AddHints.ChooseLang)
async def edit_quest_solve(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    quest_date = datetime.datetime.strptime(callback_data['q_date'], '%Y-%m-%d %H:%M:%S')
    page = int(callback_data['page'])
    hint_n = int(callback_data['hint_n'][-1])
    lang = callback_data['lang']
    hint = await db.get_hints(quest_date)
    hint_text = None
    if lang == 'en':
        if hint_n == 1:
            await hint.update(hint1=hint_text).apply()
        elif hint_n == 2:
            await hint.update(hint2=hint_text).apply()
        elif hint_n == 3:
            await hint.update(hint3=hint_text).apply()
        elif hint_n == 4:
            await hint.update(hint4=hint_text).apply()
    else:
        if hint_n == 1:
            await hint.update(hint1_ru=hint_text).apply()
        elif hint_n == 2:
            await hint.update(hint2_ru=hint_text).apply()
        elif hint_n == 3:
            await hint.update(hint3_ru=hint_text).apply()
        elif hint_n == 4:
            await hint.update(hint4_ru=hint_text).apply()
    msg = _('Hint {n} was deleted!'
            '\nChoose another hint to edit or press finish button.').format(n=hint_n)
    await call.answer()
    await state.reset_state()
    await call.message.edit_text(msg)
    await call.message.edit_reply_markup(reply_markup=await keyboards.admin_hints_kb(quest_date, page))


@dp.callback_query_handler(IsAdmin(), state=AddHints.ChooseLang)
async def add_edit_hints(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    hint_n = data.get('hint_n')
    page = data.get('page')
    q_date = datetime.datetime.strptime(data.get('q_date'), '%Y-%m-%d %H:%M:%S')
    callback_d = call.data
    lang = callback_d[:2]
    hint = await db.get_hints(q_date)
    hint_text = '-'
    if lang == 'en':
        if hint_n[1] == '0':
            hint_text = '-'
        elif hint_n[0] == '1':
            hint_text = hint.hint1
        elif hint_n[0] == '2':
            hint_text = hint.hint2
        elif hint_n[0] == '3':
            hint_text = hint.hint3
        elif hint_n[0] == '4':
            hint_text = hint.hint4
    else:
        if hint_n[2] == '0':
            hint_text = '-'
        elif hint_n[0] == '1':
            hint_text = hint.hint1_ru
        elif hint_n[0] == '2':
            hint_text = hint.hint2_ru
        elif hint_n[0] == '3':
            hint_text = hint.hint3_ru
        elif hint_n[0] == '4':
            hint_text = hint.hint4_ru
    if callback_d[-1] == 'E':
        hint_text = '-'
    msg = _('Please enter hint:')
    if hint_text != '-':
        msg = _('This hint is:\n{hint}').format(hint=hint_text)
        await call.answer()
        await call.message.delete()
        await call.message.answer(msg, reply_markup=await keyboards.edit_hint(hint_n[0], q_date, page, lang))
        return
    else:
        hint = await db.get_hints(q_date)
        mess = await call.message.answer(msg)
    await call.message.delete()
    await call.answer()
    await AddHints.Confirm.set()
    await state.update_data(hint=hint, hint_n=hint_n[0], mess=mess, page=page, lang=lang)


@dp.message_handler(IsAdmin(), state=AddHints.Confirm)
async def confirm_hints(message: types.Message, state: FSMContext):
    hint_text = message.text
    length = len(hint_text)
    data = await state.get_data()
    mess = data.get('mess')
    if length > 200:
        warning = _('Length of hint is {l} chars.'
                    '\nLength should be less than or equal to 200 chars.'
                    '\nTry again.').format(l=length)
        try:
            await mess.delete()
        except:
            pass
        await message.answer(warning)
        return
    lang = data.get('lang')
    page = data.get('page')
    hint_n = data.get('hint_n')
    hint = data.get('hint')
    if lang == 'en':
        if hint_n == '1':
            await hint.update(hint1=hint_text).apply()
        elif hint_n == '2':
            await hint.update(hint2=hint_text).apply()
        elif hint_n == '3':
            await hint.update(hint3=hint_text).apply()
        elif hint_n == '4':
            await hint.update(hint4=hint_text).apply()
    else:
        if hint_n == '1':
            await hint.update(hint1_ru=hint_text).apply()
        elif hint_n == '2':
            await hint.update(hint2_ru=hint_text).apply()
        elif hint_n == '3':
            await hint.update(hint3_ru=hint_text).apply()
        elif hint_n == '4':
            await hint.update(hint4_ru=hint_text).apply()
    msg = _('Hint {n} {lang} was created!'
            '\nChoose another hint to edit or press finish button.').format(n=hint_n, lang=lang)
    try:
        await mess.delete()
    except:
        pass
    await message.answer(msg, reply_markup=await keyboards.admin_hints_kb(hint.date, page))
    await state.reset_state()


@dp.callback_query_handler(IsAdmin(), keyboards.finish_hints_cb.filter())
async def finish_hints(call: types.CallbackQuery, callback_data: dict):
    page = callback_data['page']
    await call.answer()
    await generate_admin_quests(call, page, gen_new=False)


@dp.callback_query_handler(IsAdmin(), text='back_to_menu')
async def back_to_menu(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=await keyboards.admin_kb())


@dp.callback_query_handler(IsAdmin(), text='add_edit_quests')
async def quest_menu(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=await keyboards.admin_quest_menu())


@dp.callback_query_handler(IsAdmin(), text='back_to_main_menu')
async def main_menu(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()


@dp.callback_query_handler(IsAdmin(), text='edit_quest')
async def edit_quest(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    await generate_admin_quests(call, 1)


@dp.callback_query_handler(IsAdmin(), keyboards.edit_quest_cb.filter(action=['edit_solve']))
async def edit_quest_solve(call: types.CallbackQuery, callback_data: dict):
    quest_date = datetime.datetime.strptime(callback_data['quest'], '%Y-%m-%d %H:%M:%S')
    page = int(callback_data['data'])
    quest = await db.get_quest(quest_date)
    if quest.solved:
        await quest.update(solved=False).apply()
    else:
        await quest.update(solved=True).apply()
    await call.answer()
    await generate_admin_quests(call, page, gen_new=False)


@dp.callback_query_handler(IsAdmin(), keyboards.edit_quest_cb.filter(action=['next_page', 'prev_page']))
async def edit_quest_page(call: types.CallbackQuery, callback_data: dict):
    page = int(callback_data['data'])
    await call.answer()
    await generate_admin_quests(call, page, gen_new=False)


@dp.callback_query_handler(IsAdmin(), text='exit_edit_quest')
async def edit_quest_page(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text(_('Admin panel.'))
    await call.message.edit_reply_markup(reply_markup=await keyboards.admin_quest_menu())


@dp.callback_query_handler(IsAdmin(), keyboards.edit_quest_cb.filter(action='delete_quest'))
async def del_quest(call: types.CallbackQuery, callback_data: dict):
    quest_date = datetime.datetime.strptime(callback_data['quest'], '%Y-%m-%d %H:%M:%S')
    page = callback_data['data']
    await call.answer()
    await call.message.delete()
    await db.del_quest(quest_date)
    await generate_admin_quests(call, page, is_call=True)


# ---------------------------- App handlers -----------------------------
@dp.callback_query_handler(IsAdmin(), text='admin_app')
async def admin_app(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text(_('Choose platform to edit:'))
    await call.message.edit_reply_markup(reply_markup=await keyboards.admin_app_kb())


@dp.callback_query_handler(IsAdmin(), text='admin_app', state=AddApp)
async def admin_app(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text(_('Choose platform to edit:'))
    await call.message.edit_reply_markup(reply_markup=await keyboards.admin_app_kb())


@dp.callback_query_handler(IsAdmin(), keyboards.edit_apps_cb.filter(set='False'))
async def new_app(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    platform = callback_data['platform']
    await call.answer()
    await call.message.edit_text(_('Enter app url for {p} platform:').format(p=platform))
    await AddApp.Confirm.set()
    await state.update_data(platform=platform)


@dp.message_handler(IsAdmin(), state=AddApp.Confirm)
async def confirm_new_app(message: types.Message, state: FSMContext):
    url = message.text
    data = await state.get_data()
    platform = data.get('platform')
    app = await db.get_app(platform)
    await app.update(url=url).apply()
    await message.answer(_('Choose platform to edit:'), reply_markup=await keyboards.admin_app_kb())
    await state.reset_state()


@dp.callback_query_handler(IsAdmin(), keyboards.edit_apps_cb.filter(set='True'))
async def edit_app(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    platform = callback_data['platform']
    app = await db.get_app(platform)
    await call.answer()
    await call.message.edit_text(_('Platform {p} url is:\n{url}').format(p=platform, url=app.url))
    await call.message.edit_reply_markup(reply_markup=await keyboards.app_edit_kb(platform))
    await AddApp.Edit.set()
    await state.update_data(app=app)


@dp.callback_query_handler(IsAdmin(), keyboards.edit_apps_cb.filter(set='delete'), state=AddApp.Edit)
async def delete_app(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    app = data.get('app')
    await call.answer()
    await app.update(url=None).apply()
    await call.message.edit_text(_('Choose platform to edit:'))
    await call.message.edit_reply_markup(reply_markup=await keyboards.admin_app_kb())
    await state.reset_state()


@dp.callback_query_handler(IsAdmin(), keyboards.edit_apps_cb.filter(set='edit'), state=AddApp.Edit)
async def edit_app_url(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text(_('Enter new url:'))
    await AddApp.ConfirmEdit.set()


@dp.message_handler(IsAdmin(), state=AddApp.ConfirmEdit)
async def confirm_edit_app(message: types.Message, state: FSMContext):
    url = message.text
    data = await state.get_data()
    app = data.get('app')
    await app.update(url=url).apply()
    await message.answer(_('Choose platform to edit:'), reply_markup=await keyboards.admin_app_kb())
    await state.reset_state()


# ---------------------------- News handlers -----------------------------
@dp.callback_query_handler(IsAdmin(), text='admin_news')
async def admin_news_menu(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=await keyboards.admin_news_menu())


@dp.callback_query_handler(IsAdmin(), text='add_news')
async def admin_add_news(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer(_("Enter news date in format DD-MM-YYYY "
                                "or type '-' to assign today's date, or press /cancel"))
    await AddNews.EnterDate.set()


@dp.message_handler(IsAdmin(), state=AddNews.EnterDate)
async def enter_quest_date(message: types.Message, state: FSMContext):
    if message.text == '-':
        date = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    else:
        try:
            date = datetime.datetime.strptime(message.text, '%d-%m-%Y')
        except:
            await message.answer(_('Incorrect date format. Try again.'))
            return
    news = News()
    news.date = date
    await message.answer(_('News date is: {date}'
                           '\nNow enter news english Title/Description or press /cancel').format(date=date))
    await AddNews.EnterDesc.set()
    await state.update_data(news=news)


@dp.message_handler(IsAdmin(), state=AddNews.EnterDesc)
async def enter_quest_desc(message: types.Message, state: FSMContext):
    desc = message.text
    data = await state.get_data()
    news = data.get('news')
    news.desc = desc
    await message.answer(_('News english desc: {desc}'
                           '\nNow enter news russian Title/Description or press /cancel').format(desc=desc))
    await AddNews.EnterDesc_ru.set()
    await state.update_data(news=news)


@dp.message_handler(IsAdmin(), state=AddNews.EnterDesc_ru)
async def enter_quest_desc_ru(message: types.Message, state: FSMContext):
    desc = message.text
    data = await state.get_data()
    news = data.get('news')
    news.desc_ru = desc
    await message.answer(_('News russian desc: {desc}'
                           '\nNow enter news english url or press /cancel').format(desc=desc))
    await AddNews.EnterUrl.set()
    await state.update_data(news=news)


@dp.message_handler(IsAdmin(), state=AddNews.EnterUrl)
async def enter_quest_url(message: types.Message, state: FSMContext):
    url = message.text
    data = await state.get_data()
    news = data.get('news')
    news.url = url
    await message.answer(_('News english url: {url}'
                           '\nNow enter news russian url or press /cancel').format(url=url))
    await AddNews.EnterUrl_ru.set()
    await state.update_data(news=news)


@dp.message_handler(IsAdmin(), state=AddNews.EnterUrl_ru)
async def enter_quest_date(message: types.Message, state: FSMContext):
    url = message.text
    data = await state.get_data()
    news = data.get('news')
    news.url_ru = url
    await message.answer(_('News russian url is: {url_ru}'
                           '\n\nNow check news:'
                           '\nDate: {date}'
                           '\nUrl eng: [{url}]({url})'
                           '\nUrl rus: [{url_ru}]({url_ru})'
                           '\nDescription eng: {desc}'
                           '\nDescription rus: {desc_ru}'
                           '\n\nIf everything is correct press confirm or press /cancel').format(
        desc=news.desc, date=news.date, url=news.url, url_ru=url, desc_ru=news.desc_ru),
        parse_mode=types.ParseMode.MARKDOWN, reply_markup=await keyboards.confirm_kb())
    await AddNews.Confirm.set()
    await state.update_data(news=news)


@dp.callback_query_handler(IsAdmin(), text='confirm', state=AddNews.Confirm)
async def confirm_news(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    news: News = data.get('news')
    await news.create()
    await call.message.answer(_('Admin menu.'), reply_markup=await keyboards.admin_news_menu())
    await state.reset_state()


@dp.callback_query_handler(IsAdmin(), text='start_again', state=AddNews.Confirm)
async def start_again_news(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer(_("Enter news date in format DD-MM-YYYY "
                                "or type '-' to assign today's date, or press /cancel"))
    await AddNews.EnterDate.set()


@dp.callback_query_handler(IsAdmin(), text='edit_news')
async def edit_news(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    await generate_admin_news(call, 1)


@dp.callback_query_handler(IsAdmin(), keyboards.edit_news_cb.filter(action=['next_page', 'prev_page']))
async def edit_news_page(call: types.CallbackQuery, callback_data: dict):
    page = int(callback_data['data'])
    await call.answer()
    await generate_admin_news(call, page, gen_new=False)


@dp.callback_query_handler(IsAdmin(), text='exit_edit_news')
async def edit_news_page(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text(_('Admin panel.'))
    await call.message.edit_reply_markup(reply_markup=await keyboards.admin_news_menu())


@dp.callback_query_handler(IsAdmin(), keyboards.edit_news_cb.filter(action=['edit_desc_en', 'edit_desc_ru']))
async def desc(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    news_date = datetime.datetime.strptime(callback_data['news'], '%Y-%m-%d %H:%M:%S')
    page = callback_data['data']
    lang = callback_data['action'][-2:]
    msg = _('Enter new Title/Description:')
    await call.answer()
    mess = await call.message.answer(msg)
    await call.message.delete()
    await EditNews.ConfirmDesc.set()
    await state.update_data(n_date=news_date, page=page, mess=mess, lang=lang)


@dp.message_handler(IsAdmin(), state=EditNews.ConfirmDesc)
async def confirm_desc(message: types.Message, state: FSMContext):
    desc = message.text
    data = await state.get_data()
    lang = data.get('lang')
    date = data.get('n_date')
    page = data.get('page')
    mess = data.get('mess')
    news = await db.get_news(date)
    if lang == 'en':
        await news.update(desc=desc).apply()
    else:
        await news.update(desc_ru=desc).apply()
    await mess.delete()
    await generate_admin_news(message, page, is_call=False)
    await state.reset_state()


@dp.callback_query_handler(IsAdmin(), keyboards.edit_news_cb.filter(action='edit_date'))
async def date_n(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    news_date = datetime.datetime.strptime(callback_data['news'], '%Y-%m-%d %H:%M:%S')
    page = callback_data['data']
    msg = _('Enter new date in format DD-MM-YYYY:')
    await call.answer()
    mess = await call.message.answer(msg)
    await call.message.delete()
    await EditNews.ConfirmDate.set()
    await state.update_data(n_date=news_date, page=page, mess=mess)


@dp.message_handler(IsAdmin(), state=EditNews.ConfirmDate)
async def confirm_date_n(message: types.Message, state: FSMContext):
    date_t = message.text
    if date_t == '-':
        date_n = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    elif len(message.text.split('-')) == 3:
        date_n = datetime.datetime.strptime(date_t, '%d-%m-%Y')
    else:
        await message.answer(_('Incorrect date format. Try again.'))
        return
    data = await state.get_data()
    date = data.get('n_date')
    page = data.get('page')
    mess = data.get('mess')
    news = await db.get_news(date)
    await news.update(date=date_n).apply()
    await mess.delete()
    await generate_admin_news(message, page, is_call=False, news_d=date_n)
    await state.reset_state()


@dp.callback_query_handler(IsAdmin(), keyboards.edit_news_cb.filter(action=['edit_url_en', 'edit_url_ru']))
async def url_n(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    news_date = datetime.datetime.strptime(callback_data['news'], '%Y-%m-%d %H:%M:%S')
    lang = callback_data['action'][-2:]
    page = callback_data['data']
    msg = _('Enter new url:')
    await call.answer()
    mess = await call.message.answer(msg)
    await call.message.delete()
    await EditNews.ConfirmUrl.set()
    await state.update_data(n_date=news_date, page=page, mess=mess, lang=lang)


@dp.message_handler(IsAdmin(), state=EditNews.ConfirmUrl)
async def confirm_url_n(message: types.Message, state: FSMContext):
    url = message.text
    data = await state.get_data()
    lang = data.get('lang')
    date = data.get('n_date')
    page = data.get('page')
    mess = data.get('mess')
    news = await db.get_news(date)
    if lang == 'en':
        await news.update(url=url).apply()
    else:
        await news.update(url_ru=url).apply()
    await mess.delete()
    await generate_admin_news(message, page, is_call=False)
    await state.reset_state()


@dp.callback_query_handler(IsAdmin(), keyboards.edit_news_cb.filter(action='delete_news'))
async def del_news(call: types.CallbackQuery, callback_data: dict):
    news_date = datetime.datetime.strptime(callback_data['news'], '%Y-%m-%d %H:%M:%S')
    page = callback_data['data']
    await call.answer()
    await call.message.delete()
    await db.del_news(news_date)
    await generate_admin_news(call, page, is_call=True)


# ---------------------------- Stats handlers -----------------------------
@dp.callback_query_handler(IsAdmin(), text='admin_stats')
async def admin_stats(call: types.CallbackQuery):
    s_data = await db.get_stats()
    admins = []
    for admin in s_data[3]:
        admins.append('@' + admin.username)
    msg = _('📊 Stats 📊'
            '\n\n🔍 Quests: {q_n}'
            '\n📰 News: {n_n}'
            '\n🐸 Users: {u_n}'
            '\n💼 Admins: {a_l}').format(q_n=s_data[0], n_n=s_data[1], u_n=s_data[2], a_l=' '.join(admins))
    await call.answer()
    await call.message.edit_text(msg)
    await call.message.edit_reply_markup(reply_markup=await keyboards.stats_back())


@dp.callback_query_handler(IsAdmin(), text='stats_back')
async def stats_back(call: types.CallbackQuery):
    msg = _('Admin panel.')
    await call.answer()
    await call.message.edit_text(msg)
    await call.message.edit_reply_markup(reply_markup=await keyboards.admin_kb())
