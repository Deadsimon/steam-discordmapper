import discord
import requests
import mysql.connector
import config

# Access Discord Bot Token
discord_token = config.discord_token

# Access Steam API Key
steam_api_key = config.steam_api_key

# Access MySQL Database Config
mysql_config = config.mysql_config

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def get_steam_id(username):
    api_key = '595337B9C677D4ADDFF1A88A75F869C1'  # Replace with your own Steam Web API key
    api_url = f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={api_key}&vanityurl={username}'

    response = requests.get(api_url)
    data = response.json()

    if data['response']['success'] == 1:
        steam_id_64 = data['response']['steamid']
        return steam_id_64
    else:
        return None

def insert_user_mapping(steam_id, discord_id):
    # Connect to the MySQL server
    conn = mysql.connector.connect(
        host='192.168.50.164',
        port=3306,
        user='python',
        password='$M1n1stry$!',
        database='player_data'
    )  # Connect to the MySQL server
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User_mapping (
            steam_id DECIMAL(20, 0) PRIMARY KEY,
            discord_id DECIMAL(18, 0)
        )
    ''')

    # Insert or replace the user mapping
    cursor.execute('''
        INSERT INTO User_mapping (steam_id, discord_id)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE discord_id = %s
    ''', (str(steam_id), int(discord_id), int(discord_id)))

    conn.commit()  # Commit the changes
    conn.close()  # Close the database connection

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/join'):
        command = message.content.split(' ')
        if len(command) != 2:
            await message.channel.send('Invalid command. Usage: /join <steam_name>')
            return

        username = command[1]
        steam_id = get_steam_id(username)

        if steam_id:
            insert_user_mapping(steam_id, message.author.id)  # Insert user mapping into the database

            response = f'User mapping for {username} has been created.'
            await message.channel.send(response)
        else:
            await message.channel.send(f'Unable to find SteamID64 for {username}')

client.run(discord_token)
