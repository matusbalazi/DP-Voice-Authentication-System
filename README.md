# Voice Authentication System
<p align="justify">
    <i><b>The aim of this work</b></i> is to explore and analyze the current state of 
    voice authentication technology, its principles, benefits, and limitations.
    The software part includes an application programmed in the Python programming language and 
    controlled through a graphical user interface. This program incorporates modules for encryption, 
    authentication, language localization, file management, internet and database connection control,
    database operations, logging mechanism, voice recorder, voice and speech recognizer, and additional 
    scripts extending the application's functionality. The SpeechBrain tool is used for voice recognition, and 
    speech recognition works with the Google API. We further improved and expanded these tools to meet 
    all the requirements for creating high-quality voice authentication.
</p>
<br>

## Installation Guidelines
Content:
<ol type="1">
    <li>Cloning the repository</li>
    <li>Installation of system packages</li>
    <li>Installation of required packages (requirements.txt)</li>
    <li>Initialization of database and database table</li>
    <li>Enabling microphone</li>
    <li>Installation of text fonts</li>
    <li>Extending application is not responding time</li>
</ol>
<br>

### 1. Cloning the repository
<ol type="a">
    <li>open terminal</li>
    <li>run update:</li>
    <pre><code>sudo apt-get update</code></pre>
    <li>install git:</li>
    <pre><code>sudo apt-get install git</code></pre>
    <li>clone repository:</li>
    <pre><code>sudo git clone https://github.com/matusbalazi/DP-Voice-Authentication-System.git</code></pre>
    <li>change location:</li>
    <pre><code>cd DP-Voice-Authentication-System/</code></pre>
</ol>

### 2. Installation of system packages
<ol type="a">
    <li>change location:</li>
    <pre><code>cd DP-Voice-Authentication-System/installation/</code></pre>
    <li>make installation file executable:</li>
    <pre><code>sudo chmod +x ./install_system_packages</code></pre>
    <li>run installation:</li>
    <pre><code>./install_system_packages</code></pre>
</ol>
<p align="justify">
    <i><b>NOTE:</b></i>&nbsp; all packages should install succesfully
</p>

### 3. Installation of required packages (requirements.txt)
<ol type="a">
    <li>change location if needed:</li>
    <pre><code>cd DP-Voice-Authentication-System/installation/</code></pre>
    <li>make installation file executable:</li>
    <pre><code>sudo chmod +x ./install_requirements</code></pre>
    <li>run installation:</li>
    <pre><code>./install_requirements</code></pre>
    <li>additionally install speechbrain again:</li>
    <pre><code>sudo pip install speechbrain --break-system-packages</code></pre>
    <p align="justify">
        <i>only speechbrain package must be installed this way to be accessible by the application</i>
    </p>
</ol>
<p align="justify">
    <i><b>NOTE:</b></i>&nbsp; after installation if there is an error with cryptography package just ignore that error
    <br>
    <i><b>NOTE:</b></i>&nbsp; other packages should install succesfully
</p>

### 4. Initialization of database and database table
<ol type="a">
    <li>ensure that the server starts every time the operating system is started:</li>
    <pre><code>sudo systemctl start mariadb.service</code></pre>
    <li>[CAN BE DEPRECATED] if this command is still present in the mariadb-service package, then configure the server using it, else go to the next step:</li>
    <pre><code>sudo mysql_secure_installation</code></pre>
    <li>start MariaDB command prompt:</li>
    <pre><code>sudo mariadb</code></pre>
    <li>create database:</li>
    <pre><code>CREATE DATABASE IF NOT EXISTS voice_authentication_system;</code></pre>
    <li>change location:</li>
    <pre><code>USE voice_authentication_system;</code></pre>
    <li>create table inside the database:</li>
    <pre><code>CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    login_name VARCHAR(50) NOT NULL,
    unique_phrase_hash VARCHAR(100) NOT NULL,
    unique_phrase_salt VARCHAR(100) NOT NULL,
    registration_w_internet BOOLEAN NOT NULL,
    voiceprint_1 BLOB, voiceprint_2 BLOB, voiceprint_3 BLOB, voiceprint_4 BLOB,
    voiceprint_5 BLOB, voiceprint_6 BLOB, voiceprint_7 BLOB, voiceprint_8 BLOB,
    voiceprint_9 BLOB, voiceprint_10 BLOB, voiceprint_11 BLOB, voiceprint_12 BLOB
    );</code></pre>
    <li>grant privileges for user root:</li>
    <pre><code>GRANT ALL PRIVILEGES ON *.* TO 'root'@localhost IDENTIFIED BY 'root';</code></pre>
</ol>
<p align="justify">
    <i><b>NOTE:</b></i>&nbsp; ensure that created user is 'root' with password 'root'
    <br>
    <i><b>NOTE:</b></i>&nbsp; if you are not able to connect to database from application, double check database privileges for user 'root'
</p>

### 5. Enabling microphone
<ol type="a">
    <li>start pulseaudio:</li>
    <pre><code>pulseaudio --start</code></pre>
    <li>start pavucontrol and close after start:</li>
    <pre><code>pavucontrol</code></pre>
    <li>check information about connected microphones:</li>
    <pre><code>arecord -l</code></pre>
    <p align="justify">
        <i>notice the card number which is displayed for your microphone</i>
    </p>
    <li>open alsa.conf file in text editor:</li>
    <pre><code>sudo nano /usr/share/alsa/alsa.conf</code></pre>
    <p align="justify">
        <i>find <b>defaults.pcm.card #number#</b> and replace the <b>#number#</b> with the card number of your connected microphone</i>
    </p>
    <li>test microphone if it is recording correctly:</li>
    <pre><code>sudo arecord --format=S16_LE --duration=5 --rate=16000 --file-type=wav out.wav</code></pre>
    <li>check microphone settings:</li>
    <p align="justify">
        <i>go to Settings -> Sound -> check if set microphone is the correct microphone</i>
    </p>
</ol>

### 6. Installation of text fonts
<ol type="a">
    <li>create system folders for the new fonts:</li>
    <pre><code>sudo mkdir /usr/share/fonts/truetype/Raleway</code></pre>
    <pre><code>sudo mkdir /usr/share/fonts/truetype/RedHatDisplay</code></pre>
    <li>change location:</li>
    <pre><code>cd DP-Voice-Authentication-System/fonts/Raleway/</code></pre>
    <li>copy all .ttf files to your system:</li>
    <pre><code>sudo cp * /usr/share/fonts/truetype/Raleway</code></pre>
    <li>change location:</li>
    <pre><code>cd DP-Voice-Authentication-System/fonts/RedHatDisplay/</code></pre>
    <li>copy all .ttf files to your system:</li>
    <pre><code>sudo cp * /usr/share/fonts/truetype/RedHatDisplay</code></pre>
    <li>update the font cache:</li>
    <pre><code>sudo fc-cache -f -v</code></pre>
    <li>verify installed fonts:</li>
    <pre><code>fc-list | grep "Raleway"</code></pre>
    <pre><code>fc-list | grep "Red Hat Display"</code></pre>
</ol>

### 7. Extending application is not responding time
<ol type="a">
    <li>extend not responding time to one minute:</li>
    <pre><code>gsettings set org.gnome.mutter check-alive-timeout 60000</code></pre>
</ol>


## Application Start
There are different versions of the application:
<ol type="1">
    <li><i><b>gui.py</b></i> - the old version with three-phases security check mechanism (UI created in CustomTkinter)</li>
    <li><i><b>gui_simple.py</b></i> - the old version with two-phases security check mechanism (UI created in CustomTkinter)</li>
    <li><i><b>gui_new.py</b></i> - the new version with three-phases security check mechanism (UI created in PyQt6)</li>
    <li><i><b>gui_new.py [simple_mode]</b></i> - the new version with argument to launch simple mode with two-phases security check mechanism (UI created in PyQt6)</li>
</ol>

To run the new version of application:
<ol type="a">
    <li>open the terminal</li>
    <li>change location:</li>
    <pre><code>cd DP-Voice-Authentication-System/</code></pre>
    <li>start application in full mode</li>
    <pre><code>sudo python3 gui_new.py</code></pre>
    <li>start application in simple mode</li>
    <pre><code>sudo python3 gui_new.py -s True</code></pre>
    <p align="justify">
        <i>or</i>
    </p>
    <pre><code>sudo python3 gui_new.py --simple True</code></pre>
</ol>
