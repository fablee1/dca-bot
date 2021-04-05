from aiogram import types, Bot
from gino import Gino
from sqlalchemy import (Column, Integer, BigInteger, String,
                        Sequence, DateTime, Boolean)
from sqlalchemy import sql
from gino.schema import GinoSchemaVisitor
from config import db_user, db_pass, host

db = Gino()


class Apps(db.Model):
    __tablename__ = 'Apps'
    query: sql.select
    id = Column(Integer, Sequence('apps_id_seq'), primary_key=True)
    platform = Column(String(3))
    name = Column(String(20))
    url = Column(String(100), default=None)


class User(db.Model):
    __tablename__ = 'Users'
    query: sql.select
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column(BigInteger)
    language = Column(String(2), default='en')
    full_name = Column(String(100))
    username = Column(String(50))
    is_admin = Column(Boolean, default=False)


class News(db.Model):
    __tablename__ = 'News'
    query: sql.select
    id = Column(Integer, Sequence('news_seq'), primary_key=True)
    date = Column(DateTime)
    desc = Column(String(200))
    desc_ru = Column(String(200))
    url = Column(String(50))
    url_ru = Column(String(50))


class Quests(db.Model):
    __tablename__ = 'Quests'
    query: sql.select
    id = Column(Integer, Sequence('quests_seq'), primary_key=True)
    date = Column(DateTime)
    url = Column(String(100))
    diff = Column(Integer)
    image_name = Column(String(200), default=None)
    solved = Column(Boolean, default=False)


class Hints(db.Model):
    __tablename__ = 'Hints'
    query: sql.select
    id = Column(Integer, Sequence('hint_seq'), primary_key=True)
    date = Column(DateTime)
    hint1 = Column(String(200), default=None)
    hint2 = Column(String(200), default=None)
    hint3 = Column(String(200), default=None)
    hint4 = Column(String(200), default=None)
    hint1_ru = Column(String(200), default=None)
    hint2_ru = Column(String(200), default=None)
    hint3_ru = Column(String(200), default=None)
    hint4_ru = Column(String(200), default=None)



class Languages(db.Model):
    __tablename__ = 'Languages'
    query: sql.select
    name = Column(String(100))
    en = Column(String(500), default=None)
    ru = Column(String(500), default=None)


class DBCommands:
    async def get_stats(self):
        quest_count = await db.func.count(Quests.id).gino.scalar()
        news_count = await db.func.count(News.id).gino.scalar()
        user_count = await db.func.count(User.id).gino.scalar()
        admins = await User.query.where(User.is_admin == True).gino.all()
        return [quest_count, news_count, user_count, admins]

    async def get_lang(self):
        user_id = types.User.get_current().id
        user_db = await self.get_user(user_id)
        lang = user_db.language
        return lang

    async def get_apps(self):
        apps = await Apps.query.gino.all()
        return apps

    async def get_app(self, platform):
        app = await Apps.query.where(Apps.platform == platform).gino.first()
        return app

    async def get_user(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        return user

    async def get_news(self, date):
        news = await News.query.where(News.date == date).gino.first()
        return news

    async def get_quest(self, date):
        quest = await Quests.query.where(Quests.date == date).gino.first()
        return quest

    async def get_hints(self, date):
        hints = await Hints.query.where(Hints.date == date).gino.first()
        return hints

    async def last_quests(self):
        quests = await Quests.query.order_by(Quests.date.desc()).gino.all()
        if not quests:
            return None
        return quests

    async def last_news(self):
        news = await News.query.order_by(News.date.desc()).gino.all()
        if not news:
            return None
        return news

    async def add_admin(self, user_id):
        user = await self.get_user(user_id)
        await user.update(is_admin=True).apply()

    async def is_admin(self):
        user = types.User.get_current()
        is_admin = await User.select('is_admin').where(User.user_id == user.id).gino.scalar()
        if is_admin is True:
            return True
        return False

    async def del_admin(self, user_id):
        user = await self.get_user(user_id)
        await user.update(is_admin=False).apply()

    async def add_new_user(self):
        user = types.User.get_current()
        old_user = await self.get_user(user.id)
        if old_user:
            return old_user
        new_user = User()
        new_user.user_id = user.id
        new_user.username = user.username
        new_user.full_name = user.full_name
        await new_user.create()

    async def set_language(self, language):
        user_id = types.User.get_current().id
        user = await self.get_user(user_id)
        await user.update(language=language).apply()

    async def add_new_news(self, desc, url, diff, date):
        new_news = News()
        new_news.date = date
        new_news.desc = desc
        new_news.url = url
        new_news.diff = diff
        await new_news.create()
        return new_news

    async def del_quest(self, date):
        quest = await self.get_quest(date)
        hints = await self.get_hints(date)
        await hints.delete()
        await quest.delete()

    async def del_news(self, date):
        news = await self.get_news(date)
        await news.delete()

    async def quest_solved(self, quest_date):
        quest = await Quests.query.where(Quests.date == quest_date).gino.first()
        await quest.update(solved=True).apply()

    async def quest_not_solved(self, quest_date):
        quest = await Quests.query.where(Quests.date == quest_date).gino.first()
        await quest.update(solved=False).apply()


async def create_db():
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/gino')
    db.gino: GinoSchemaVisitor
    #await db.gino.drop_all()
    await db.gino.create_all()
