LOGIN_SUCCESS = True
VERIFICATION_SUCCESS = True
AUTHENTICATION_SUCCESS = True
IS_ADMIN = True
PARTIAL_AUTHORIZATION = True
NUMBER_OF_VOICEPRINTS = 10
PARTIAL_AUTHORIZATION_THRESHOLD = 70
RELAY_PIN = 17
BUZZER_PIN = 27

RECORDED_AUDIO_FILENAME = "recorded_audio.wav"
USERS_FILENAME = "users.json"
TMP_USERS_FILENAME = "tmp_users.json"
CONNECTION_LOGS_FILENAME = "logs/VAS_connection_logs.txt"
DATABASE_LOGS_FILENAME = "logs/VAS_database_logs.txt"
ENCODING_LOGS_FILENAME = "logs/VAS_encoding_logs.txt"
FILE_MANAGER_LOGS_FILENAME = "logs/VAS_file_manager_logs.txt"
MAIN_APP_LOGS_FILENAME = "logs/VAS_main_app_logs.txt"
SPEECH_RECOGNIZER_LOGS_FILENAME = "logs/VAS_speech_recognizer_logs.txt"
USERS_LOGS_FILENAME = "logs/VAS_users_logs.txt"
VOICE_RECOGNIZER_LOGS_FILENAME = "logs/VAS_voice_recognizer_logs.txt"
VOICE_RECORDER_LOGS_FILENAME = "logs/VAS_voice_recorder_logs.txt"

SPEAKER_RECORDINGS_DIR = "speech_and_voice/speaker_recognition/speaker_recordings/"
SPEAKER_VOICEPRINTS_DIR = "speech_and_voice/speaker_recognition/speaker_voiceprints/"

VERIFICATION_WORDS = {
    "SK": ("zelené jablko padlo zo stromu",
           "tento kamenný stôl je veľmi ťažký",
           "dnes je nádherná modrá obloha",
           "bol som si v lese zabehať",
           "od hladiny sa odrážajú slnečné lúče",
           "v záhrade je veľa krásnych ruží",
           "rád píšem romantické básne",
           "rozbila sa mi sklenená fľaša",
           "rozsvietili sme vianočný stromček",
           "ideme na letnú dovolenku k moru",
           "rozbúrené more vzbudzovalo rešpekt",
           "vysoké hory sa ťahajú až k oblohe",
           "počúval som relaxačnú hudbu",
           "rád rozpráva dobrodružné príbehy",
           "celý deň sme hrali plážový volejbal",
           "bola to útulná horská chata",
           "cestovanie vlakom je veľmi pohodlné",
           "bol som si zaplávať v jazere",
           "v meste budujú novú cyklistickú trasu",
           "môj obľúbený zimný šport je hokej",
           "maľujeme drevený plot okolo záhrady",
           "kuchynský riad som naložil do umývačky",
           "školská tabuľa bola celá popísaná",
           "tradičné oblečenie je súčasťou kultúry",
           "kúpil som si nové slnečné okuliare",
           "pozorovali sme nádherné hviezdne nebo",
           "z útesu sa lial majestátny vodopád ",
           "jahodovú zmrzlinu majú ľudia najradšej",
           "urobili sme si piknik v parku",
           "horská dráha bola veľmi vzrušujúca",
           "s bratom sme si hádzali loptu"),

    "EN": ("the green apple fell from the tree",
           "this stone table is very heavy",
           "today there is a beautiful blue sky",
           "I went for a run in the forest",
           "the sunlight reflects off the surface",
           "there are many beautiful roses in the garden",
           "I enjoy writing romantic poems",
           "my glass bottle broke",
           "we light up the Christmas tree",
           "we're going on a summer vacation to the sea",
           "the rough sea inspired respect",
           "the high mountains reach up to the sky",
           "I listened to relaxing music",
           "I like to tell adventurous stories",
           "we played beach volleyball all day",
           "it was a cozy mountain cabin",
           "traveling by train is very comfortable",
           "I went for a swim in the lake",
           "they're building a new cycling route in the city",
           "my favorite winter sport is hockey",
           "we're painting the wooden fence around the garden",
           "I loaded the kitchen dishes into the dishwasher",
           "the school board was completely written on",
           "traditional clothing is part of the culture",
           "I bought myself new sunglasses",
           "we observed the beautiful starry sky",
           "a majestic waterfall poured down from the cliff",
           "people love strawberry ice cream the most",
           "we had a picnic in the park",
           "the mountain roller coaster was very exciting",
           "my brother and I were tossing the ball",)
}

VOICEPRINT_PHRASES = {
       "SK": ("Dnes je krásne slnečné počasie.",
              "Ahoj, ako sa máš?",
              "Prajem ti pekný a úspešný deň!",
              "Na večeru pôjdeme do reštaurácie.",
              "Kedy si naposledy čítal knihu?",
              "Cez víkend budem doma oddychovať.",
              "Veľa šťastia na dnešnej obhajobe!",
              "Ktorý film by si chcel vidieť?",
              "Ráno musím skoro vstávať.",
              "Poobede cestujem do zahraničia.",
              "Na obed som mal rybu so zemiakmi.",
              "Mal by som viac relaxovať.",
              "Stratil som kľúče od auta.",
              "Rád chodím na horskú turistiku.",
              "Dúfam, že sa nikomu nič nestalo.",
              "Prajem ti šťastné a pokojné sviatky.",
              "Kde pôjdeme v lete na dovolenku?",
              "Polej kvety a potom povysávaj!",
              "Chcel by som vedieť tvoj názor.",
              "Mohol by som vám nejako pomôcť?"),

       "EN": ("Today is beautiful sunny weather.",
              "Hello, how are you?",
              "I wish you a nice and successful day!",
              "We will go to a restaurant for dinner.",
              "When was the last time you read a book?",
              "I will rest at home during the weekend.",
              "Good luck on your exam today!",
              "Which movie would you like to watch?",
              "I have to get up early in the morning.",
              "I am traveling abroad in the afternoon.",
              "I had fish and potatoes for lunch.",
              "I should relax more.",
              "I lost my car keys.",
              "I like to go mountain hiking.",
              "I hope no one got hurt.",
              "I wish you happy and peaceful holidays.",
              "Where will we go on vacation in the summer?",
              "Water the flowers and then vacuum!",
              "I would like to know your opinion.",
              "Could I help you in any way?")
}

FONT_ROBOTO = "Roboto"
FONT_BOLD = "bold"
FONT_52 = 52
FONT_48 = 48
FONT_42 = 42
FONT_38 = 38
FONT_36 = 36
FONT_32 = 32
FONT_30 = 30
FONT_28 = 28
WIDTH_275 = 275
WIDTH_150 = 150
HEIGHT_100 = 100
HEIGHT_70 = 70
HEIGHT_60 = 60
HEIGHT_50 = 50

FONT_RALEWAY_BOLD = "Raleway ExtraBold"
FONT_RALEWAY_MEDIUM = "Raleway Medium"
FONT_RALEWAY = "Raleway"
FONT_RHD_BOLD = "Red Hat Display SemiBold"
FONT_RHD_MEDIUM = "Red Hat Display Medium"
FONT_RHD = "Red Hat Display"

FONT_LARGE = 50
FONT_MEDIUM = 40
FONT_SMALL_MEDIUM = 35
FONT_SMALL = 30

IMAGE_RESCALER_FHD = 3
IMAGE_RESCALER_HD = 4

BTN_PADDING_T_B_20 = 20
BTN_PADDING_T_B_30 = 30
BTN_PADDING_T_B_60 = 60
BTN_PADDING_L_R_30 = 30
BTN_PADDING_L_R_40 = 40
BTN_PADDING_L_R_60 = 60
BTN_PADDING_L_R_80 = 80
BTN_MARGIN_0 = 0
BTN_MARGIN_20 = 20
LBL_PADDING_10 = 10
LBL_PADDING_20 = 20
IMG_MARGIN_30 = 30
IMG_MARGIN_40 = 40
BORDER_WIDTH_5 = 5
BORDER_RADIUS_10 = 10
BORDER_RADIUS_15 = 15

INDEX_INTRO_FRAME = 0
INDEX_OPEN_DOOR_FRAME = 1
INDEX_ADMIN_FRAME = 2
INDEX_ABOUT_FRAME = 3
INDEX_SIGN_IN_FRAME = 4
INDEX_SIGN_UP_FRAME = 5
INDEX_FIRST_PHASE_SUCCESS_FRAME = 6
INDEX_SECOND_PHASE_SUCCESS_FRAME = 7
INDEX_AUTH_FIRST_PHASE_FRAME = 8
INDEX_AUTH_SECOND_PHASE_FRAME = 9
INDEX_AUTH_THIRD_PHASE_FRAME = 10
INDEX_NOT_INTERNET_CONN_FRAME = 11
INDEX_AUTH_UNSUCCESS_FRAME = 12
INDEX_AUTH_SUCCESS_FRAME = 13
INDEX_REGISTER_FRAME = 14
INDEX_REG_FIRST_PHASE_COMPLETED_FRAME = 15
INDEX_REG_SECOND_PHASE_COMPLETED_FRAME = 16
INDEX_REG_FIRST_PHASE_FRAME = 17
INDEX_REG_SECOND_PHASE_FRAME = 18
INDEX_REG_THIRD_PHASE_FRAME = 19
INDEX_REG_NOT_INTERNET_CONN_FRAME = 20
INDEX_REG_SUCCESS_FRAME = 21
INDEX_MANAGE_USERS = 22

