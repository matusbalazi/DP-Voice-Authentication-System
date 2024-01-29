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
            'first_phase': "1. fáza autentifikácie",
            'come_closer_1': "• Pristúpte bližšie k mikrofónu zariadenia a povedzte\n  svoje prihlasovacie meno.",
            'start_recording': "• Nahrávanie spustíte stlačením tlačidla Autentifikovať.",
            'recording': "PREBIEHA NAHRÁVANIE... ",
            'recording_ended': "Nahrávanie skončilo.",

            'sign_in_success': "Prihlásenie prebehlo úspešne!",
            'second_phase': "2. fáza autentifikácie",
            'come_closer_2': "• Pristúpte bližšie k mikrofónu zariadenia a povedzte náhodne\n  vygenerované slovo, ktoré sa zobrazí na displeji.",

            'verification_success': "Overenie prebehlo úspešne!",
            'third_phase': "3. fáza autentifikácie",
            'come_closer_3': "• Pristúpte bližšie k mikrofónu zariadenia a povedzte jedinečnú\n  frázu, ktorú ste si zvolili pri registrácii."
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

            'authenticate': "Authenticate",
            'first_phase': "1st Authentication Phase",
            'come_closer_1': "• Come closer to the device's microphone and say your login name.",
            'start_recording': "• You can start recording by pressing the Authenticate button.",
            'recording': "RECORDING...",
            'recording_ended': "Recording ended.",

            'sign_in_success': "Login successful!",
            'second_phase': "2nd Authentication Phase",
            'come_closer_2': "• Come closer to the device's microphone and say a randomly\n  generated word that appears on the display.",

            'verification_success': "Verification successful!",
            'third_phase': "3rd Authentication Phase",
            'come_closer_3': "• Come closer to the device's microphone and say the unique\n  phrase you chose during registration."
        }
    }

    current_language = 'SK'

    @classmethod
    def get_translation(cls, key):
        return cls.translations[cls.current_language][key]

    @classmethod
    def set_language(cls, language):
        cls.current_language = language
