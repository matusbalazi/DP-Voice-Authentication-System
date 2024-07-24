LOGIN_SUCCESS = True
VERIFICATION_SUCCESS = True
AUTHENTICATION_SUCCESS = True
IS_ADMIN = True
PARTIAL_AUTHORIZATION = True
NUMBER_OF_VOICEPRINTS = 10
PARTIAL_AUTHORIZATION_THRESHOLD = 70

RECORDED_AUDIO_FILENAME = "recorded_audio.wav"
USERS_FILENAME = "users.json"
TMP_USERS_FILENAME = "tmp_users.json"
LOGS_FILENAME = "app_logs.txt"
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
FONT_RALEWAY_BOLD = "Raleway ExtraBold"
FONT_RALEWAY_MEDIUM = "Raleway Medium"
FONT_RALEWAY = "Raleway"
FONT_RHD_BOLD = "Red Hat Display SemiBold"
FONT_RHD_MEDIUM = "Red Hat Display Medium"
FONT_RHD = "Red Hat Display"
FONT_BOLD = "bold"
FONT_LARGE = 50
FONT_MEDIUM = 40
FONT_SMALL = 30
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


# VERIFICATION_WORDS = ["kvet", "počítač", "rieka", "stolička", "jablko", "škola", "letisko", "nástenka", "pláž", "okno",
#                      "hora", "kľúč", "rukavica", "káva", "slúchadlo", "vlak"]
# SPEAKERS = ["martin", "ema", "baláži"]
# USERS = {
#    "martin": ("a713e2c7b57053c8ec7b709b553bdfab77f185f2d07cc7c6fab661a00b7e794e", "c0fac90777089ec970ef51edf5fb6ea9"),
#    "ema": ("a713e2c7b57053c8ec7b709b553bdfab77f185f2d07cc7c6fab661a00b7e794e", "c0fac90777089ec970ef51edf5fb6ea9"),
#    "baláži": ("a713e2c7b57053c8ec7b709b553bdfab77f185f2d07cc7c6fab661a00b7e794e", "c0fac90777089ec970ef51edf5fb6ea9"),
#    "vista": ("a713e2c7b57053c8ec7b709b553bdfab77f185f2d07cc7c6fab661a00b7e794e", "c0fac90777089ec970ef51edf5fb6ea9")
# }
