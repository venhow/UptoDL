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

system("title " + "UptoDL")

init(convert=True)

def process_exists(process_name):
    progs = str(check_output('tasklist'))
    if process_name in progs:
        return True
    else:
        return False

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
  video_temp_path = "assets/dl_temp/video_temp.mp4"
  audio_temp_path = "assets/dl_temp/audio_temp.mp3"

  if path.exists(video_temp_path):
    remove(video_temp_path)
    remove(audio_temp_path)

  ascii_print()

  firefox_path_file = open('assets/firefox_path.json', 'r', encoding='utf-8')
  data = load(firefox_path_file)

  if not data["firefox_path"]:
      firefox_path = input(f'\r\nSpecified the path of {Fore.LIGHTMAGENTA_EX}Firefox{Fore.WHITE} (basic "C:\Program Files\Mozilla Firefox\\firefox.exe", once specified, it will not be \r\nasked again) : {Fore.LIGHTMAGENTA_EX}')
      data.update({"firefox_path": firefox_path})

  firefox_json_write =  open('assets/firefox_path.json', 'w', encoding='utf-8')
  dump(data, firefox_json_write)
  firefox_json_write.close()

  print(f"\r\n{Fore.WHITE}Starting proxy server.\r\n")

  Popen(r"tor.exe -f Tor/torrc", shell=True, cwd="assets", stdout=DEVNULL)

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
  options.add_argument('--headless')
  options.set_preference("media.volume_scale", "0.0")

  driver = webdriver.Firefox(executable_path=path.abspath(r"geckodriver.exe"), service_log_path=path.devnull, options=options, seleniumwire_options=proxy_options)

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

  network_requests = driver.requests

  for request in network_requests:
      request_url = request.url
      response_request = request.response.body.decode('ISO-8859-1') if request.response and request.response.body else None

      if ".mpd" in request_url:
        mpd_file_url = request_url
        xml_mpd_file = response_request
        break

  driver.quit()

  uptobox_stream_file = mpd_file_url.removesuffix("_m_main_0.mpd")

  try:
    tree = fromstring(xml_mpd_file)
  except:
    input(f"\r\n{Fore.LIGHTRED_EX}The proxy used has no more video credits on Uptostream. Press {Fore.LIGHTMAGENTA_EX}[ENTER] {Fore.LIGHTRED_EX}to change the proxy and try again.{Fore.WHITE}")
    upto_dl()

  video_file_codes = []

  for multimedia_codes_files in tree.findall('.//{*}BaseURL'):
      if multimedia_codes_files.text.startswith("_a"):
        audio_file = multimedia_codes_files.text
      else:
        video_file_code = multimedia_codes_files.text
        video_file_codes.append(video_file_code)

  audio_link = uptobox_stream_file+audio_file

  video_qualities = ['360p', '480p', '720p', '1080p']

  result = {video_qualities[i]: video_file_codes[i] for i in range(len(video_file_codes))}

  print("\r\nChoose the quality you want :\r\n")

  for choice_number, available_quality in enumerate(result.keys(), 1):
      print(f"{choice_number}. {Fore.LIGHTMAGENTA_EX}{available_quality}{Fore.WHITE}")

  quality_choice = int(input(f"\r\n[>] Choice : {Fore.LIGHTMAGENTA_EX}"))

  video_link = uptobox_stream_file+list(result.values())[quality_choice-1]

  ascii_print()

  print(f"\r\n{Fore.WHITE}Links of the video successfully recovered. Downloading...{Fore.LIGHTMAGENTA_EX}\r\n")

  download(video_link, video_temp_path)
  download(audio_link, audio_temp_path)

  print(f"\r\n\r\n{Fore.WHITE}Finished downloading, compiling audio and video...\r\n")

  if process_exists('tor.exe'):
      Popen(r"TASKKILL /F /IM tor.exe", shell=True, stdout=DEVNULL)

  if path.exists(f"{uptostream_title_content}.mp4"):
    remove(f"{uptostream_title_content}.mp4")

  video_compiling = Popen(fr"assets/ffmpeg.exe -i {audio_temp_path} -i {video_temp_path} -acodec copy -vcodec copy {uptostream_title_content}.mp4 -hide_banner -loglevel error")

  video_compiling.wait()

  end_choice = input(f"{Fore.LIGHTGREEN_EX}Download and compile completed.\r\n\r\n{Fore.WHITE}Your file is ready : {Fore.LIGHTMAGENTA_EX}{uptostream_title_content}.mp4\r\n{Fore.WHITE}Press {Fore.LIGHTMAGENTA_EX}[ENTER] {Fore.WHITE}to open the video file or any other key then enter to return to the main menu\r\n")

  if end_choice == "":
    system(f"{uptostream_title_content}.mp4")
    upto_dl()
  else:
    upto_dl()

upto_dl()
