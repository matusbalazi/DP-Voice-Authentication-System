import customtkinter as ctk
import tkinter as tk
from translations import Translations
import time

ctk.set_ctk_parent_class(tk.Tk)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

window = ctk.CTk()

width = window.winfo_screenwidth()
height = window.winfo_screenheight()

window.geometry("%dx%d+0+0" % (width, height))
window.attributes("-fullscreen", True)
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

def create_frame():
    frame = ctk.CTkFrame(master=window)
    frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    for i in range(9):
        frame.columnconfigure(i, weight=1)
        frame.rowconfigure(i, weight=1)

    return frame


def change_language(language):
    Translations.set_language(language)
    update_translations()


def update_translations():
    label_main_title.configure(text=Translations.get_translation('system_authentication'))
    button_open_door.configure(text=Translations.get_translation('open_door'))
    button_about_project.configure(text=Translations.get_translation('about_project'))
    button_exit.configure(text=Translations.get_translation('exit'))


# create OPEN DOOR FRAME widgets
def button_open_door_callback():
    frame_intro.lower()
    frame_open_door.lift()

    label_main_title = ctk.CTkLabel(master=frame_open_door, text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    button_exit = ctk.CTkButton(master=frame_open_door, text=Translations.get_translation('exit'),
                                font=("Roboto", 32, "bold"),
                                command=button_exit_callback)
    button_exit.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_open_door, text=Translations.get_translation('back'),
                                font=("Roboto", 32, "bold"), command=button_back_callback)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_sign_in = ctk.CTkButton(master=frame_open_door, text=Translations.get_translation('sign_in'),
                                   font=("Roboto", 42, "bold"), command=button_sign_in_callback)
    button_sign_in.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_sign_up = ctk.CTkButton(master=frame_open_door, text=Translations.get_translation('sign_up'),
                                   font=("Roboto", 42, "bold"), command=button_sign_up_callback)
    button_sign_up.grid(row=5, column=4, pady=10, padx=10, sticky="nsew")


# create ABOUT FRAME widgets
def button_about_project_callback():
    frame_intro.lower()
    frame_about.lift()

    label_main_title = ctk.CTkLabel(master=frame_about, text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    button_exit = ctk.CTkButton(master=frame_about, text=Translations.get_translation('exit'),
                                font=("Roboto", 32, "bold"),
                                command=button_exit_callback)
    button_exit.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_about, text=Translations.get_translation('back'),
                                font=("Roboto", 32, "bold"), command=button_back_callback)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    label_thesis = ctk.CTkLabel(master=frame_about, text=Translations.get_translation('thesis'),
                                font=("Roboto", 42, "bold"), justify=ctk.CENTER)
    label_thesis.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

    label_about_project = ctk.CTkLabel(master=frame_about,
                                       text=Translations.get_translation('topic') + "\n" + Translations.get_translation(
                                           'student') + "\n" + Translations.get_translation(
                                           'mentor') + "\n" + Translations.get_translation('year'),
                                       font=("Roboto", 32), justify=ctk.LEFT)
    label_about_project.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    label_school = ctk.CTkLabel(master=frame_about, text=(
            Translations.get_translation('university') + "\n\n" + Translations.get_translation(
        'faculty') + "\n\n" + Translations.get_translation('department')), font=("Roboto", 32),
                                justify=ctk.CENTER)
    label_school.grid(row=5, column=4, pady=10, padx=10, sticky="nsew")

    entry_password = ctk.CTkEntry(master=frame_about, font=("Roboto", 32, "bold"), placeholder_text="", show="*",
                                  justify=ctk.CENTER)
    entry_password.grid(row=6, column=4, pady=10, padx=10, sticky="nsew")

    button_password = ctk.CTkButton(master=frame_about, text=Translations.get_translation('confirm'),
                                    font=("Roboto", 32, "bold"),
                                    command=lambda: button_password_callback(entry_password.get()))
    button_password.grid(row=7, column=4, pady=10, padx=10, sticky="nsew")


def button_exit_callback():
    window.destroy()


def segmented_button_language_callback(value):
    change_language(value)


def button_back_callback():
    frame_about.lower()
    frame_intro.lift()


def button_password_callback(value):
    if (value == "0000"):
        #frame_authentication_phrase_callback()
        pass


def button_sign_in_callback():
    frame_open_door.lower()
    frame_sign_in.lift()

    label_main_title = ctk.CTkLabel(master=frame_sign_in, text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_authenticate_user = ctk.CTkLabel(master=frame_sign_in,
                                           text=Translations.get_translation(
                                               'come_closer') + "\n\n" + Translations.get_translation(
                                               'start_recording'),
                                           font=("Roboto", 38), justify=ctk.LEFT)
    label_authenticate_user.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_sign_in, text=Translations.get_translation('back'),
                                font=("Roboto", 32, "bold"), command=button_back_callback)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_authenticate = ctk.CTkButton(master=frame_sign_in, text=Translations.get_translation('authenticate'),
                                font=("Roboto", 32, "bold"), command=lambda: button_authenticate_callback(button_authenticate, label_authenticate_user))
    button_authenticate.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")


def button_authenticate_callback(button_authenticate, label_authenticate_user):
    button_authenticate.destroy()
    label_authenticate_user.configure(text=Translations.get_translation('recording'))
    window.update()

    # Tento sleep potom vymazat
    time.sleep(2)

    label_authenticate_user.configure(text=Translations.get_translation('recording_ended'))
    window.update()
    # Tento sleep potom vymazat
    time.sleep(2)

    # frame_authentication_phrase_callback()

def button_sign_up_callback():
    pass

# create INTRO FRAME
frame_intro = create_frame()
frame_intro.lift()

# create ABOUT FRAME
frame_about = create_frame()
frame_about.lower()

# create OPEN DOOR FRAME
frame_open_door = create_frame()
frame_open_door.lower()

# create SIGN IN FRAME
frame_sign_in = create_frame()
frame_sign_in.lower()

# create INTRO FRAME widgets
label_main_title = ctk.CTkLabel(master=frame_intro, text=Translations.get_translation('system_authentication'),
                                font=("Roboto", 48, "bold"), justify=ctk.CENTER)
label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

button_open_door = ctk.CTkButton(master=frame_intro, text=Translations.get_translation('open_door'),
                                 font=("Roboto", 42, "bold"), command=button_open_door_callback)
button_open_door.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

button_about_project = ctk.CTkButton(master=frame_intro, text=Translations.get_translation('about_project'),
                                     font=("Roboto", 32, "bold"), command=button_about_project_callback)
button_about_project.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

button_exit = ctk.CTkButton(master=frame_intro, text=Translations.get_translation('exit'), font=("Roboto", 32, "bold"),
                            command=button_exit_callback)
button_exit.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

segmented_button_language = ctk.CTkSegmentedButton(master=frame_intro, values=["SK", "EN"], font=("Roboto", 32, "bold"),
                                                   command=segmented_button_language_callback)
segmented_button_language.grid(row=6, column=7, pady=10, padx=10, sticky="nsew")


def disable_minimize(event):
    window.overrideredirect(True)


window.bind("<Map>", disable_minimize)

window.mainloop()