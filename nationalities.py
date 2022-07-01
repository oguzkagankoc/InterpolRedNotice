import requests
from bs4 import BeautifulSoup
from classes import get_request

# Maximum 160 people can be shown.

nationals_with_less_than_160_results = []
nationals_with_more_than_160_results = []
nationals_with_no_results = []
for n in [i for i in BeautifulSoup(requests.get("https://www.interpol.int/How-we-work/Notices/View-Red-Notices").content, "html.parser").find(id='nationality').find_all("option")[1:]]:
    response = get_request(
        f"https://ws-public.interpol.int/notices/v1/red?nationality={n.get('value')}&resultPerPage=20&page=1")
    if response.json()['total'] > 160:
        # More than 160 results in nationality filtering.
        nationals_with_more_than_160_results.append(
            [n.get('value'), n.text, response.json()['total']])
    elif response.json()['total'] == 0:
        # No one results in nationality filtering.
        nationals_with_no_results.append(
            [n.get('value'), n.text, response.json()['total']])
    else:
        # Less than 160 results in nationality filtering.
        nationals_with_less_than_160_results.append(
            [n.get('value'), n.text, response.json()['total']])
print(nationals_with_more_than_160_results)
russian_nationality = []
for z in range(1, 110):
    response = get_request(
        f"https://ws-public.interpol.int/notices/v1/red?nationality=RU&ageMin={z}&ageMax={z}&resultPerPage=20&page=1")
    if response.json()['total'] == 0:
        continue
    elif response.json()['total'] > 159:
        russian_nationality.append((int(response.json()['total']), z))
print(russian_nationality)
nationals_with_less_than_160_results.sort(key=lambda x: x[2], reverse=True)
print(nationals_with_less_than_160_results)
# Despite filtering by nationality and age (30, 31, 32, 33, 34), we can't see all of them as it returns more than 160 results.
