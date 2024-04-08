virtualenv --python="/opt/homebrew/bin/python3.11" venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
brew install python-tk

source venv/bin/activate

pip install pillow --break-system-packages

pyinstaller --name 'MailEagle' \
            --icon 'icon.ico' \
            --windowed  \
            --add-data='./blacklist.txt:.' \
            main.py

brew install create-dmg

mkdir -p dist/dmg
cp -r "dist/MailEagle.app" dist/dmg

create-dmg \
  --volname "MailEagle" \
  --volicon "icon.ico" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "MailEagle.app" 175 120 \
  --hide-extension "MailEagle.app" \
  --app-drop-link 425 120 \
  "dist/MailEagle.dmg" \
  "dist/dmg/"