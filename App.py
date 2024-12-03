from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import os
import time

# Configurazione di Chrome in modalità completamente headless
def configure_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Modalità headless
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")  # Per garantire che i contenuti siano caricati correttamente
    chrome_options.add_argument("--log-level=3")  # Minimizza i log
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument("--disable-extensions")  # Disabilita le estensioni
    chrome_options.add_argument("--disable-popup-blocking")  # Disabilita i popup
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Nasconde che è un browser automatizzato
    return chrome_options

# Funzione per ottenere le date del mese corrente
def get_current_month_dates():
    today = datetime.today()
    first_day = today.replace(day=1).strftime("%d/%m/%Y")
    next_month = today.replace(day=28) + timedelta(days=4)
    last_day = (next_month.replace(day=1) - timedelta(days=1)).strftime("%d/%m/%Y")
    return first_day, last_day

# Funzione per effettuare il login
def login(driver, username, password):
    print("Visito il sito di login...")
    login_url = "https://vr.krossbooking.com/pegasoflorencegroupsrl/login?logout=true"
    driver.get(login_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))

    print("Inserisco le credenziali...")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "login_form").click()

    WebDriverWait(driver, 10).until(EC.url_changes(login_url))
    print("Login completato.")

# Funzione per ottenere l'ultimo file scaricato
def get_latest_file_from_downloads(download_folder):
    files = [os.path.join(download_folder, f) for f in os.listdir(download_folder) if f.endswith('.csv')]
    return max(files, key=os.path.getctime) if files else None

# Funzione per attendere il completamento del download
def wait_for_download(download_folder, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        latest_file = get_latest_file_from_downloads(download_folder)
        if latest_file and os.path.exists(latest_file):
            return latest_file
        time.sleep(1)
    return None

# Funzione per scaricare il CSV
def download_csv(driver, first_day, last_day, download_folder):
    print("Visito la pagina delle prenotazioni...")
    reservations_url = f"https://vr.krossbooking.com/pegasoflorencegroupsrl/reservations?from={first_day.replace('/', '%2F')}&to={last_day.replace('/', '%2F')}&type=checkin&apt=&status"
    driver.get(reservations_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "fa-download")))

    print("Clicco su 'Download CSV'...")
    driver.find_element(By.CLASS_NAME, "fa-download").click()

    print("Attendo il completamento del download...")
    return wait_for_download(download_folder)

# Funzione per caricare il CSV
def upload_csv(driver, csv_file):
    print(f"Carico il file CSV: {csv_file}")
    driver.get("https://magenta-souffle-38eb2f.netlify.app/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='root']/div/main/div/div/div/footer/div/div/div/input")))

    upload_input = driver.find_element(By.XPATH, "//*[@id='root']/div/main/div/div/div/footer/div/div/div/input")
    upload_input.send_keys(csv_file)
    print("File CSV caricato con successo.")
    time.sleep(2)

# Funzione per svuotare la cartella dei download
def clear_downloads_folder(download_folder):
    for file in os.listdir(download_folder):
        file_path = os.path.join(download_folder, file)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"File rimosso: {file_path}")
            except Exception as e:
                print(f"Errore nel rimuovere {file_path}: {e}")

# Funzione principale
def main():
    print("Avvio del programma...")
    username = "mirkobologna"
    password = "Pegaso24"
    download_folder = r"C:\Users\Daniel\Downloads"

    while True:
        try:
            # Creazione e configurazione del driver per ogni ciclo
            driver = webdriver.Chrome(options=configure_chrome_options())
            clear_downloads_folder(download_folder)

            first_day, last_day = get_current_month_dates()
            login(driver, username, password)

            csv_file = download_csv(driver, first_day, last_day, download_folder)
            if csv_file:
                upload_csv(driver, csv_file)

        except Exception as e:
            print(f"Errore: {e}")
        finally:
            print("Chiusura del browser...")
            driver.quit()

        # Reset delle informazioni al nuovo ciclo
        print("Reset delle informazioni e preparazione al nuovo ciclo.")
        time.sleep(120)

if __name__ == "__main__":
    main()
