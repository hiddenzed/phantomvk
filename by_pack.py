import json
from pathlib import Path
import prepare_functions


def write_json (account, promopost):
	account ['status'] = '1'
	account.update ({'promopost': promopost})

	myjson = json.loads (Path ('accounts.json').read_text (encoding='utf-8'))

	myjson ['ready'].append (account)

	with open ('accounts.json', 'w') as file:
		json.dump (myjson, file, indent=2, ensure_ascii=False)


def main ():
	accounts = json.loads (Path ('accounts.json').read_text (encoding='utf-8')) ['almost_ready']

	if len (accounts) % 5 != 0:
		pack_count = int (len (accounts) // 5 + 1)

	else:
		pack_count = int (len (accounts) / 5)

	for i in range (pack_count):
		pack = accounts [ i*5 : (i + 1)*5]

		promolink = input ('input promolink with https://\n')


		data    = json.loads (Path ('data.json').read_text(encoding='utf-8'))
		message = data ['message1'] + promolink + data ['message2']

		access_token = pack [0]['access_token']
		proxy        = pack [0]['proxy']

		proxies = {
			'http': 'http://{}'.format (proxy),
			'https': 'https://{}'.format (proxy)}

		pub_id = prepare_functions.create_pub (access_token, proxies)

		prepare_functions.pubfill (pub_id, access_token, proxies)
		prepare_functions.pubpost (pub_id, access_token, proxies)

		promopost = 'wall-{}_{}'.format (pub_id, prepare_functions.promopost (pub_id, access_token, proxies, message, promolink))

		for acc in pack:
			access_token = acc ['access_token']
			proxy = acc ['proxy']

			proxies = {
				'http': 'http://{}'.format (proxy),
				'https': 'https://{}'.format (proxy)}

			prepare_functions.repost (access_token, proxies, [promopost])

			write_json (acc, promopost)



if __name__ == '__main__':
	main()