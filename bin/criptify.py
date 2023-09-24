from cryptography.fernet import Fernet
import os
import tkinter as tk
from tkinter import filedialog
import time

logo = "\033[32m" + """

 ▄████████    ▄████████  ▄█     ▄███████▄     ███      ▄█     ▄████████ ▄██   ▄   
███    ███   ███    ███ ███    ███    ███ ▀█████████▄ ███    ███    ███ ███   ██▄ 
███    █▀    ███    ███ ███▌   ███    ███    ▀███▀▀██ ███▌   ███    █▀  ███▄▄▄███ 
███         ▄███▄▄▄▄██▀ ███▌   ███    ███     ███   ▀ ███▌  ▄███▄▄▄     ▀▀▀▀▀▀███ 
███        ▀▀███▀▀▀▀▀   ███▌ ▀█████████▀      ███     ███▌ ▀▀███▀▀▀     ▄██   ███ 
███    █▄  ▀███████████ ███    ███            ███     ███    ███        ███   ███ 
███    ███   ███    ███ ███    ███            ███     ███    ███        ███   ███ 
████████▀    ███    ███ █▀    ▄████▀         ▄████▀   █▀     ███         ▀█████▀  
             ███    ███                                                           
                                     
""" + "\033[0m"
# clear console command
def clear(): return os.system('cls' if os.name == 'nt' else 'clear')

# Function to generate a Fernet key
def generate_key():
    key = Fernet.generate_key()
    return key

# Function to encrypt a file using a Fernet key
def encrypt_file(key, filename):
    fernet = Fernet(key)

    with open(filename, 'rb') as f:
        data = f.read()

    encrypted_data = fernet.encrypt(data)
    encrypted_filename = filename + '.enc'

    with open(encrypted_filename, 'wb') as f:
        f.write(encrypted_data)

    return encrypted_filename

# Function to decrypt a file using a Fernet key
def decrypt_file(key, filename):
    fernet = Fernet(key)

    with open(filename, 'rb') as f:
        encrypted_data = f.read()

    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except:
        return None

    decrypted_filename = os.path.splitext(filename)[0]

    with open(decrypted_filename, 'wb') as f:
        f.write(decrypted_data)

    return decrypted_filename


# Loop until the user chooses to quit
while True:
    # clear the console on program launch
    clear()
    print(logo)
    # Ask the user if they want to encrypt or decrypt files
    print("🔹1. Encrypt files.")
    print("🔹2. Decrypt files.")
    print("🔹Q. Quit.")
    print(" ")
    mode = input(
        "⚡ Enter your choice: ")

    if mode == '1':
        # Clear the screen       
        os.system('cls' if os.name == 'nt' else 'clear')
        print(logo)
        # Ask the user to select a file to encrypt
        root = tk.Tk()
        root.withdraw()
        filenames = filedialog.askopenfilenames()
        if not filenames:
            print("⛔ No files selected.")
            time.sleep(3)
            continue
        
        # Ask the user if they want to generate a new key or enter an existing one
        print("🔹1. Generate a new key 🔑.")
        print("🔹2. Enter an existing key 🔑.")
        print(" ")
        key_choice = input(
            "⚡ Enter your choice: ")
        if key_choice == '1':
            # Clear the screen       
            os.system('cls' if os.name == 'nt' else 'clear')
            print(logo)
            # Generate a new Fernet key
            key = generate_key()
            print("🔑 Key:", key.decode())
            print("📑 Copy the Key and press Enter to continue...")
            input()  # Waits for the user to press enter
            print("")
        elif key_choice == '2':
            # Clear the screen       
            os.system('cls' if os.name == 'nt' else 'clear')
            print(logo)
            # Ask the user for a key
            key = input("🔑 Enter the key: ")
            if not key:
                print("⛔ No key entered.")
                time.sleep(3)
                continue
            try:
                key = key.encode()
                fernet = Fernet(key)
            except ValueError:
                print("⛔ Invalid key. Please enter a valid Fernet key.")
                time.sleep(3)
                continue
        else:
            print(
                "⚠️ Invalid choice. Please enter 1 to generate a new key or 2 to enter an existing key.")
            time.sleep(3)
            continue

        for filename in filenames:
            # Encrypt the file
            encrypted_file = encrypt_file(key, filename)

            # Print the encrypted file name
            print(f"🔒 Encrypted: {filename}")

            # Delete the original file
            os.unlink(filename)

            time.sleep(3)

    elif mode == '2':
        # Clear the screen       
        os.system('cls' if os.name == 'nt' else 'clear')
        print(logo)
        # Ask the user to select files to decrypt
        root = tk.Tk()
        root.withdraw()
        filenames = filedialog.askopenfilenames()
        if not filenames:
            print("⛔ No files selected.")
            time.sleep(3)
            continue

        # Ask the user for the key
        key = input("🔑 Enter the key: ")
        if not key:
            print("⛔ No key entered.")
            time.sleep(3)
            continue

        # Decrypt the files
        for filename in filenames:
            decrypted_file = decrypt_file(key.encode(), filename)

            if decrypted_file is None:
                print(
                    f"⛔ Failed to decrypt the file {filename}. Please check the decryption key and try again.")
                time.sleep(3)
            else:
                # Print the decrypted file name
                print("🔓 Decrypted file:", decrypted_file)

                # Delete the original encrypted file
                os.unlink(filename)

                time.sleep(3)

    elif mode == 'q':
        break

    else:
        print("⚠️ Invalid mode. Please enter 1 to encrypt files, 2 to decrypt files, or q to quit.")
