import json
import os

REQUESTS_FOLDER_PATH = 'requests/'

SIGNUP_USER_FOLDER_NAME = 'sign_up_requests/'
SIGNUP_USER_JSON_FOLDER_PATH = REQUESTS_FOLDER_PATH + SIGNUP_USER_FOLDER_NAME

ORDER_REQUESTS_FOLDER_NAME = 'order_requests/'
ORDER_REQUESTS_FOLDER_PATH = REQUESTS_FOLDER_PATH + ORDER_REQUESTS_FOLDER_NAME

CONFIRMATION_FOLDER_PATH = 'response/'

CONFIRMATION_SIGNUP_FOLDER_NAME = 'signup_response/'
CONFIRMATION_SIGNUP_FOLDER_PATH = CONFIRMATION_FOLDER_PATH + CONFIRMATION_SIGNUP_FOLDER_NAME

CONFIRMATION_ORDER_FOLDER_NAME = 'order_response/'
CONFIRMATION_ORDER_FOLDER_PATH = CONFIRMATION_FOLDER_PATH + CONFIRMATION_ORDER_FOLDER_NAME
SIGN_UP_SUCCESS_EMAILS = []

def initialize():
	open("db.json","a+")	#create the database json if it is not present, a+ appending and reading
	if os.stat("db.json").st_size == 0:	#initialize
		temp = {}
		with open('db.json','w') as f:
			json.dump(temp, f)
	open("main_catalog.json","a+")	#create the database json if it is not present, a+ appending and reading
	if os.stat("main_catalog.json").st_size == 0:	#initialize
		temp = {}
		with open('main_catalog.json','w') as f:
			json.dump(temp, f)

 
def execute():
	with open('db.json','r') as db_file:
			db_file_data = db_file.read()
	loaded_db = json.loads(db_file_data)		#load the json db to a dict
	for filename in os.listdir(SIGNUP_USER_JSON_FOLDER_PATH):
		if filename[0] == '.':
			continue
		with open(SIGNUP_USER_JSON_FOLDER_PATH+filename,'r') as new_users_file:  	#open the new users json file
				new_users_data = new_users_file.read()
		data = json.loads(new_users_data)
   		response = process_signup(data, loaded_db)	#get response
   		os.remove(SIGNUP_USER_JSON_FOLDER_PATH+filename)
   		generate_confirmation(data, response, filename[:-5])	#generate confirmation file in json format


def append_info(user_dict, db):
	#format = {email:[bool_is_central,fname,lname,email,pwd1,pwd2]}; email is the key, for 0(1) retrieval
	temp = {user_dict['email']:
			[user_dict['fname'],user_dict['lname'],
			user_dict['email'],user_dict['password1'],user_dict['password2']]}
	db.update(temp)

	with open('db.json','w') as f:
		json.dump(db, f)

def process_signup(user_dict,db):
	user_email = user_dict['email']	#exception handling might be required if json_str is invalid
	if db.get(user_email) is None:
		append_info(user_dict,db)	#add to the database
		return 1
	return 0

def generate_confirmation(user, response, filename):
	res = 'SUCCESS' if response == 1 else 'FAIL'
	email = user['email']
	if response == 1:
		SIGN_UP_SUCCESS_EMAILS.append(email)
	temp = email +' ' + res 				#format : abc@xyz.com SUCCESS
	conf_data=[temp]
	temp_fname = CONFIRMATION_SIGNUP_FOLDER_PATH+ filename+'.json'
	with open(temp_fname,'w+') as f:
		json.dump(conf_data, f)
	write_delimiter(temp_fname)

def generate_order_confirmation(email, response, order_id, filename):
	res = 'SUCCESS' if response == 1 else 'FAIL'
	temp = email +' ' + str(order_id) + ' ' + res 				#format : abc@xyz.com SUCCESS
	conf_data=[temp]
	temp_fname = CONFIRMATION_ORDER_FOLDER_PATH+ filename+'.json'
	with open(temp_fname,'w+') as f:
		json.dump(conf_data, f)
	write_delimiter(temp_fname)

def process_order(order_details, catalog):
	for item in order_details['order']['cart']:
		wanted_qty = item['Quantity']
		print(wanted_qty)
		wanted_name = item['Name'].lower()
		instock_qty = catalog[wanted_name]['stock']
		if int(instock_qty) - int(wanted_qty) <0:
			return 0
		else:
			current = catalog[wanted_name]
			stock = {"stock": instock_qty - wanted_qty}
			temp = {wanted_name:stock}
			print(temp)
			catalog.update(temp)
	return 1


def fulfill_order():	#temp function
	# print("ORDER TEST")
	with open('main_catalog.json','r') as catalog_file:
		catalog_file_data = catalog_file.read()
	loaded_catalog = json.loads(catalog_file_data)
	for filename in os.listdir(ORDER_REQUESTS_FOLDER_PATH):
		if filename[0] == '.':
			continue
		with open(ORDER_REQUESTS_FOLDER_PATH+filename,'r') as new_users_file:  	#open the new users json file
				new_users_data = new_users_file.read()
		data = json.loads(new_users_data)
		email = data['email']
		if email not in SIGN_UP_SUCCESS_EMAILS:
			continue
		order_id = data['order']['id']
		response = process_order(data, loaded_catalog)
		if response == 1:
			with open('main_catalog.json','w') as catalog_writer:
				json.dump(loaded_catalog, catalog_writer)
			generate_order_confirmation(email, response, order_id, filename[:-5])
		elif response == 0:
			generate_order_confirmation(email, response, order_id, filename[:-5])

	

def write_delimiter(fname):
	with open(fname, 'a') as input:
		input.write("\n=====")
	input.close()

def sign_up():
	initialize()
	execute()
	print('k')

def check_requests():	#temp main function
	#returns a tuple with two digits, where 1st element refers to sign up requests and
	#the other element to order requests
	result = [0,0]
	for folder in os.listdir(REQUESTS_FOLDER_PATH):
		if folder[0] == '.':
			continue
		if len(os.listdir(REQUESTS_FOLDER_PATH+folder)) > 0:
			if folder == SIGNUP_USER_FOLDER_NAME[:-1]:		#slice since only folder name without '/' is needed
				result[0]+=1
			elif folder == ORDER_REQUESTS_FOLDER_NAME[:-1]:
				result[1]+=1
	return result


def main():
	response = check_requests()
	if response[0]>0:
		sign_up()
	if response[1]>0:
		fulfill_order()

main()

