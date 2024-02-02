import os
import requests
import re
import json
import tarfile
import shutil
import subprocess
import tempfile
import pwd
import urllib.request
import zipfile
from html.parser import HTMLParser

# Change to the home folder
os.chdir(os.path.expanduser("~"))

# Check sudo privileges
print("Checking sudo privileges")
try:
    subprocess.run(['sudo', '-v'], check=True)
    print("Sudo credentials authenticated.")
except subprocess.CalledProcessError:
    print("Failed to verify sudo credentials.")
    exit(1)

try:
    # Update and upgrade packages
    subprocess.run(['sudo', 'apt', '-y', 'update'])
    subprocess.run(['sudo', 'apt', '-y', 'upgrade'])
    print("Finished apt upgrade")
except subprocess.CalledProcessError:
    print("Failed to run apt upgrade")
    exit(1)


# Prompt User to select an Ethereum execution client
def is_valid_client(client):
    valid_exec_clients = ['GETH', 'BESU', 'NETHERMIND', 'SKIP']
    return client in valid_exec_clients

while True:
    execution_client = input("\nSelect Execution Client to update: (geth, besu, nethermind, or skip): ").upper()
    if is_valid_client(execution_client):
        print(f"Selected client: {execution_client}")
        break
    else:
        print("Invalid client. Please try again.")

execution_client = execution_client.lower()
execution_client_cap = execution_client.capitalize()

# Prompt User to select a consensus client
def is_valid_consensus_client(client):
    valid_consensus_clients = ['LIGHTHOUSE', 'TEKU', 'PRYSM', 'NIMBUS', 'SKIP']
    return client in valid_consensus_clients

while True:
    consensus_client = input("\nSelect Consensus Client to update: (lighthouse, teku, prysm, nimbus, or skip): ").upper()
    if is_valid_consensus_client(consensus_client):
        print(f"Selected client: {consensus_client}")
        break
    else:
        print("Invalid client. Please try again.")

# Variables

execution_client = execution_client.lower()
consensus_client = consensus_client.lower()



############ NETHERMIND ##################
if execution_client == 'nethermind':
    # Define the Github API endpoint to get the latest release
    url = 'https://api.github.com/repos/NethermindEth/nethermind/releases/latest'

    # Send a GET request to the API endpoint
    response = requests.get(url)

    # Search for the asset with the name that ends in linux-x64.zip
    assets = response.json()['assets']
    download_url = None
    zip_filename = None
    for asset in assets:
        if asset['name'].endswith('linux-x64.zip'):
            download_url = asset['browser_download_url']
            zip_filename = asset['name']
            break

    if download_url is None or zip_filename is None:
        print("Error: Could not find the download URL for the latest release.")
        exit(1)

    # Download the latest release binary
    response = requests.get(download_url)

    # Save the binary to a temporary file
    with tempfile.NamedTemporaryFile('wb', suffix='.zip', delete=False) as temp_file:
        temp_file.write(response.content)
        temp_path = temp_file.name

    # Create a temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract the binary to the temporary directory
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Copy the contents of the temporary directory to /usr/local/bin/nethermind using sudo
        print("Stopping nethermind service")
        subprocess.run(['sudo', 'systemctl', 'stop', 'nethermind'])
        subprocess.run(["sudo", "cp", "-a", f"{temp_dir}/.", "/usr/local/bin/nethermind"])
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'])
        subprocess.run(['sudo', 'systemctl', 'start', 'nethermind'])
        print("Restarted nethermind service")
    # Remove the temporary zip file
    os.remove(temp_path)

    nethermind_version = os.path.splitext(zip_filename)[0]

############ TEKU ##################
# if consensus_client == 'teku':
#     # Change to the home folder
#     os.chdir(os.path.expanduser("~"))

#     # Define the Github API endpoint to get the latest release
#     url = 'https://api.github.com/repos/ConsenSys/teku/releases/latest'

#     # Send a GET request to the API endpoint
#     response = requests.get(url)

#     # Get the latest release tag
#     latest_version = response.json()['tag_name']

#     # Define the download URL for the latest release
#     download_url = f"https://artifacts.consensys.net/public/teku/raw/names/teku.tar.gz/versions/{latest_version}/teku-{latest_version}.tar.gz"
#     teku_version = latest_version
#     # Download the latest release binary
#     response = requests.get(download_url)

#     # Save the binary to the home folder
#     with open('teku.tar.gz', 'wb') as f:
#         f.write(response.content)

#     # Extract the binary to the home folder
#     with tarfile.open('teku.tar.gz', 'r:gz') as tar:
#         tar.extractall()

#     # Copy the binary folder to /usr/local/bin using sudo
#     os.system(f"sudo cp -r teku-{latest_version} /usr/local/bin/teku")

#     # Remove the teku.tar.gz file and extracted binary folder
#     os.remove('teku.tar.gz')
#     shutil.rmtree(f'teku-{latest_version}')

#     print("Teku binary installed successfully!")
#     print(f"Download URL: {download_url}")
#     print(f"teku-v{latest_version}")

################ PRYSM ###################
# if consensus_client == 'prysm':
#     base_url = "https://api.github.com/repos/prysmaticlabs/prysm/releases/latest"
#     response = requests.get(base_url)
#     response_json = response.json()
#     download_links = []

#     for asset in response_json["assets"]:
#         if re.search(r'beacon-chain-v\d+\.\d+\.\d+-linux-amd64$', asset["browser_download_url"]):
#             download_links.append(asset["browser_download_url"])
#         elif re.search(r'validator-v\d+\.\d+\.\d+-linux-amd64$', asset["browser_download_url"]):
#             download_links.append(asset["browser_download_url"])

#     if len(download_links) >= 2:
#         for link in download_links[:2]:
#             cmd = f"curl -LO {link}"
#             os.system(cmd)

#         os.system("mv beacon-chain-*-linux-amd64 beacon-chain")
#         os.system("mv validator-*-linux-amd64 validator")
#         os.system("chmod +x beacon-chain")
#         os.system("chmod +x validator")
#         os.system("sudo cp beacon-chain /usr/local/bin")
#         os.system("sudo cp validator /usr/local/bin")
#         os.system("rm beacon-chain && rm validator")
#     else:
#         print("Error: Could not find the latest release links.")

#     prysm_version = link.split("/")[-1]

#     print(f"Successfully installed Prsym {prysm_version}")

################ NIMBUS ##################
# if consensus_client == 'nimbus':
#     # Change to the home folder
#     os.chdir(os.path.expanduser("~"))

#     # Define the Github API endpoint to get the latest release
#     url = 'https://api.github.com/repos/status-im/nimbus-eth2/releases/latest'

#     # Send a GET request to the API endpoint
#     response = requests.get(url)

#     # Search for the asset with the name that ends in _Linux_amd64.tar.gz
#     assets = response.json()['assets']
#     download_url = None
#     for asset in assets:
#         if '_Linux_amd64' in asset['name'] and asset['name'].endswith('.tar.gz'):
#             download_url = asset['browser_download_url']
#             break

#     if download_url is None:
#         print("Error: Could not find the download URL for the latest release.")
#         exit(1)

#     # Download the latest release binary
#     response = requests.get(download_url)

#     # Save the binary to the home folder
#     with open('nimbus.tar.gz', 'wb') as f:
#         f.write(response.content)

#     # Extract the binary to the home folder
#     with tarfile.open('nimbus.tar.gz', 'r:gz') as tar:
#         tar.extractall()

#     # Find the extracted folder
#     extracted_folder = None
#     for item in os.listdir():
#         if item.startswith("nimbus-eth2_Linux_amd64"):
#             extracted_folder = item
#             break

#     if extracted_folder is None:
#         print("Error: Could not find the extracted folder.")
#         exit(1)

#     # Copy the binary to /usr/local/bin using sudo
#     os.system(f"sudo cp {extracted_folder}/build/nimbus_beacon_node /usr/local/bin")

#     # Remove the nimbus.tar.gz file and extracted folder
#     os.remove('nimbus.tar.gz')
#     os.system(f"rm -r {extracted_folder}")
    
#     version = download_url.split("/")[-2]

#     print("Nimbus binary installed successfully!")
#     print(f"Download URL: {download_url}")
#     print(f"\nSuccessfully Installed Nimbus Version {version}")

############ LIGHTHOUSE ##################
if consensus_client == 'lighthouse':
    # Change to the home folder
    os.chdir(os.path.expanduser("~"))

    # Define the Github API endpoint to get the latest release
    url = 'https://api.github.com/repos/sigp/lighthouse/releases/latest'

    # Send a GET request to the API endpoint
    response = requests.get(url)

    # Search for the asset with the name that ends in x86_64-unknown-linux-gnu.tar.gz
    assets = response.json()['assets']
    download_url = None
    for asset in assets:
        if asset['name'].endswith('x86_64-unknown-linux-gnu.tar.gz'):
            download_url = asset['browser_download_url']
            break

    if download_url is None:
        print("Error: Could not find the download URL for the latest release.")
        exit(1)

    # Download the latest release binary
    response = requests.get(download_url)

    # Save the binary to the home folder
    with open('lighthouse.tar.gz', 'wb') as f:
        f.write(response.content)

    # Extract the binary to the home folder
    with tarfile.open('lighthouse.tar.gz', 'r:gz') as tar:
        tar.extractall()
        
    print("Stopping lighthouse beacon service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'lighthousebeacon'])
    print("Stopping lighthouse validator service")
    subprocess.run(['sudo', 'systemctl', 'stop', 'lighthousevalidator'])

    # Copy the binary to /usr/local/bin using sudo
    os.system("sudo cp lighthouse /usr/local/bin")
    subprocess.run(['sudo', 'systemctl', 'daemon-reload'])
    
    print("Starting lighthouse beacon service")
    subprocess.run(['sudo', 'systemctl', 'start', 'lighthousebeacon'])
    print("Starting lighthouse validator service")
    subprocess.run(['sudo', 'systemctl', 'start', 'lighthousevalidator'])

    # Remove the lighthouse.tar.gz file and extracted binary
    os.remove('lighthouse.tar.gz')
    os.remove('lighthouse')

    lighthouse_version = download_url.split("/")[-2]

    print("Lighthouse binary installed successfully!")
    print(f"Download URL: {download_url}")

######## PRINT OUTPUT ############
print("\nUpdate Successful! See versions listed below:")
# Geth Print
if execution_client == 'geth':
    geth_version = subprocess.run(["geth", "--version"], stdout=subprocess.PIPE).stdout
    if geth_version is not None:
        geth_version = geth_version.decode()
        geth_version = (geth_version.split(" ")[-1]).split("-")[-3]
    else:
        geth_version = ""
    print(f'\nGeth Version: v{geth_version}\n')

# Besu Print
if execution_client == 'besu':
    print(f'\nBesu Version: v{besu_version}\n')

# Nethermind Print
if execution_client == 'nethermind':
    # Use regular expression to extract the version number
    match = re.search(r'(\d+\.\d+\.\d+)', nethermind_version)
    
    if match:
        extracted_version = match.group(1)
        print(f'\nNethermind Version: v{extracted_version}\n')

# Teku Print
if consensus_client == 'teku':
    print(f"Teku Version: v{latest_version}\n")

# Prysm Print
if consensus_client == 'prysm':
    prysm_version = subprocess.run(["beacon-chain", "--version"], stdout=subprocess.PIPE).stdout
    if prysm_version is not None:
        prysm_version = prysm_version.decode().splitlines()[0]
        prysm_version = prysm_version.split("/")[-2]
    else:
        prysm_version = ""
    print(f'Prysm Version: {prysm_version}\n')

# Nimbus Print
if consensus_client == 'nimbus':
    nimbus_version = subprocess.run(["nimbus_beacon_node", "--version"], stdout=subprocess.PIPE).stdout
    if nimbus_version is not None:
        nimbus_version = nimbus_version.decode().splitlines()[0]
        nimbus_version = nimbus_version.split(" ")[-1]
        nimbus_version = nimbus_version.split("-")[-3]
    else:
        nimbus_version = ""
    print(f'Nimbus Version: {nimbus_version}\n')

# LIGHTHOUSE PRINT
if consensus_client == 'lighthouse':
    lighthouse_version = subprocess.run(["lighthouse", "-V"], stdout=subprocess.PIPE).stdout
    if lighthouse_version is not None:
        lighthouse_version = lighthouse_version.decode()
        lighthouse_version = (lighthouse_version.split(" ")[-1]).split("-")[-2]
    else:
        lighthouse_version = ""
    print(f'Lighthouse Version: {lighthouse_version}\n')


