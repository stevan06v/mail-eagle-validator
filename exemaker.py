import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--noconsole',
    '--name=mail-eagle',
    '--icon=icon.ico',
    '--add-data=icon.ico;.',
    '--add-data=blacklist.txt;.'
])
