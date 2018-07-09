from selenium import webdriver
from random   import choice, shuffle
from bs4      import BeautifulSoup

import requests
import lxml.html
import os
import time



def get_access_token (login, paswd, proxies, headers):
	s = requests.session()
	login_page = s.get('https://m.vk.com/login', proxies=proxies, headers=headers)

	parsed_login_page = lxml.html.fromstring(login_page.content)
	form = parsed_login_page.forms[0]

	form.fields['email'] = login
	form.fields['pass']  = paswd

	auth = s.post(form.action, data=form.form_values(), proxies=proxies, headers=headers)

	params = {
		'client_id'     : '4083558',
		'scope'         : 'friends,photos,audio,video,docs,notes,pages,status,offers,questions,wall,groups,messages,notifications,stats,ads,market,offline',
		'redirect_uri'  : 'https://api.vk.com/blank.html',
		'display'       : 'wap',
		'v'             : '5.80',
		'response_type' : 'token',
		'revoke'        : 0
	}

	data = s.get('https://oauth.vk.com/authorize', params=params, proxies=proxies, headers=headers)

	try:
		toked = lxml.html.fromstring(data.content)
		form = toked.forms[0]

		data = s.post(form.action, proxies=proxies)
	except:
		pass

	try:
		access_token = data.url.split('access_token=')[1].split('&expires')[0]

	except:
		access_token = data.url

	return access_token


def set_mail_privacy (login, paswd, proxy):
	proxyIp   = proxy.split ('@') [1]
	proxyAuth = proxy.split ('@') [0]

	service_args = [
		'--proxy={}'.format (proxyIp),
		'--proxy-auth={}'.format (proxyAuth)
	]

	b = webdriver.PhantomJS (service_args=service_args)

	b.get ('https://m.vk.com/login')

	b.find_element_by_name ('email').send_keys (login)
	b.find_element_by_name ('pass').send_keys (paswd)

	b.find_element_by_xpath ('/html/body/div[1]/div[2]/div[2]/div/div[2]/div[2]/div/form/div[1]/input').click ()

	b.get ('https://m.vk.com/settings?act=privacy&privacy_edit=mail_send')

	try:

		b.find_element_by_xpath ('/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div[1]/div[2]/form/label[2]/div[2]').click ()
		b.find_element_by_class_name ('Btn').click ()

		print ('mail privacy set')

	except:

		print ('error while mail privacy setting')

	b.close ()


def set_privacy (proxies, login, paswd, headers):
	s    = requests.session ()
	form = lxml.html.fromstring(s.get ('https://m.vk.com/login', headers=headers, proxies=proxies).content).forms [0]

	form.fields ['email'] = login
	form.fields ['pass']  = paswd

	response = s.post(form.action, data=form.form_values (), proxies=proxies)

	def set_one (url):
		form = lxml.html.fromstring (s.get (url, headers=headers, proxies=proxies).content).forms [0]

		form.fields['val'] = '3'

		s.post('https://m.vk.com/' + form.action, headers=headers, proxies=proxies, data=form.form_values ())

	set_one ('https://m.vk.com/settings?act=privacy&privacy_edit=groups')
	set_one ('https://m.vk.com/settings?act=privacy&privacy_edit=status_replies')
	set_one ('https://m.vk.com/settings?act=privacy&privacy_edit=mail_send')

	get_free_stickers (s)


def avatar_post (access_token, proxies):
	s = requests.session ()

	files = {'file': open('avatars/' + choice(os.listdir('avatars/')), 'rb')}

	params = s.post (s.get ('https://api.vk.com/method/photos.getOwnerPhotoUploadServer', params={'access_token': access_token, 'version': '5.80'}, proxies=proxies).json()['response']['upload_url'], files=files, proxies=proxies).json()

	params.update({'version': '5.80', 'access_token': access_token})


	print (s.get ('https://api.vk.com/method/photos.saveOwnerPhoto', params=params, proxies=proxies).json())


def repost (access_token, proxies, posts):
	shuffle(posts)
	s = requests.session ()

	for post in posts:

		params = {
			'access_token': access_token,
			'version'     : '5.80',
			'object'      : post
		}

		resp = s.get('https://api.vk.com/method/wall.repost', params=params, proxies=proxies).json()

		try:
			print (resp ['response'])

		except:
			print (resp)

		time.sleep(2)


def delete_all_photos ():
	s = requests.session ()
	# getting all photos
	params = {
		'access_token': access_token,
		'v'           : '5.80',
		'count'       : 200,
	}

	all_photos = s.get ('https://api.vk.com/method/photos.getAll', params=params, proxies=proxies).json () ['response']['items']

	# deleting all photos
	for item in all_photos:
		try:
			params = {
				'access_token' : access_token,
				'v'            : '5.80',
				'owner_id'     : item ['owner_id'],
				'photo_id'     : item ['id']
			}

			print (s.get ('https://api.vk.com/method/photos.delete', params=params, proxies=proxies).json ())

			time.sleep (1)

		except:
			print ('error while deleting photo')


def delete_all_friends (access_token, proxies):
	s = requests.session ()
	ids = s.get ('https://api.vk.com/method/friends.get', params={'access_token': access_token, 'v': '5.80'}, proxies=proxies).json () ['response']['items']

	# deleting all friends
	for friend in ids:

		params = {
			'access_token': access_token,
			'v'           : '5.80',
			'user_id'     : friend
		}

		print (s.get ('https://api.vk.com/method/friends.delete', params=params, proxies=proxies).json ())

		time.sleep (0.3)

	# set all requests canceled
	print (s.get (url + 'friends.deleteAllRequests', params={'access_token': access_token, 'v': '5.80'}, proxies=proxies).json ())


def get_free_stickers (s):
	# try to get stickers
	stickerLinks = [
		'https://m.vk.com/stickers?stickers_id=1&tab=free',
		'https://m.vk.com/stickers?stickers_id=2&tab=free',
		'https://m.vk.com/stickers?stickers_id=4&tab=free',
		'https://m.vk.com/stickers?stickers_id=75&tab=free',
		'https://m.vk.com/stickers?stickers_id=108&tab=free',
		'https://m.vk.com/stickers?stickers_id=139&tab=free',
		'https://m.vk.com/stickers?stickers_id=148&tab=free']

	for url in stickerLinks:
		data = s.get (url)

		try:
			soup = BeautifulSoup (data.content, 'html.parser')
			q = soup.find ('a', class_="button wide_button sp_buy_str").get ('href')

			s.get ('https://m.vk.com/' + str (q))

		except:
			print ('error while stickers gettig')


def change_sex_and_name ():
	sex = r.get ('https://api.vk.com/method/account.getProfileInfo', params=params, proxies=proxies).json () ['response']['sex']

	# if sex == 2:
	# 	import data

	# 	names      = data.names
	# 	last_names = data.last_names

	# 	params = {
	# 		'access_token'     : access_token,
	# 		'v'                : '5.48',
	# 		'first_name'       : choice (names),
	# 		'last_name'        : choice (last_names),
	# 		'sex'              : 1,
	# 		'bdate_visibility' : 0
	# 	}

	# 	print (r.get ('https://api.vk.com/method/account.saveProfileInfo', params=params, proxies=proxies).json ())

def create_pub(access_token, proxies=None):
	create_pub_params = {
		'title'          : 'Настенька',
		'type'           : 'public',
		'public_category': 1,
		'subtype'        : 1,
		'version'        : '5.80',
		'access_token'   : access_token
	}

	createpubanswer = requests.get('https://api.vk.com/method/groups.create', params=create_pub_params, proxies=proxies).json()

	if 'error' in createpubanswer:

		if createpubanswer['error']['error_code'] == 14:

			print ('captcha needed')

			import captcha as cap

			capkey = cap.main(createpubanswer['error']['captcha_img'])
			create_pub_params.update({'captcha_sid' : createpubanswer['error']['captcha_sid'],'captcha_key' : capkey})
			
			createpubanswer = requests.get('https://api.vk.com/method/groups.create', params=create_pub_params, proxies=proxies).json()

		else:
			print ('unknown error')
			print (createpubanswer)

	pubid = createpubanswer['response']['gid']
	print ('pub created, link: https://vk.com/club{}'.format(pubid))

	return pubid

def pubfill(pubid, access_token, proxies=None):
	editpubparams = {
		'contacts'    : 0,
		'wall'        : 0,
		'audio'       : 0,
		'video'       : 3,
		'photos'      : 0,
		'topics'      : 0,
		'group_id'    : pubid,
		'access_token': access_token,
		'version': '5.75'
	}

	link = 'https://api.vk.com/method/'

	requests.get(link + 'groups.edit', params=editpubparams, proxies=proxies).json()
	print ('pub is edited')


	pubavatargeturlparams = {
		'owner_id'     : -pubid,
		'access_token' : access_token,
		'version'      : '5.80'
	}

	url = requests.get(link + 'photos.getOwnerPhotoUploadServer', params=pubavatargeturlparams, proxies=proxies).json()['response']['upload_url']

	files = {'file': open('photos/' + choice(os.listdir('photos/')), 'rb')}
	q1 = requests.post(url, files=files).json()
	q1.update({'version': '5.80', 'access_token': access_token})


	requests.get(link + 'photos.saveOwnerPhoto', params=q1, proxies=proxies).json()
	print ('pub is ready')

def pubpost (pubid, access_token, proxies=None, count=2):
	for i in range (0, count):
		link = 'https://api.vk.com/method/'

		url = requests.get(link + 'photos.getWallUploadServer', params={'access_token': access_token, 'version': '5.80', 'group_id': pubid}, proxies=proxies).json()['response']['upload_url']
		files = {'file': open('photos/' + choice(os.listdir('photos/')), 'rb')}
		photoload = requests.post(url, files=files, proxies=proxies).json()

		wallsaveparams = {
			'access_token' : access_token,
			'version'      : '5.80',
			'group_id'     : pubid,
			'photo'        : photoload['photo'],
			'server'       : photoload['server'],
			'hash'         : photoload['hash']
			}

		photo = requests.get(link + 'photos.saveWallPhoto', params=wallsaveparams, proxies=proxies).json()['response'][0]['id']

		postparams = {
			'owner_id'     : -pubid,
			'access_token' : access_token,
			'version'      : '5.80',
			'attachments'  : photo
		}

		answertopost = requests.post(link + 'wall.post', params=postparams, proxies=proxies)

		print (answertopost.json())

def promopost (pubid, access_token, proxies, message, promolink):
	link = 'https://api.vk.com/method/'

	url       = requests.get(link + 'photos.getWallUploadServer', params={'access_token': access_token, 'version': '5.80', 'group_id': pubid}, proxies=proxies).json()['response']['upload_url']
	files     = {'file': open('promo_photos/' + choice(os.listdir('promo_photos/')), 'rb')}
	photoload = requests.post(url, files=files, proxies=proxies).json()

	wallsaveparams = {
		'access_token' : access_token,
		'version'      : '5.80',
		'group_id'     : pubid,
		'photo'        : photoload['photo'],
		'server'       : photoload['server'],
		'hash'         : photoload['hash']
		}

	photo = requests.get(link + 'photos.saveWallPhoto', params=wallsaveparams, proxies=proxies).json()['response'][0]['id']

	postparams = {
		'owner_id'     : -pubid,
		'message'      : message,
		'access_token' : access_token,
		'version'      : '5.80',
		'attachments'  : photo + ',' + promolink
	}

	answertopost = requests.post (link + 'wall.post', params=postparams, proxies=proxies).json ()

	try:
		post_id = answertopost ['response']['post_id']
		print ('promopost added')
		return post_id

	except:
		print ('REALLY BIG ERROR WHILE PROMO POST ADDING AAAAAAA')