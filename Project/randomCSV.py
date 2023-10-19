import csv
import uuid
import random
import lorem

# Fungsi untuk menghasilkan UUID acak
def generate_uuid():
    return str(uuid.uuid4())

# Fungsi untuk menghasilkan kata acak
def generate_word():
    word_list = ["Apple", "Banana", "Grape", "Honeydew", "Kiwi", "Lemon", "Afternoon", "Evening", "Night", "Morning", "Tree"]
    return random.choice(word_list)

# Fungsi untuk menghasilkan deskripsi acak
def generate_description():
    word_list = ["Apple", "Banana", "Grape", "Honeydew", "Kiwi", "Lemon", "Afternoon", "Evening", "Night", "Morning", "Tree"]
    return random.choice(word_list)
    # return lorem.paragraph()

# Tentukan nama file CSV
file_path = "Samples/random_data1.csv"

# Tentukan ukuran file dalam byte (2 MB)
file_size = 2 * 1024 * 1024

# Buka file CSV untuk ditulis
with open(file_path, mode='w', newline='') as file:
    writer = csv.writer(file, delimiter=';')

    # Tulis header kolom
    writer.writerow(["UUID", "Word", "Description", ""])

    # Hitung jumlah data yang harus ditambahkan untuk mencapai ukuran yang diinginkan
    data_size = 0
    while data_size < file_size:
        uuid_data = generate_uuid()
        word_data = generate_word()
        description_data = generate_description()
        row = [uuid_data, word_data, description_data, ""]

        # Tulis baris data ke file CSV
        writer.writerow(row)

        # Hitung ukuran data yang sudah ditambahkan
        data_size = file.tell()

print(f"File CSV '{file_path}' telah berhasil dibuat dengan ukuran {data_size / (1024 * 1024):.2f} MB.")
