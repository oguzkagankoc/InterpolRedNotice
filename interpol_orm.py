import interpol_functions
from classes import get_request, CriminalDb, Criminal
from flask import Flask, jsonify

interpol_functions.create_pictures_folder()
active_people_list = []
response = get_request(
    f"https://ws-public.interpol.int/notices/v1/red?nationality=PE&resultPerPage=20&page=1")
max_page = int(response.json()['_links']['last']['href'][-1])
for i in range(1, max_page + 1):
    url = f"https://ws-public.interpol.int/notices/v1/red?nationality=PE&resultPerPage=20&page={i}"
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
        interpol_functions.check_language(person, person_db, person_db_id)
        interpol_functions.check_nationality(person, person_db, person_db_id)
        interpol_functions.check_arrest_warrants(person, person_db, person_db_id)
        interpol_functions.check_pictures(person, person_db, person_db_id)
active_people_db_entities = interpol_functions.get_active_person_db_entities()
interpol_functions.set_inactive_people(
    active_people_list, active_people_db_entities)
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
