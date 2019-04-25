CONFIRMATION_FOLDER_PATH = 'response/'

CONFIRMATION_SIGNUP_FOLDER_NAME = 'signup_response/'
CONFIRMATION_SIGNUP_FOLDER_PATH = CONFIRMATION_FOLDER_PATH + CONFIRMATION_SIGNUP_FOLDER_NAME

CONFIRMATION_ORDER_FOLDER_NAME = 'order_response/'
CONFIRMATION_ORDER_FOLDER_PATH = CONFIRMATION_FOLDER_PATH + CONFIRMATION_ORDER_FOLDER_NAME
FAIL = 'FAIL'
SUCCESS = 'SUCCESS'

import json 
import os

def update_pending_confirmation(local_db):
	for su_conf in os.listdir(CONFIRMATION_SIGNUP_FOLDER_PATH):
		if su_conf[0] == '.':
			continue
		print(su_conf)
		update_signup_c_pending(local_db, su_conf)
		os.remove(CONFIRMATION_SIGNUP_FOLDER_PATH+su_conf)

	for o_conf in os.listdir(CONFIRMATION_ORDER_FOLDER_PATH):
		if o_conf[0] == '.':
			continue
		print(o_conf)
		update_order_c_pending(local_db, o_conf)
		# os.remove(CONFIRMATION_ORDER_FOLDER_PATH+o_conf)

def update_signup_c_pending(local_db, filename):
	with open(CONFIRMATION_SIGNUP_FOLDER_PATH +filename,'r') as new_users_file:  	#open the new users json file
			new_users_data = new_users_file.read()
	data = json.loads(new_users_data)
	temp = data[0].split()
	email = temp[0]
	status = temp[1]
	#write to the buffer
	current = local_db.get(email)
	if status == FAIL:
		current["pc_signup"] = 0
	elif status == SUCCESS:
		current["pc_signup"] = 1
	temp = {email: current}
	local_db.update(temp)


def update_order_c_pending(local_db, filename):
	with open(CONFIRMATION_ORDER_FOLDER_PATH +filename,'r') as orders_c_file:  	#open the new users json file
			ord_c_data = orders_c_file.read()
	data = json.loads(ord_c_data)
	temp = data[0].split()
	email = temp[0]
	orderid = temp[1]
	status = temp[2]
	
	#write to the file
	current = local_db.get(email)
	current["pc_order"].append((orderid, status))
	temp = {email: current}
	local_db.update(temp)


def main():
	with open('signup_central.json','r') as local_db_file:  	#open the new users json file
			local_db_data = local_db_file.read()
	loaded_local_db = json.loads(local_db_data)
	update_pending_confirmation(loaded_local_db)
	with open('signup_central.json','w') as f:
		json.dump(loaded_local_db, f)

main()

