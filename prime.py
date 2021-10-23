# Dependencies
# I chose Firefox because it's my main browser
# You may change it to any other that's supported by selenium

import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

import discord
import os

# Since my main language is portuguese, I ran into some issues comparing unicode characters
# This just fixes it
# For the english prime's page, this should be useless
def remove_unicode( str ):
    encoded_string = str.encode( "ascii", "ignore" )
    return encoded_string.decode( )

# Create our discord client
client = discord.Client( )

# Callback called when we connect
@client.event
async def on_ready( ):
    print( 'We have logged in as {0.user}'.format( client ) )

    new_stuff = []
    lines = []

    # Reads the previous content
    # TODO: make it handle when the file isn't created yet (but it should be created before sending it to the servers, so that we don't spam)
    with open( 'previous_dlcs.txt', encoding = "utf8" ) as f:
        lines = f.readlines( )
    
    with open( 'previous_games.txt', encoding = "utf8" ) as f:
        lines.extend( f.readlines( ) )

    # Removes the new-line characters and other redundant stuff
    for i in range( len( lines ) ):
        lines[ i ] = lines[ i ].strip( )

    # Create our driver
    # Since this runs only once on my machine, I didn't make it headless
    with webdriver.Firefox( ) as driver:
        # Some setup
        ignored_exceptions = ( selenium.common.exceptions.NoSuchElementException, selenium.common.exceptions.StaleElementReferenceException )
        wait = WebDriverWait( driver, 20, ignored_exceptions = ignored_exceptions )

        # Navigate to the prime page
        driver.get( "https://gaming.amazon.com/intro" )
        
        # Find the DLC list
        dlcs = wait.until( lambda d: d.find_elements( By.XPATH, "/html/body/div[1]/div/div/main/div/div[2]/div/div[3]/div[1]/div/div/div/div[2]/div/div/div/div/div/div/div/*/div/button/div/div/div/div[1]/figure/img" ) )
        
        # We create a new file, and save the new content to it
        with open( 'previous_dlcs2.txt', "w", encoding = "utf8" ) as f:
            for d in dlcs:
                # 'alt' refers to the text, 'src' to the image
                f.write( remove_unicode( d.get_property( "alt" ) ) + '\n' )

                # If it isn't in our previous searches, add it to our vector
                if remove_unicode( d.get_property( "alt" ) ) not in lines:
                    new_stuff.append( "dlc&&{0}&&{1}".format( d.get_property( "alt" ), d.get_property( "src" ) ) )

        # Find the game list
        games = wait.until( lambda d: d.find_elements( By.XPATH, "/html/body/div[1]/div/div/main/div/div[2]/div/div[3]/div[2]/div/div/div/div/div[2]/div/div/div/div/div/div/div/*/div/button/div/div/div/div[1]/figure/img" ) )
        
        # Same as before
        with open( 'previous_games2.txt', "w", encoding = "utf8" ) as f:
            for g in games:
                f.write( remove_unicode( g.get_property( "alt" ) ) + '\n' )

                if remove_unicode( g.get_property( "alt" ) ) not in lines:
                    new_stuff.append( "game&&{0}&&{1}".format( g.get_property( "alt" ), g.get_property( "src" ) ) )

        # Replace the old file with the new
        os.remove( 'previous_dlcs.txt' )
        os.rename( 'previous_dlcs2.txt', 'previous_dlcs.txt' )
        os.remove( 'previous_games.txt' )
        os.rename( 'previous_games2.txt', 'previous_games.txt' )

    # If we actually have something new
    if ( len( new_stuff ) ):
        # Iterate the servers we are in
        for server in client.guilds:
            # Find the channel (you can change to whatever you want)
            channel = discord.utils.get( server.channels, name = "🎮・jogos-free" )
            
            # Iterate the new content
            for item in new_stuff:
                # Parse it
                split = item.split( '&&' )

                # Define the title of the embed (again, customizable)
                title = ''
                if split[ 0 ] == 'dlc':
                    title = "Novo complemento disponível"
                else:
                    title = "Novo jogo disponível"

                # Create the embed
                embed = discord.Embed( title = title, description = split[ 1 ], color = discord.Color.blue( ), url = 'https://gaming.amazon.com/intro' )
                
                # Set the image
                embed.set_image( url = split[ 2 ] )

                # Send it
                await channel.send( embed = embed )

# Run the client (put your token on the '')
client.run( '' )
