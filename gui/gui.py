import customtkinter as ctk
import tkinter as tk
from translations import Translations
from authentication import credentials, hash_password
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


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def clear_authentication_frames():
    for frame in authentication_frames:
        for widget in frame.winfo_children():
            widget.destroy()


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
                                font=("Roboto", 38, "bold"),
                                command=button_exit_callback, width=150, height=50)
    button_exit.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_open_door, text=Translations.get_translation('back'),
                                font=("Roboto", 38, "bold"),
                                command=lambda: button_back_callback(frame_open_door, frame_intro), width=150,
                                height=50)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_sign_in = ctk.CTkButton(master=frame_open_door, text=Translations.get_translation('sign_in'),
                                   font=("Roboto", 48, "bold"), command=button_sign_in_callback)
    button_sign_in.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_sign_up = ctk.CTkButton(master=frame_open_door, text=Translations.get_translation('sign_up'),
                                   font=("Roboto", 48, "bold"), command=button_sign_up_callback)
    button_sign_up.grid(row=5, column=4, pady=10, padx=10, sticky="nsew")


# create ABOUT FRAME widgets
def button_about_project_callback():
    frame_intro.lower()
    frame_about.lift()

    label_main_title = ctk.CTkLabel(master=frame_about, text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    button_exit = ctk.CTkButton(master=frame_about, text=Translations.get_translation('exit'),
                                font=("Roboto", 38, "bold"),
                                command=button_exit_callback, width=150, height=100)
    button_exit.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_about, text=Translations.get_translation('back'),
                                font=("Roboto", 38, "bold"),
                                command=lambda: button_back_callback(frame_about, frame_intro), width=150, height=100)
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

    entry_password = ctk.CTkEntry(master=frame_about, font=("Roboto", 38, "bold"), placeholder_text="", show="*",
                                  justify=ctk.CENTER, width=150, height=100)
    entry_password.grid(row=6, column=4, pady=10, padx=10, sticky="nsew")

    button_password = ctk.CTkButton(master=frame_about, text=Translations.get_translation('confirm'),
                                    font=("Roboto", 38, "bold"),
                                    command=lambda: button_password_callback(entry_password.get()), width=150,
                                    height=100)
    button_password.grid(row=7, column=4, pady=10, padx=10, sticky="nsew")


def button_exit_callback():
    window.destroy()


def segmented_button_language_callback(value):
    change_language(value)


def button_back_callback(frame_to_hide, frame_to_show):
    clear_frame(frame_to_hide)
    frame_to_hide.lower()
    frame_to_show.lift()


def button_password_callback(value):
    correct_password = hash_password.check_password(value, credentials.password, credentials.sol)
    if (correct_password):
        button_open_door_callback()
        frame_open_door.lower()
        button_sign_in_callback()
        frame_authentication_phase_1.lower()
        frame_authentication_phase_3_callback()


# create AUTHENTICATION PHASE 1 FRAME widgets -> after click on SIGN IN button
def button_sign_in_callback():
    frame_open_door.lower()
    frame_authentication_phase_1.lift()
    clear_authentication_frames()

    label_main_title = ctk.CTkLabel(master=frame_authentication_phase_1,
                                    text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_first_phase = ctk.CTkLabel(master=frame_authentication_phase_1,
                                     text=Translations.get_translation('first_phase'),
                                     font=("Roboto", 38, "bold"), text_color=("light green"), justify=ctk.CENTER)
    label_first_phase.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    label_authenticate_user = ctk.CTkLabel(master=frame_authentication_phase_1,
                                           text=Translations.get_translation(
                                               'come_closer_1') + "\n\n" + Translations.get_translation(
                                               'start_recording'),
                                           font=("Roboto", 38), justify=ctk.LEFT)
    label_authenticate_user.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_authentication_phase_1, text=Translations.get_translation('back'),
                                font=("Roboto", 38, "bold"),
                                command=lambda: button_back_callback(frame_authentication_phase_1, frame_open_door),
                                width=275,
                                height=70)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_authenticate = ctk.CTkButton(master=frame_authentication_phase_1,
                                        text=Translations.get_translation('authenticate'),
                                        font=("Roboto", 38, "bold"),
                                        command=lambda: button_authenticate_phase_1_callback(label_first_phase,
                                                                                             label_authenticate_user,
                                                                                             button_back,
                                                                                             button_authenticate),
                                        width=275,
                                        height=70)
    button_authenticate.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")


def button_authenticate_phase_1_callback(label_first_phase, label_authenticate_user, button_back, button_authenticate):
    label_first_phase.destroy()
    button_back.destroy()
    button_authenticate.destroy()
    label_authenticate_user.configure(text=Translations.get_translation('recording'))
    window.update()

    # Tento sleep potom vymazat
    time.sleep(2)

    label_authenticate_user.configure(text=Translations.get_translation('recording_ended'))
    window.update()

    # Tento sleep potom vymazat
    time.sleep(2)

    frame_authentication_phase_2_callback()


# create AUTHENTICATION PHASE 2 FRAME widgets
def frame_authentication_phase_2_callback():
    frame_authentication_phase_1.lower()
    frame_authentication_phase_2.lift()
    clear_authentication_frames()

    label_main_title = ctk.CTkLabel(master=frame_authentication_phase_2,
                                    text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_sign_in_success = ctk.CTkLabel(master=frame_authentication_phase_2,
                                         text=Translations.get_translation('sign_in_success'),
                                         font=("Roboto", 38, "bold"), text_color=("light green"), justify=ctk.CENTER)
    label_sign_in_success.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

    window.update()

    # Pozor sleep
    time.sleep(2)

    label_sign_in_success.destroy()

    label_second_phase = ctk.CTkLabel(master=frame_authentication_phase_2,
                                      text=Translations.get_translation('second_phase'),
                                      font=("Roboto", 38, "bold"), text_color=("light green"), justify=ctk.CENTER)
    label_second_phase.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    label_authenticate_user = ctk.CTkLabel(master=frame_authentication_phase_2,
                                           text=Translations.get_translation(
                                               'come_closer_2') + "\n\n" + Translations.get_translation(
                                               'start_recording'),
                                           font=("Roboto", 38), justify=ctk.LEFT)
    label_authenticate_user.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_authentication_phase_2, text=Translations.get_translation('back'),
                                font=("Roboto", 38, "bold"),
                                command=lambda: button_back_callback(frame_authentication_phase_2, frame_open_door),
                                width=275,
                                height=70)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_authenticate = ctk.CTkButton(master=frame_authentication_phase_2,
                                        text=Translations.get_translation('authenticate'),
                                        font=("Roboto", 38, "bold"),
                                        command=lambda: button_authenticate_phase_2_callback(label_second_phase,
                                                                                             label_authenticate_user,
                                                                                             button_back,
                                                                                             button_authenticate),
                                        width=275,
                                        height=70)
    button_authenticate.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    window.update()


def button_authenticate_phase_2_callback(label_second_phase, label_authenticate_user, button_back, button_authenticate):
    label_second_phase.destroy()
    button_back.destroy()
    button_authenticate.destroy()
    label_authenticate_user.configure(text=Translations.get_translation('recording'))
    window.update()

    # Tento sleep potom vymazat
    time.sleep(2)

    label_authenticate_user.configure(text=Translations.get_translation('recording_ended'))
    window.update()

    # Tento sleep potom vymazat
    time.sleep(2)

    frame_authentication_phase_3_callback()


# create AUTHENTICATION PHASE 3 FRAME widgets
def frame_authentication_phase_3_callback():
    frame_authentication_phase_2.lower()
    frame_authentication_phase_3.lift()
    clear_authentication_frames()

    label_main_title = ctk.CTkLabel(master=frame_authentication_phase_3,
                                    text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_verification_success = ctk.CTkLabel(master=frame_authentication_phase_3,
                                              text=Translations.get_translation('verification_success'),
                                              font=("Roboto", 38, "bold"), text_color=("light green"),
                                              justify=ctk.CENTER)
    label_verification_success.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

    window.update()

    # Pozor sleep
    time.sleep(2)

    label_verification_success.destroy()

    label_third_phase = ctk.CTkLabel(master=frame_authentication_phase_3,
                                     text=Translations.get_translation('third_phase'),
                                     font=("Roboto", 38, "bold"), text_color=("light green"), justify=ctk.CENTER)
    label_third_phase.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    label_authenticate_user = ctk.CTkLabel(master=frame_authentication_phase_3,
                                           text=Translations.get_translation(
                                               'come_closer_3') + "\n\n" + Translations.get_translation(
                                               'start_recording'),
                                           font=("Roboto", 38), justify=ctk.LEFT)
    label_authenticate_user.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_authentication_phase_3, text=Translations.get_translation('back'),
                                font=("Roboto", 38, "bold"),
                                command=lambda: button_back_callback(frame_authentication_phase_3, frame_open_door),
                                width=275,
                                height=70)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_authenticate = ctk.CTkButton(master=frame_authentication_phase_3,
                                        text=Translations.get_translation('authenticate'),
                                        font=("Roboto", 38, "bold"),
                                        command=lambda: button_authenticate_phase_3_callback(label_third_phase,
                                                                                             label_authenticate_user,
                                                                                             button_back,
                                                                                             button_authenticate),
                                        width=275,
                                        height=70)
    button_authenticate.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    window.update()


def button_authenticate_phase_3_callback(label_third_phase, label_authenticate_user, button_back, button_authenticate):
    label_third_phase.destroy()
    button_back.destroy()
    button_authenticate.destroy()
    label_authenticate_user.configure(text=Translations.get_translation('recording'))
    window.update()

    # Tento sleep potom vymazat
    time.sleep(2)

    label_authenticate_user.configure(text=Translations.get_translation('recording_ended'))
    window.update()

    # Tento sleep potom vymazat
    time.sleep(2)

    frame_authentication_success_callback()


def frame_authentication_success_callback():
    frame_authentication_phase_3.lower()
    frame_authentication_success.lift()

    label_main_title = ctk.CTkLabel(master=frame_authentication_success,
                                    text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_authentication_success = ctk.CTkLabel(master=frame_authentication_success,
                                                text=Translations.get_translation('authentication_success'),
                                                font=("Roboto", 38, "bold"), text_color=("light green"),
                                                justify=ctk.CENTER)
    label_authentication_success.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

    window.update()

    # Pozor sleep
    time.sleep(2)

    label_authentication_success.destroy()

    button_end_interaction = ctk.CTkButton(master=frame_authentication_success,
                                           text=Translations.get_translation('end_interaction'),
                                           font=("Roboto", 48, "bold"), command=button_end_interaction_callback)
    button_end_interaction.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_register_user = ctk.CTkButton(master=frame_authentication_success,
                                         text=Translations.get_translation('register_user'),
                                         font=("Roboto", 48, "bold"), command=button_register_user_callback)
    button_register_user.grid(row=5, column=4, pady=10, padx=10, sticky="nsew")


def button_end_interaction_callback():
    frame_authentication_success.lower()
    clear_frame(frame_authentication_success)
    frame_intro.lift()


def button_register_user_callback():
    pass


def button_sign_up_callback():
    pass


authentication_frames = []

# create INTRO FRAME
frame_intro = create_frame()
frame_intro.lift()

# create ABOUT FRAME
frame_about = create_frame()
frame_about.lower()

# create OPEN DOOR FRAME
frame_open_door = create_frame()
frame_open_door.lower()

# create AUTHENTICATION PHASE 1 FRAME -> after click on SIGN IN button
frame_authentication_phase_1 = create_frame()
frame_authentication_phase_1.lower()
authentication_frames.append(frame_authentication_phase_1)

# create AUTHENTICATION PHASE 2 FRAME
frame_authentication_phase_2 = create_frame()
frame_authentication_phase_2.lower()
authentication_frames.append(frame_authentication_phase_2)

# create AUTHENTICATION PHASE 3 FRAME
frame_authentication_phase_3 = create_frame()
frame_authentication_phase_3.lower()
authentication_frames.append(frame_authentication_phase_3)

# create AUTHENTICATION SUCCESS FRAME
frame_authentication_success = create_frame()
frame_authentication_success.lower()

# create INTRO FRAME widgets
label_main_title = ctk.CTkLabel(master=frame_intro, text=Translations.get_translation('system_authentication'),
                                font=("Roboto", 48, "bold"), justify=ctk.CENTER)
label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

button_open_door = ctk.CTkButton(master=frame_intro, text=Translations.get_translation('open_door'),
                                 font=("Roboto", 48, "bold"), command=button_open_door_callback)
button_open_door.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

button_about_project = ctk.CTkButton(master=frame_intro, text=Translations.get_translation('about_project'),
                                     font=("Roboto", 38, "bold"), command=button_about_project_callback, width=150,
                                     height=50)
button_about_project.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

button_exit = ctk.CTkButton(master=frame_intro, text=Translations.get_translation('exit'), font=("Roboto", 38, "bold"),
                            command=button_exit_callback, width=150, height=50)
button_exit.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

segmented_button_language = ctk.CTkSegmentedButton(master=frame_intro, values=["SK", "EN"], font=("Roboto", 38, "bold"),
                                                   command=segmented_button_language_callback, width=150, height=50)
segmented_button_language.grid(row=6, column=7, pady=10, padx=10, sticky="nsew")


def disable_minimize(event):
    window.overrideredirect(True)


window.bind("<Map>", disable_minimize)

window.mainloop()
