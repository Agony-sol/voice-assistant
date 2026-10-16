import sounddevice as sd
from faster_whisper import WhisperModel
import numpy as np
import queue
import subprocess
from ollama import chat
import json
import urllib.parse
import yt_dlp 
import os
import difflib
from ddgs import DDGS
from trafilatura import fetch_url, extract


#Voice Recording Setup
#----------------------
RATE = 16000
CHUNK = 1024
THRESHOLD = 0.1
SILENCE_LIMIT = 1.0
FORMAT = 'float32'
filename = "output.txt"

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(indata.copy())

#Whisper Model Setup
#--------------------p  
print("Loading Faster-Whisper...")
model = WhisperModel("/home/agony/Projects/VoiceRecognition/python-code/my_models/faster-whisper-medium", device="cpu", compute_type="int8")
print("Model Loaded and Ready to Fire.")

is_speaking = False
is_awake = False
silence_data = 0
audio_buffer = []
silence_limit = int((RATE / CHUNK) * SILENCE_LIMIT) #Rate/Chunk = 1 sec (15 Audio_Chunks)

#Starting the recording
#-----------------------
try:
    with open(filename, "w", encoding="utf-8") as file, sd.InputStream(samplerate=RATE, channels=1, dtype=FORMAT, blocksize=CHUNK, callback=callback):

        subprocess.run(["notify-send", "-t", "2000", "Έρις", "🎧 Σε ακούω..."])
        
        while True:
            #Filtering Information
            #----------------------
            data = q.get()
            volume = np.sqrt(np.mean(data**2))

            #Start When You Hear Me Speak
            #-----------------------------
            if volume > THRESHOLD:
                if is_speaking == False:
                    is_speaking = True
                audio_buffer.append(data)
                silence_data = 0
                # print("Listening...")

            elif is_speaking == True:
                # print("Not Listening...")
                silence_data += 1 #silence_data=15 stop
                audio_buffer.append(data)

                #Stop After 1sec Silence
                #------------------------
                if silence_data > silence_limit:
                    break

        #Append Data
        #------------
        audio_data = np.concatenate(audio_buffer)

        if len(audio_data) > RATE * 0.5:
            audio_data = audio_data.flatten()

            #Whisper Model Parameters
            #-------------------------
            segments, _ = model.transcribe(audio_data, beam_size=5, language="el", vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500))
            text = "".join([s.text for s in segments]).strip()

            #Print Input
            #------------
            if text:
                print(f"Είπες: {text}")
                file.write(text + "\n")
                file.flush()

                #Load Ollama Model
                #------------------
                response = chat(model='qwen2.5:7b', format='json', messages=[
                    {
                                    'role': 'system',
                                    'content': '''Είσαι η Έρις, η ψηφιακή μου βοηθός. Έχεις έξυπνη, σαρκαστική και ειρωνική (snarky) προσωπικότητα.
                                    ΑΠΑΓΟΡΕΥΕΤΑΙ να απαντήσεις με ελεύθερο κείμενο. ΠΡΕΠΕΙ να επιστρέφεις ΠΑΝΤΑ ένα έγκυρο JSON.

                                    ΑΠΑΙΤΟΥΜΕΝΗ ΔΟΜΗ (πρέπει να περιέχει ΠΑΝΤΑ και τα 5 κλειδιά):
                                    {"command_type": "", "app_name": "", "search_query": "", "target_site": "", "reply": ""}
                                    
                                    ΚΑΝΟΝΕΣ:
                                    1. ΑΠΛΟ ΑΝΟΙΓΜΑ: Αν ζητήσω απλά να ανοίξω κάτι, βάλε command_type: "open", app_name: το όνομα, και άσε τα υπόλοιπα κενά.
                                    2. ΑΝΑΖΗΤΗΣΗ / ΑΝΑΠΑΡΑΓΩΓΗ: Αν ζητήσω να ψάξεις κάτι στο ίντερνετ ή να βάλεις να παίξει ένα τραγούδι, βάλε command_type: "search". 
                                    - Στο search_query βάλε ΑΚΡΙΒΩΣ αυτό που πρέπει να ψάξω (χωρίς περιττά λόγια).
                                    - Στο target_site βάλε "youtube" (αν ζητήσω τραγούδι/βίντεο) ή "google" (για γενική αναζήτηση).
                                    3. ΕΡΩΤΗΣΕΙΣ: Αν ρωτήσω κάτι γενικό, βάλε command_type: "chat", και άσε app_name, search_query, target_site ΚΕΝΑ.
                                    4. ΑΣΥΝΑΡΤΗΣΙΕΣ: Αν δεν βγάζει νόημα, βάλε command_type: "ignore" και τα υπόλοιπα κενά.
                                    5. Πάντα να απαντάς ειρωνικά στο "reply".
                                    6. Στο κλειδί "app_name", πρέπει ΠΑΝΤΑ να γράφεις το επίσημο Αγγλικό όνομα της εφαρμογής, ακόμα και αν το ζήτησα στα Ελληνικά ή έχει ορθογραφικό λάθος (π.χ. αν δεις "στιμ" ή "steem" γράψε "steam", αν δεις "ντισκορντ" γράψε "discord").

                                    ΠΑΡΑΔΕΙΓΜΑΤΑ:
                                    - {"command_type": "search", "app_name": "firefox", "search_query": "πως βρισκω το χ δακτυλιδι dark souls 3", "target_site": "google", "reply": "Πάλι πέθανες; Άντε, σου ανοίγω οδηγό στο Google μπας και σωθείς."}
                                    - {"command_type": "search", "app_name": "firefox", "search_query": "i can helloween", "target_site": "youtube", "reply": "Επιτέλους, λίγη σωστή μουσική. Σου βάζω Helloween στο YouTube."}
                                    - {"command_type": "open", "app_name": "firefox", "search_query": "", "target_site": "", "reply": "Ανοίγω τον Firefox. Μην αργήσεις."}
                                    - {"command_type": "chat", "app_name": "", "search_query": "", "target_site": "", "reply": "Ένα και ένα κάνουν δύο. Μήπως θες να σου μάθω και την αλφαβήτα;"}
                                    '''
                    },
                    {
                                    'role': 'user',
                                    'content': text,
                    },
                ])
                            

                #Print Response
                #--------------
                lollipop = response['message']['content']
                try:
                    clean_lollipop = lollipop.replace("```json", "").replace("```", "").strip()

                    eris_response = json.loads(clean_lollipop)

                    cmd_type = eris_response.get('command_type', '')
                    open_app = eris_response.get('app_name', '')
                    query = eris_response.get('search_query', '')
                    target = eris_response.get('target_site', '')
                    #print(f"{eris_response.get('reply')}")
                    print(f"{eris_response}")

                    #Open App
                    #---------
                    if cmd_type == "open":
                        open_app = open_app.lower().replace(" ","").strip()
                        app_path = ["/usr/share/applications", os.path.expanduser("~/.local/share/applications")]        
                        
                        app_dict = {}

                        #Create App/Path Dictionary
                        #---------------------------
                        for path in app_path:
                            for app in os.listdir(path):
                                if app.endswith(".desktop"):
                                    name = app.replace('.desktop', '').split('.')[-1].lower()
                                    app_dict[name] = os.path.join(path, app)   

                        matches = difflib.get_close_matches(open_app, app_dict.keys(), 1, 0.6)

                        if matches:
                            best_match = matches[0]
                            true_app = app_dict[best_match]
                            subprocess.Popen(["gio", "launch", true_app]) #Με αυτον τον τρόπο τώρα ανοίγει και STEAM games
                        else:
                            subprocess.Popen([open_app])

                    #Make a Search
                    #--------------
                    elif cmd_type == "search":
                        app_to_use = open_app.lower() if open_app else "firefox"

                        safe_query = urllib.parse.quote(query)

                        if target == "youtube":
                            # url = f"https://www.youtube.com/results?search_query={safe_query}"
                            url = ""

                            #Setup yt-dlp
                            #-------------
                            ydl_opts = {'quiet': True, #μην πετας μεγαλο κειμενο
                                        'extract_flat': True,#δεν δινει το πληρη link(αλλιως χρειαζεται js)
                                        }
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                info = ydl.extract_info(f"ytsearch1:{query}", download=False)#ytsearch1: Best Result

                                if 'entries' in info:
                                    video_id = info['entries'][0].get('id')
                                    url = f"https://www.youtube.com/watch?v={video_id}&autoplay=1"
                                    name = info['entries'][0]['title']
                            print(f">> Αναζήτηση στο YouTube: {query}")
                        else:
                            url = f"https://www.google.com/search?q={safe_query}"
                            print(f">> Αναζήτηση στο Google: {query}")

                            
                            # #Search Using DDGS engine
                            # #-------------------------  
                            # results = DDGS().text(query, max_results=1)
                            # result_url = result[0].get('href')
                                        
                        subprocess.Popen([app_to_use, "--new-tab", url])

                except Exception as e:
                    print(f"\nError: {e}")
                        
            with q.mutex:
                q.queue.clear()

except KeyboardInterrupt:
    print('\nInterrupted by User.')
except Exception as e:
    print(f"\nError: {e}")