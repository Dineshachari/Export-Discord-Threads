import subprocess
import os
import time
import requests
from math import floor
from urllib.parse import urlencode

def get_channel_info(channel_id, auth_token):
    """
    Fetches channel information from Discord API.
    """
    url = f'https://discord.com/api/v9/channels/{channel_id}'
    headers = {'Authorization': auth_token.strip()}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('name', channel_id) # Returns channel name if found, otherwise channel_id
    return channel_id # Returns channel_id if API call fails

def get_thread_info(thread_id, auth_token):
    """
    Fetches thread information from Discord API.
    """
    url = f'https://discord.com/api/v9/channels/{thread_id}'
    headers = {'Authorization': auth_token.strip()}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return {
            'id': thread_id,
            'name': data.get('name', thread_id) # Returns thread name if found, otherwise thread_id
        }
    return {'id': thread_id, 'name': thread_id} # Returns thread_id as name if API call fails

def get_thread_ids(channel_id, auth_token):
    """
    Fetches all thread IDs and names from a Discord channel.
    """
    base = f'https://discord.com/api/v9/channels/{channel_id.strip()}/threads/search?'
    params = {
        'sort_by': 'last_message_time', # Sort threads by last message time
        'sort_order': 'desc',          # Sort in descending order (newest first)
        'limit': 25,                   # Fetch 25 threads per API call (Discord API limit)
        'tag_setting': 'match_some',    # Include threads with any tags (not strictly necessary for thread listing, but kept from original)
        'offset': 0                     # Start from the beginning of the thread list
    }

    s = requests.Session() # Use a session to persist headers across requests
    s.headers = {'Authorization': auth_token.strip()}

    thread_count = None # Initialize thread_count to None, determined on first API response
    threads = []        # Initialize an empty list to store thread information

    while True: # Loop to handle pagination of thread results
        res = s.get(base + urlencode(params)) # Make API request with parameters
        if res.status_code == 200: # Check if API call was successful
            data = res.json() # Parse JSON response

            for thread in data['threads']: # Iterate through threads in the current response
                thread_info = {
                    'id': thread['id'],
                    'name': thread.get('name', thread['id']) # Get thread name, default to ID if name not found
                }
                if thread_info not in threads: # Check for duplicate threads (might occur due to pagination)
                    threads.append(thread_info) # Add thread info to the list if not already present
                else:
                    print(f'Skip {thread["id"]} - seen already') # Debug message for skipped duplicates

            if thread_count is None: # On the first successful response, get total thread count
                thread_count = data['total_results']
                print('Total threads:', thread_count)
            if not data['has_more']: # Check if there are more pages of threads
                break # Exit loop if no more threads to fetch
            params['offset'] += 25 # Increment offset to fetch the next page of threads
        else: # Handle API errors
            print(f'Error {res.status_code}: {res.json()["message"]}') # Print error status code and message
            break # Exit loop if API call fails

    return threads # Return the list of thread information

def sanitize_filename(filename):
    """
    Remove invalid characters from filename
    """
    invalid_chars = '<>:"/\\|?*' # Define characters invalid in filenames
    for char in invalid_chars: # Iterate through invalid characters
        filename = filename.replace(char, '_') # Replace each invalid character with underscore
    return filename # Return the sanitized filename

def export_threads_html_with_assets(threads, discord_token, discord_exporter_cli_path, channel_name, base_directory="discord_exports"):
    """
    Exports a list of Discord threads to HTML with assets using DiscordChatExporter.Cli.
    All files and assets will be stored in a channel-specific directory.
    """
    output_directory = os.path.join(base_directory, channel_name) # Create channel-specific output directory
    os.makedirs(output_directory, exist_ok=True) # Create directory if it doesn't exist

    assets_dir = os.path.join(output_directory, "assets") # Create assets subdirectory within channel directory
    os.makedirs(assets_dir, exist_ok=True) # Create assets directory if it doesn't exist

    for thread in threads: # Iterate through the list of threads to export
        safe_name = sanitize_filename(thread['name']) # Sanitize thread name for use as filename
        output_file_path = os.path.join(output_directory, f"{safe_name}.html") # Define output HTML file path

        command = [ # Construct the command to execute DiscordChatExporter.Cli
            discord_exporter_cli_path, # Path to the DiscordChatExporter.Cli executable
            "export",                  # 'export' command for the CLI tool
            "-t", discord_token,        # Discord token for authentication
            "-c", thread['id'],         # Channel/Thread ID to export
            "-f", "HtmlDark",          # Output format: HTML with dark theme
            "--media",                 # Download media files (images, attachments)
            "--media-dir", assets_dir,  # Directory to save media files
            "-o", output_file_path      # Output file path for the HTML export
        ]

        print(f"Exporting thread: {thread['name']}...") # Informative message about thread export
        try: # Use try-except block to handle potential errors during subprocess execution
            process = subprocess.run(command, capture_output=True, text=True, check=True) # Execute the command
            # capture_output=True: Capture stdout and stderr
            # text=True: Decode stdout and stderr as text
            # check=True: Raise CalledProcessError if return code is non-zero
            print(f"Thread '{thread['name']}' exported successfully to: {output_file_path}") # Success message
            if process.stderr: # Print any standard error output from the CLI tool (for debugging)
                print(f"Standard Error (Thread: {thread['name']}):")
                print(process.stderr)

        except subprocess.CalledProcessError as e: # Catch errors if the CLI tool returns a non-zero exit code
            print(f"Error exporting thread: {thread['name']}") # Error message
            print(f"Command: {e.cmd}") # Print the command that failed
            print(f"Return Code: {e.returncode}") # Print the return code of the failed command
            print(f"Standard Output:\n{e.stdout}") # Print standard output
            print(f"Standard Error:\n{e.stderr}") # Print standard error
        except FileNotFoundError: # Catch error if DiscordChatExporter.Cli is not found at the specified path
            print(f"Error: DiscordChatExporter.Cli not found at path: {discord_exporter_cli_path}")
            print("Please ensure the path is correct.")
            return # Exit the function if CLI tool is not found
        except Exception as e: # Catch any other unexpected exceptions
            print(f"An unexpected error occurred while exporting thread: {thread['name']}")
            print(e) # Print the exception details

if __name__ == "__main__":
    # --- Configuration ---
    discord_cli_path = r"/path/to/DiscordChatExporter.Cli" # **[Sensitive: Path to DiscordChatExporter.Cli, needs to be configured by user]**
    token = "YOUR_DISCORD_BOT_TOKEN" # **[Sensitive: Discord Bot Token, needs to be replaced with your actual token]**
    channel_id = input('Enter the forum channel ID: ') # Prompts user to enter the Discord channel ID
    base_directory = "discord_exports" # Base directory where exports will be saved
    # --- End Configuration ---

    if not os.path.exists(discord_cli_path): # Check if DiscordChatExporter.Cli exists at the specified path
        print(f"DiscordChatExporter.Cli not found at: {discord_cli_path}")
        print("Please update 'discord_cli_path' in the script to the correct path.")
    else: # Proceed if DiscordChatExporter.Cli is found
        print(f"Fetching channel information...")
        channel_name = get_channel_info(channel_id, token) # Get channel name using Discord API
        print(f"Channel name: {channel_name}")

        print(f"Fetching threads from channel {channel_id}...")
        threads = get_thread_ids(channel_id, token) # Get list of thread IDs and names from the channel

        if threads: # Check if any threads were found
            print(f"Found {len(threads)} threads. Starting export...")
            export_threads_html_with_assets(threads, token, discord_cli_path, channel_name, base_directory) # Export threads to HTML
            print(f"\nThread exports completed! Output directory: {os.path.join(base_directory, channel_name)}") # Completion message with output directory
        else:
            print("No threads found in the channel.") # Message if no threads are found
