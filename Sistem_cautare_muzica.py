import requests
import pyodbc

# API keys and endpoints
GENIUS_API_KEY = "YOUR_GENIUS_API_KEY"
#MIDI_URL = "https://example.com/midi/song.mid"

# Fetch Lyrics from Genius API
def fetch_lyrics(song_title, artist):
    headers = {"Authorization": f"Bearer {GENIUS_API_KEY}"}
    search_url = "https://api.genius.com/search"
    params = {"q": f"{song_title} {artist}"}
    response = requests.get(search_url, headers=headers, params=params)
    data = response.json()
    if data['response']['hits']:
        return data['response']['hits'][0]['result']['url']  # or extract lyrics if provided
    return None

# Fetch MIDI File
def fetch_midi_file(song_title, artist):
    """
    Search for a MIDI file by song title and artist, then download it.
    """
    save_path = "song.mid"
    try:
        # Example search API for MIDI files (replace with a real MIDI API)
        search_url = "https://example-midi-api.com/search"
        params = {"title": song_title, "artist": artist}
        response = requests.get(search_url, params=params)
        response.raise_for_status()

        # Parse the search results
        results = response.json()
        if not results or "midi_url" not in results[0]:
            logging.warning(f"No MIDI file found for '{song_title}' by '{artist}'.")
            return None

        # Get the URL of the first MIDI file
        midi_url = results[0]["midi_url"]

        # Download the MIDI file
        logging.info(f"Downloading MIDI file for '{song_title}' by '{artist}' from {midi_url}.")
        midi_response = requests.get(midi_url)
        midi_response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(midi_response.content)

        return save_path

    except Exception as e:
        logging.error(f"Error fetching MIDI file for '{song_title}' by '{artist}': {e}")
        return None


# Insert Data into MySQL
def insert_data(song_title, artist, lyrics, midi_path):
    try:
        connection = pyodbc.connect(
            "DRIVER={MySQL ODBC 8.0 Driver};"
            "SERVER=server_name;"
            "DATABASE=database_name;"
            "Trusted_Connection=yes;"
        )
        print("Connection successful!")
    except pyodbc.Error as e:
        print(f"Error connecting to the database: {e}")
    cursor = connection.cursor()

    # Insert lyrics
    cursor.execute("INSERT INTO song_lyrics (song_title, artist, lyrics) VALUES (%s, %s, %s)",
                   (song_title, artist, lyrics))
    lyrics_id = cursor.lastrowid

    # Insert MIDI file
    with open(midi_path, 'rb') as file:
        midi_data = file.read()
    cursor.execute("INSERT INTO midi_files (file_name, file_data) VALUES (%s, %s)",
                   (f"{song_title}.mid", midi_data))
    midi_id = cursor.lastrowid

    # Link in the songs table
    cursor.execute("INSERT INTO songs (title, artist, midi_file_id, lyrics_id) VALUES (%s, %s, %s, %s)",
                   (song_title, artist, midi_id, lyrics_id))

    connection.commit()
    connection.close()

# Example Usage
song_title = input("Introduceti titlul: ")
artist = input("Introduceti autorul: ")
lyrics = fetch_lyrics(song_title, artist)
midi_path = fetch_midi_file(song_tite, artist)

if lyrics and midi_path:
    insert_data(song_title, artist, lyrics, midi_path)
