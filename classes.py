import requests
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, ForeignKey, Integer, Date, Numeric, Boolean, Text, DateTime
from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import math
import psycopg2

engine = create_engine(
    "postgresql+psycopg2://postgres:122333@localhost:5432/deneme")
insp = inspect(engine)
Base = declarative_base()
DBSession = sessionmaker(bind=engine)
session = DBSession()


class Criminal():
    def __init__(self, response_person_main):
        self.entity_id = response_person_main.json()['entity_id']
        self.forename = response_person_main.json()['forename']
        self.family_name = response_person_main.json()['name']
        self.gender = response_person_main.json()['sex_id']
        self.date_of_birth = self.__edit_date(
            response_person_main.json()['date_of_birth'])
        self.place_of_birth = response_person_main.json()['place_of_birth']
        self.country_of_birth = response_person_main.json()[
            'country_of_birth_id']
        self.weight = self.__edit_weight_format(
            self.__is_zero(response_person_main.json()['weight']))
        self.height = self.__edit_height_format(
            self.__is_zero(response_person_main.json()['height']))
        self.distinguishing_marks = response_person_main.json()[
            'distinguishing_marks']
        self.eyes_color = self.__split_curly_braces(
            response_person_main.json()['eyes_colors_id'])
        self.hair = self.__split_curly_braces(
            response_person_main.json()['hairs_id'])
        self.language = response_person_main.json()['languages_spoken_ids']
        self.nationality = response_person_main.json()['nationalities']
        self.arrest_warrants = response_person_main.json()['arrest_warrants']
        self.picture_link = response_person_main.json()[
            '_links']['images']['href']
        self.pictures = get_request(response_person_main.json()[
            '_links']['images']['href']).json()['_embedded']['images']

    def __edit_height_format(self, data):
        if data:
            return round(data, 2)

    def __edit_weight_format(self, data):
        if data:
            return math.floor(data)

    def __is_zero(self, data):
        """This is a function that checks if the value is zero."""
        if not data == 0:
            return data

    def __split_curly_braces(self, data):
        """This is a function that regulates hair and eyes color data."""
        if data:
            return data[0]

    def __edit_date(self, date):
        if date:
            if len(date) == 4:
                date += '/01/01'
            return date

    def list_arrest_warrants(self):
        return [[i['issuing_country_id'], i['charge'], i['charge_translation']] for i in self.arrest_warrants]

    def list_pictures(self):
        return [[int(i['picture_id']), i['_links']['self']['href']] for i in self.pictures]

    def list_languages(self):
        return [b for b in self.language]

    def list_nationalities(self):
        return [b for b in self.nationality]


class CriminalDb():
    def __init__(self, entity_id):
        self.__person_db = session.query(
            PersonalInformation).filter_by(entity_id=entity_id).first()
        self.person_db_id = session.query(
            PersonalInformation).filter_by(entity_id=entity_id).first().person_id
        self.forename = self.__person_db.forename
        self.family_name = self.__person_db.family_name
        self.gender = self.__person_db.gender
        self.date_of_birth = self.__edit_date_format(
            self.__person_db.date_of_birth)
        self.place_of_birth = self.__person_db.place_of_birth
        self.country_of_birth = self.__person_db.country_of_birth
        self.weight = self.__person_db.weight
        self.height = self.__is_float(self.__person_db.height)
        self.distinguishing_marks = self.__person_db.distinguishing_marks
        self.eyes_color = self.__person_db.eyes_color
        self.hair = self.__person_db.hair

    def __edit_date_format(self, data):
        if data:
            return data.strftime('%Y/%m/%d')

    def __is_float(self, data):
        if data:
            return float(data)

    def language_db(self):
        return session.query(Base.metadata.tables[LanguageInformation.__tablename__]).filter_by(person_id=self.person_db_id).first()

    def person_db_language_list(self):
        return [a.language_spoken for a in session.query(LanguageInformation).filter_by(person_id=self.person_db_id).all()]

    def nationality_db(self):
        return session.query(Base.metadata.tables[NationalityInformation.__tablename__]).filter_by(person_id=self.person_db_id).first()

    def person_db_nationality_list(self):
        return [a.nationality for a in session.query(NationalityInformation).filter_by(person_id=self.person_db_id).all()]

    def arrest_warrants_db(self):
        return session.query(Base.metadata.tables[ArrestWarrantInformation.__tablename__]).filter_by(person_id=self.person_db_id).first()

    def person_db_arrest_warrants_list(self):
        return [[i.issuing_country, i.charge, i.charge_translation] for i in session.query(ArrestWarrantInformation).filter_by(person_id=self.person_db_id).all()]

    def pictures_db(self):
        return session.query(Base.metadata.tables[PictureInformation.__tablename__]).filter_by(person_id=self.person_db_id).first()

    def person_db_pictures_list(self):
        return [[i.unique_picture_id, i.picture_url] for i in session.query(PictureInformation).filter_by(person_id=self.person_db_id).all()]


class PersonalInformation(Base):
    __tablename__ = "personal_informations"
    person_id = Column('person_id', Integer, primary_key=True, nullable=False)
    forename = Column('forename', String(50))
    family_name = Column('family_name', String(50))
    gender = Column('gender', String(10))
    date_of_birth = Column('date_of_birth', Date)
    place_of_birth = Column('place_of_birth', String(100))
    country_of_birth = Column('country_of_birth', String(50))
    weight = Column('weight', Numeric(5, 2))
    height = Column('height', Numeric(5, 2))
    distinguishing_marks = Column('distinguishing_marks', String(1000))
    eyes_color = Column('eyes_color', String(20))
    hair = Column('hair', String(20))
    is_active = Column('is_active', Boolean, nullable=False)
    entity_id = Column('entity_id', String(20), nullable=False)


if not insp.has_table("personal_informations"):
    Base.metadata.tables['personal_informations'].create(engine)


class LanguageInformation(Base):
    __tablename__ = "language_informations"
    language_id = Column('language_id', Integer, primary_key=True)
    person_id = Column('person_id', Integer, ForeignKey(
        "personal_informations.person_id"))
    language_spoken = Column('language_spoken', String(20))
    personal_informations = relationship(
        "PersonalInformation", backref="language", lazy=True)


if not insp.has_table("language_informations"):
    Base.metadata.tables['language_informations'].create(engine)


class NationalityInformation(Base):
    __tablename__ = "nationality_informations"
    nationality_id = Column('nationality_id', Integer, primary_key=True)
    person_id = Column('person_id', Integer, ForeignKey(
        "personal_informations.person_id"))
    nationality = Column('nationality', String(30))
    personal_informations = relationship(
        "PersonalInformation", backref="nationality", lazy=True)


if not insp.has_table("nationality_informations"):
    Base.metadata.tables['nationality_informations'].create(engine)


class ArrestWarrantInformation(Base):
    __tablename__ = "arrest_warrant_informations"
    arrest_warrant_id = Column('arrest_warrant_id', Integer, primary_key=True)
    person_id = Column('person_id', Integer, ForeignKey(
        "personal_informations.person_id"))
    issuing_country = Column('issuing_country', String(30))
    charge = Column('charge', String(1000))
    charge_translation = Column('charge_translation', String(1000))
    personal_informations = relationship(
        "PersonalInformation", backref="arrest_warrant", lazy=True)


if not insp.has_table("arrest_warrant_informations"):
    Base.metadata.tables['arrest_warrant_informations'].create(engine)


class PictureInformation(Base):
    __tablename__ = "picture_informations"
    picture_id = Column('picture_id', Integer, primary_key=True)
    person_id = Column('person_id', Integer, ForeignKey(
        "personal_informations.person_id"))
    unique_picture_id = Column('unique_picture_id', Integer)
    picture_url = Column('picture_url', String(200))
    picture_file_path = Column('picture_file_path', String(50))
    picture_base64 = Column('picture_base64', Text)
    personal_informations = relationship(
        "PersonalInformation", backref="picture_of_the_criminal", lazy=True)


if not insp.has_table("picture_informations"):
    Base.metadata.tables['picture_informations'].create(engine)


class ChangeLogInformation(Base):
    __tablename__ = "change_log"
    log_id = Column('log_id', Integer, primary_key=True)
    person_id = Column('person_id', Integer, ForeignKey(
        "personal_informations.person_id"))
    modification_in_database = Column('modification_in_database', String(1000))
    modification_date = Column('modification_date', DateTime)
    personal_informations = relationship(
        "PersonalInformation", backref="change_log", lazy=True)


if not insp.has_table("change_log"):
    Base.metadata.tables['change_log'].create(engine)


def get_request(url):
    """Returns Response object"""
    payload = {}
    headers = {}
    return requests.request("GET", url, headers=headers, data=payload)
