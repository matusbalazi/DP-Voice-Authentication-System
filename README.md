# Voice Authentication System
<p align="justify">
    <b>The aim of this work</b> is to explore and analyze the current state of 
    voice authentication technology, its principles, benefits, and limitations.
    Further, we present the ongoing work on the development of the voice 
    authentication system both from software and hardware perspectives. 
    We demonstrate its usability in a pilot application for controlling 
    an electromagnetic lock. We designed the solution to be functional, fast, 
    secure, reliable, and user-friendly.
</p>

## Installation Guidelines
<p align="justify">
<b>Content:</b>
</p>
<ol type="1">
    <li>Cloning the repository</li>
    <li>Installation of system packages</li>
    <li>Installation of required packages (requirements.txt)</li>
    <li>Initialization of database and database table</li>
    <li>Enabling microphone</li>
    <li>Installation of text fonts</li>
    <li>Extending application is not responding time</li>
</ol>

### 1. Cloning the repository
<ol type="a">
    <li>open terminal</li>
    <li>run update:</li>
        ```
        sudo apt-get update
        ```
    <li>install git:</li>
        ```
        sudo apt-get install git
        ```
    <li>clone repository:</li>
        ```
        sudo git clone https://github.com/matusbalazi/DP-Voice-Authentication-System.git
        ```
    <li>change location:</li>
        ```
        cd /DP-Voice-Authentication-System
        ```

2. Installation of system packages
    a) change location:
        cd /DP-Voice-Authentication-System/installation
    b) make installation file executable:
        sudo chmod +x ./install_system_packages
    c) run installation:
        ./install_system_packages

    - ALL PACKAGES should install succesfully

3. Installation of required packages (requirements.txt)
    a) change location if needed:
        cd /DP-Voice-Authentication-System/installation
    b) make installation file executable:
        sudo chmod +x ./install_requirements
    c) run installation:
        ./install_requirements

    - AFTER INSTALLATION if there is an error with cryptography package just ignore that error
    - OTHER PACKAGES should install succesfully

4. Initialization of database and database table

5. Enabling microphone

6. Installation of text fonts

7. Extending application is not responding time
    a) extend not responding time to one minute:
        gsettings set org.gnome.mutter check-alive-timeout 60000
