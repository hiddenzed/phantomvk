from pathlib   import Path
from threading import Thread as thread
from bs4       import BeautifulSoup

import time
import json
import random
import captcha
import requests as r



def way (access_token, proxies):
	closed_pubs = []
	open_pubs   = []

	with open ('closed.txt', 'r') as file:
		for line in file:
			closed_pubs.append (line.strip ())

	with open ('open.txt', 'r') as file:
		for line in file:
			open_pubs.append (line.strip ())

	random.shuffle (closed_pubs)
	random.shuffle (open_pubs)    


	base = closed_pubs [0:18] + open_pubs [0:75]
	random.shuffle (base)

	s = r.session()

	for pub in base:
		joinparams = {
			'access_token': access_token,
			'version'     : '5.80',
			'group_id'    : pub}
		
		try:
			result = s.get('https://api.vk.com/method/groups.join', params=joinparams, proxies=proxies).json()

		except:
			sleep (4)

		if 'error' in result:
			if result ['error']['error_code'] == 14:
				print ('error: captcha needed')

				capkey = captcha.main (result ['error']['captcha_img'])

				joincaptchaparams = {
					'access_token': access_token,
					'version'     : '5.80',
					'group_id'    : line.strip (),
					'captcha_sid' : result ['error']['captcha_sid'],
					'captcha_key' : capkey}

				s.get ('https://api.vk.com/method/groups.join', params=joincaptchaparams, proxies=proxies).json ()
		
		time.sleep (random.randint (7, 20))

def output (accounts):
	def status_check (uid):
		soup = BeautifulSoup (r.get ('https://m.vk.com/id{}'.format(uid)).text, 'lxml')

		q = soup.find('div', class_="owner_panel profile_panel").find('img', class_="pp_img")['src']

		if '/images/deactivated_100.png' in q:
			return 'banned'

		else:
			return 'active'

	def groups_count (account):
		access_token = account ['access_token']

		proxies = {
			'http': 'http://{}'.format (account ['proxy']),
			'https': 'https://{}'.format (account ['proxy'])
		}

		q = r.get ('https://api.vk.com/method/groups.get', params={'access_token': access_token, 'version': '5.80', 'extended': 1}, proxies=proxies).json ()

		try:
			return str (q ['response'][0])

		except:
			return 'None'

	while True:
		outmessage = '\n\n[{}]\n\n'.format (time.ctime (time.time ()))

		for account in accounts:
			outmessage += 'id: {} || status: {} || groups count: {}\n'.format (account ['id'], status_check (account ['id']), groups_count (account))

		print (outmessage)

		time.sleep (35)


def main ():
	accounts = json.loads (Path ('accounts.json').read_text (encoding='utf-8')) ['almost_ready']

	for account in accounts:
		print ('account with id {} is starting'.format (account ['id']))

		proxies = {
			"http"  :"http://{}".format (account ['proxy']),
			"https" :"https://{}".format (account ['proxy'])}

		thread  (target=way, args= (account ['access_token'], proxies)).start ()

	output (accounts)


if __name__ == '__main__':
	main()