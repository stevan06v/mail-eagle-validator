import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import imaplib
from email import message_from_bytes
from email.utils import getaddresses
import os
from PIL import Image, ImageTk
import base64

logo_base64 = """
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
"""

class EmailDownloaderApp:
    def __init__(self, root):
        self.root = root
        root.title('E-Mail-Downloader')

        # Variablen für die Auswahl-Widgets initialisieren
        self.separator_var = tk.StringVar(value=";")
        self.format_var = tk.StringVar(value="CSV")

        # Erstelle einen Frame als Container für alle Widgets, mit einem Rahmenabstand
        container = tk.Frame(root, padx=20, pady=20)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        # Dekodieren des Base64-Strings und Anzeigen des Bildes
        logo_data = base64.b64decode(logo_base64)
        self.logo_image = tk.PhotoImage(data=logo_data)
        logo_label = tk.Label(container, image=self.logo_image)
        logo_label.grid(row=0, column=0, columnspan=3, pady=(10, 10))

        # Eingabefelder und Beschriftungen
        tk.Label(container, text="E-Mail-Adresse:").grid(row=1, column=0, sticky=tk.W)
        self.email_entry = tk.Entry(container, width=30)
        self.email_entry.grid(row=1, column=1, sticky=tk.W+tk.E)

        tk.Label(container, text="Passwort:").grid(row=2, column=0, sticky=tk.W)
        self.password_entry = tk.Entry(container, show="*", width=30)
        self.password_entry.grid(row=2, column=1, sticky=tk.W+tk.E)

        tk.Label(container, text="IMAP-Server:").grid(row=3, column=0, sticky=tk.W)
        self.server_entry = tk.Entry(container, width=30)
        self.server_entry.grid(row=3, column=1, sticky=tk.W+tk.E)

        tk.Label(container, text="IMAP-Port:").grid(row=4, column=0, sticky=tk.W)
        self.port_entry = tk.Entry(container, width=10)
        self.port_entry.grid(row=4, column=1, sticky=tk.W+tk.E)
        self.port_entry.insert(0, "993")

        tk.Label(container, text="Speicherort:").grid(row=5, column=0, sticky=tk.W)
        self.filename_entry = tk.Entry(container, width=30)
        self.filename_entry.grid(row=5, column=1, sticky=tk.W+tk.E)
        
        # Der "Durchsuchen"-Button steht nun unter dem Eingabefeld
        self.browse_button = tk.Button(container, text="Durchsuchen", command=self.browse)
        self.browse_button.grid(row=6, column=1, sticky=tk.W)

        # Auswahl für Trennzeichen und Dateiformat
        tk.Label(container, text="Trennzeichen:").grid(row=7, column=0, sticky=tk.W)
        ttk.Combobox(container, textvariable=self.separator_var, values=[";", ","], state="readonly").grid(row=7, column=1, sticky=tk.W+tk.E)
        tk.Label(container, text="Dateiformat:").grid(row=8, column=0, sticky=tk.W)
        ttk.Combobox(container, textvariable=self.format_var, values=["CSV", "TXT"], state="readonly").grid(row=8, column=1, sticky=tk.W+tk.E)

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(container, textvariable=self.status_var)
        self.status_label.grid(row=9, column=0, columnspan=3, sticky=tk.W+tk.E)

        self.download_button = tk.Button(container, text="Download starten", command=self.start_download)
        self.download_button.grid(row=10, column=0, columnspan=3, sticky=tk.W+tk.E, pady=(5, 5))

        # Hinzufügen des "Powered by" Labels
        powered_label = tk.Label(container, text="Powered by Webagentur Hochmeir")
        powered_label.grid(row=11, column=0, columnspan=3, sticky=tk.S, pady=(5, 5))

    def browse(self):
        filetype = [('CSV files', '*.csv')] if self.format_var.get() == "CSV" else [('Text files', '*.txt')]
        filepath = filedialog.asksaveasfilename(defaultextension=filetype[0][1], filetypes=filetype)
        if filepath:
            self.filename_entry.delete(0, tk.END)
            self.filename_entry.insert(0, filepath)

    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()

    def start_download(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        server = self.server_entry.get()
        port = int(self.port_entry.get())
        filename = self.filename_entry.get()
        separator = self.separator_var.get()
        format = self.format_var.get()

        if not os.path.isabs(filename):
            messagebox.showerror("Fehler", "Bitte geben Sie einen vollständigen \nPfad zum Speichern der Datei an.")
            return

        self.update_status("Verbindung zum Server wird hergestellt...")

        try:
            email_addresses = set()
            mail = imaplib.IMAP4_SSL(server, port)
            mail.login(email, password)
            self.update_status("Verbindung zum Server erfolgreich.")
            
            mail.select('inbox')
            self.update_status("E-Mail-Adressen werden gesammelt...")

            result, messages = mail.search(None, 'ALL')
            if result == 'OK':
                for num in messages[0].split():
                    result, data = mail.fetch(num, '(RFC822)')
                    if result == 'OK':
                        msg = message_from_bytes(data[0][1])
                        email_from = msg['From']
                        addresses = getaddresses([email_from])
                        for name, addr in addresses:
                            if addr:
                                email_addresses.add((name, addr))  # Speichern als Tupel

            self.update_status("Schreibe E-Mails in die Datei...")
            with open(filename, 'w', encoding='utf-8') as file:
                for name, addr in sorted(email_addresses, key=lambda x: x[1]):  # Sortierung nach E-Mail
                    if format == "CSV":
                        line = f'"{name}"{separator}"{addr}"'
                    else:  # TXT-Format
                        line = f"{name}\t{addr}"
                    file.write(line + "\n")

            self.update_status("Die E-Mails wurden erfolgreich \nheruntergeladen und gespeichert.")
            messagebox.showinfo("Erfolg", "Die E-Mails wurden erfolgreich \nheruntergeladen und gespeichert.")
        except Exception as e:
            self.update_status("Ein Fehler ist aufgetreten.")
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {e}")
        finally:
            if 'mail' in locals():
                mail.logout()


if __name__ == "__main__":
    root = tk.Tk()
    app = EmailDownloaderApp(root)
    
    # Update root to ensure all widgets are accounted for
    root.update()
    
    # Berechnen der Fensterposition, um es zentriert anzuzeigen
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    
    # Setzen der Position des Hauptfensters
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    root.mainloop()
