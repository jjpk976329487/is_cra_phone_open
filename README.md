# CRA Wait Time Checker

This Python script automates the tedious process of checking the Canada Revenue Agency (CRA) website to see if their personal tax phone lines are open. When the line becomes available, it triggers a loud, persistent audio alert to notify you.

It's designed for anyone who has been frustrated by repeatedly refreshing the CRA "Contact us" page only to find the lines are still "not available."

## Features

-   **Automated Monitoring**: Runs in the background, checking the CRA website at a set interval.
-   **Specific Target**: Monitors the "Personal taxes, benefits and trusts" phone line status (1-800-959-8281).
-   **Loud, Persistent Alert**: When the line is open, it plays a loud, continuous alert for a configurable duration to ensure you don't miss it.
-   **Configurable**: Easily change the refresh interval, alert duration, and WebDriver path.
-   **Robust Scraping**: Uses Selenium's explicit waits to handle page load times and has retry logic for finding elements.

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.x**: If you don't have it, download it from [python.org](https://www.python.org/downloads/).
2.  **Microsoft Edge Browser**: The script is configured to use MS Edge.
3.  **Microsoft Edge WebDriver**: This is a separate executable that allows Selenium to control the Edge browser.
    -   **Crucially, the WebDriver version must match your MS Edge browser version.**
    -   Check your Edge version by going to `edge://settings/help`.
    -   Download the matching WebDriver from the [official Microsoft Edge WebDriver page](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/).
4.  **Python Libraries**: The script depends on `selenium` and `beautifulsoup4`.

## Setup and Installation

1.  **Download the Script**: Save the Python script to a folder on your computer (e.g., `cra_checker.py`).

2.  **Install Python Libraries**: Open your terminal or command prompt and run the following command to install the necessary packages:
    ```sh
    pip install selenium beautifulsoup4
    ```

3.  **Place the WebDriver**: Unzip the `msedgedriver.exe` file you downloaded and place it in a known location on your computer. A good practice is to create a dedicated `drivers` folder.

4.  **Configure the Script**: Open the script file (`cra_checker.py`) in a text editor and update the `EDGEDRIVER_PATH` variable to point to the exact location of your `msedgedriver.exe` file.

    **Important for Windows users**: Use a raw string (`r"..."`) or double backslashes (`\\`) in your path to avoid issues.

    ```python
    # Example of a correct path in the script
    EDGEDRIVER_PATH = r"C:\Users\YourUser\Documents\WebDrivers\msedgedriver.exe"
    ```

## How to Run

1.  Open a terminal or command prompt.
2.  Navigate to the directory where you saved the script.
3.  Run the script using Python:
    ```sh
    python cra_checker.py
    ```

The script will launch a new Microsoft Edge browser window and begin monitoring the CRA page. You will see status updates printed in your terminal. You can minimize the browser window and the terminal while it runs.

When the phone line is open, the loud alert will sound, and the script will terminate. To stop the script manually at any time, press `Ctrl+C` in the terminal.

## Configuration

You can customize the script's behavior by modifying these variables at the top of the file:

-   `CRA_URL`: The target URL to monitor. (Default is the CRA Contact page).
-   `REFRESH_INTERVAL_SECONDS`: The number of seconds to wait between checks. **(Default: 60)**. Avoid setting this too low to be respectful to the CRA's servers.
-   `ALERT_DURATION_SECONDS`: The number of seconds the loud alert will play for. **(Default: 30)**.

## Important Notes & Disclaimer

-   **Website Changes**: This script relies on the specific structure (HTML layout) of the CRA website. If the CRA updates their website, the script may break. It might require updating the XPath selectors in the `get_cra_wait_time` function.
-   **Not Affiliated with CRA**: This tool is an unofficial, third-party script and is not endorsed by or affiliated with the Canada Revenue Agency.
-   **Use Responsibly**: Do not set the refresh interval to an extremely low value (e.g., less than 15-20 seconds), as this could place an unnecessary load on the CRA's web servers.
