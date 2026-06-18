import csv
import os
import re
import subprocess
import webbrowser
import requests
from bs4 import BeautifulSoup
import pyttsx3
from datetime import datetime
import cv2
import random
import asyncio
import edge_tts
import pygame
import uuid
import time
from colorama import init, Fore
import webbrowser

# =========================
# EDGE TTS FIX
# =========================
VOICE = "id-ID-GadisNeural"

pygame.mixer.init()

async def generate_voice(text):

    filename = f"voice_{uuid.uuid4().hex}.mp3"

    try:

        await edge_tts.Communicate(
            text=text,
            voice=VOICE
        ).save(filename)

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)

        pygame.mixer.music.unload()

        time.sleep(0.2)

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        print("VOICE ERROR:", e)

# =========================
# SPEAK
# =========================
def speak(text):

    if not text:
        return

    print(f"\n🎀 Rara-chan: {text}")

    try:
        asyncio.run(generate_voice(str(text)))

    except Exception as e:
        print("TTS ERROR:", e)

# =========================
# DATABASE
# =========================
FILES = {
    "chat": "chat.csv",
    "youtube": "youtube.csv",
    "google": "google.csv",
    "instagram": "instagram.csv",
    "scholar": "scholar.csv",
    "roblox": "roblox.csv",
    "canva": "canva.csv",
    "boc": "boc.csv",
    "wa": "wa.csv",
    "miniwa": "miniwa_chat.csv",
    "kamera": "kamera.csv",
    "calculator": "calculator.csv",
    "waktu": "waktu.csv",
    "spotify": "spotify.csv",
    "browser": "browser.csv"
}

# =========================
# CHAT MEMORY (INTERNAL)
# =========================
chat_memory = []

def show_chat_memory():
    for i, c in enumerate(chat_memory):
        print(i, c)

def delete_last_chat():
    if chat_memory:
        chat_memory.pop()

# =========================
# STATE KALKULATOR
# =========================
calc_state = {
    "nilai": 0,
    "history": []
}

# =========================
# ADD
# =========================
def calc_add(num):
    calc_state["nilai"] += num
    calc_state["history"].append(("tambah", num, calc_state["nilai"]))

# =========================
# SUBTRACT (KURANG)
# =========================
def calc_subtract(num):
    calc_state["nilai"] -= num
    calc_state["history"].append(("kurang", num, calc_state["nilai"]))

# =========================
# MULTIPLY (KALI)
# =========================
def calc_multiply(num):
    calc_state["nilai"] *= num
    calc_state["history"].append(("kali", num, calc_state["nilai"]))

# =========================
# DIVIDE (BAGI)
# =========================
def calc_divide(num):
    if num == 0:
        return "Error: tidak bisa bagi 0"

    calc_state["nilai"] /= num
    calc_state["history"].append(("bagi", num, calc_state["nilai"]))

# =========================
# RESULT
# =========================
def calc_result():
    return calc_state["nilai"]

# =========================
# RESET
# =========================
def calc_reset():
    calc_state["nilai"] = 0
    calc_state["history"].append(("reset", 0, 0))

def calc_remove():
    calc_state["nilai"] -= 1
    calc_state["history"].append(("hapus", 1, calc_state["nilai"]))
    return 1

def calc_history():
    return calc_state["history"]

# =========================
# SAVE CALCULATOR
# =========================
def save_calc(user, operasi, angka, hasil):

    file = FILES["calculator"]

    if os.path.exists(file):
        data = list(csv.DictReader(open(file, "r", encoding="utf-8")))
    else:
        data = []

    calc_id = len(data) + 1
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if calc_id == 1:
            writer.writerow(["id","user","operasi","angka","hasil","waktu"])

        writer.writerow([
            calc_id,
            user,
            operasi,
            angka,
            hasil,
            waktu
        ])

# =========================
# SHOW CSV
# =========================
def show_csv(file_name):
    try:
        with open(file_name, "r", newline="") as file:
            reader = csv.reader(file)
            rows = list(reader)

            if len(rows) <= 1:
                return None  # cuma header atau kosong

            hasil = ""
            for row in rows[1:]:  # skip header
                hasil += " | ".join(row) + "\n"

            return hasil

    except FileNotFoundError:
        return None
# =========================
# INIT CSV
# =========================
def init_files():
    for f in FILES.values():
        if not os.path.exists(f):
            with open(f, "w", newline="", encoding="utf-8") as file:
                csv.writer(file).writerow(["id", "user", "query", "time"])

# =========================
# SAVE CSV
# =========================
import csv
from datetime import datetime

def save(table, user, message):

    file = FILES[table]

    with open(file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            user,
            message,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])

# =========================
# CHROME
# =========================
def chrome():
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def open_url(url):
    c = chrome()
    if c:
        subprocess.Popen([c, url])
    else:
        webbrowser.open(url)

# =========================
# CLEAN TOPIC
# =========================
def clean_topic(msg):

    msg = msg.lower()

    words = [
        "siapa",
        "apa",
        "itu",
        "jelaskan",
        "tentang",
        "pengertian",
        "definisi",
        "tolong",
        "coba",
        "wikipedia",
        "gpt"
    ]

    for word in words:
        msg = msg.replace(word, "")

    msg = re.sub(r"[^a-zA-Z0-9\s]", "", msg)

    return " ".join(msg.split())


# =========================
# WIKIPEDIA + GOOGLE FALLBACK
# =========================
def wiki_answer(msg):

    topic = clean_topic(msg)

    if topic == "":
        return "Topik tidak jelas"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        # =========================
        # SEARCH WIKIPEDIA INDONESIA
        # =========================
        search_url = "https://id.wikipedia.org/w/api.php"

        params = {
            "action": "opensearch",
            "search": topic,
            "limit": 1,
            "namespace": 0,
            "format": "json"
        }

        r = requests.get(
            search_url,
            params=params,
            headers=headers,
            timeout=5
        )

        data = r.json()

        if len(data[1]) == 0:
            raise Exception("Artikel tidak ditemukan")

        title = data[1][0]

        page_url = (
            "https://id.wikipedia.org/wiki/"
            + title.replace(" ", "_")
        )

        res = requests.get(
            page_url,
            headers=headers,
            timeout=5
        )

        soup = BeautifulSoup(
            res.text,
            "html.parser"
        )

        paragraphs = soup.find_all("p")

        for p in paragraphs:

            text = p.get_text().strip()

            if len(text) > 80:

                print("\n" + "=" * 60)
                print("📚 WIKIPEDIA")
                print("=" * 60)
                print("Judul :", title)
                print(text[:300])
                print("=" * 60)

                return "Menurut Wikipedia, " + text[:300]

        raise Exception("Ringkasan kosong")

    except Exception as e:

        print("Wikipedia Error:", e)

        # =========================
        # GOOGLE FALLBACK
        # =========================
        try:

            q = topic.replace(" ", "+")

            google_url = (
                "https://www.google.com/search?q="
                + q
            )

            res = requests.get(
                google_url,
                headers=headers,
                timeout=5
            )

            soup = BeautifulSoup(
                res.text,
                "html.parser"
            )

            text = soup.get_text(" ", strip=True)

            if len(text) > 100:

                print("\n" + "=" * 60)
                print("🔎 GOOGLE")
                print("=" * 60)
                print(text[:300])
                print("=" * 60)

                return "Menurut Google, " + text[:300]

        except Exception as e:

            print("Google Error:", e)

        # =========================
        # BUKA GOOGLE DI CHROME
        # =========================
        open_url(
            "https://www.google.com/search?q="
            + topic
        )

        return (
            f"Saya tidak dapat mengakses Wikipedia saat ini. "
            f"Google telah dibuka untuk mencari {topic}."
        )
            
def wiki_search_log(user, query):
    save("chat", user, f"wiki search: {query}")
    return wiki_answer(query)

# =========================
# CAMERA
# =========================
def camera(user):

    speak("Kamera aktif. Spasi untuk foto, ESC untuk keluar.")

    cap = cv2.VideoCapture(0)

    start_time = time.time()
    open_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("kamera.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "OPEN",
            user,
            "camera_opened",
            0,
            open_time,
            0
        ])

    if not cap.isOpened():
        speak("Kamera tidak terdeteksi")
        return "failed"

    folder = "photos"
    os.makedirs(folder, exist_ok=True)

    db_file = "photo_db.csv"

    # init CSV
    if not os.path.exists(db_file):
        with open(db_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "user", "filename", "time"])

    photo_id = 0

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Rara AI Camera", frame)

        key = cv2.waitKey(1) & 0xFF

        # =========================
        # EXIT CAMERA
        # =========================
        if key == 27:
            speak("Kamera ditutup")
            break

        # =========================
        # TAKE PHOTO
        # =========================
        elif key == 32:

            photo_id += 1

            filename = f"{folder}/photo_{photo_id}.jpg"
            cv2.imwrite(filename, frame)

            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # SAVE CSV
            
            with open(db_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    photo_id,
                    user,
                    filename,
                    time_now
                ])

            # =========================
            # AMBIL TOTAL FOTO
            # =========================
            with open(db_file, "r", encoding="utf-8") as f:
                total = len(list(csv.reader(f))) - 1

            # =========================
            # OUTPUT RAPI (INI YANG KAMU MAU)
            # =========================
            print("\n📸 Rara AI Camera Report")
            print(f"📷 Foto {photo_id} disimpan ke database")
            print(f"👤 User: {user}")
            print(f"📊 Total foto: {total}")
            print(f"📁 File: {filename}")
            print(f"🕒 Waktu: {time_now}")

            speak(f"Foto {photo_id} berhasil disimpan")

    end_time = time.time()
    durasi = round((end_time - start_time) / 60, 2)

    close_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("kamera.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "CLOSE",
            user,
            "camera_closed",
            photo_id,
            close_time,
            durasi
        ])

    cap.release()
    cv2.destroyAllWindows()
    
    return "closed"

# =========================
# TIME
# =========================
def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ai(user, msg):
    m = msg.lower().strip()

    # CAMERA
    if "kamera" in m:
        camera()
        return "Camera closed"

    # TIME
    elif "jam" in m or "waktu" in m:
        return get_time()

    # =========================
    # TAMBAH / ADD
    # =========================
    elif m.startswith("add ") or m.startswith("tambah "):
        try:
            num = float(m.split()[-1])
            calc_add(num)
            hasil = calc_result()
            save_calc(user, "add", num, hasil)
            return f"Baik {user}, angka {num} ditambahkan. Hasil sekarang: {hasil}"
        except:
            return "Format salah. Contoh: tambah 1"

    # =========================
    # HAPUS / KURANG 1
    # =========================
    elif m.startswith("hapus"):
        angka = calc_remove()
        hasil = calc_result()
        save_calc(user, "hapus", angka, hasil)
        return f"Baik {user}, angka {angka} dihapus. Hasil sekarang: {hasil}"

    # =========================
    # HASIL / SAMA DENGAN
    # =========================
    elif m == "hasil" or m == "sama dengan":
        hasil = calc_result()
        return f"Baik {user}, hasil perhitungannya adalah {hasil}."

    # =========================
    # RESET
    # =========================
    elif m == "reset kalkulator":
        calc_reset()
        return "Baik, kalkulator berhasil direset."

    # =========================
    # HISTORY
    # =========================
    elif m == "history kalkulator":
        return calc_history()

    # =========================
    # CHAT MEMORY
    # =========================
    elif m == "lihat chat":
        show_chat_memory()
        return "Done"

    elif m == "hapus chat":
        delete_last_chat()
        return "Deleted"

        return "Perintah tidak dikenali."

    elif "youtube" in m:
        q = m.replace("youtube","").strip()
        open_url("https://youtube.com" if q=="" else "https://youtube.com/results?search_query="+q)
        return "YouTube"

    elif any(x in m for x in ["siapa","apa","jelaskan","tentang"]):
        return wiki_answer(msg)

    elif "halo" in m:
        return f"Halo {user}"

    return "Perintah tidak dikenali"

# =========================
# WHATSAPP MINI
# =========================
USERS_FILE = "users.csv"
CHAT_FILE = "miniwa_chat.csv"

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
    print("\nJika belum memiliki akun silakan register terlebih dahulu.")

    username = input("Username: ")
    password = input("Password: ")

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["username"] == username and row["password"] == password:
                print("\n✅ Login berhasil!")
                print(f"Selamat datang {username}")
                return username

    print("\n❌ Login gagal!")
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
            print("\n👋 Anda logout dari akun.")
            print("Silakan login kembali untuk menggunakan Mini WhatsApp.")
            break
        else:
            print("Pilihan salah!")

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
            print("Keluar...")
            break
        else:
            print("Pilihan tidak valid!")

# =========================
# WHATSAPP
# =========================
def whatsapp(user):

    print("\n===== WHATSAPP =====")
    print("1. Desktop")
    print("2. Web")
    print("3. Mini WA")
    print("4. Kembali")

    c = input("Pilih: ")

    if c == "1":

        path = r"C:\Program Files\WhatsApp\WhatsApp.exe"

        if os.path.exists(path):

            subprocess.Popen([path])

            replies = [
                "Baik, saya akan membuka WhatsApp Desktop.",
                "Tunggu sebentar, saya sedang menjalankan WhatsApp Desktop.",
                "Siap, WhatsApp Desktop akan segera dibuka.",
                "Baik, saya akan membuka aplikasi WhatsApp Desktop untuk Anda."
            ]

            return random.choice(replies)

        return "Maaf, saya tidak menemukan WhatsApp Desktop di komputer ini."

    elif c == "2":

        open_url("https://web.whatsapp.com")
        save("wa", user, "web")

        replies = [
            "Baik, saya akan membuka WhatsApp Web.",
            "Tunggu sebentar, saya sedang membuka WhatsApp Web.",
            "Siap, WhatsApp Web akan segera ditampilkan.",
            "Baik, saya akan menghubungkan Anda ke WhatsApp Web."
        ]

        return random.choice(replies)

    elif c == "3":

        replies = [
            "Baik, saya akan membuka Mini WhatsApp.",
            "Tunggu sebentar, saya sedang menjalankan Mini WhatsApp.",
            "Siap, Mini WhatsApp akan segera dibuka.",
            "Baik, saya akan membuka aplikasi Mini WhatsApp."
        ]

        run_miniwa()

        return "Terima kasih telah menggunakan Mini WhatsApp."

    elif c == "4":
        return "Baik, kembali ke menu utama."

    return "Pilihan tidak valid."

def delete_by_id(file_path, target_id):
    if not os.path.exists(file_path):
        return "File tidak ditemukan"

    rows = []

    with open(file_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows.append(header)

        found = False

        for row in reader:
            if row[0] != str(target_id):
                rows.append(row)
            else:
                found = True

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return "Dihapus" if found else "ID tidak ditemukan"

# =========================
# MINI WA LAUNCHER
# =========================
def run_miniwa():
    init_files()

    while True:
        print("\n===== MINI WA =====")
        print("1. Register")
        print("2. Login")
        print("3. Kembali")

        pilih = input("Pilih: ")

        if pilih == "1":
            register()

        elif pilih == "2":
            user = login()

            if user:
                menu(user)

        elif pilih == "3":
            print("\n🙏 Terima kasih sudah menggunakan APK Mini WA.")
            break

        else:
            print("Pilihan tidak valid!")

# =========================
# REFRESH ALL DATABASE
# =========================
def refresh_all_data():
    files = [
        "chat.csv",
        "youtube.csv",
        "google.csv",
        "instagram.csv",
        "scholar.csv",
        "roblox.csv",
        "canva.csv",
        "wa.csv",
        "boc.csv",
        "miniwa_chat.csv",
        "kamera.csv",
        "calculator.csv",
        "waktu.csv",
        "spotify.csv",
        "browser.csv",
        "users.csv",
        "data.csv",
        "photo_db.csv"
    ]

    total = 0

    for file in files:
        if os.path.exists(file):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    try:
                        header = next(reader)
                    except StopIteration:
                        continue

                with open(file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(header)

                total += 1
            except:
                pass

    return f"{total} database berhasil di-refresh"

# =========================
# REFRESH DATABASE SYSTEM
# =========================
def refresh_csv(file_path):
    if not os.path.exists(file_path):
        return f"{file_path} tidak ditemukan"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)

            try:
                header = next(reader)
            except StopIteration:
                return f"{file_path} kosong"

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)

        return f"{file_path} berhasil di-refresh"

    except Exception as e:
        return f"Error: {e}"

def refresh_all_data():

    files = [
        "chat.csv",
        "youtube.csv",
        "google.csv",
        "instagram.csv",
        "scholar.csv",
        "roblox.csv",
        "canva.csv",
        "wa.csv",
        "boc.csv",
        "miniwa_chat.csv",
        "kamera.csv",
        "calculator.csv",
        "waktu.csv",
        "spotify.csv",
        "browser.csv",
        "users.csv",
        "data.csv",
        "photo_db.csv"
    ]

    total = 0

    for file in files:

        if os.path.exists(file):

            try:
                with open(file, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)

                    try:
                        header = next(reader)
                    except StopIteration:
                        continue

                with open(file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(header)

                total += 1

            except:
                pass

    return f"{total} database berhasil di-refresh"


init(autoreset=True)

# =========================
# DATABASE TABLE
# =========================
def show_database_table():

    files = [
        "chat.csv",
        "youtube.csv",
        "google.csv",
        "instagram.csv",
        "scholar.csv",
        "roblox.csv",
        "canva.csv",
        "wa.csv",
        "boc.csv",
        "miniwa_chat.csv",
        "kamera.csv",
        "calculator.csv",
        "waktu.csv",
        "spotify.csv",
        "browser.csv",
        "users.csv",
        "data.csv",
        "photo_db.csv"
    ]

    print("\n" + "=" * 60)
    print("📊 DATABASE STATUS")
    print("=" * 60)

    print(f"{'No':<4}{'Database':<20}{'Jumlah Data'}")
    print("-" * 60)

    total = 0

    for i, file in enumerate(files, start=1):

        if os.path.exists(file):

            try:
                with open(file, "r", encoding="utf-8") as f:

                    reader = csv.reader(f)
                    rows = list(reader)

                    jumlah = max(0, len(rows) - 1)

                    total += jumlah

                    warna = (
                        Fore.GREEN
                        if jumlah > 0
                        else Fore.WHITE
                    )

                    print(
                        warna +
                        f"{i:<4}{file:<20}{jumlah}"
                    )

            except:
                print(
                    Fore.RED +
                    f"{i:<4}{file:<20}ERROR"
                )

        else:
            print(
                Fore.RED +
                f"{i:<4}{file:<20}TIDAK ADA"
            )

    print("-" * 60)
    print(
        Fore.CYAN +
        f"TOTAL DATA : {total}"
    )
    print("=" * 60)

# =========================
# BROWSER
# =========================
def browser(user, query=""):

    if query == "":
        url = "https://www.google.com"

        webbrowser.open(url)

        save("browser", user, "open home")

        return "Baik, saya akan membuka browser."

    else:

        url = "https://www.google.com/search?q=" + query.replace(" ", "+")

        webbrowser.open(url)

        save("browser", user, f"search: {query}")

        return f"Baik {user}, saya akan mencari {query} di browser."
    
# =========================
# AI BRAIN
# =========================
def ai(user, msg):
    m = msg.lower()

    if "youtube" in m:
        q = m.replace("youtube","").strip()

        if q == "":
            open_url("https://youtube.com")
            save("youtube", user, "home")
            return "Baik, saya akan membuka halaman utama YouTube."

        else:
            open_url("https://youtube.com/results?search_query=" + q)

        # simpan data yang benar ke database
        save("youtube", user, f"search: {q}")

        return f"Baik, saya akan membuka YouTube dan mencari {q}."

    elif "google" in m:

        q = m.replace("google", "").replace("chrome", "").strip()

        open_url("https://google.com/search?q=" + q)

        save("google", user, f"search: {q}")

        replies = [
        f"Baik {user}, saya akan mencari {q} melalui Google.",
        f"Tunggu sebentar, saya sedang mencari informasi tentang {q}.",
        f"Saya akan membuka Google dan mencari {q}.",
        f"Baik, saya akan membantu menemukan informasi mengenai {q}.",
        f"Sedang memproses pencarian {q} melalui Google.",
        f"Oke {user}, saya akan mencari {q} untuk Anda.",
        f"Baik, hasil pencarian Google untuk {q} sedang dibuka.",
        f"Saya sedang membuka Google dan mencari topik {q}.",
        f"Siap, saya akan menampilkan hasil pencarian tentang {q}.",
        f"Baik, saya akan mencari informasi yang berkaitan dengan {q}."
        ]

        return random.choice(replies)

    elif "instagram" in m:
        q = m.replace("instagram", "").strip()
        open_url("https://instagram.com/" + q)
        save("instagram", user, f"profile: {q}")
        return f"Baik, saya akan membuka profil Instagram {q}."

    
    elif "kamera" in m:

        result = camera(user)

        # STOP TOTAL RESPONSE
        if result == "closed":
            return ""   # tidak ada reply lagi

        return ""

    elif "scholar" in m:

        q = m.replace("scholar", "").strip()

        open_url("https://scholar.google.com/scholar?q=" + q)

        save("scholar", user, f"search: {q}")

        replies = [
        f"Baik {user}, saya akan mencari referensi ilmiah tentang {q} melalui Google Scholar.",
        f"Tunggu sebentar, saya sedang mencari jurnal mengenai {q}.",
        f"Baik, saya akan membuka Google Scholar dan mencari topik {q}.",
        f"Saya akan membantu menemukan artikel dan jurnal yang berkaitan dengan {q}.",
        f"Sedang memproses pencarian referensi akademik tentang {q}.",
        f"Oke {user}, saya akan mencari sumber ilmiah mengenai {q}.",
        f"Baik, hasil pencarian Google Scholar untuk {q} sedang dibuka.",
        f"Saya sedang mencari publikasi dan jurnal terkait {q}.",
        f"Siap, saya akan menampilkan referensi akademik tentang {q}.",
        f"Baik, saya akan membantu menemukan penelitian yang berkaitan dengan {q}."
        ]

        return random.choice(replies)

    elif "roblox" in m:
        q = m.replace("roblox", "").strip()
        open_url("https://roblox.com/search?keyword=" + q)
        save("roblox", user, f"search: {q}")
        return f"Baik, saya akan mencari {q} di Roblox."

    elif "canva" in m:

        q = m.replace("canva", "").strip()

        open_url("https://canva.com/search?q=" + q)

        save("canva", user, f"search: {q}")

        replies = [
        f"Baik {user}, saya akan membuka Canva dan mencari desain {q}.",
        f"Tunggu sebentar, saya sedang mencari template {q} di Canva.",
        f"Baik, saya akan membantu menemukan desain {q} melalui Canva.",
        f"Sedang membuka Canva dan mencari inspirasi desain {q}.",
        f"Oke {user}, saya akan mencari template yang berkaitan dengan {q}.",
        f"Saya akan membuka Canva dan menampilkan hasil pencarian untuk {q}.",
        f"Baik, saya sedang mencari desain dan template {q}.",
        f"Siap, saya akan membantu menemukan desain {q} di Canva.",
        f"Tunggu sebentar, saya sedang membuka Canva untuk mencari {q}.",
        f"Baik, saya akan menampilkan berbagai template Canva yang berkaitan dengan {q}."
        ]

        return random.choice(replies)

    elif "spotify" in m:

        q = m.replace("spotify", "").strip()

        # =========================
        # JIKA TIDAK ADA KATA KUNCI (HOME)
        # =========================
        if q == "":
            open_url("https://open.spotify.com/")
            save("spotify", user, "open home")
            return "Baik, saya membuka beranda Spotify untuk kamu."

        # =========================
        # JIKA ADA PENCARIAN
        # =========================
        else:
            search_url = "https://open.spotify.com/search/" + q.replace(" ", "%20")
            open_url(search_url)

            save("spotify", user, f"search: {q}")
            return f"Baik, saya sedang mencari '{q}' di Spotify."
    
    elif m == "wa" or m == "whatsapp":

        save("wa", user, "opened whatsapp")

        return whatsapp(user)

    elif m == "browser":

        return browser(user)

    elif "browser" in m:

        q = m.replace("browser", "").strip()

        return browser(user, q)
    
    elif "boc" in m:
        open_url("https://elearning.ubpkarawang.ac.id/")
        save("boc", user, "login portal")
        return "Baik, saya akan membuka portal BOC UBP Karawang."

    elif "wikipedia" in m:

        q = msg.replace("wikipedia", "").strip()

        save("chat", user, f"wiki command: {q}")

        replies = [
        f"Baik {user}, saya akan mencari informasi tentang {q} melalui Wikipedia.",
        f"Tunggu sebentar, saya sedang mencari penjelasan mengenai {q}.",
        f"Baik, saya akan membuka Wikipedia dan mencari topik {q}.",
        f"Saya akan membantu menemukan informasi mengenai {q}.",
        f"Sedang memproses pencarian tentang {q} melalui Wikipedia.",
        f"Oke {user}, saya akan mencari informasi yang berkaitan dengan {q}.",
        f"Baik, saya sedang mengambil ringkasan mengenai {q} dari Wikipedia.",
        f"Siap, saya akan menampilkan informasi tentang {q}.",
        f"Tunggu sebentar, saya sedang mencari penjelasan yang relevan mengenai {q}.",
        f"Baik, saya akan mencoba menemukan informasi yang paling sesuai tentang {q}."
        ]

        speak(random.choice(replies))

        return wiki_search_log(user, q)

    elif any(x in m for x in ["siapa", "apa", "jelaskan", "tentang"]):
        save("chat", user, f"auto wiki: {msg}")
        return wiki_answer(msg)

    # =========================
    # 🧮 KALKULATOR
    # =========================

    elif m.startswith("tambah "):
        try:
            num = float(m.replace("tambah ", "").strip())

            calc_add(num)
            hasil = calc_result()

            save_calc(user, "tambah", num, hasil)

            return f"Baik {user}, saya telah menambahkan {num}. Nilai saat ini adalah {hasil}."
        except:
            return "Format salah. Contoh: tambah 1"


    elif m.startswith("kurang "):
        try:
            num = float(m.replace("kurang ", "").strip())

            calc_subtract(num)
            hasil = calc_result()

            save_calc(user, "kurang", num, hasil)

            return f"Baik {user}, saya telah mengurangi {num}. Nilai saat ini adalah {hasil}."
        except:
            return "Format salah. Contoh: kurang 1"


    elif m.startswith("kali "):
        try:
            num = float(m.replace("kali ", "").strip())

            calc_multiply(num)
            hasil = calc_result()

            save_calc(user, "kali", num, hasil)

            return f"Baik {user}, saya telah mengalikan dengan {num}. Nilai saat ini adalah {hasil}."
        except:
            return "Format salah. Contoh: kali 2"


    elif m.startswith("bagi "):
        try:
            num = float(m.replace("bagi ", "").strip())

            if num == 0:
                return "Maaf, pembagian dengan nol tidak diperbolehkan."

            calc_divide(num)
            hasil = calc_result()

            save_calc(user, "bagi", num, hasil)

            return f"Baik {user}, saya telah membagi dengan {num}. Nilai saat ini adalah {hasil}."
        except:
            return "Format salah. Contoh: bagi 2"


    elif m in ["hasil", "sama dengan"]:
        hasil = calc_result()
        return f"Baik {user}, hasil perhitungan saat ini adalah {hasil}."


    elif m == "reset kalkulator":
        calc_reset()
        return "Baik, kalkulator berhasil direset menjadi 0."


    elif m == "lihat kalkulator":
        show_csv(FILES.get("calculator"))
        return "Baik, saya menampilkan riwayat kalkulator."


    elif m.startswith("hapus kalkulator "):
        target_id = m.replace("hapus kalkulator ", "").strip()

        if not target_id:
            return "Masukkan ID yang ingin dihapus."

        return delete_by_id(FILES.get("calculator"), target_id)


    elif m == "refresh kalkulator":
        return refresh_csv(FILES.get("calculator"))

    # =========================
    # ⏰ WAKTU SYSTEM
    # =========================
    elif "jam" in m or "waktu" in m:

        now = get_time()

        save("waktu", user, now)

        return (
            f"Baik {user}...\n"
            f"Waktu saat ini menunjukkan kalender {now}.\n"
            f"Setiap detik terus berjalan, membawa kita menuju cerita baru dalam hidup."
        )

    elif m.startswith("gpt"):
        q = msg.replace("gpt", "").strip()
        open_url("https://chat.openai.com")
        save("chat", user, f"gpt request: {q}")
        return wiki_answer(q) if q else "Membuka GPT"

    elif any(x in m for x in ["siapa", "apa", "jelaskan", "tentang"]):
        save("chat", user, f"wiki query: {msg}")
        return wiki_answer(msg)

    # =========================
    # 🗑️ DELETE DATABASE SYSTEM
    # =========================
    elif m.startswith("hapus youtube "):
        return delete_by_id(FILES["youtube"], m.replace("hapus youtube ", "").strip())

    elif m.startswith("hapus google "):
        return delete_by_id(FILES["google"], m.replace("hapus google ", "").strip())

    elif m.startswith("hapus instagram "):
        return delete_by_id(FILES["instagram"], m.replace("hapus instagram ", "").strip())

    elif m.startswith("hapus chat "):
        return delete_by_id(FILES["chat"], m.replace("hapus chat ", "").strip())

    # =========================
    # REFRESH DATABASE COMMAND
    # =========================

    elif m == "refresh youtube":
        return refresh_csv(FILES["youtube"])

    elif m == "refresh google":
        return refresh_csv(FILES["google"])

    elif m == "refresh instagram":
        return refresh_csv(FILES["instagram"])

    elif m == "refresh scholar":
        return refresh_csv(FILES["scholar"])

    elif m == "refresh roblox":
        return refresh_csv(FILES["roblox"])

    elif m == "refresh canva":
        return refresh_csv(FILES["canva"])

    elif m == "refresh wa":
        return refresh_csv(FILES["wa"])

    elif m == "refresh boc":
        return refresh_csv(FILES["boc"])

    elif m == "refresh chat":
        return refresh_csv(FILES["chat"])
    
    elif m == "refresh miniwa":

        refresh_csv("miniwa_chat.csv")
        refresh_csv("miniwa_users.csv")

        return "Mini WhatsApp berhasil di-refresh"

    elif m == "refresh data":

        print("\n⚠️ PERINGATAN")
        print("Semua database akan dihapus!")

        konfirmasi = input(
            "Ketik YA untuk melanjutkan: "
        )

        if konfirmasi.upper() == "YA":
            return refresh_all_data()

        return "Refresh dibatalkan"

    # =========================
    # LIHAT DATABASE
    # =========================

    elif "lihat database" in m or "liat database" in m:
        show_database_table()
        return "Menampilkan database"
    
    # =========================
    # INTERAKTIF RARA AI
    # =========================
    elif "halo" in m:
        return f"Halo {user}, ada yang bisa Rara bantu hari ini?"

    elif "selamat pagi" in m:
        return f"Selamat pagi {user}, semoga harimu menyenangkan."

    elif "selamat siang" in m:
        return f"Selamat siang {user}, ada yang ingin dicari?"

    elif "selamat malam" in m:
        return f"Selamat malam {user}, jangan lupa istirahat ya."

    elif "terima kasih" in m:
        return "Sama-sama. Senang bisa membantu."

    elif "siapa kamu" in m:
        return "Aku Rara AI, asisten virtual pribadi milikmu."

# =========================
# CHAT LOOP
# =========================
def chat():
    print("\n" + "=" * 40)
    print("🤖 ASISTEN RARA AI BY RAJENDRA DEV ")
    print("=" * 40)

    user = input("Nama kamu: ")

    speak(f"Halo {user}... selamat datang tuan.")

    speak("Saya Rara, asisten digital yang siap membantu kamu kapan saja.")

    while True:

        msg = input(f"\n{user}: ")

        if msg.lower() in ["exit", "keluar"]:
            speak(
                "Sampai jumpa, semoga harimu selalu baik dan saya akan selalu siap saat kamu kembali."
            )
            break

        # PANGGIL AI HANYA SEKALI
        reply = ai(user, msg)

        # SPEAK HANYA SEKALI
        if reply:
            speak(reply)

        # SIMPAN CHAT USER
        save("chat", user, msg)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    chat()