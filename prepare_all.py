import json
import requests          as r
import prepare_functions as pf

from pathlib import Path

tempdata = json.loads (Path ('data.json').read_text (encoding='utf-8'))

headers = tempdata ['headers']
posts   = tempdata ['reposts']


def write_json (uid, name, login, paswd, proxy, status, access_token):
	newobject = {
		"id"          : uid,
		"link"        : 'https://vk.com/id{}'.format(uid),
		"name"        : name,
		"login"       : login,
		"pass"        : paswd,
		"proxy"       : proxy,
		"status"      : status,
		"access_token": access_token}

	myjson = json.loads (Path ('accounts.json').read_text (encoding='utf-8'))

	myjson ['almost_ready'].append (newobject)

	with open ('accounts.json', 'w') as file:
		json.dump (myjson, file, indent=2, ensure_ascii=False)


def main ():
	accounts   = []
	allproxies = []

	with open ('accs.txt', 'r') as file:
		for line in file:
			accounts.append (line.strip ())

	with open ('proxies.txt', 'r') as file:
		for line in file:
			allproxies.append (line.strip ())

	# checking proxies count
	if len (accounts) > len (allproxies):
		print ('error: proxies is not enough')

	else:
		for i in range (len (accounts)):
			login = accounts [i].split (':') [0]
			paswd = accounts [i].split (':') [1]
			proxy = allproxies [i] 

			proxies = {
				'http': 'http://{}'.format (proxy),
				'https': 'https://{}'.format (proxy)
			}

			# getting access token
			access_token = pf.get_access_token (login, paswd, proxies, headers)

			if 'blocked' in access_token:
				print ('error: account is blocked')

				with open ('blocked.txt', 'a') as file:
					file.write (accounts [i] + '\n')

			elif access_token == 'https://m.vk.com/':
				print ('error: can\'t get access token, try to use another proxy')

				with open ('error_accounts.txt', 'a') as file:
					file.write (accounts [i] + '\n')

			else:
				print ('done: access token successfully recieved')

				uid          = r.get('https://api.vk.com/method/users.get', params={'access_token': access_token, 'v': '5.80'}, proxies=proxies).json()['response'][0]['id']
				name         = r.get('https://api.vk.com/method/users.get', params={'access_token': access_token, 'v': '5.80'}, proxies=proxies).json()['response'][0]['first_name']
				status       = '0'

				write_json (uid, name, login, paswd, proxy, status, access_token)

				pf.avatar_post      (access_token, proxies)
				pf.repost           (access_token, proxies, posts)
				pf.set_privacy      (proxies, login, paswd, headers)

				print ('done: account is almost ready')


if __name__ == '__main__':
	main ()