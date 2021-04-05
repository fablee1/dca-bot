from aiogram.dispatcher.filters.state import State, StatesGroup


class AddQuest(StatesGroup):
    EnterDate = State()
    EnterUrl = State()
    EnterDiff = State()
    Confirm = State()


class AddHints(StatesGroup):
    ChooseLang = State()
    Confirm = State()


class EditQuest(StatesGroup):
    ConfirmDiff = State()
    ConfirmUrl = State()
    ConfirmDate = State()


class EditNews(StatesGroup):
    ConfirmDesc = State()
    ConfirmUrl = State()
    ConfirmDate = State()


class AddApp(StatesGroup):
    Confirm = State()
    Edit = State()
    ConfirmEdit = State()


class AddNews(StatesGroup):
    EnterDate = State()
    EnterDesc = State()
    EnterDesc_ru = State()
    EnterUrl = State()
    EnterUrl_ru = State()
    Confirm = State()
