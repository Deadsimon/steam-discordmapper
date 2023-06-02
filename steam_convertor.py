import discord
import requests
import mysql.connector

from config import *

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def get_steam_id(username):
    api_key = steam_api_key  # Replace with your own Steam Web API key
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
        host=mysql_config['host'],
        port=mysql_config['port'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User_mapping (
            steam_id DECIMAL(20, 0) PRIMARY KEY,
            discord_id DECIMAL(18, 0)
        )
    ''')

    try:
        # Convert to decimal format
        steam_id_decimal = int(steam_id)
        discord_id_decimal = int(discord_id)

        # Insert or replace the user mapping
        cursor.execute('''
            INSERT INTO User_mapping (steam_id, discord_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE discord_id = %s
        ''', (steam_id_decimal, discord_id_decimal, discord_id_decimal))

        conn.commit()  # Commit the changes
        print("Data inserted successfully!")
    except mysql.connector.Error as error:
        print("Error inserting data:", error)

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

            response = f'SteamID64 for {username}: {steam_id}\nDiscord ID: {message.author.id}'
            await message.channel.send(response)
        else:
            await message.channel.send(f'Unable to find SteamID64 for {username}')

client.run(discord_token)
