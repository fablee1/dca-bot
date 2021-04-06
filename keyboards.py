from aiogram.types import ReplyKeyboardMarkup, \
    KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from database import DBCommands
from aiogram.utils.callback_data import CallbackData
from load_all import _

quest_cb = CallbackData('quest', 'action', 'text', sep=';')
admin_hint_cb = CallbackData('admin_hint', 'hint_n', 'q_date', 'page', sep=';')
del_hint_cb = CallbackData('del_hint', 'hint_n', 'q_date', 'page', 'lang', sep='+')
edit_quest_cb = CallbackData('edit_quest', 'action', 'quest', 'data', sep=';')
edit_news_cb = CallbackData('edit_news', 'action', 'news', 'data', sep=';')
finish_hints_cb = CallbackData('finish_hint', 'page', sep=';')
edit_apps_cb = CallbackData('edit_apps', 'set', 'platform', sep=';')
more_news_cb = CallbackData('more_news', 'page')

db = DBCommands()


async def quest_hints(h1=False, h2=False, h3=False, h4=False):
    if not h1 and not h2 and not h3 and not h4:
        return None
    else:
        qh_kb = InlineKeyboardMarkup(row_width=2)
        if h1:
            qh_kb.insert(InlineKeyboardButton(_('Hint'), callback_data='hint1'))
        if h2:
            qh_kb.insert(InlineKeyboardButton(_('Hint'), callback_data='hint2'))
        if h3:
            qh_kb.insert(InlineKeyboardButton(_('Hint'), callback_data='hint3'))
        if h4:
            qh_kb.insert(InlineKeyboardButton(_('Hint'), callback_data='hint4'))
        return qh_kb


async def lang_kb():
    lang_kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🇷🇺 RUS', callback_data='RU'),
        InlineKeyboardButton('🇬🇧 ENG', callback_data='EN')
    )
    return lang_kb


async def finish_hints():
    finish_hints = InlineKeyboardMarkup().add(
        InlineKeyboardButton(_('Cancel'), callback_data='finish_hints')
    )
    return finish_hints


async def lang_conf_kb():
    lang_conf_kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(_('Confirm'), callback_data='lang_confirm')
    )
    return lang_conf_kb


async def main_kb():
    main_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(_('🔍 Quests')),
                KeyboardButton(_('🗞 News'))
            ],
            [
                KeyboardButton(_('📱 Apps')),
                KeyboardButton(_('💽 Scan QR'))
            ],
            [
                KeyboardButton(_('🌐 Website')),
                KeyboardButton(_('⚙️ Language'))
            ]
        ], resize_keyboard=True
    )
    return main_kb


async def more_news(page):
    news_more_kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(_('⬇️ More news ⬇️'), callback_data=more_news_cb.new(page=page + 1))
    )
    return news_more_kb


async def app_kb():
    apps = await db.get_apps()
    kb = InlineKeyboardMarkup(row_width=2)
    for x in apps:
        if x.url is not None:
            kb.insert(InlineKeyboardButton('✅ ' + x.name + ' ✅', url=x.url))
        else:
            kb.insert(InlineKeyboardButton('❌ ' + x.name + ' ❌', callback_data='app_not_exists'))
    return kb


async def admin_quest_menu():
    admin_quest_menu = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(_('Add quest'), callback_data='add_quest'),
        InlineKeyboardButton(_('Edit quests and hints'), callback_data='edit_quest'),
        InlineKeyboardButton(_('Back'), callback_data='back_to_menu')
    )
    return admin_quest_menu


async def admin_news_menu():
    admin_news_menu = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(_('Add news'), callback_data='add_news'),
        InlineKeyboardButton(_('Edit news'), callback_data='edit_news'),
        InlineKeyboardButton(_('Back'), callback_data='back_to_menu')
    )
    return admin_news_menu


async def admin_kb():
    admin_main_kb = InlineKeyboardMarkup(row_width=2)
    button_rows = [
        [
            InlineKeyboardButton(_('Quests'), callback_data='admin_quests'),
            InlineKeyboardButton(_('News'), callback_data='admin_news')
        ],
        [
            InlineKeyboardButton(_('App'), callback_data='admin_app'),
            InlineKeyboardButton(_('Stats'), callback_data='admin_stats')
        ],
        InlineKeyboardButton(_('Exit admin panel'), callback_data='back_to_main_menu')
    ]
    for x in button_rows:
        if type(x) is list:
            admin_main_kb.add(x[0])
            for b in x[1:]:
                admin_main_kb.insert(b)
        else:
            admin_main_kb.add(x)
    return admin_main_kb


async def confirm_kb():
    confirm_kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(_('Confirm'), callback_data='confirm'),
        InlineKeyboardButton(_('Start again'), callback_data='start_again')
    )
    return confirm_kb


async def edit_hint(hint_n, q_date, page, lang):
    kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(_('Edit'), callback_data=lang+'E'),
        InlineKeyboardButton(_('Delete'), callback_data=del_hint_cb.new(hint_n=hint_n, q_date=q_date, page=page, lang=lang)),
        InlineKeyboardButton(_('Back'), callback_data=edit_quest_cb.new(action='edit_hints', quest=q_date, data=page))
    )
    return kb


async def hint_kb(quest_date, page=1, lang='en', next_page=False):
    kb = InlineKeyboardMarkup(row_width=2)
    hints = await db.get_hints(quest_date)
    quest_date = str(quest_date)
    if hints is None:
        return kb
    if lang == 'en':
        if hints.hint1 is not None:
            kb.insert(InlineKeyboardButton(_('Hint 💡'), callback_data=quest_cb.new(action='hint', text='1'+quest_date)))
        if hints.hint2 is not None:
            kb.insert(InlineKeyboardButton(_('Hint 💡'), callback_data=quest_cb.new(action='hint', text='2'+quest_date)))
        if hints.hint3 is not None:
            kb.insert(InlineKeyboardButton(_('Hint 💡'), callback_data=quest_cb.new(action='hint', text='3'+quest_date)))
        if hints.hint4 is not None:
            kb.insert(InlineKeyboardButton(_('Hint 💡'), callback_data=quest_cb.new(action='hint', text='4'+quest_date)))
    else:
        if hints.hint1_ru is not None:
            kb.insert(InlineKeyboardButton(_('Hint 💡'), callback_data=quest_cb.new(action='hint', text='1'+quest_date)))
        if hints.hint2_ru is not None:
            kb.insert(InlineKeyboardButton(_('Hint 💡'), callback_data=quest_cb.new(action='hint', text='2'+quest_date)))
        if hints.hint3_ru is not None:
            kb.insert(InlineKeyboardButton(_('Hint 💡'), callback_data=quest_cb.new(action='hint', text='3'+quest_date)))
        if hints.hint4_ru is not None:
            kb.insert(InlineKeyboardButton(_('Hint 💡'), callback_data=quest_cb.new(action='hint', text='4'+quest_date)))
    if next_page:
        kb.add(InlineKeyboardButton(_('⬇️ More quests ⬇️'),
                                    callback_data=quest_cb.new(action='more_quests', text=page + 1)))
    return kb


async def admin_hints_kb(quest_date, page):
    kb = InlineKeyboardMarkup(row_width=2)
    hints = await db.get_hints(quest_date)
    h_str = _('Hint')
    h1m = h_str + ' 1 EN❌ RU❌'
    h2m = h_str + ' 2 EN❌ RU❌'
    h3m = h_str + ' 3 EN❌ RU❌'
    h4m = h_str + ' 4 EN❌ RU❌'
    p1 = '00'
    p2 = '00'
    p3 = '00'
    p4 = '00'
    if hints is not None:
        if hints.hint1 is not None:
            p1 = '10'
            h1m = h1m[:-5] + '✅ RU❌'
        if hints.hint1_ru is not None:
            p1 = p1[:-1] + '1'
            h1m = h1m[:-1] + '✅'
        if hints.hint2 is not None:
            p2 = '10'
            h2m = h2m[:-5] + '✅ RU❌'
        if hints.hint2_ru is not None:
            p2 = p2[:-1] + '1'
            h2m = h2m[:-1] + '✅'
        if hints.hint3 is not None:
            p3 = '10'
            h3m = h3m[:-5] + '✅ RU❌'
        if hints.hint3_ru is not None:
            p3 = p3[:-1] + '1'
            h3m = h3m[:-1] + '✅'
        if hints.hint4 is not None:
            p4 = '10'
            h4m = h4m[:-5] + '✅ RU❌'
        if hints.hint4_ru is not None:
            p4 = p4[:-1] + '1'
            h4m = h4m[:-1] + '✅'
    hint1 = InlineKeyboardButton(h1m, callback_data=admin_hint_cb.new(hint_n='1' + p1, q_date=quest_date, page=page))
    hint2 = InlineKeyboardButton(h2m, callback_data=admin_hint_cb.new(hint_n='2' + p2, q_date=quest_date, page=page))
    hint3 = InlineKeyboardButton(h3m, callback_data=admin_hint_cb.new(hint_n='3' + p3, q_date=quest_date, page=page))
    hint4 = InlineKeyboardButton(h4m, callback_data=admin_hint_cb.new(hint_n='4' + p4, q_date=quest_date, page=page))
    finish = InlineKeyboardButton(_('Finish'), callback_data=finish_hints_cb.new(page=page))
    kb.add(hint1, hint2, hint3, hint4, finish)
    return kb


async def hint_lang():
    hint_lang_kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🇷🇺 RUS', callback_data='ru'),
        InlineKeyboardButton('🇬🇧 ENG', callback_data='en')
    )
    return hint_lang_kb


async def edit_quest_kb(quest, page_n, next_page=False, prev_page=False):
    kb = InlineKeyboardMarkup(row_width=3)
    edit_date = InlineKeyboardButton(_('Edit date'), callback_data=edit_quest_cb.new(action='edit_date',
                                                                                     quest=quest.date, data=page_n))
    edit_url = InlineKeyboardButton(_('Edit url'), callback_data=edit_quest_cb.new(action='edit_url',
                                                                                   quest=quest.date, data=page_n))
    edit_diff = InlineKeyboardButton(_('Edit diff'), callback_data=edit_quest_cb.new(action='edit_diff',
                                                                                     quest=quest.date, data=page_n))
    edit_hints = InlineKeyboardButton(_('Edit hints'), callback_data=edit_quest_cb.new(action='edit_hints',
                                                                                       quest=quest.date, data=page_n))
    del_quest = InlineKeyboardButton(_('Delete'), callback_data=edit_quest_cb.new(action='delete_quest',
                                                                                  quest=quest.date, data=page_n))
    solve = _('Unsolved ❌')
    if quest.solved:
        solve = _('Solved ✅')
    edit_solved = InlineKeyboardButton(solve, callback_data=edit_quest_cb.new(action='edit_solve',
                                                                              quest=quest.date, data=page_n))
    kb.add(edit_date, edit_url)
    kb.add(edit_diff, edit_hints)
    kb.add(edit_solved, del_quest)
    if prev_page:
        prev_page_b = InlineKeyboardButton(_('Prev page'), callback_data=edit_quest_cb.new(action='prev_page',
                                                                                           quest=quest.date,
                                                                                           data=page_n - 1))
        kb.add(prev_page_b)
    if next_page:
        next_page_b = InlineKeyboardButton(_('Next page'), callback_data=edit_quest_cb.new(action='next_page',
                                                                                           quest=quest.date,
                                                                                           data=page_n + 1))
        if prev_page:
            kb.insert(next_page_b)
        else:
            kb.add(next_page_b)
    kb.insert(InlineKeyboardButton(_('Exit'), callback_data='exit_edit_quest'))
    return kb


async def edit_news_kb(news, page_n, next_page=False, prev_page=False):
    kb = InlineKeyboardMarkup(row_width=3)
    edit_date = InlineKeyboardButton(_('Edit date'), callback_data=edit_news_cb.new(action='edit_date',
                                                                                    news=news.date, data=page_n))
    edit_url = InlineKeyboardButton(_('Edit english url'), callback_data=edit_news_cb.new(action='edit_url_en',
                                                                                          news=news.date, data=page_n))
    edit_desc = InlineKeyboardButton(_('Edit english desc'), callback_data=edit_news_cb.new(action='edit_desc_en',
                                                                                            news=news.date,
                                                                                            data=page_n))
    edit_url_ru = InlineKeyboardButton(_('Edit russian url'), callback_data=edit_news_cb.new(action='edit_url_ru',
                                                                                             news=news.date,
                                                                                             data=page_n))
    edit_desc_ru = InlineKeyboardButton(_('Edit russian desc'), callback_data=edit_news_cb.new(action='edit_desc_ru',
                                                                                               news=news.date,
                                                                                               data=page_n))
    delete_news = InlineKeyboardButton(_('Delete'), callback_data=edit_news_cb.new(action='delete_news',
                                                                                   news=news.date, data=page_n))
    kb.add(edit_date, delete_news)
    kb.add(edit_url, edit_url_ru)
    kb.add(edit_desc, edit_desc_ru)
    if prev_page:
        prev_page_b = InlineKeyboardButton(_('Prev page'), callback_data=edit_news_cb.new(action='prev_page',
                                                                                          news=news.date,
                                                                                          data=page_n - 1))
        kb.add(prev_page_b)
    if next_page:
        next_page_b = InlineKeyboardButton(_('Next page'), callback_data=edit_news_cb.new(action='next_page',
                                                                                          news=news.date,
                                                                                          data=page_n + 1))
        if prev_page:
            kb.insert(next_page_b)
        else:
            kb.add(next_page_b)
    kb.insert(InlineKeyboardButton(_('Exit'), callback_data='exit_edit_news'))
    return kb


async def admin_app_kb():
    apps = await db.get_apps()
    kb = InlineKeyboardMarkup(row_width=3)
    for x in apps:
        if x.url is not None:
            kb.insert(InlineKeyboardButton('✅ ' + x.name + ' ✅',
                                           callback_data=edit_apps_cb.new(set=True, platform=x.platform)))
        else:
            kb.insert(InlineKeyboardButton('❌ ' + x.name + ' ❌',
                                           callback_data=edit_apps_cb.new(set=False, platform=x.platform)))
    kb.add(InlineKeyboardButton(_('Back'), callback_data='back_to_menu'))
    return kb


async def app_edit_kb(platform):
    kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(_('Edit'), callback_data=edit_apps_cb.new(set='edit', platform=platform)),
        InlineKeyboardButton(_('Delete'), callback_data=edit_apps_cb.new(set='delete', platform=platform)),
        InlineKeyboardButton(_('Back'), callback_data='admin_app')
    )
    return kb


async def stats_back():
    stats_back_kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(_('Back'), callback_data='stats_back')
    )
    return stats_back_kb
