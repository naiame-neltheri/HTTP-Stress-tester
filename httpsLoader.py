from logging import exception
from requests.models import MissingSchema
import urllib3, time
import requests, sys
import argparse, threading
from mysql.connector import pooling
import ctypes
libgcc_s = ctypes.CDLL('libgcc_s.so.1')

consumedLst = []
site_root = "https://website.com"
apiGatewayLive = "##########"
# apiGatewayLive = "##########"
timeout = 10
pool_counter = 0
pool_counter_size = 0

def upload_to_s3(id, fileUrl, fileName, ssl_verify, connection_pool):
    # start = time.time()
    payload = {'fileUrl':fileUrl,'fileName':fileName}

    try:
        if ssl_verify:
            r = requests.post(apiGatewayLive, timeout = timeout,json=payload) 
        else:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            r = requests.post(apiGatewayLive, verify = False, timeout = timeout,json=payload)      

        if r.status_code == 200:
            connection_object = connection_pool.get_connection()
            if connection_object.is_connected():
                cursor = connection_object.cursor()
                cursor.execute("UPDATE images SET uploaded_image=1 WHERE id="+str(id))
                cursor.close()
                connection_object.commit()
                connection_object.close()
            
    except requests.exceptions.MissingSchema:
        print("[-] Error schema is not supplied, please provide http or https schema to URL")
    except requests.exceptions.ReadTimeout:
        print(f"[*] Timeout occured on with timeout set to : {timeout} sec")
    except requests.exceptions.SSLError as err:
        print(f"[!] SSL error occured use -k option to skip it")
        print(err)
    except requests.exceptions.ConnectionError as err:
        print("\n Connection refused \n")
        # print(err)
    except Exception as err:
        print("Something wrong: \n")
        print(payload)
        print("\n")
        print(err)

if "__main__" in __name__:
    parser = argparse.ArgumentParser(description = "POST Request Sender")
    parser.add_argument("max", help = "Number of select query", type = int)
    parser.add_argument("thread", help = "Number of thread", type = int)
    args = parser.parse_args()

    threads = []
    connection_pool = []
    max = args.max
    cnt_thread = args.thread
    cnt = 0
    for i in range(0,30):
        connection_pool.append( pooling.MySQLConnectionPool(pool_name="pynative_pool"+str(i),pool_size=32,pool_reset_session=True,host='127.0.0.1',database='mangakor',user='root',password='Bojo123$%') )
    
    connection_object = connection_pool[0].get_connection()

    if connection_object.is_connected():
        cursor = connection_object.cursor()
        cursor.execute("SELECT id,web_path_image,path FROM images WHERE uploaded_image=0 LIMIT "+str(max))
        records = cursor.fetchall()
        cursor.close()
        connection_object.close()
        max = len(records)

        while cnt < max:
            pool_counter = 0
            pool_counter_size = 0

            for i in range(0, cnt_thread):
                if cnt >= max:
                    break
                if pool_counter_size >= 30:
                    pool_counter += 1
                    pool_counter_size = 0

                id = records[cnt][0]
                fileUrl = site_root+records[cnt][1]
                fileName = records[cnt][2]
                t = threading.Thread(target = upload_to_s3, args=(id, fileUrl, fileName, True, connection_pool[pool_counter],))
                t.start()
                threads.append(t)
                cnt += 1
                pool_counter_size += 1

                if pool_counter >= 30:
                    pool_counter = 0
                    pool_counter_size = 0

                print(f"\r[+] Total of {cnt} requests sent", end="", flush = True)

            for thread in threads:
                thread.join()