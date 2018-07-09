import json
import time
import captcha
import requests as r

from bs4       import BeautifulSoup
from random    import choice, randint
from pathlib   import Path
from threading import Thread as thread

tempdata = json.loads (Path ('data.json').read_text (encoding='utf-8'))

comms = tempdata ['comms']
sids  = tempdata ['sids']


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

	def views (uid):
		try:
			page = r.get('https://m.vk.com/id{}'.format(uid))

			soup = BeautifulSoup(page.text, 'lxml')
			div  = soup.find('span', class_="item_views ")

			return (str(div).split('"v_views">')[1].split('</b>')[0])

		except:
			return 'None'

	while True:
		outmessage = '\n\n[{}]\n\n'.format (time.ctime (time.time ()))

		for account in accounts:
			outmessage += 'id: {} || status: {} || groups count: {} || views: {}\n'.format (account ['id'], status_check (account ['id']), groups_count (account), views (account ['id']))

		print (outmessage)

		time.sleep (35)


def way (access_token, proxies):
	def getfeed (a, s, count=10):
		feedparams = {
			'access_token': a [0],
			'version'     : '5.78',
			'filters'     : 'post',
			'count'       : count
		}

		feed = s.get ('https://api.vk.com/method/newsfeed.get', params=feedparams, proxies=a [1]).json () ['response']['items']

		return feed

	def createcomment (a, s, p, m):
		params = {
			'access_token': a [0],
			'version'     : '5.78',
			'owner_id'    : p [0],
			'post_id'     : p [1],
			'message'     : m [0],
			'sticker_id'  : m [1]
		}

		z = s.get ('https://api.vk.com/method/wall.createComment', params=params, proxies=a [1])

		if 'error' in z.json ():
			if z.json () ['error']['error_code'] == 14:
				print ('captcha')

				capkey = captcha.main (z.json () ['error']['captcha_img'])
				params.update ({'captcha_sid': z.json () ['error']['captcha_sid'], 'captcha_key': capkey})
				z = s.get ('https://api.vk.com/method/wall.createComment', params=params, proxies=a [1])

			elif z.json () ['error']['error_code'] == 213:
				print ('error: banned in the group, leaving it')

				params = {
					'group_id'    : -p [0], 
					'access_token': a [0],
					'version'     : '5.80'
				}

				print (s.get ('https://api.vk.com/method/groups.leave', params=params, proxies=a [1]).json ())

		print (z.json ())

	s = r.session ()
	a = [access_token, proxies]

	while True:
		feed = getfeed (a, s)

		for item in feed:
			p = [item ['source_id'], item ['post_id']]
			m = choice ([[None, choice (range (sids [0], sids [1]))], [choice (comms), None]])

			createcomment (a, s, p, m)

			time.sleep (randint (30, 90))

		time.sleep (250)


def main ():
	while True:
		try:
			accounts = json.loads (Path ('accounts.json').read_text (encoding='utf-8')) ['ready']
			for account in accounts:
				print ('start: account {}'.format (account ['id']))

				proxies = {
					'http': 'http://{}'.format (account ['proxy']),
					'https': 'https://{}'.format (account ['proxy'])
				}

				thread (target=way, args=(account ['access_token'], proxies)).start ()
				time.sleep (3)

			output (accounts)



		except:
			print ('BIG ERROR')
			time.sleep (5)


if __name__ == '__main__':
	main()