class Translations:
    translations = {
        'SK': {
            'system_authentication': "Systém hlasovej autentifikácie",
            'open_door': "Otvoriť dvere",
            'about_project': "O projekte",
            'exit': "Koniec",
            'university': "ŽILINSKÁ UNIVERZITA V ŽILINE",
            'faculty': "FAKULTA ELEKTROTECHNIKY\nA INFORMAČNÝCH TECHNOLÓGIÍ",
            'department': "Katedra multimédií a informačno-\nkomunikačných technológií",

            'back': "Späť",
            'thesis': "Diplomová práca",
            'topic': "Téma:\tSystém hlasovej autentifikácie",
            'student': "Študent:\tBc. Matúš Baláži",
            'mentor': "Vedúci:\tdoc. Ing. Roman Jarina, PhD.",
            'year': "Rok:\t2023/2024",
            'confirm': "Potvrdiť",

            'sign_in': "Prihlásenie",
            'sign_up': "Registrácia",

            'authenticate': "Autentifikovať",
            'come_closer': "• Pristúpte bližšie k mikrofónu zariadenia a povedzte svoje prihlasovacie meno.",
            'start_recording': "• Nahrávanie spustíte stlačením tlačidla Autentifikovať.",
            'recording': "PREBIEHA NAHRÁVANIE... ",
            'recording_ended': "Nahrávanie skončilo."
        },
        'EN': {
            'system_authentication': "Voice Authentication System",
            'open_door': "Open the Door",
            'about_project': "About",
            'exit': "Exit",
            'university': "UNIVERSITY OF ŽILINA",
            'faculty': "Faculty of Electrical Engineering\n and Information Technology",
            'department': "Department of Multimedia and Information-\nCommunication Technologies",

            'back': "Back",
            'thesis': "Diploma Thesis",
            'topic': "Topic:\tVoice Authentication System",
            'student': "Student:\tBc. Matúš Baláži",
            'mentor': "Mentor:\tdoc. Ing. Roman Jarina, PhD.",
            'year': "Year:\t2023/2024",
            'confirm': "Confirm",

            'sign_in': "Sign in",
            'sign_up': "Sign up",

            'interrupt': "Interrupt Authentication",
            'come_closer': "• Move closer to the device's microphone and say your login name.",
            'countdown_first_part': "• Recording will start in ",
            'countdown_second_part': " sec. and will last 10 seconds.",
            'recording': "RECORDING...",
            'recording_ended': "Recording ended."
        }
    }

    current_language = 'SK'

    @classmethod
    def get_translation(cls, key):
        return cls.translations[cls.current_language][key]

    @classmethod
    def set_language(cls, language):
        cls.current_language = language
