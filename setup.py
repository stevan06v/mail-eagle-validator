╰─ pyinstaller --name 'MailEagle' \
            --windowed  \
            --add-data='./blacklist.txt:.' \
            --icon 'icon.icsn' \ 
            main.py