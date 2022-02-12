
from __future__ import unicode_literals
import youtube_dl
import os
import discord
#from discord.ext import commands
from googleapiclient.discovery import build
import requests
import asyncio  
import random
import json
#other things needed: pynacl, ffmpeg

file = open("config.json",'r')
x = json.load(file)
token = x['DISCORD_TOKEN']
YT_DEV_KEY = x['YT_DEV_KEY']


client = discord.Client()#attention to the uppercase 'C' in 'Client'


#there's yet a looooot of space for optimization
'''
#testing of  discord.ext stuff 
bot = commands.Bot(command_prefix='!')
@bot.command()  
async def test1(ctx): 
  print("smthadsd")
'''


#--------------------------------------------------
#YOUTUBE DL CONFIGURATION:

ydl_opts = {
    'format':
    'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

#------------------------------------------------
#youtube api setup
                                                        
api_service_name = "youtube"
api_version = "v3"
youtube = build("youtube","v3",developerKey=YT_DEV_KEY)
#-----------------------------------------------------


#=======================================================
#FUNCTIONS 
#=======================================================

#URL PREPERING ----------------------------------------
#this prepares the url for streaming
def url_prep(i_think_this_is_a_url):
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(i_think_this_is_a_url, download=False)
    url = info['formats'][0]['url']
    return(url)
#-----------------------------------------------
#YOUTUBE SEARCH --------------------------------------
def yt_search(search_term):
  
  request = youtube.search().list(
        part="snippet",
        order="relevance",
        q = search_term,#search word
        type="video",
        videoDefinition="any"
    )
  response = request.execute()# 'response' is a dictionary that contains the searched videos' info

    #print("NOW: ")
    #print(response)
    #print("NOT NOW")
    #print(response['items'][0]['id']['videoId'])

  i_think_this_is_a_url = "https://www.youtube.com/watch?v=" + response['items'][0]['id']['videoId']#collects the 'videoId' from the response dictionary and turns it into the youtube url. The '[0]' is for first search result

    #print(i_think_this_is_a_url)
  title = response['items'][0]['snippet']['title']
  return(i_think_this_is_a_url,title)
#----------------------------------------------------

def fetch_all_youtube_videos(playlistId): #NOT MY CODE: https://stackoverflow.com/questions/18804904/retrieve-all-videos-from-youtube-playlist-using-youtube-v3-api
    youtube = build("youtube",
                    "v3",
                    developerKey=YT_DEV_KEY)
    res = youtube.playlistItems().list(
    part="snippet",
    playlistId=playlistId,
    maxResults="50"
    ).execute()

    nextPageToken = res.get('nextPageToken')
    while ('nextPageToken' in res):
        nextPage = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlistId,
        maxResults="50",
        pageToken=nextPageToken
        ).execute()
        res['items'] = res['items'] + nextPage['items']

        if 'nextPageToken' not in nextPage:
            res.pop('nextPageToken', None)
        else:
            nextPageToken = nextPage['nextPageToken']

    return res

#=======================================================

#-----------------------------------------------
loop_song = False
song_list = []
title_list = []
#list of song's urls and titles
bot_in_channel = False
is_bot_paused = False

print("On we go!")
@client.event  #activation upon event
async def on_message(message):
  await asyncio.sleep(1)


  global loop_song
  global bot_in_channel
  global is_bot_paused
  global song_list
  global title_list
  global conec

  print("[message detected]")
  mes_cont = message.content
  mes_core = ""


  if (mes_cont == "+help") or (mes_cont == "+h"):
    print("help function")
    await message.channel.send('''COMANDOS: 
"**+p** *nome da música*" -> toca a musica

"**+s**" -> pula de musica
    
"**+fila**" -> mostra a fila de execução

"**+pause**" -> pausa a musica (para resumir mande apenas "+p")

"**+shuffle**" -> embaralha lista de execução

"**+activity X**" -> te da uma atividade aleatoria para X numero de pessoas

"**+loop**" -> ativa / destavia loop (proxima musica toca indefinidamente)

"**+quit**" -> bot vai embora pra sempre forever te deixa sozinho solitario sem nunca voltar tristão forever com o coração partido... a não ser é claro que vc chame ele de novo

-----------------------------------------
**adendos:**
* para os comandos funcionarem você precisa estar conectado em um canal de voz
* se der algm merda ou as coisas não tão funcionando como esperado tenta dar um "+quit" que ele reseta as variaveis do bot''') 
    return



  #print("fon>> " + str(message.author.voice))
  if str(message.author.voice) == "None":
    print("sender of message not connected to voice")
    return
  
  voiceChannel = message.author.voice.channel
  # print("voice channel: " + str(voiceChannel))
  

  
  async def execute_song(conec,fMessage):
    global loop_song
    global song_list
    global title_list
    
    print("executing -------")
    #print("Song list: " + str(song_list))
    #print("Title list: " + str(title_list))

    #f discord.client.VoiceClient.is_playing(conec):
    #  return
    

    #CHECK IF LIST EMPTY:
    if not song_list:  #python gives booleans to lists on whether or not they have content in them
      print("no song in list")
      return

    source_temp = song_list[0]
    title_temp = title_list[0]

    if not loop_song:
      
      song_list.pop(0)
      title_list.pop(0)

    source = url_prep(source_temp)

    
    await fMessage.channel.send("tocando: **" + title_temp + "**")


    source = await discord.FFmpegOpusAudio.from_probe(source)

    loop = asyncio.get_running_loop() #loop for threadsafe running
  
    discord.client.VoiceClient.play(conec, source, after = lambda e:(asyncio.run_coroutine_threadsafe(execute_song(conec,fMessage),loop))) #this has to be run as threadsafe (took me fucking weeks to understand)

    
    return
    


  
  if mes_cont == "+p" or mes_cont =="+play":
    print("'+p' function ")
    if is_bot_paused:
      await message.channel.send("resumindo...")
      discord.client.VoiceClient.resume(conec)
      is_bot_paused = False
      return
    else:
      return

  

  elif mes_cont == "testermode":
    print("TESTERMODE.........")

  elif (mes_cont.startswith("+p ") or (mes_cont.startswith("+play ")) or mes_cont.startswith("+P ") or mes_cont.startswith("+PLAY ")):
    print("--function: PLAY--")

    if mes_cont.startswith("+p "):
      mes_cont = mes_cont.split("+p ")

    elif mes_cont.startswith("+play "):
      mes_cont = mes_cont.split("+play ")

    elif mes_cont.startswith("+P "):
      mes_cont = mes_cont.split("+P ")
      
    elif mes_cont.startswith("+PLAY "):
      mes_cont = mes_cont.split("+PLAY ")

    else:
      return
    
    mes_core = mes_cont[1]
    #-------------------
    if not bot_in_channel:
      conec = await voiceChannel.connect()  #this makes the bot to join whatever joice channel the sender of the message is in. Saves the 'is_connected' status in 'conec'
      #'conec' is also often used as 'self' in functions
      print("NOW CONNECTING TO CHANNEL")
      bot_in_channel = True
    #-------------------

    if ("youtube.com" in mes_core) or ("https://" in mes_core):#for parsing yt links
      if ("youtube.com/playlist?list=" in mes_core):
        print("playlist detected")
        playlist_raw = mes_core

        playlist_raw = playlist_raw.split("outube.com/playlist?list=")

        playlist_raw = playlist_raw[1]
        
        playlist = fetch_all_youtube_videos(playlist_raw)

        title_temp = "Playlist"
        for x in playlist['items']:
          title_list.append(x['snippet']['title'])
          song_list.append(x['snippet']['resourceId']['videoId'])

      
      else:
        print("video link detected")
        song_list.append(mes_core)
        title_temp = ("youtube link") 
        title_list.append(title_temp)
      
    else:
      url_temp = yt_search(mes_core)
      title_list.append(url_temp[1])
      song_list.append(url_temp[0])
      title_temp = url_temp[1]


    await message.channel.send("Adicionando **" + title_temp + "** à fila de execução")

    if discord.client.VoiceClient.is_playing(conec):
      return
    else:
      print("executing")
      is_bot_paused = False
      await  execute_song(conec,message) 
      return
      
  elif mes_cont == "+fila":
    await message.channel.send(title_list)
    return

  elif (mes_cont in ["+s","+S","+skip","+Skip","+next","+Next"]):
    print("--function: SKIP--")
    discord.client.VoiceClient.pause(conec)
    is_bot_paused = False
    await execute_song(conec,message)
    return

  elif mes_cont.startswith(("+shuffe", "+sh", "+embaralhar","+embaralhe")):
    print("--function: SHUFFLE--")

    if song_list:
      await message.channel.send("embaralhando lista de reprodução...")

      c = list(zip(song_list,title_list))
      random.shuffle(c)
      song_list,title_list = zip(*c)
      song_list = list(song_list)
      title_list = list(title_list)

    else:
      await message.channel.send("não há musica na lista para embaralhar")

    return

  elif mes_cont in ["+loop","+Loop","+L","+l"]:
    print("--function: LOOP--")

    if not loop_song:
      await message.channel.send("**ligando Loop**")
      loop_song = True;
    elif loop_song:
      await message.channel.send("**desligando loop**")
      loop_song = False;
    return

  elif mes_cont.startswith(("+pl","+Pl","+PL","+Playlist","+playlist")):
    print("--function: PLAYLIST--")

    mes_cont = mes_cont.split(" ",1)
    if len(mes_cont) == 1:
      await message.channel.send("playlists are: [...]") #IN MAINTAINANCE
    else:
      print(mes_cont[1])

    return

  elif mes_cont == "+pause":
    print("--function: PAUSE--")
    await message.channel.send("pausando...")
    discord.client.VoiceClient.pause(conec)
    is_bot_paused = True
    return

  elif mes_cont in ["+quit","+Quit","+QUIT","+Q","+q"]: #if any other global variable is added in the future, make sure to wipe it clean in here
    print("--function: QUIT--") 
    await discord.client.VoiceClient.disconnect(conec)
    is_bot_paused = False
    bot_in_channel = False
    song_list = []
    title_list = []
    loop_song = False
    conec = 0
    return

  elif mes_cont.startswith(("+activity", "+atividade","+act","+Act","+Activity","+ACTIVITY","+Atividade","+ATIVIDADE")):
    #spits out a random activity with the indicated number of people 
    print("--function: ACTIVITY--")
    link = 'http://www.boredapi.com/api/activity/'
    
    mes_cont = mes_cont.split(" ")

    if len(mes_cont)>1:
        link = link + "?participants=" + str(mes_cont[1])

    r = requests.get(link)#web scraping boredapi.com
    r = r.json()
    await message.channel.send(str(r['activity']))  
   

  else:
    return
    
  #-------------------------- ---------------------------
  
  #TESTER MODE:

  print("TESTING SECTION...") #when user input is 'testermode' the following should run


  #=====================================================
  #=====================================================


client.run(token)