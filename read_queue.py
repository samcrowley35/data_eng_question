import requests
from pprint import pprint
import xmltodict
import json
import time
import psycopg2
from datetime import datetime, timezone
from cryptography.fernet import Fernet

key = Fernet.generate_key()
fernet = Fernet(key)

def mask_fields(device_id:str, ip:str):   
    enc_did = fernet.encrypt(device_id.encode())
    enc_ip = fernet.encrypt(ip.encode())
    return enc_did, enc_ip

def unmask_fields(masked_did:bytes, masked_ip:bytes):
    unmasked_did = fernet.decrypt(masked_did).decode()
    unmasked_ip = fernet.decrypt(masked_ip).decode()
    return unmasked_did, unmasked_ip

def insert_data(data:dict):
    conn = psycopg2.connect(database='postgres', host= 'localhost', user='postgres', password='postgres', port='5432')
    cursor = conn.cursor()

    # Create the user_logins table if it doesn't exist already
    exists = False
    try:
        cursor.execute("select exists(select * from information_schema.tables where table_name='user_logins')")
        exists = cursor.fetchone()[0]
    except psycopg2.Error as e:
        print(e)    
    if not exists:
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS user_logins(
            user_id varchar(128),
            device_type varchar(32),
            masked_ip varchar(256),
            masked_device_id varchar(256),
            locale varchar(32),
            app_version integer,
            create_date date
            );
            '''
        )    

    # Insert the data 
    try: 
        insert_query = (
            '''
            INSERT INTO user_logins(
            user_id,
            device_type,
            masked_ip,
            masked_device_id,
            locale,
            app_version,
            create_date
            ) VALUES(%s, %s, %s, %s, %s, %s, %s);
            '''
        )
        data_to_insert = (data['user_id'], data['device_type'], data['masked_ip'], data['masked_device_id'], data['locale'], data['app_version'], data['create_date'])
        cursor.execute(insert_query, data_to_insert)
        conn.commit()
        print('Row has been inserted')
    except (Exception, psycopg2.Error) as error:
        print('Insertion to postgres table failed with error: ' + str(error))
    finally:
        if conn: 
            cursor.close()
            conn.close()

def main():
    while(True): 
        # Read the messages from the sqs queue
        response = requests.get(
            url= "http://localhost:4566/000000000000/login-queue?Action=ReceiveMessage",
            headers={ 'Accept' : 'application/json' }
        )
        xml_dict = xmltodict.parse(response.content)
        login_data = xml_dict['ReceiveMessageResponse']['ReceiveMessageResult']['Message']['Body']
        login_dict = json.loads(login_data)

        # Mask the device_id and ip fields
        enc_did, enc_ip = mask_fields(login_dict['device_id'], login_dict['ip'])

        # Convert the app version to an int
        app_version_str = str(login_dict['app_version']).replace('.', '')
        app_version_int = int(app_version_str)

        # Insert data into postgres table
        data_to_insert = {
            'user_id': login_dict['user_id'],
            'device_type': login_dict['device_type'],
            'masked_ip': enc_ip,
            'masked_device_id': enc_did,
            'locale': login_dict['locale'],
            'app_version': app_version_int,
            'create_date': datetime.now(timezone.utc)
        }
        insert_data(data_to_insert)
        time.sleep(5)

if __name__ == "__main__":
    main()