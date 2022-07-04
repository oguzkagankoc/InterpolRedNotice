import interpol_functions
from classes import get_request, CriminalDb, Criminal
from flask import Flask, jsonify

interpol_functions.create_pictures_folder()
active_people_list = []
response = get_request(
    f"https://ws-public.interpol.int/notices/v1/red?nationality=US&resultPerPage=20&page=1")
max_page = int(response.json()['_links']['last']['href'][-1])
for i in range(1, max_page + 1):
    url = f"https://ws-public.interpol.int/notices/v1/red?nationality=US&resultPerPage=20&page={i}"
    response = get_request(url)
    people_on_the_page = len(response.json()['_embedded']['notices'])
    print(f"Page {i}")
    for j in range(0, people_on_the_page):
        person_url = response.json(
        )['_embedded']['notices'][j]['_links']['self']['href']
        response_person_main = get_request(person_url)
        person = Criminal(response_person_main)
        active_people_list.append(person.entity_id)
        # This is where the information is checked when the entity_id of the requested person is in the database.
        # request ile çekilen kişinin entity_id'si veritabanında olduğunda bilgilerinin kontrol edildiği yer.
        if any(interpol_functions.get_person_db_personal_information(person.entity_id)):
            person_db = CriminalDb(person.entity_id)
            interpol_functions.set_active_person(person.entity_id)
            if not person.forename == person_db.forename:
                interpol_functions.update_forename(person, person_db)
            if not person.family_name == person_db.family_name:
                interpol_functions.update_family_name(person, person_db)
            if not person.gender == person_db.gender:
                interpol_functions.update_gender(person, person_db)
            if not person.date_of_birth == person_db.date_of_birth:
                interpol_functions.update_date_of_birth(person, person_db)
            if not person.place_of_birth == person_db.place_of_birth:
                interpol_functions.update_place_of_birth(person, person_db)
            if not person.country_of_birth == person_db.country_of_birth:
                interpol_functions.update_country_of_birth(person, person_db)
            if not person.weight == person_db.weight:
                interpol_functions.update_weight(person, person_db)
            if not person.height == person_db.height:
                interpol_functions.update_height(person, person_db)
            if not person.distinguishing_marks == person_db.distinguishing_marks:
                interpol_functions.update_distinguishing_marks(
                    person, person_db)
            if not person.eyes_color == person_db.eyes_color:
                interpol_functions.update_eyes_color(person, person_db)
            if not person.hair == person_db.hair:
                interpol_functions.update_hair(person, person_db)
        else:   # request ile çekilen kişinin entity_id'si veritabanında yoksa bilgilerin veritabanına kaydedildiği yer.
            # This is where the information is saved in the database, if the entity_id of the requested person is not in the database.
            interpol_functions.insert_personal_informations(person)
            person_db = CriminalDb(person.entity_id)
        person_db_id = interpol_functions.get_person_db_id_from_entity_id(
            person.entity_id)
        language_db = person_db.language_db()
        if person.language:
            # request ile çekilen kişinin dil bilgisi olduğunda
            # when the requested person has information of the language
            if not language_db:
                # request ile çekilen kişinin dil bilgisi veritabanında olmadığında
                # when the requested person's language information is not in the database
                interpol_functions.insert_language_informations(
                    person_db_id, person)
            else:
                person_db_language_list = person_db.person_db_language_list()
                person_language_list = person.list_languages()
                for c in person_db_language_list:
                    if not c in person_language_list:
                        # kişinin veritabanındaki konuştuğu diller arasında request ile eklenecek diller arasında bulunmadığındaki koşul
                        # when the person's language information in the database does not have in the requested person's language information
                        interpol_functions.delete_language(
                            c, person_db_id, person.entity_id)
                for d in person_language_list:
                    if not d in person_db_language_list:
                        # request'ten gelen dil bilgisi veritabanında yoksa:
                        # when the requested person's language information does not have in the person's language information in the database
                        interpol_functions.insert_language_information(
                            d, person_db_id, person.entity_id)
        nationality_db = person_db.nationality_db()
        if person.nationality:
            # request ile çekilen kişinin uyruk bilgisi olduğunda
            # when the requested person has information of the nationality
            if not nationality_db:
                # request ile çekilen kişinin uyruk bilgisi veritabanında olmadığında
                # when the requested person's nationality information is not in the database
                interpol_functions.insert_nationality_informations(
                    person_db_id, person)
            else:
                person_db_nationality_list = person_db.person_db_nationality_list()
                person_nationality_list = person.list_nationalities()
                for c in person_db_nationality_list:
                    if not c in person_nationality_list:
                        # kişinin veritabanındaki uyruklar arasında request ile eklenecek uyruklar arasında bulunmadığındaki koşul
                        # when the person's nationality information in the database does not have in the requested person's nationality information
                        interpol_functions.delete_nationality(
                            c, person_db_id, person.entity_id)
                for d in person_nationality_list:
                    if not d in person_db_nationality_list:
                        # request'ten gelen uyruk veritabanında yoksa:
                        # when the requested person's nationality information does not have in the person's nationality information in the database
                        interpol_functions.insert_nationality_information(
                            d, person_db_id, person.entity_id)
        arrest_warrants_db = person_db.arrest_warrants_db()
        if person.arrest_warrants:
            # request ile çekilen kişinin yakalama emir bilgisi olduğunda
            # when the requested person has information of the arrest warrant
            if not arrest_warrants_db:
                # request ile çekilen kişinin yakalama emir bilgisi veritabanında olmadığında
                # when the requested person's arrest warrant information is not in the database
                interpol_functions.insert_arrest_warrants(person_db_id, person)
            else:
                person_db_arrest_warrants_list = person_db.person_db_arrest_warrants_list()
                person_arrest_warrants_list = person.list_arrest_warrants()
                for c in person_db_arrest_warrants_list:
                    if not c in person_arrest_warrants_list:
                        # kişinin veritabanındaki tutuklama emirleri arasında request ile eklenecek tutuklama emirleri arasında bulunmadığındaki koşul
                        # when the person's arrest warrant information in the database does not have in the requested person's arrest warrant information
                        interpol_functions.delete_arrest_warrants(
                            c[0], c[1], person_db.person_db_id, person.entity_id)
                for d in person_arrest_warrants_list:
                    if not d in person_db_arrest_warrants_list:
                        # request'ten gelen tutuklama emri veritabanında yoksa
                        # when the requested person's arrest warrant information does not have in the person's arrest warrant information in the database
                        interpol_functions.insert_arrest_warrant(
                            d[0], d[1], d[2], person_db.person_db_id, person.entity_id)
        pictures_db = person_db.pictures_db()
        if person.pictures:
            # request ile çekilen kişinin resim bilgisi olduğunda
            # when the requested person has information of the picture
            if not pictures_db:
                # request ile çekilen kişinin resim bilgisi veritabanında olmadığında
                # when the requested person's picture information is not in the database
                interpol_functions.insert_pictures(person_db_id, person)
            else:
                person_db_pictures_list = person_db.person_db_pictures_list()
                person_pictures_list = person.list_pictures()
                for c in person_db_pictures_list:
                    if not c in person_pictures_list:
                        # kişinin veritabanındaki resimler arasında request ile eklenecek resimler arasında bulunmadığındaki koşul
                        # when the person's picture information in the database does not have in the requested person's picture information
                        interpol_functions.delete_picture(
                            c[0], person_db_id, person.entity_id)
                for d in person_pictures_list:
                    if not d in person_db_pictures_list:
                        # request'ten gelen resim veritabanında yoksa
                        # when the requested person's picture information does not have in the person's picture information in the database
                        interpol_functions.insert_picture(
                            d[0], d[1], person_db_id, person.entity_id)
active_people_db_entities = interpol_functions.get_active_person_db_entities()
for i in active_people_db_entities:
    if not i in active_people_list:
        interpol_functions.set_inactive_person(i)
        # Veritabanında olup request ile alınan kişiler arasında olmayan kişileri is_active = False yapan kısım.
        # This is the condition that makes is_active = False for people who are in the database but are not among requested people
interpol_functions.session.close_all()

total_number_of_inactive_people_db = interpol_functions.get_inactive_person_db_count()
total_number_of_active_people_db = interpol_functions.get_active_person_db_count()
total_number_of_people_db = interpol_functions.get_total_person_db_count()

app = Flask(__name__)


@app.route("/page/<int:page_num>")          
def criminals(page_num):
    # The place that shows everyone in the database, starting at this address "http://127.0.0.1:5000/page/1", by paginating them 20 each.
    total_person_per_page = interpol_functions.page_return_db(page_num)
    if not len(total_person_per_page) == 0:

        return jsonify(interpol_functions.get_people_db_to_api(total_person_per_page, total_number_of_active_people_db, total_number_of_inactive_people_db, page_num, total_number_of_people_db)), 200
    else:

        return '<center><font size="22">Error!</font></center>', 400


@app.route("/active/page/<int:page_num>")
def active_criminals(page_num):
    # The place that shows active people in the database, starting at this address "http://127.0.0.1:5000/active/page/1", by paginating them 20 each.
    total_active_person_per_page = interpol_functions.page_return_db_active(
        page_num)
    if not len(total_active_person_per_page) == 0:

        return jsonify(interpol_functions.get_people_db_to_api(total_active_person_per_page, total_number_of_active_people_db, total_number_of_inactive_people_db, page_num, total_number_of_active_people_db)), 200
    else:

        return '<center><font size="22">Error!</font></center>', 400


@app.route("/id/<int:person_id>")
def criminals_id(person_id):
    # The place that shows everyone in the database one by one, starting with the id address "http://127.0.0.1:5000/id/1".
    criminal = interpol_functions.get_one_person_from_person_id(person_id)
    if criminal:

        return jsonify(criminal), 200
    else:

        return '<center><font size="22">Error!</font></center>', 400


app.run()
