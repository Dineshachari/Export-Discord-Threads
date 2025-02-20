This Python script is designed to export Discord forum threads from a specified channel into individual HTML files. It uses the Discord API to fetch thread information and an external command-line tool, DiscordChatExporter.Cli, to perform the actual export to HTML.

Let's break down each part of the code:

1. Imports:

subprocess: Allows running external commands, in this case, DiscordChatExporter.Cli.

os: Provides functions for interacting with the operating system, like creating directories and joining paths.

time: Used for time-related operations (though not explicitly used in the provided code snippet, it's often used in similar scripts for delays or timestamps).

requests: A library for making HTTP requests, used here to interact with the Discord API.

math.floor: Used for rounding down numbers (not used in this specific snippet, might be remnants from a larger script).

urllib.parse.urlencode: Used to encode parameters into a URL query string for API requests.

2. Functions:

get_channel_info(channel_id, auth_token):

Purpose: Fetches the name of a Discord channel using the Discord API.

Parameters:

channel_id: The ID of the Discord channel.

auth_token: Your Discord authorization token (user token or bot token).

Functionality:

Constructs the Discord API URL for fetching channel information.

Sets the Authorization header with the provided auth_token.

Makes a GET request to the API.

If the request is successful (status code 200):

Parses the JSON response.

Returns the channel name from the 'name' field in the JSON data. If 'name' is not found, it returns the channel_id as a fallback.

If the request fails, it returns the channel_id. This acts as a default name if the API call fails.

get_thread_info(thread_id, auth_token):

Purpose: Fetches information about a specific Discord thread (currently only name and ID).

Parameters:

thread_id: The ID of the Discord thread.

auth_token: Your Discord authorization token.

Functionality:

Similar to get_channel_info, but fetches information for a specific thread.

Returns a dictionary containing the thread's 'id' and 'name'. If the API call fails or the name is not found, the 'name' in the dictionary defaults to the thread_id.

get_thread_ids(channel_id, auth_token):

Purpose: Retrieves a list of thread IDs and names from a given Discord channel. It handles pagination to fetch all threads, as the Discord API limits the number of threads returned per request.

Parameters:

channel_id: The ID of the Discord channel to fetch threads from.

auth_token: Your Discord authorization token.

Functionality:

Constructs the base Discord API URL for searching threads within a channel.

Sets up parameters for the API request:

sort_by: Sorts threads by last_message_time.

sort_order: Sorts in descending order (newest threads first).

limit: Sets the number of threads to fetch per request (25 is the Discord API limit for this endpoint).

tag_setting: Includes threads with any tags (potentially not strictly necessary for just listing threads).

offset: Starts at 0 for the first page of results and is incremented for subsequent pages to handle pagination.

Creates a requests.Session() to reuse the connection and headers for multiple requests.

Sets the Authorization header for the session.

Initializes thread_count to None and an empty list threads to store thread information.

Enters a while True loop to handle pagination:

Makes a GET request to the Discord API with the current parameters.

If the request is successful:

Parses the JSON response.

Iterates through the 'threads' in the response:

Creates a thread_info dictionary with 'id' and 'name'.

Checks for duplicate threads (to avoid adding the same thread multiple times if pagination overlaps).

Appends thread_info to the threads list if it's not a duplicate.

If thread_count is None (first response), it gets the total number of threads from data['total_results'].

Checks data['has_more'] to see if there are more pages of threads. If not, it breaks the loop.

Increments params['offset'] by 25 to fetch the next page.

If the request fails, it prints an error message and breaks the loop.

Returns the threads list containing dictionaries of thread IDs and names.

sanitize_filename(filename):

Purpose: Removes characters that are invalid in filenames across different operating systems. This ensures that thread names can be used as filenames without causing errors.

Parameter:

filename: The string to sanitize (typically a thread name).

Functionality:

Defines a string invalid_chars containing characters that are commonly invalid in filenames (<>:"/\|?*).

Iterates through invalid_chars and replaces each invalid character in the filename with an underscore _.

Returns the sanitized filename.

export_threads_html_with_assets(threads, discord_token, discord_exporter_cli_path, channel_name, base_directory="discord_exports"):

Purpose: This is the core function for exporting threads to HTML. It uses the DiscordChatExporter.Cli command-line tool to perform the export. It handles creating output directories and running the external tool for each thread.

Parameters:

threads: A list of thread information dictionaries (as returned by get_thread_ids).

discord_token: Your Discord authorization token.

discord_exporter_cli_path: The file path to the DiscordChatExporter.Cli executable.

channel_name: The name of the Discord channel (used for creating output directories).

base_directory: The base directory where all exports will be saved (defaults to "discord_exports").

Functionality:

Constructs the output directory path based on base_directory and channel_name.

Creates the output directory and an assets subdirectory within it (using os.makedirs(exist_ok=True) to avoid errors if directories already exist).

Iterates through the threads list:

Sanitizes the thread name using sanitize_filename to create a safe filename.

Constructs the full output file path for the HTML file.

Constructs the command to run DiscordChatExporter.Cli as a list of strings. This is important for subprocess.run to handle spaces and arguments correctly. The command includes:

Path to DiscordChatExporter.Cli executable.

"export" command.

"-t" and discord_token for authentication.

"-c" and thread['id'] to specify the thread to export.

"-f" "HtmlDark" to set the output format to HTML with a dark theme.

"--media" to download media files (attachments, images).

"--media-dir" and assets_dir to specify where to save media files.

"-o" and output_file_path to set the output HTML file path.

Prints a message indicating that it's exporting a thread.

Uses a try-except block to handle potential errors during the subprocess.run call:

subprocess.run(command, capture_output=True, text=True, check=True): Executes the command.

capture_output=True: Captures the standard output and standard error of the command.

text=True: Decodes the output as text (UTF-8).

check=True: Raises a subprocess.CalledProcessError if the command returns a non-zero exit code (indicating an error).

If successful, prints a success message and prints any standard error output from DiscordChatExporter.Cli (useful for debugging).

except subprocess.CalledProcessError as e:: Catches errors from DiscordChatExporter.Cli (e.g., if the export fails). Prints detailed error information including the command, return code, standard output, and standard error.

except FileNotFoundError:: Catches FileNotFoundError if DiscordChatExporter.Cli is not found at the specified path. Prints an error message and returns from the function.

except Exception as e:: Catches any other unexpected exceptions during the export process. Prints a generic error message and the exception details.

3. if __name__ == "__main__": Block:

This block of code runs only when the script is executed directly (not when imported as a module).

Configuration:

discord_cli_path = r"/path/to/DiscordChatExporter.Cli": [SENSITIVE PATH - NEEDS USER CONFIGURATION] This line defines the path to the DiscordChatExporter.Cli executable. You need to replace "/path/to/DiscordChatExporter.Cli" with the actual path to the executable on your system. The r prefix indicates a raw string, which is helpful for Windows paths that use backslashes.

token = "YOUR_DISCORD_BOT_TOKEN": [SENSITIVE TOKEN - NEEDS USER REPLACEMENT] This line is where you need to put your Discord bot token or user authorization token. Replace "YOUR_DISCORD_BOT_TOKEN" with your actual token. Important: For this script, a user authorization token is likely required as it's interacting with the Discord API to get channel and thread information, which bot tokens might not have sufficient permissions for in all cases, especially for accessing private channels.

channel_id = input('Enter the forum channel ID: '): Prompts the user to enter the Discord forum channel ID they want to export threads from.

base_directory = "discord_exports": Sets the base directory where the exported HTML files and assets will be saved. You can change this if you want to save them somewhere else.

Path Check:

if not os.path.exists(discord_cli_path):: Checks if the DiscordChatExporter.Cli executable exists at the specified path. If not, it prints an error message and instructions to update the discord_cli_path variable.

Execution Flow (if DiscordChatExporter.Cli is found):

print(f"Fetching channel information..."): Prints a message indicating that it's fetching channel info.

channel_name = get_channel_info(channel_id, token): Calls get_channel_info to get the channel name from the Discord API.

print(f"Channel name: {channel_name}"): Prints the fetched channel name.

print(f"Fetching threads from channel {channel_id}..."): Prints a message indicating thread fetching.

threads = get_thread_ids(channel_id, token): Calls get_thread_ids to get the list of thread IDs and names.

if threads:: Checks if any threads were found.

print(f"Found {len(threads)} threads. Starting export..."): Prints the number of threads found and starts the export process.

export_threads_html_with_assets(threads, token, discord_cli_path, channel_name, base_directory): Calls export_threads_html_with_assets to export all the fetched threads to HTML.

print(f"\nThread exports completed! Output directory: {os.path.join(base_directory, channel_name)}"): Prints a completion message and the output directory path.

else: print("No threads found in the channel."): If no threads were found, prints a message indicating that.

Sensitive Information Removed and Placeholders:

discord_cli_path = r"/path/to/DiscordChatExporter.Cli": Replaced the user-specific path with a placeholder "/path/to/DiscordChatExporter.Cli". You MUST replace this with the actual path to the DiscordChatExporter.Cli executable on your system. This path will vary depending on where you downloaded and extracted the tool.

token = "YOUR_DISCORD_BOT_TOKEN": Replaced the actual Discord token with the placeholder "YOUR_DISCORD_BOT_TOKEN". You MUST replace this with your valid Discord bot token or, more likely, a user authorization token. Be very careful about storing and handling your Discord token securely. Do not commit your actual token to public repositories.

To use this code:

Install requests library:

pip install requests
Use code with caution.
Bash
Download DiscordChatExporter.Cli: Download the appropriate version of DiscordChatExporter.Cli for your operating system from the official GitHub repository or releases page.

Update discord_cli_path: Edit the discord_cli_path variable in the if __name__ == "__main__": block to point to the correct location of the DiscordChatExporter.Cli executable on your system.

Get a Discord Token: You'll need a Discord authorization token. For personal use cases like this, a user token is often used. Be very careful about how you obtain and use user tokens as they are sensitive. Generating user tokens directly is generally discouraged and can be against Discord's Terms of Service. Using a bot token might be possible depending on the channel's permissions, but might not have the necessary access to all threads in all scenarios.

Update token: Replace "YOUR_DISCORD_BOT_TOKEN" with your actual Discord token in the if __name__ == "__main__": block.

Run the script: Execute the Python script. It will prompt you to enter the Discord forum channel ID. Enter the ID and press Enter.

Check the output directory: The exported HTML files and assets will be saved in the discord_exports directory (or the directory specified by base_directory), under a subdirectory named after the channel.

Important Security Notes:

Discord Tokens: Treat your Discord token like a password. Keep it secret and secure. Do not share it or commit it to public code repositories.

User Tokens: Be extremely cautious when using user tokens. They grant broad access to your Discord account. Misuse can lead to account compromise. Consider using bot tokens if possible and if they have the necessary permissions.

DiscordChatExporter.Cli: Download DiscordChatExporter.Cli from a trusted source ([the official GitHub repository](https://github.com/Tyrrrz/DiscordChatExporter)). Be aware of the security implications of running external executables.
