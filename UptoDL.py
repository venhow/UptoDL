from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from xml.etree.ElementTree import fromstring
from os import path, remove, system
from time import sleep
from json import load, dump
from wget import download
from subprocess import Popen, DEVNULL, check_output
from colorama import Fore, init
from requests import get
from socks import set_default_proxy, SOCKS5, socksocket
import socket

system("title " + "UptoDL ~ Nathoune987")

init(convert=True)

def kill_tor():
  if "tor.exe" in str(check_output('tasklist')):
    Popen(r"TASKKILL /F /IM tor.exe", shell=True, stdout=DEVNULL)

def try_remove_temp_files(path_file):
  if path.exists(path_file):
    remove(path_file)

def ascii_print():
  system("cls")
  print(f"""{Fore.LIGHTMAGENTA_EX}
   _   _       _       ______ _     
  | | | |     | |      |  _  \ |    
  | | | |_ __ | |_ ___ | | | | |    
  | | | | '_ \| __/ _ \| | | | |{Fore.MAGENTA}
  | |_| | |_) | || (_) | |/ /| |____
   \___/| .__/ \__\___/|___/ \_____/
        | |                         
        |_|{Fore.LIGHTMAGENTA_EX}                         

  ~ {Fore.WHITE}https://github.com/Nathoune987""")

def upto_dl():
  #Useful for comparisons
  french_forced_vtt_file = None
  french_full_vtt_file = None
  
  video_temp_path = r"assets/dl_temp/video_temp.mp4"
  audio_temp_path = r"assets/dl_temp/audio_temp.mp3"
  french_forced_subtitle_temp_path = r"assets/dl_temp/french_forced_subtitle_temp.vtt"
  french_full_subtitle_temp_path = r"assets/dl_temp/french_full_subtitle_temp.vtt"

  try_remove_temp_files(video_temp_path)
  try_remove_temp_files(audio_temp_path)
  try_remove_temp_files(french_forced_subtitle_temp_path)
  try_remove_temp_files(french_full_subtitle_temp_path)

  kill_tor()

  ascii_print()

  firefox_path_file = open('assets/firefox_path.json', 'r', encoding='utf-8')
  data = load(firefox_path_file)

  if not data["firefox_path"]:
    firefox_path = input(f'\r\nSpecified the path of {Fore.LIGHTMAGENTA_EX}Firefox{Fore.WHITE} (basic "C:\Program Files\Mozilla Firefox\\firefox.exe", oncespecified, it will not be \r\nasked again) : {Fore.LIGHTMAGENTA_EX}')
    data.update({"firefox_path": firefox_path})

  firefox_json_write =  open('assets/firefox_path.json', 'w', encoding='utf-8')
  dump(data, firefox_json_write)
  firefox_json_write.close()

  print(f"\r\n{Fore.WHITE}Starting proxy server.\r\n")

  Popen(r"tor.exe -f Tor/torrc", shell=True, cwd="assets", stdout=DEVNULL)

  #To see if Tor is running correctly, I make a request to a site with the proxy settings
  while True:
    try:
      get("https://torproject.org/", proxies={"http": "socks5://127.0.0.1:987", "https": "socks5://127.0.0.1:987"})
      break
    except:
      pass

  print(f"{Fore.WHITE}Starting Firefox driver.\r\n")

  proxy_options = {'proxy': {'http': 'socks5://127.0.0.1:987', 'https': 'socks5://127.0.0.1:987'}}
  options = webdriver.FirefoxOptions()
  options.binary_location = data["firefox_path"]
  #These two options make firefox not visible and mute
  options.add_argument('--headless')
  options.set_preference("media.volume_scale", "0.0")

  driver = webdriver.Firefox(executable_path=path.abspath(r"assets/geckodriver.exe"), service_log_path=path.devnull, options=options, seleniumwire_options=proxy_options)

  ascii_print()

  input_link = input(f"\r\nEnter an {Fore.LIGHTMAGENTA_EX}Uptobox/Uptostream{Fore.WHITE} link : ")

  if input_link.startswith("https://uptostream.com"):
    uptostream_link = input_link
  elif input_link.startswith("https://uptobox.com"):
    uptostream_link = input_link.replace("uptobox", "uptostream")
  else:
    input(f"{Fore.LIGHTRED_EX}\r\n[!] This link is not valid, enter an Uptobox or Uptostream link.{Fore.WHITE}")
    upto_dl()

  print("\r\nLoading, please wait.")

  driver.get(uptostream_link)

  recovered_video_title = driver.find_element(By.CSS_SELECTOR, ".file-title").text.replace(" ", "_")

  ascii_print()

  print(f"\r\nThis video will be recovered : {Fore.LIGHTMAGENTA_EX}{recovered_video_title}{Fore.WHITE}")

  movie_extensions = [".mkv", ".mp4", ".avi", ".mov"]

  for extension in movie_extensions:
    if recovered_video_title.endswith(extension):
      uptostream_title_content = recovered_video_title.removesuffix(extension)
      break

  sleep(2)

  driver.find_element(By.CSS_SELECTOR, ".vjs-big-play-button").click()

  sleep(6)

  #The script analyzes all the requests made by the site and brings out only the one ending with ".mpd" containing the necessary information to download
  for request in driver.requests:
    if ".mpd" in request.url:
      mpd_file_url = request.url
      xml_mpd_file = request.response.body.decode('ISO-8859-1') if request.response else None
      break

  vtt_file_urls = [request.url for request in driver.requests if ".vtt" in request.url]

  subtitle_file_numbers = []

  #These two "for" loops analyze the potential ".vtt" files containing the subtitles. These files have a special number identifying them, so it must be extracted.
  for subtitles_file in vtt_file_urls:
    if "_s_" in subtitles_file:
      subtitle_file_number = int(subtitles_file.split("_")[2].replace(".vtt", ""))
      subtitle_file_numbers.append(subtitle_file_number)
      if str(max(subtitle_file_numbers)) in subtitles_file:
        french_full_vtt_file = subtitles_file 
      
  for subtitles_file in vtt_file_urls:
    if "_s_" in subtitles_file and str(min(subtitle_file_numbers)) in subtitles_file:
      french_forced_vtt_file = subtitles_file
      break

  driver.quit()

  uptobox_stream_file = mpd_file_url.removesuffix("_m_main_0.mpd")

  try:
    tree = fromstring(xml_mpd_file)
  except:
    input(f"\r\n{Fore.LIGHTRED_EX}The proxy used has no more video credits on Uptostream. Press {Fore.LIGHTMAGENTA_EX}[ENTER] {Fore.LIGHTRED_EX}to change the proxy and try again.{Fore.WHITE}")
    upto_dl()

  video_file_codes = []

  #This "for" loop analyzes the recovered ".mpd" file. In this file there are the links of the videos and the audio.
  for multimedia_codes_files in tree.findall('.//{*}BaseURL'):
    if multimedia_codes_files.text.startswith("_a"):
      audio_file = multimedia_codes_files.text
    else:
      video_file_code = multimedia_codes_files.text
      video_file_codes.append(video_file_code)

  audio_link = uptobox_stream_file+audio_file

  video_qualities = ['360p', '480p', '720p', '1080p']

  qualities_and_links = {video_qualities[i]: video_file_codes[i] for i in range(len(video_file_codes))}

  print("\r\nChoose the quality you want :\r\n")

  for choice_number, available_quality in enumerate(qualities_and_links.keys(), 1):
      print(f"{choice_number}. {Fore.LIGHTMAGENTA_EX}{available_quality}{Fore.WHITE}")

  quality_choice = int(input(f"\r\n[>] Choice : {Fore.LIGHTMAGENTA_EX}"))

  video_link = uptobox_stream_file+list(qualities_and_links.values())[quality_choice-1]

  ascii_print()

  print(f"\r\n{Fore.WHITE}Links of the video successfully recovered. Downloading...{Fore.LIGHTMAGENTA_EX}\r\n")

  #To establish a connection with the Tor proxies for downloading
  set_default_proxy(SOCKS5, "127.0.0.1", 987)
  socket.socket = socksocket

  download(video_link, video_temp_path)
  download(audio_link, audio_temp_path)
  if french_forced_vtt_file != None:
    download(french_forced_vtt_file, french_forced_subtitle_temp_path)
    download(french_full_vtt_file, french_full_subtitle_temp_path)

  #To reset the default proxy connection
  set_default_proxy()
  socket.socket = socksocket

  print(f"\r\n\r\n{Fore.WHITE}Finished downloading, compiling audio and video...\r\n")

  kill_tor()

  #If subtitle files have been found, the ffmpeg command for assembling audio and video changes, adding the subtitle source and options
  if french_forced_vtt_file and french_full_vtt_file != None:
    uptostream_title_content = f"{uptostream_title_content}.mkv"
    try_remove_temp_files(uptostream_title_content)
    video_compiling = Popen(fr'assets/ffmpeg.exe -i {audio_temp_path} -i {video_temp_path} -i {french_forced_subtitle_temp_path} -i {french_full_subtitle_temp_path} -acodec copy -vcodec copy -map 0:a -map 1:v -map 2:s -map 3:s -c:s webvtt -metadata:s:s:0 language=fra -metadata:s:s:0 title="French-Forced (possibly incorrect)" -metadata:s:s:1 language=fra -metadata:s:s:1 title="French-Full (possibly incorrect)" {uptostream_title_content} -hide_banner -loglevel error')
  else:
    uptostream_title_content = f"{uptostream_title_content}.mp4"
    try_remove_temp_files(uptostream_title_content)
    video_compiling = Popen(fr'assets/ffmpeg.exe -i {audio_temp_path} -i {video_temp_path} -acodec copy -vcodec copy {uptostream_title_content} -hide_banner -loglevel error')

  video_compiling.wait()

  end_choice = input(f"{Fore.LIGHTGREEN_EX}Download and compile completed.\r\n\r\n{Fore.WHITE}Your file is ready : {Fore.LIGHTMAGENTA_EX}{uptostream_title_content}\r\n{Fore.WHITE}Press {Fore.LIGHTMAGENTA_EX}[ENTER] {Fore.WHITE}to open the video file or any other key then enter to return to the main menu\r\n")

  if end_choice == "":
    system(f"{uptostream_title_content}")
    upto_dl()
  else:
    upto_dl()

upto_dl()
