import os
import base64
from sqlalchemy import false, insert, update, delete, and_
from datetime import datetime
import datetime
import requests
from classes import LanguageInformation, NationalityInformation, ArrestWarrantInformation, PictureInformation, ChangeLogInformation, PersonalInformation, session, Base, engine


def get_people_db_to_api(total_person_per_page, number_of_active_people, number_of_inactive_people, page, total_people_db):
    """ This function makes all the information in the database available to the api """
    return {'DB': [{'forename': i.forename, 'family_name': i.family_name, 'gender': i.gender, 'date_of_birth': i.date_of_birth, 'place_of_birth': i.place_of_birth, 'country_of_birth': i.country_of_birth, 'weight': i.weight, 'height': i.height, 'distinguishing_marks': i.distinguishing_marks, 'eyes_color': i.eyes_color, 'hair': i.hair, 'entity_id': i.entity_id, 'is_active': i.is_active,

                    'language_spoken': [a.language_spoken for a in session.query(LanguageInformation).filter_by(person_id=get_person_db_id_from_entity_id(i.entity_id)).all()],

                    'nationality': [b.nationality for b in session.query(NationalityInformation).filter_by(person_id=get_person_db_id_from_entity_id(i.entity_id)).all()],

                    'arrest_warrants': [{'issuing_country': c.issuing_country, 'charge': c.charge, 'charge_translation': c.charge_translation} for c in session.query(ArrestWarrantInformation).filter_by(person_id=get_person_db_id_from_entity_id(i.entity_id)).all()],

                    'pictures': [{'unique_picture_id': d.unique_picture_id, 'picture_url': d.picture_url, 'picture_base64': d.picture_base64} for d in session.query(PictureInformation).filter_by(person_id=get_person_db_id_from_entity_id(i.entity_id)).all()],

                    'change_log': [{'modification_in_database': f.modification_in_database, 'modification_date': f.modification_date} for f in session.query(ChangeLogInformation).filter_by(person_id=get_person_db_id_from_entity_id(i.entity_id)).all()]
                    } for i in total_person_per_page], 'result_this_page': len(total_person_per_page), 'active': number_of_active_people, 'inactive': number_of_inactive_people, 'page': page, 'total number_of_pages': int(total_people_db/20), 'total': total_people_db}


def get_one_person_from_person_id(person_id):
    """ This function makes the information of a single person in the database available to the api """
    person = session.query(PersonalInformation).filter_by(
        person_id=person_id).first()
    if person:
        id = get_person_db_id_from_entity_id(person.entity_id)
        return {'DB': [{'forename': person.forename, 'family_name': person.family_name, 'gender': person.gender, 'date_of_birth': person.date_of_birth, 'place_of_birth': person.place_of_birth, 'country_of_birth': person.country_of_birth, 'weight': person.weight, 'height': person.height, 'distinguishing_marks': person.distinguishing_marks, 'eyes_color': person.eyes_color, 'hair': person.hair, 'entity_id': person.entity_id, 'is_active': person.is_active,
                        'language_spoken': [a.language_spoken for a in session.query(LanguageInformation).filter_by(person_id=id).all()],

                        'nationality': [b.nationality for b in session.query(NationalityInformation).filter_by(person_id=id).all()],

                        'arrest_warrants': [{'issuing_country': c.issuing_country, 'charge': c.charge, 'charge_translation': c.charge_translation} for c in session.query(ArrestWarrantInformation).filter_by(person_id=id).all()],

                        'pictures': [{'unique_picture_id': d.unique_picture_id, 'picture_url': d.picture_url, 'picture_base64': d.picture_base64} for d in session.query(PictureInformation).filter_by(person_id=id).all()],

                        'change_log': [{'modification_in_database': f.modification_in_database, 'modification_date': f.modification_date} for f in session.query(ChangeLogInformation).filter_by(person_id=id).all()]
                        }]}
    else:
        return False


def page_return_db(page):
    """ This function paginates the information in the database and the parameter to return the information on the page """
    return session.query(PersonalInformation).order_by(PersonalInformation.person_id.asc()).limit(20).offset(page*20).all()


def page_return_db_active(page):
    """ This function paginates the active people information in the database and the parameter to return the information on the page """
    return session.query(PersonalInformation).filter_by(is_active=True).order_by(PersonalInformation.person_id.asc()).limit(20).offset(page*20).all()


def get_person_db_id_from_entity_id(entity_id):
    """The function to find the person_id of the person insert to the personal_informations section via the entity id"""
    return session.query(PersonalInformation).filter_by(entity_id=entity_id).first().person_id


def get_active_person_db_count():
    """ This function returns how many active people are in the database. """
    return session.query(
        PersonalInformation).filter_by(is_active=True).count()


def get_inactive_person_db_count():
    """ This function returns how many inactive people are in the database. """
    return session.query(
        PersonalInformation).filter_by(is_active=False).count()


def get_total_person_db_count():
    """ This function returns how many total people are in the database. """
    return session.query(PersonalInformation).count()


def get_active_person_db_entities():
    """This is a function that returns the list of active contacts in the database."""
    return [a[0] for a in session.query(PersonalInformation.entity_id).filter_by(is_active=True).all()]

def get_base64_data_from_unique_picture_id(unique_picture_id):
    return session.query(PictureInformation.picture_base64).filter_by(unique_picture_id=unique_picture_id).first()[0]

def get_inactive_person_db_entities():
    """This is a function that returns the list of active contacts in the database."""
    return [a[0] for a in session.query(PersonalInformation.entity_id).filter_by(is_active=False).all()]


def get_person_db_personal_information(entity_id):
    """ This is a function that returns whether the person at the specified entity_id is in the database. """
    return session.query(PersonalInformation).filter_by(entity_id=entity_id).all()


def create_pictures_folder():
    """This is a function that creates the folder where the images to be downloaded are stored."""
    try:
        os.mkdir('Pictures')
    except:
        print("The new folder was not created because the folder that will contain the images already exists.")


def picture_download(p_path, pUrl):
    """This is a function that uses the image file path (pPath) and image link (pUrl) parameters. Download the picture in the file path"""
    with open(p_path, 'wb') as handle:
        response = requests.get(pUrl, stream=False)
        if not response.ok:
            print(response)
        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)


def picture_b64(p_path):
    """This function converts the image in the file path to base64 format."""
    with open(p_path, "rb") as image2string:
        return base64.b64encode(image2string.read()).decode("utf-8")


def create_file_path(picture_id):
    """This is a function that returns the file path of the image using the image id."""
    file_name = str(picture_id)
    main_filePath = 'Pictures'
    picture_filePath = main_filePath + '/' + file_name + '.jpg'
    return picture_filePath


def insert_personal_informations(person):
    """This is a function that insert personal information to the database."""
    stmt = (insert(Base.metadata.tables[PersonalInformation.__tablename__]).values(forename=person.forename, family_name=person.family_name, gender=person.gender, date_of_birth=person.date_of_birth, place_of_birth=person.place_of_birth,
            country_of_birth=person.country_of_birth, weight=person.weight, height=person.height, distinguishing_marks=person.distinguishing_marks, eyes_color=person.eyes_color, hair=person.hair, is_active=True, entity_id=person.entity_id))
    try:
        engine.connect().execute(stmt)
        insert_new_person_info_to_change_log_table(person.entity_id)
    except:
        print(
            f"The personal informations of the person with the entity_id: {person.entity_id} could not be insert the database.")


def insert_language_informations(person_db_id, person):
    """This is a function that insert language informations to the database."""
    for i in person.language:
        stmt = (insert(Base.metadata.tables[LanguageInformation.__tablename__]).values(
            person_id=person_db_id, language_spoken=i))
        try:
            engine.connect().execute(stmt)
            insert_language_info_to_change_log(i, person.entity_id)

        except:
            print(
                f"The personal language informations of the person with the person_id: {person_db_id} could not be insert the database.")


def insert_language_information(data, person_db_id, entity_id):
    """This is a function that insert language information to the database."""
    stmt = (insert(Base.metadata.tables[LanguageInformation.__tablename__]).values(
        person_id=person_db_id, language_spoken=data))
    try:
        engine.connect().execute(stmt)
        insert_language_info_to_change_log(
            data, entity_id)
    except:
        print(
            f"The personal language information of the person with the person_id: {person_db_id} could not be insert the database.")


def insert_nationality_informations(person_db_id, person):
    """This is a function that insert nationality information to the database."""
    for i in person.nationality:
        stmt = (insert(Base.metadata.tables[NationalityInformation.__tablename__]).values(
            person_id=person_db_id, nationality=i))
        try:
            engine.connect().execute(stmt)
            insert_nationality_info_to_change_log(i, person.entity_id)
        except:
            print(
                f"The personal nationality informations of the person with the person_id: {person_db_id} could not be insert the database.")


def insert_nationality_information(data, person_db_id, entity_id):
    """This is a function that insert nationality informations to the database."""
    stmt = (insert(Base.metadata.tables[NationalityInformation.__tablename__]).values(
        person_id=person_db_id, nationality=data))
    try:
        engine.connect().execute(stmt)
        insert_nationality_info_to_change_log(
            data, entity_id)
    except:
        print(
            f"The personal nationality information of the person with the person_id: {person_db_id} could not be insert the database.")


def insert_arrest_warrants(person_db_id, person):
    """This is a function that insert arrest warrants informations to the database."""
    for i in person.arrest_warrants:
        stmt = (insert(Base.metadata.tables[ArrestWarrantInformation.__tablename__]).values(
            person_id=person_db_id, issuing_country=i['issuing_country_id'], charge=i['charge'], charge_translation=i['charge_translation']))
        try:
            engine.connect().execute(stmt)
            insert_arrest_warrant_info_to_change_log(i['issuing_country_id'], i['charge'], i['charge_translation'], person.entity_id)
        except:
            print(
                f"The personal arrest warrants informations of the person with the person_id: {person_db_id} could not be insert the database.")


def insert_arrest_warrant(issuing_country, charge, charge_translation, person_id, entity_id):
    """This is a function that insert arrest warrants information to the database."""
    stmt = (insert(Base.metadata.tables[ArrestWarrantInformation.__tablename__]).values(
        person_id=person_id, issuing_country=issuing_country, charge=charge, charge_translation=charge_translation))
    try:
        engine.connect().execute(stmt)
        insert_arrest_warrant_info_to_change_log(
            issuing_country, charge, charge_translation, entity_id)
    except:
        print(
            f"The personal arrest warrants informations of the person with the person_id: {person_id} could not be insert the database.")


def insert_pictures(person_db_id, person):
    """This is a function that insert pictures informations to the database."""
    for i in person.pictures:
        picture_id = i['picture_id']
        picture_url = i['_links']['self']['href']
        picture_file_path = create_file_path(picture_id)
        try:
            picture_download(picture_file_path, picture_url)
            picture_base64 = picture_b64(picture_file_path)
            stmt = (insert(Base.metadata.tables[PictureInformation.__tablename__]).values(
                person_id=person_db_id, unique_picture_id=picture_id, picture_url=picture_url, picture_file_path=picture_file_path, picture_base64=picture_base64))
            engine.connect().execute(stmt)
            insert_picture_info_to_change_log(picture_id, person.entity_id)
        except:
            print(
                f"The picture of the person with the Id {person_db_id} could not be insert.")


def insert_picture(picture_id, picture_url, person_db_id, entity_id):
    """This is a function that insert picture information to the database."""
    picture_file_path = create_file_path(picture_id)
    try:
        picture_download(picture_file_path, picture_url)
        picture_base64 = picture_b64(picture_file_path)
        stmt = (insert(Base.metadata.tables[PictureInformation.__tablename__]).values(
            person_id=person_db_id, unique_picture_id=picture_id, picture_url=picture_url, picture_file_path=picture_file_path, picture_base64=picture_base64))
        engine.connect().execute(stmt)
        insert_picture_info_to_change_log(
            picture_id, entity_id)
    except:
        print(
            f"The picture of the person with the Id {person_db_id} could not be insert.")


def update_forename(person, person_db):
    """This is a function that update forename information to the database."""
    stmt = (update(Base.metadata.tables[PersonalInformation.__tablename__]).where(
        Base.metadata.tables[PersonalInformation.__tablename__].c.entity_id == person.entity_id).values(forename=person.forename))
    try:
        engine.connect().execute(stmt)
        insert_updated_forename_info_change_log(person, person_db)
    except:
        print(
            f"Forename information of the person with entity_id: {person.entity_id} could not be updated.")


def update_family_name(person, person_db):
    """This is a function that update family name information to the database."""
    stmt = (update(Base.metadata.tables[PersonalInformation.__tablename__]).where(
        Base.metadata.tables[PersonalInformation.__tablename__].c.entity_id == person.entity_id).values(family_name=person.family_name))
    try:
        engine.connect().execute(stmt)
        insert_updated_family_name_info_change_log(person, person_db)
    except:
        print(
            f"Family name information of the person with entity_id: {person.entity_id} could not be updated.")


def update_gender(person, person_db):
    """This is a function that update gender information to the database."""
    stmt = (update(Base.metadata.tables[PersonalInformation.__tablename__]).where(
        Base.metadata.tables[PersonalInformation.__tablename__].c.entity_id == person.entity_id).values(gender=person.gender))
    try:
        engine.connect().execute(stmt)
        insert_updated_gender_info_change_log(person, person_db)
    except:
        print(
            f"Gender information of the person with entity_id: {person.entity_id} could not be updated.")


def update_date_of_birth(person, person_db):
    """This is a function that update date of birth information to the database."""
    stmt = (update(Base.metadata.tables[PersonalInformation.__tablename__]).where(
        Base.metadata.tables[PersonalInformation.__tablename__].c.entity_id == person.entity_id).values(date_of_birth=person.date_of_birth))
    try:
        engine.connect().execute(stmt)
        insert_updated_date_of_birth_info_change_log(person, person_db)
    except:
        print(
            f"Date of birth information of the person with entity_id: {person.entity_id} could not be updated.")


def update_place_of_birth(person, person_db):
    """This is a function that update place birth information to the database."""
    stmt = (update(Base.metadata.tables[PersonalInformation.__tablename__]).where(
        Base.metadata.tables[PersonalInformation.__tablename__].c.entity_id == person.entity_id).values(place_of_birth=person.place_of_birth))
    try:
        engine.connect().execute(stmt)
        insert_updated_place_of_birth_info_change_log(person, person_db)
    except:
        print(
            f"Place of birth information of the person with entity_id: {person.entity_id} could not be updated.")


def update_country_of_birth(person, person_db):
    """This is a function that update country of birth information to the database."""
    stmt = (update(Base.metadata.tables[PersonalInformation.__tablename__]).where(
        Base.metadata.tables[PersonalInformation.__tablename__].c.entity_id == person.entity_id).values(country_of_birth=person.country_of_birth))
    try:
        engine.connect().execute(stmt)
        insert_updated_country_of_birth_info_change_log(person, person_db)
    except:
        print(
            f"Country of birth information of the person with entity_id: {person.entity_id} could not be updated.")


def update_weight(person, person_db):
    """This is a function that update weight information to the database."""
    stmt = (update(Base.metadata.tables[PersonalInformation.__tablename__]).where(
        Base.metadata.tables[PersonalInformation.__tablename__].c.entity_id == person.entity_id).values(weight=person.weight))
    try:
        engine.connect().execute(stmt)
        insert_updated_weight_info_change_log(person, person_db)
    except:
        print(
            f"Weight information of the person with entity_id: {person.entity_id} could not be updated.")


def update_height(person, person_db):
    """This is a function that update height information to the database."""
    stmt = (update(Base.metadata.tables[PersonalInformation.__tablename__]).where(
        Base.metadata.tables[PersonalInformation.__tablename__].c.entity_id == person.entity_id).values(height=person.height))
    try:
        engine.connect().execute(stmt)
        insert_updated_height_info_change_log(person, person_db)
    except:
        print(
            f"Height information of the person with entity_id: {person.entity_id} could not be updated.")


def update_distinguishing_marks(person, person_db):
    """This is a function that update distinguishing information to the database."""
    stmt = (update(Base.metadata.tables[PersonalInformation.__tablename__]).where(
        Base.metadata.tables[PersonalInformation.__tablename__].c.entity_id == person.entity_id).values(distinguishing_marks=person.distinguishing_marks))
    try:
        engine.connect().execute(stmt)
        insert_updated_distinguishing_marks_info_change_log(person, person_db)
    except:
        print(
            f"Distinguishing information of the person with entity_id: {person.entity_id} could not be updated.")


def update_eyes_color(person, person_db):
    """This is a function that update eyes color information to the database."""
    stmt = (update(Base.metadata.tables[PersonalInformation.__tablename__]).where(
        Base.metadata.tables[PersonalInformation.__tablename__].c.entity_id == person.entity_id).values(eyes_color=person.eyes_color))
    try:
        engine.connect().execute(stmt)
        insert_updated_eyes_color_info_change_log(person, person_db)
    except:
        print(
            f"Eyes color information of the person with entity_id: {person.entity_id} could not be updated.")


def update_hair(person, person_db):
    """This is a function that update hair information to the database."""
    stmt = (update(Base.metadata.tables[PersonalInformation.__tablename__]).where(
        Base.metadata.tables[PersonalInformation.__tablename__].c.entity_id == person.entity_id).values(hair=person.hair))
    try:
        engine.connect().execute(stmt)
        insert_updated_hair_info_change_log(person, person_db)
    except:
        print(
            f"Hair information of the person with entity_id: {person.entity_id} could not be updated.")


def delete_language(data, person_db_id, entity_id):
    """This is a function that deletes data that is in the database of the person but not in the information we obtain upon request."""
    stmt = (delete(Base.metadata.tables[LanguageInformation.__tablename__]).filter(and_(
        Base.metadata.tables[LanguageInformation.__tablename__].c.language_spoken == data, Base.metadata.tables[LanguageInformation.__tablename__].c.person_id == person_db_id)))
    try:
        engine.connect().execute(stmt)
        insert_deleted_language_info_change_log(
            data, entity_id)
    except:
        print(
            f"Language information of the person with entity_id: {person_db_id} could not be deleted.")


def delete_nationality(data, person_db_id, entity_id):
    """This is a function that deletes data that is in the database of the person but not in the information we obtain upon request."""
    stmt = (delete(Base.metadata.tables[NationalityInformation.__tablename__]).filter(and_(
        Base.metadata.tables[NationalityInformation.__tablename__].c.nationality == data, Base.metadata.tables[NationalityInformation.__tablename__].c.person_id == person_db_id)))
    try:
        engine.connect().execute(stmt)
        insert_deleted_nationality_info_change_log(
            data, entity_id)

    except:
        print(
            f"Nationality information of the person with entity_id: {person_db_id} could not be deleted.")


def delete_arrest_warrants(issuing_country, charge, person_db_id, entity_id):
    """This is a function that deletes data that is in the database of the person but not in the information we obtain upon request."""
    stmt = (delete(Base.metadata.tables[ArrestWarrantInformation.__tablename__]).filter(and_(Base.metadata.tables[ArrestWarrantInformation.__tablename__].c.issuing_country == issuing_country,
            Base.metadata.tables[ArrestWarrantInformation.__tablename__].c.charge == charge, Base.metadata.tables[ArrestWarrantInformation.__tablename__].c.person_id == person_db_id)))
    try:
        engine.connect().execute(stmt)
        insert_deleted_arrest_warrant_info_change_log(
            issuing_country, charge, entity_id)
    except:
        print(
            f"Arrest warrants information of the person with entity_id: {person_db_id} could not be deleted.")


def delete_picture(unique_picture_id, person_db_id, entity_id):
    """This is a function that deletes data that is in the database of the person but not in the information we obtain upon request."""
    bs64 = get_base64_data_from_unique_picture_id(unique_picture_id)
    stmt = (delete(Base.metadata.tables[PictureInformation.__tablename__]).filter(
        Base.metadata.tables[PictureInformation.__tablename__].c.unique_picture_id == unique_picture_id))
    try:
        engine.connect().execute(stmt)
        insert_deleted_picture_info_change_log(
            unique_picture_id, entity_id, bs64)
    except:
        print(
            f"Picture information of the person with entity_id: {person_db_id} could not be deleted.")


def insert_new_person_info_to_change_log_table(entity_id):
    """This is a function that adds this information to the log table when a new person is added to the database."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(
        entity_id), modification_in_database=f"A new contact with entity_id {entity_id} has been added to the database.", modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"A new contact with entity_id {entity_id} has been successfully added to the log table.")
    except:
        print(
            f"A new contact with entity_id {entity_id} could not be added to the log table.")


def insert_inactive_person_change_log_table(entity_id):
    """This is a function that adds this information to the log table when an inactive person is added to the database."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(
        entity_id), modification_in_database=f"The inactive person with entity_id {entity_id} has been added to the database.", modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"A inactive person with entity_id {entity_id} has been successfully added to the log table.")
    except:
        print(
            f"The inactive person with entity_id {entity_id} could not be added to the log table.")


def insert_language_info_to_change_log(language, entity_id):
    """This is a function that adds this change to the log table when a new language is inserted."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(
        entity_id), modification_in_database=f'The person with entity_id {entity_id} added new language: {language}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {entity_id} added new language: {language}")
    except:
        print(
            f"The new language({language}) of the person could not be added to the log table.")


def insert_nationality_info_to_change_log(nationality, entity_id):
    """This is a function that adds this change to the log table when a new language is inserted."""
    stmt = (
        insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(entity_id), modification_in_database=f'The person with entity_id {entity_id} added new nationality: {nationality}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {entity_id} added new nationality: {nationality}")
    except:
        print(
            f"The new nationality({nationality}) of the person could not be added to the log table.")



def insert_arrest_warrant_info_to_change_log(issuing_country, charge, charge_translation, entity_id):
    """This is a function that adds this change to the log table when a new arrest warrant is inserted."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(
        entity_id), modification_in_database=f'The person with entity_id {entity_id} added new arrest warrant. issuing_country: {issuing_country}, charge: {charge}, charge_translation: {charge_translation}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {entity_id} added new new arrest warrant. issuing_country: {issuing_country}, charge: {charge}, charge_translation: {charge_translation}")
    except:
        print(
            f"The new arrest warrant(issuing_country: {issuing_country}, charge: {charge}, charge_translation: {charge_translation}) of the person with entity_id {entity_id} could not be added to the log table.")


def insert_arrest_warrants_info_to_change_log(person):
    """This is a function that adds this change to the log table when a new arrest warrants are inserted."""
    for i in person.arrest_warrants:
        issuing_country = i['issuing_country_id']
        charge = i['charge']
        charge_translation = i['charge_translation']
        stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(
            person.entity_id), modification_in_database=f'The person with entity_id {person.entity_id} added new arrest warrant. issuing_country: {issuing_country}, charge: {charge}, charge_translation: {charge_translation}', modification_date=datetime.datetime.now()))
        try:
            engine.connect().execute(stmt)
            print(
                f"The person with entity_id {person.entity_id} added new new arrest warrant. issuing_country: {issuing_country}, charge: {charge}, charge_translation: {charge_translation}")
        except:
            print(
                f"The new arrest warrant(issuing_country: {issuing_country}, charge: {charge}, charge_translation: {charge_translation}) of the person with entity_id {person.entity_id} could not be added to the log table.")


def insert_picture_info_to_change_log(picture_id, entity_id):
    """This is a function that adds this change to the log table when a new picture is inserted."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(
        entity_id), modification_in_database=f'The person with entity_id {entity_id} added new picture. picture_id: {picture_id}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {entity_id} added new new picture. picture_id: {picture_id}")
    except:
        print(
            f"The new picture(picture_id: {picture_id}) of the person with entity_id {entity_id} could not be added to the log table.")


def insert_updated_forename_info_change_log(person, person_db):
    """This is the function that adds the forename change to the log table."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(
        person.entity_id), modification_in_database=f'The person with entity_id {person.entity_id} updated new forename: {person_db.forename} to {person.forename}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {person.entity_id} updated forename: {person_db.forename} to {person.forename}")
    except:
        print(
            f"The person with entity_id {person.entity_id} could not be update forename: {person_db.forename} to {person.forename}")


def insert_updated_family_name_info_change_log(person, person_db):
    """This is the function that adds the family name change to the log table."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(
        person.entity_id), modification_in_database=f'The person with entity_id {person.entity_id} updated new family name: {person_db.family_name} to {person.family_name}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {person.entity_id} updated family name: {person_db.family_name} to {person.family_name}")
    except:
        print(
            f"The person with entity_id {person.entity_id} could not be update family name: {person_db.family_name} to {person.family_name}")


def insert_updated_gender_info_change_log(person, person_db):
    """This is the function that adds the gender change to the log table."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(
        person.entity_id), modification_in_database=f'The person with entity_id {person.entity_id} updated new gender: {person_db.gender} to {person.gender}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {person.entity_id} updated gender: {person_db.gender} to {person.gender}")
    except:
        print(
            f"The person with entity_id {person.entity_id} could not be update gender: {person_db.gender} to {person.gender}")


def insert_updated_date_of_birth_info_change_log(person, person_db):
    """This is the function that adds the date of birth change to the log table."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(person.entity_id
                                                                                                                              ), modification_in_database=f'The person with entity_id {person.entity_id} updated new date of birth: {person_db.date_of_birth} to {person.date_of_birth}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {person.entity_id} updated date of birth: {person_db.date_of_birth} to {person.date_of_birth}")
    except:
        print(
            f"The person with entity_id {person.entity_id} could not be update date of birth: {person_db.date_of_birth.strftime('%Y/%m/%d')} to {person.date_of_birth}")


def insert_updated_place_of_birth_info_change_log(person, person_db):
    """This is the function that adds the place of birth change to the log table."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(person.entity_id
                                                                                                                              ), modification_in_database=f'The person with entity_id {person.entity_id} updated new place of birth: {person_db.place_of_birth} to {person.place_of_birth}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {person.entity_id} updated place of birth: {person_db.place_of_birth} to {person.place_of_birth}")
    except:
        print(
            f"The person with entity_id {person.entity_id} could not be update place of birth: {person_db.place_of_birth} to {person.place_of_birth}")


def insert_updated_country_of_birth_info_change_log(person, person_db):
    """This is the function that adds the country of birth change to the log table."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(person.entity_id
                                                                                                                              ), modification_in_database=f'The person with entity_id {person.entity_id} updated new country of birth: {person_db.country_of_birth} to {person.country_of_birth}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {person.entity_id} updated country of birth: {person_db.country_of_birth} to {person.country_of_birth}")
    except:
        print(
            f"The person with entity_id {person.entity_id} could not be update country of birth: {person_db.country_of_birth} to {person.country_of_birth}")


def insert_updated_weight_info_change_log(person, person_db):
    """This is the function that adds the weight change to the log table."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(person.entity_id
                                                                                                                              ), modification_in_database=f'The person with entity_id {person.entity_id} updated new weight: {person_db.weight} to {person.weight}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {person.entity_id} updated weight: {person_db.weight} to {person.weight}")
    except:
        print(
            f"The person with entity_id {person.entity_id} could not be update weight: {person_db.weight} to {person.weight}")


def insert_updated_height_info_change_log(person, person_db):
    """This is the function that adds the height change to the log table."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(person.entity_id
                                                                                                                              ), modification_in_database=f'The person with entity_id {person.entity_id} updated new height: {person_db.height} to  {person.height}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {person.entity_id} updated height: {person_db.height} to {person.height}")
    except:
        print(
            f"The person with entity_id {person.entity_id} could not be update height: {person_db.height} to {person.height}")


def insert_updated_distinguishing_marks_info_change_log(person, person_db):
    """This is the function that adds the distinguishing marks change to the log table."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(person.entity_id
                                                                                                                              ), modification_in_database=f'The person with entity_id {person.entity_id} updated new distinguishing marks: {person_db.distinguishing_marks} to {person.distinguishing_marks}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {person.entity_id} updated distinguishing marks: {person_db.distinguishing_marks} to {person.distinguishing_marks}")
    except:
        print(
            f"The person with entity_id {person.entity_id} could not be update distinguishing marks: {person_db.distinguishing_marks} to {person.distinguishing_marks}")


def insert_updated_eyes_color_info_change_log(person, person_db):
    """This is the function that adds the eyes color change to the log table."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(person.entity_id
                                                                                                                              ), modification_in_database=f'The person with entity_id {person.entity_id} updated new eyes color: {person_db.eyes_color} to {person.eyes_color}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {person.entity_id} updated eyes color: {person_db.eyes_color} to {person.eyes_color}")
    except:
        print(
            f"The person with entity_id {person.entity_id} could not be update eyes color: {person_db.eyes_color} to {person.eyes_color}")


def insert_updated_hair_info_change_log(person, person_db):
    """This is the function that adds the hair change to the log table."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(person.entity_id
                                                                                                                              ), modification_in_database=f'The person with entity_id {person.entity_id} updated new hair: {person_db.hair} to {person.hair}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {person.entity_id} updated hair: {person_db.hair} to {person.hair}")
    except:
        print(
            f"The person with entity_id {person.entity_id} could not be update hair: {person_db.hair} to {person.hair}")


def insert_deleted_picture_info_change_log(picture_id, entity_id, bs64):
    """This is a function that adds the deleted image information to the log table."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(entity_id), modification_in_database=f"The person with entity_id {entity_id} deleted the picture. unique_picture_id: {picture_id}. base64: {bs64}", modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {entity_id} deleted the picture: {picture_id}.")

    except:
        print(
            f"The person with entity_id {entity_id} could not be insert to change log table the picture: {picture_id}")


def insert_deleted_arrest_warrant_info_change_log(issuing_country, charge, entity_id):
    """This is a function that adds the deleted arrest warrant information to the log table."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(entity_id
                                                                                                                              ), modification_in_database=f'The person with entity_id {entity_id} deleted the arrest warrant. issuing_country: {issuing_country}, charge: {charge}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {entity_id} deleted the arrest warrant. issuing_country: {issuing_country}, charge: {charge}")
    except:
        print(
            f"The person with entity_id {entity_id} could not be delete the arrest warrant. issuing_country: {issuing_country}, charge: {charge}")


def insert_deleted_nationality_info_change_log(data, entity_id):
    """This is a function that adds the deleted nationality information to the log table."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(entity_id
                                                                                                                              ), modification_in_database=f'The person with entity_id {entity_id} deleted the nationality: {data}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {entity_id} deleted the nationality: {data}")
    except:
        print(
            f"The person with entity_id {entity_id} could not be delete the nationality: {data}")


def insert_deleted_language_info_change_log(data, entity_id):
    """This is a function that adds the deleted language information to the log table."""
    stmt = (insert(Base.metadata.tables[ChangeLogInformation.__tablename__]).values(person_id=get_person_db_id_from_entity_id(entity_id
                                                                                                                              ), modification_in_database=f'The person with entity_id {entity_id} deleted the language: {data}', modification_date=datetime.datetime.now()))
    try:
        engine.connect().execute(stmt)
        print(
            f"The person with entity_id {entity_id} deleted the language: {data}")
    except:
        print(
            f"The person with entity_id {entity_id} could not be delete the language: {data}")


def set_active_person(entity_id):
    """This is the function that activates the person."""
    stmt = (update(Base.metadata.tables[PersonalInformation.__tablename__]).where(
        Base.metadata.tables[PersonalInformation.__tablename__].c.entity_id == entity_id).values(is_active=True))
    try:
        engine.connect().execute(stmt)
    except:
        print(
            f"People with entity_id {entity_id} could not be activated.")


def set_inactive_person(entity_id):
    """This is the function that activates the person."""
    stmt = (update(Base.metadata.tables[PersonalInformation.__tablename__]).where(
        Base.metadata.tables[PersonalInformation.__tablename__].c.entity_id == entity_id).values(is_active=False))
    try:
        engine.connect().execute(stmt)
        insert_inactive_person_change_log_table(entity_id)
    except:
        print(
            f"People with entity_id {entity_id} could not be inactivated.")


def check_language(person, person_db, person_db_id):
    if person.language:
        # request ile ??ekilen ki??inin dil bilgisi oldu??unda
        # when the requested person has information of the language
        if not person_db.language_db():
            # request ile ??ekilen ki??inin dil bilgisi veritaban??nda olmad??????nda
            # when the requested person's language information is not in the database
            insert_language_informations(
                person_db_id, person)
        else:
            for c in person_db.person_db_language_list():
                if not c in person.list_languages():
                    # ki??inin veritaban??ndaki konu??tu??u diller aras??nda request ile eklenecek diller aras??nda bulunmad??????ndaki ko??ul
                    # when the person's language information in the database does not have in the requested person's language information
                    delete_language(
                        c, person_db_id, person.entity_id)
            for d in person.list_languages():
                if not d in person_db.person_db_language_list():
                    # request'ten gelen dil bilgisi veritaban??nda yoksa:
                    # when the requested person's language information does not have in the person's language information in the database
                    insert_language_information(
                        d, person_db_id, person.entity_id)
    elif person_db.language_db():
        for c in person_db.person_db_language_list():
            delete_language(
                c, person_db_id, person.entity_id)


def check_nationality(person, person_db, person_db_id):
    if person.nationality:
        # request ile ??ekilen ki??inin uyruk bilgisi oldu??unda
        # when the requested person has information of the nationality
        if not person_db.nationality_db():
            # request ile ??ekilen ki??inin uyruk bilgisi veritaban??nda olmad??????nda
            # when the requested person's nationality information is not in the database
            insert_nationality_informations(
                person_db_id, person)
        else:
            for c in person_db.person_db_nationality_list():
                if not c in person.list_nationalities():
                    # ki??inin veritaban??ndaki uyruklar aras??nda request ile eklenecek uyruklar aras??nda bulunmad??????ndaki ko??ul
                    # when the person's nationality information in the database does not have in the requested person's nationality information
                    delete_nationality(
                        c, person_db_id, person.entity_id)
            for d in person.list_nationalities():
                if not d in person_db.person_db_nationality_list():
                    # request'ten gelen uyruk veritaban??nda yoksa:
                    # when the requested person's nationality information does not have in the person's nationality information in the database
                    insert_nationality_information(
                        d, person_db_id, person.entity_id)
    elif person_db.nationality_db():
        for c in person.list_nationalities():
            delete_nationality(
                c, person_db_id, person.entity_id)


def check_arrest_warrants(person, person_db, person_db_id):
    if person.arrest_warrants:
        # request ile ??ekilen ki??inin yakalama emir bilgisi oldu??unda
        # when the requested person has information of the arrest warrant
        if not person_db.arrest_warrants_db():
            # request ile ??ekilen ki??inin yakalama emir bilgisi veritaban??nda olmad??????nda
            # when the requested person's arrest warrant information is not in the database
            insert_arrest_warrants(person_db_id, person)
        else:
            for c in person_db.person_db_arrest_warrants_list():
                if not c in person.list_arrest_warrants():
                    # ki??inin veritaban??ndaki tutuklama emirleri aras??nda request ile eklenecek tutuklama emirleri aras??nda bulunmad??????ndaki ko??ul
                    # when the person's arrest warrant information in the database does not have in the requested person's arrest warrant information
                    delete_arrest_warrants(
                        c[0], c[1], person_db.person_db_id, person.entity_id)
            for d in person.list_arrest_warrants():
                if not d in person_db.person_db_arrest_warrants_list():
                    # request'ten gelen tutuklama emri veritaban??nda yoksa
                    # when the requested person's arrest warrant information does not have in the person's arrest warrant information in the database
                    insert_arrest_warrant(
                        d[0], d[1], d[2], person_db.person_db_id, person.entity_id)
    elif person_db.arrest_warrants_db():
        for c in person_db.person_db_arrest_warrants_list():
            delete_arrest_warrants(
                c[0], c[1], person_db.person_db_id, person.entity_id)


def check_pictures(person, person_db, person_db_id):
    if person.pictures:
        # request ile ??ekilen ki??inin resim bilgisi oldu??unda
        # when the requested person has information of the picture
        if not person_db.pictures_db():
            # request ile ??ekilen ki??inin resim bilgisi veritaban??nda olmad??????nda
            # when the requested person's picture information is not in the database
            insert_pictures(person_db_id, person)
        else:
            for c in person_db.person_db_pictures_list():
                if not c in person.list_pictures():
                    # ki??inin veritaban??ndaki resimler aras??nda request ile eklenecek resimler aras??nda bulunmad??????ndaki ko??ul
                    # when the person's picture information in the database does not have in the requested person's picture information
                    delete_picture(
                        c[0], person_db_id, person.entity_id)
            for d in person.list_pictures():
                if not d in person_db.person_db_pictures_list():
                    # request'ten gelen resim veritaban??nda yoksa
                    # when the requested person's picture information does not have in the person's picture information in the database
                    insert_picture(
                        d[0], d[1], person_db_id, person.entity_id)
    elif person_db.pictures_db():
        for c in person_db.person_db_pictures_list():
            delete_picture(
                c[0], person_db_id, person.entity_id)


def set_inactive_people(active_people_list, active_people_db_entities):
    for i in active_people_db_entities:
        if not i in active_people_list:
            set_inactive_person(i)
            # Veritaban??nda olup request ile al??nan ki??iler aras??nda olmayan ki??ileri is_active = False yapan k??s??m.
            # This is the condition that makes is_active = False for people who are in the database but are not among requested people
