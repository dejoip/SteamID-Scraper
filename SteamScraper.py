import itertools
import os
import http.client
import json
import time
import re
from colorama import Fore, Style

API_KEY = "YOUR_API_KEY"  # Replace with your Steam Web API key

def is_valid_steam_id(api_key, id):
    conn = http.client.HTTPSConnection("api.steampowered.com")
    url = f"/ISteamUser/ResolveVanityURL/v0001/?key={api_key}&vanityurl={id}"
    conn.request("GET", url)
    response = conn.getresponse()
    response_text = response.read().decode('utf-8')
    
    if not response_text:
        return f"{Fore.YELLOW}INVALID RESPONSE{Style.RESET_ALL}", "Empty response"
    
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as e:
        return f"{Fore.YELLOW}INVALID JSON{Style.RESET_ALL}", response_text

    if data.get("response") and data["response"].get("success") == 1:
        status = f"{Fore.RED}TAKEN{Style.RESET_ALL}"
    else:
        status = f"{Fore.GREEN}FREE{Style.RESET_ALL}"
    
    return status, response_text

def sanitize_words(words):
    sanitized_words = [re.sub(r'[\x00-\x1F]+', '', word) for word in words]
    return sanitized_words

def generate_combinations(characters):
    combinations = list(itertools.product(characters, repeat=3))
    return [''.join(combination) for combination in combinations]

def check_steam_ids(api_key, characters, output_path, run):
    url_count = 0
    with open(output_path, "a") as file:
        for i, id in enumerate(characters, start=1):
            status, response_text = is_valid_steam_id(api_key, id)
            url_count += 1
            print(f"{run} | {Fore.BLUE}URL {url_count}{Style.RESET_ALL} | https://steamcommunity.com/id/{id} | {status}")
            if "FREE" in status:
                file.write(f"{run} | {Fore.BLUE}URL {url_count}{Style.RESET_ALL} | https://steamcommunity.com/id/{id} | {status}\n")
            print(f"Response: {response_text}\n")

def main():
    print("Select an option:")
    print("1. Use included ASCII library")
    print("2. Use custom character library")
    print("3. Use custom word library")
    
    option = input("Enter the option (1/2/3): ")
    
    if option == '1':
        valid_characters = [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)] + [str(i) for i in range(10)] + ["-"]
        characters = generate_combinations(valid_characters)
    elif option == '2':
        custom_library_path = input("Enter the path to a .txt file with the custom character library: ")
        with open(custom_library_path, 'r') as file:
            characters = file.read().strip()
    elif option == '3':
        custom_word_library_path = input("Enter the path to a .txt file with the custom word library: ")
        with open(custom_word_library_path, 'r') as file:
            custom_words = file.read().split('\n')
            sanitized_custom_words = sanitize_words(custom_words)
            characters = sanitized_custom_words
    else:
        print("Invalid option. Please select 1, 2, or 3.")
        return

    output_path = input("Enter the output path (or press Enter for the default path): ")
    if not output_path:
        output_path = os.path.abspath(os.path.dirname(__file__))
    
    output_path = os.path.join(output_path, "nonexistent_ids.txt")
    
    run = 1

    while True:
        start_time = time.time()
        check_steam_ids(API_KEY, characters, output_path, run)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Run {run} completed in {elapsed_time} seconds")
        
        run += 1
        again = input("Do you want to run another check? (yes/no): ")
        if again.lower() != "yes":
            break

if __name__ == "__main__":
    main()
