import threading
import requests


class DownloadThread(threading.Thread):
    def __init__(self, url, output_file, lock):
        super().__init__()
        self.url = url
        self.output_file = output_file
        self.lock = lock

    def run(self):
        response = requests.get(self.url)
        encrypted_content = response.text
        with open(self.output_file, 'w') as file:
            file.write(encrypted_content)


def caesar_decrypt(encrypted_text, offset):
    decrypted_text = ""
    for char in encrypted_text:
        if char.isalpha():
            decrypted_text += chr((ord(char) - offset - ord('A')) % 26 + ord('A')) if char.isupper() else chr(
                (ord(char) - offset - ord('a')) % 26 + ord('a'))
        else:
            decrypted_text += char
    return decrypted_text


class DecryptThread(threading.Thread):
    def __init__(self, input_file, decrypted_data, lock):
        super().__init__()
        self.input_file = input_file
        self.decrypted_data = decrypted_data
        self.lock = lock

    def run(self):
        with open(self.input_file, 'r') as file:
            encrypted_content = file.read()
        decrypted_content = caesar_decrypt(encrypted_content, offset=8)

        with self.lock:
            self.decrypted_data.append((self.input_file, decrypted_content))


class Combiner:
    def __init__(self):
        self.data_structure = []

    def add_data(self, decrypted_data, lock):
        with lock:
            self.data_structure.append(decrypted_data)

    def write_to_file(self, output_file, lock):
        with lock:
            sorted_data = sorted(self.data_structure, key=lambda x: x[0])
            with open(output_file, 'w') as file:
                for _, content in sorted_data:
                    file.write(content)


if __name__ == "__main__":
    download_threads = []
    download_files = [
        ("https://advancedpython.000webhostapp.com/s1.txt", "s1_enc.txt"),
        ("https://advancedpython.000webhostapp.com/s2.txt", "s2_enc.txt"),
        ("https://advancedpython.000webhostapp.com/s3.txt", "s3_enc.txt")
    ]

    decryption_lock = threading.Lock()
    combiner_lock = threading.Lock()

    for url, output_file in download_files:
        thread = DownloadThread(url, output_file, decryption_lock)
        download_threads.append(thread)
        thread.start()

    for thread in download_threads:
        thread.join()

    decrypted_data = []
    decrypt_threads = []
    decrypt_files = ["s1_enc.txt", "s2_enc.txt", "s3_enc.txt"]

    for input_file in decrypt_files:
        thread = DecryptThread(input_file, decrypted_data, decryption_lock)
        decrypt_threads.append(thread)
        thread.start()

    for thread in decrypt_threads:
        thread.join()

    combiner = Combiner()
    for data in decrypted_data:
        combiner.add_data(data, combiner_lock)

    combiner.write_to_file("s_final.txt", combiner_lock)

    with open("s_final.txt", 'r') as file:
        content = file.read()
        print(content)
