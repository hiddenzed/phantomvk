import json
import requests as r

from bs4     import BeautifulSoup
from pathlib import Path


def main ():
	accounts = json.loads (Path ('accounts.json').read_text (encoding='utf-8')) ['ready']

	ready = []
	banned = []

	for account in accounts:
		soup = BeautifulSoup (r.get ('https://m.vk.com/id{}'.format(account ['id'])).text, 'lxml')

		q = soup.find('div', class_="owner_panel profile_panel").find('img', class_="pp_img")['src']

		if '/images/deactivated_100.png' in q:
			banned.append (account)

		else:
			ready.append (account)

	almost_ready = json.loads (Path ('accounts.json').read_text (encoding='utf-8')) ['almost_ready']

	newjson = {
		'ready': ready,
		'almost_ready': almost_ready,
		'banned': banned
	}

	with open ('accounts.json', 'w') as file:
		json.dump (newjson, file, indent=2, ensure_ascii=False)


if __name__ == '__main__':
	main()