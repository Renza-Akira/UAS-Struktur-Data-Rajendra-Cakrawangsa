import csv
import os
from datetime import datetime

USERS_FILE = "users.csv"
CHAT_FILE = "chat.csv"

# =========================
# INIT FILE
# =========================
def init_files():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password"])

    if not os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "sender", "receiver", "message", "time"])

# =========================
# REGISTER
# =========================
def register():
    username = input("Username baru: ")
    password = input("Password: ")

    with open(USERS_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([username, password])

    print("Akun berhasil dibuat!")

# =========================
# LOGIN
# =========================
def login():
    username = input("Username: ")
    password = input("Password: ")

    with open(USERS_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username and row["password"] == password:
                print(f"\n✅ Login berhasil! Selamat datang, {username}.")
                return username

    print("\n❌ Login gagal! Username atau password salah.")
    print("📝 Jika Anda belum memiliki akun, silakan lakukan registrasi terlebih dahulu melalui menu [1. Register].")
    return None

# =========================
# KIRIM PESAN
# =========================
def send_message(user):
    receiver = input("Kirim ke: ")
    message = input("Pesan: ")
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = []
    with open(CHAT_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)

    msg_id = len(data) + 1

    with open(CHAT_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([msg_id, user, receiver, message, time])

    print("Pesan terkirim!")

# =========================
# INBOX
# =========================
def inbox(user):
    print("\n=== INBOX ===")
    found = False

    with open(CHAT_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["receiver"] == user:
                print(f"[{row['id']}] {row['sender']} ➜ {row['message']} ({row['time']})")
                found = True

    if not found:
        print("Tidak ada pesan masuk.")

# =========================
# ALL CHAT
# =========================
def all_chat():
    print("\n=== ALL CHAT ===")

    with open(CHAT_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(f"[{row['id']}] {row['sender']} ➜ {row['receiver']}: {row['message']} ({row['time']})")

# =========================
# DELETE MESSAGE
# =========================
def delete_message():
    msg_id = input("ID pesan yang dihapus: ")

    data = []
    with open(CHAT_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["id"] != msg_id:
                data.append(row)

    with open(CHAT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "sender", "receiver", "message", "time"])

        for row in data:
            writer.writerow([
                row["id"],
                row["sender"],
                row["receiver"],
                row["message"],
                row["time"]
            ])

    print("Pesan berhasil dihapus!")

# =========================
# MENU
# =========================
def menu(user):
    while True:
        print("\n===== MINI WHATSAPP =====")
        print("1. Kirim Pesan")
        print("2. Inbox")
        print("3. Semua Chat")
        print("4. Hapus Pesan")
        print("5. Logout")

        pilih = input("Pilih: ")

        if pilih == "1":
            send_message(user)
        elif pilih == "2":
            inbox(user)
        elif pilih == "3":
            all_chat()
        elif pilih == "4":
            delete_message()
        elif pilih == "5":
            print(f"\n👋 Logout berhasil. Sampai jumpa, {user}!")
            break
        else:
            print("❌ Pilihan tidak valid!")

# =========================
# MAIN PROGRAM
# =========================
def main():
    init_files()

    while True:
        print("\n===== LOGIN SYSTEM =====")
        print("1. Register")
        print("2. Login")
        print("3. Keluar")

        pilih = input("Pilih: ")

        if pilih == "1":
            register()
        elif pilih == "2":
            user = login()
            if user:
                menu(user)
        elif pilih == "3":
            print("\n🙏 Terima kasih telah menggunakan Mini WhatsApp.")
            print("👋 Sampai jumpa lagi!")
            break
        else:
            print("❌ Pilihan tidak valid!")
            
if __name__ == "__main__":
    main()