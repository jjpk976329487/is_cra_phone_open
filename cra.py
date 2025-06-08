import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService # For Edge
from selenium.webdriver.edge.options import Options as EdgeOptions # For Edge
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- Configuration ---
CRA_URL = "https://www.canada.ca/en/revenue-agency/corporate/contact-information.html"
REFRESH_INTERVAL_SECONDS = 60
MAX_RETRIES_ELEMENT = 3
ALERT_DURATION_SECONDS = 30 # Duration for the loud alert

# --- Edge WebDriver Configuration ---
EDGEDRIVER_PATH = r"" # Raw string for Windows paths: insert driver exe here 

edge_options = EdgeOptions()
# edge_options.add_argument("--headless")  # Optional: Run in background
edge_options.add_argument("--disable-gpu")
edge_options.add_argument("--no-sandbox") # Often helpful
edge_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.62") # Edge user agent

# Check if the driver path exists
if not os.path.exists(EDGEDRIVER_PATH):
    print(f"ERROR: Edge WebDriver not found at {EDGEDRIVER_PATH}")
    print("Please ensure the path is correct and the msedgedriver.exe file exists.")
    exit()

try:
    service = EdgeService(executable_path=EDGEDRIVER_PATH)
    driver = webdriver.Edge(service=service, options=edge_options)
except Exception as e:
    print(f"Error initializing Edge WebDriver: {e}")
    print("Make sure your Edge browser version is compatible with the msedgedriver version.")
    exit()


# --- Helper for sound ---
def play_loud_alert(duration_seconds=ALERT_DURATION_SECONDS):
    """Plays a more noticeable alert sound for a specified duration."""
    print(f"!!! PLAYING LOUD ALERT FOR {duration_seconds} SECONDS !!!")
    start_time = time.time()

    def _play_windows_beep_loop(duration):
        try:
            import winsound
            loop_start_time = time.time()
            while time.time() - loop_start_time < duration:
                winsound.Beep(2500, 150)
                if time.time() - loop_start_time >= duration: break
                winsound.Beep(2000, 100)
                if time.time() - loop_start_time >= duration: break
                time.sleep(0.05)
        except ImportError:
            print("`winsound` module not found for Windows. Using terminal bell.")
            _play_terminal_bell_loop(duration)
        except Exception as e_winsound:
            print(f"Error with winsound: {e_winsound}. Using terminal bell.")
            _play_terminal_bell_loop(duration)

    def _play_speech_loop(command_template, message, estimated_speech_len_sec, duration):
        loop_start_time = time.time()
        iterations = 0
        while time.time() - loop_start_time < duration:
            if iterations > 0 and (time.time() - loop_start_time + estimated_speech_len_sec > duration + 1):
                break
            safe_message = message.replace("'", "'\\''")
            os.system(command_template.format(message=safe_message))
            iterations += 1
            if time.time() - loop_start_time >= duration:
                break
        print(f"Played speech alert {iterations} times.")

    def _play_terminal_bell_loop(duration):
        loop_start_time = time.time()
        while time.time() - loop_start_time < duration:
            print("\007" * 3, end='', flush=True)
            time.sleep(0.5)
            if time.time() - loop_start_time >= duration: break
            
    try:
        if os.name == 'nt':
            _play_windows_beep_loop(duration_seconds)
        elif os.uname().sysname == "Darwin":
            alert_message = "Alert. C R A. Line open."
            estimated_len = 1.5
            _play_speech_loop("say '{message}'", alert_message, estimated_len, duration_seconds)
        else: # Linux
            alert_message = "Alert. C R A. Line open."
            estimated_len = 1.5
            command_to_use = None
            if os.system("command -v spd-say > /dev/null") == 0:
                command_to_use = "spd-say '{message}'"
            elif os.system("command -v espeak > /dev/null") == 0:
                command_to_use = "espeak -a 150 '{message}'"
            if command_to_use:
                _play_speech_loop(command_to_use, alert_message, estimated_len, duration_seconds)
            else:
                print("No speech synthesizer (spd-say, espeak) found on Linux. Using terminal bell.")
                _play_terminal_bell_loop(duration_seconds)
    except Exception as e:
        print(f"An unexpected error occurred in play_loud_alert: {e}. Using terminal bell as final fallback.")
        _play_terminal_bell_loop(duration_seconds)
    print(f"Loud alert finished after approximately {time.time() - start_time:.1f} seconds.")


def get_cra_wait_time(current_driver):
    try:
        summary_xpath = "//summary[normalize-space()='Personal taxes, benefits and trusts']"
        menu_summary = WebDriverWait(current_driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, summary_xpath))
        )
        details_element = menu_summary.find_element(By.XPATH, "./parent::details")
        if not details_element.get_attribute("open"):
            current_driver.execute_script("arguments[0].scrollIntoView(true);", menu_summary)
            time.sleep(0.5)
            menu_summary.click()
            print("Clicked on 'Personal taxes, benefits and trusts' menu.")
            time.sleep(2)
        else:
            print("'Personal taxes, benefits and trusts' menu was already open.")

        wait_time_element_xpath = (
            "//tr[@id='prs-01']//ul[contains(@class, 'fa-ul')]"
            "//div[strong[contains(text(), 'Wait time:')]]/a"
        )
        wait_time_anchor = WebDriverWait(current_driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, wait_time_element_xpath))
        )
        wait_time_text = wait_time_anchor.text.strip()
        if not wait_time_text:
            anchor_html = wait_time_anchor.get_attribute('innerHTML')
            soup_anchor = BeautifulSoup(anchor_html, 'html.parser')
            for inv_span in soup_anchor.find_all('span', class_='wb-inv'):
                inv_span.decompose()
            wait_time_text = soup_anchor.get_text(strip=True)
        return wait_time_text
    except Exception as e:
        print(f"Error extracting wait time: {e}")
        return None

def main():
    print(f"Monitoring CRA contact page using Microsoft Edge: {CRA_URL}")
    print(f"Will check for Personal Taxes (1-800-959-8281) line status.")
    print(f"Refresh interval: {REFRESH_INTERVAL_SECONDS} seconds.\n")

    global driver # Make sure 'driver' is accessible in finally block

    try:
        driver.get(CRA_URL)
        time.sleep(3)

        retry_count = 0
        while True:
            print(f"--- [{time.strftime('%Y-%m-%d %H:%M:%S')}] Attempting to check ---")
            wait_time = get_cra_wait_time(driver) # Pass the driver instance

            if wait_time:
                print(f"Current Wait Time Status: '{wait_time}'")
                if "not available" not in wait_time.lower() and "unavailable" not in wait_time.lower():
                    print("\n" + "="*50)
                    print(">>> !!! CRA PHONE LINE IS LIKELY OPEN !!! <<<")
                    print(f">>> Wait Time: {wait_time} <<<")
                    print("="*50 + "\n")
                    play_loud_alert()
                    break
                else:
                    print("Line is currently not available. Will re-check...")
                retry_count = 0
            else:
                print("Failed to get wait time. Retrying or refreshing.")
                retry_count += 1
                if retry_count >= MAX_RETRIES_ELEMENT:
                    print(f"Max retries ({MAX_RETRIES_ELEMENT}) for element finding reached. Performing full page refresh.")
                    driver.refresh()
                    time.sleep(5)
                    retry_count = 0
                else:
                    time.sleep(5)

            print(f"Waiting for {REFRESH_INTERVAL_SECONDS} seconds before next check...")
            time.sleep(REFRESH_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    except Exception as e:
        print(f"A critical error occurred: {e}")
    finally:
        print("Closing browser.")
        if 'driver' in globals() and driver: # Check if driver was successfully initialized
            driver.quit()

if __name__ == "__main__":
    main()
