import requests
import polars as pl
import os
import re

def modify_file(input_file, output_file, string_to_add):
  with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
    for line in f_in:
      # Remove trailing newline character if present
      line = line.rstrip('\n')
      # Add the string and a newline character
      modified_line = line + string_to_add + '\n'
      f_out.write(modified_line)


def check_string1(string):
    if "v" in string[0]: 
        if not "." in string[1]: 
            filtered_string = "".join([char for char in string if char.isalpha()]) 
            return (filtered_string == "v") and len(filtered_string) == 1 
        else: return False 
    else: return False
    
def check_string2(string):
    if re.fullmatch(r'[0-9.]+', string):
        return True


def check_strings(value, string1, string2):
    if string1 in value and string2 in value:
        return True
    else:
        return False

df_issues = pl.read_csv("data/OpenPRs.csv")


pat = os.environ["TOKEN"]

headers = {"Authorization": f"token {pat}",
           "Accept": "application/vnd.github.v3+json",
           }

df = pl.read_csv("data/GitHub_Releasess.csv")
df_new = df.filter(pl.col('update_requires') == 'Yes')
df_new = df_new.filter(pl.col('extension') != 'zip')
df_new.write_csv("data/GitHub_Releasessss.csv")    

commands = []

for row in df_new.rows():
    username, reponame, extension, pkgs_name, pkg_pattern, release_tag = row[0], row[1], row[3], row[4],  row[5], row[8]
    
    if not release_tag: continue

    download_urls = list()
    # username = "AppFlowy-IO"
    # reponame = "AppFlowy"
    # release_tag = "0.5.0"  # Check the actual release tag from the Releases tab
    
    base_url = f"https://api.github.com/repos/{username}/{reponame}/releases/tags"
    url = f"{base_url}/{release_tag}"
    
    if check_string1(release_tag.lower()):
        pass
    elif check_string1(release_tag.lower()):
        pass
    else:
        continue
    
    try:
        response = requests.get(url, headers = headers)
        response.raise_for_status()  # Raise an error for non-200 status codes
    
        if response.status_code == 200:
            data = response.json()
            if data:
                for asset in data["assets"]:
                    download_url = asset["browser_download_url"]
                    download_urls.append(download_url)
                    
                    #print(f"Download URL: {download_url}")
            else:
                print(f"No releases found for {username}/{reponame} with tag {release_tag}")
        else:
            print(f"Error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        
    proper_urls = []
    
    for download_url in download_urls:
        if f".{extension}" in download_url:
            proper_urls.append(download_url) 
        
    komac_pkgs_name = pkgs_name
    komac_version = release_tag.replace('v', '')
    komac_version = komac_version.replace('V', '')

    for value in df_issues['Title']:
        result = check_strings(value, komac_pkgs_name, komac_version)
        if result: continue
    
    if len(proper_urls) == 1:
        komac_download_url = proper_urls[0]
        
        command = f"komac update --identifier {komac_pkgs_name} --version {komac_version} --urls {komac_download_url} --submit --token"
        commands.append(command)
    

file_name = "komac_commands.sh"
with open(file_name, "w") as file:  # Open a file in write mode
    file.write("\n".join(commands))  # Join elements with newlines and write to file

print(commands)

string_to_add = f" {pat}"

modify_file(file_name, file_name, string_to_add)

print(f"Successfully modified {file_name} and saved the result to {file_name}")

