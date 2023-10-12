from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from tqdm import tqdm
from config.db import db

from decouple import config
SECRET_KEY = config('SECRET_KEY').encode('utf-8')
BATCH_SIZE = int(1 * 1024 * 1024)
# Fungsi untuk enkripsi data menggunakan AES
async def encrypt_data(data, progress_callback):
    ciphertexts=[]
    load =0
    total = sum(len(chunk) for chunk in data )
    with tqdm(total=len(data), desc="Encrypting data", unit='B', unit_scale=True, mininterval=0.5) as pbar:
        for chunk in data:
            cipher = AES.new(SECRET_KEY, AES.MODE_EAX)
            nonce = cipher.nonce
            # print(SECRET_KEY)
            ciphertext, tag = cipher.encrypt_and_digest(chunk)
            
            ciphertexts.append(nonce + ciphertext + tag)
            
            load += len(chunk)
            progress_callback((load/total)*100)
            # print((load/total)*100)
            
            pbar.update(len(chunk))
    
    return b''.join(ciphertexts)
    



# Fungsi untuk dekripsi data menggunakan AES
async def decrypt_data(data, times,progress_callback):
    offset = 0
    chunk_size = 16 + BATCH_SIZE + 16

    # Inisialisasi list_data
    data_collection = db.db["DataSample"]
    list_data = []
    current_data = ""
    data_count = 0

    with tqdm(total=len(data), desc="Decrypting data", unit='B', unit_scale=True) as pbar:
        status=True
        # print(len(data))
        while offset < len(data):
            chunk = data[offset:offset + chunk_size]
            nonce = chunk[:16]
            ciphertext = chunk[16:-16]
            tag = chunk[-16:]

            cipher = AES.new(SECRET_KEY, AES.MODE_EAX, nonce=nonce)
            plaintext = cipher.decrypt(ciphertext)
            print(len(plaintext))
            try:
                cipher.verify(tag)

                string_data = plaintext.decode('utf-8').replace('\r', '').replace('\n', '')

                for char in string_data:
                    if char == ';':
                        data_count += 1
                        if data_count == 3:
                            # list_data.append(current_data.split(';'))
                            list_data = current_data.split(';')

                            if list_data[0] == "UUID" or list_data[1] == "Word" or list_data[2] == "Description":
                                pass
                            
                            else:
                                json_data = {
                                    # "_id" : list_data[0],
                                    "date" : times[0],
                                    "time" : times[1],
                                    "world" :  list_data[1],
                                    "Deskripsi" : list_data[2]

                                }
                                # data_collection.insert_one(json_data)
                                data_collection.update_one({"_id": list_data[0]}, {"$set": json_data}, upsert=True)
                                # print(result.inserted_id)
                            current_data = ""
                            data_count = 0

                        else:
                            current_data += char
                    else:
                        current_data += char

                # plaintexts.append(plaintext)
                
                progress_callback((offset/len(data))*100) # Panggil callback progres
                # print((offset/len(data))*100)
            except ValueError:
                print("Key incorrect or message corrupted")
                status=False
                break

            offset += chunk_size
            pbar.update(chunk_size)  # Update progress bar with chunk size

    return status