import queue
import threading
import tkinter as tk
import tkinter
import customtkinter
import csv
from CTkListbox import *
from tkinter import filedialog as fd, messagebox, ttk
from email_validator import validate_email, caching_resolver, EmailNotValidError
from disposable_email_domains import blocklist
import os
import imaplib
from email import message_from_bytes
from email.utils import getaddresses
from PIL import Image, ImageTk
import base64


queue_for_insert = queue.Queue()
cores = os.cpu_count()
stop_processing_flag = threading.Event()
email_list = []
invalid_emails = []
valid_emails = []
black_list = list()
checked_domains = set()
thread_count = os.cpu_count() * 2
show_email_count = 50
validated_count = 0
validation_thread = None
stop_validation_flag = threading.Event()


class NotificationTopLevelWindow(customtkinter.CTkToplevel):
    def __init__(self, message="", valid=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("200x50")

        self.maxsize(200, 50)
        self.minsize(200, 50)
        self.title("Success" if valid else "Error")

        message_label = customtkinter.CTkLabel(master=self, text=message,
                                               font=("System", 12, "bold"), text_color="green" if valid else "red")
        message_label.place(relx=.5, rely=.45, anchor=tkinter.CENTER)


class SingleMailToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, email="", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry("500x100")
        self.title(f"{email}-Validation")
        self.maxsize(500, 100)
        self.minsize(500, 100)

        validLabel = customtkinter.CTkLabel(master=self, text_color="red",
                                            font=("System", 14, "bold"))
        validLabel.place(relx=.5, rely=.4, anchor=tkinter.CENTER)

        errorMessageLabel = customtkinter.CTkLabel(master=self, text="",
                                                   font=("System", 12))
        errorMessageLabel.place(relx=.5, rely=.45, anchor=tkinter.CENTER)

        def mail_checker():
            try:
                email_info = validate_email(email)
                validLabel.configure(text="Valid email", text_color="green")

                is_in_blocklist = email_info.domain in blocklist

                if not is_in_blocklist:
                    try:
                        with open("blacklist.txt", "r") as f:
                            blacklist = f.read().splitlines()
                            is_in_blocklist = email_info.domain in blacklist
                    except FileNotFoundError:
                        print("Die Blacklist-Datei wurde nicht gefunden.")

                if is_in_blocklist:
                    validLabel.configure(text="Email found in Blacklist", text_color="red")

            except EmailNotValidError as e:
                validLabel.configure(text="Invalid email", text_color="red")
                errorMessageLabel.configure(text=str(e))

        mail_checker()


class MailsListTopLevelWindow(customtkinter.CTkToplevel):
    def __init__(self, emails, title="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        global thread_count

        self.toplevel_window = None

        self.geometry("400x300")
        self.title(title)
        self.maxsize(400, 300)
        self.minsize(400, 300)

        def show_value(selected_option):
            if self.toplevel_window and self.toplevel_window.winfo_exists():
                self.toplevel_window.destroy()
            self.toplevel_window = SingleMailToplevelWindow(email=selected_option)

        validLabel = customtkinter.CTkLabel(master=self, text=title,
                                            text_color="red" if title == "Invalid Emails" else "green",
                                            font=("System", 14, "bold"))
        validLabel.pack(padx=20, pady=10)

        listbox = CTkListbox(self, command=show_value)
        listbox.delete("all")

        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        listbox.place(relx=.5, rely=.4, anchor=tkinter.CENTER, relwidth=.9, relheight=.4)

        def process_emails():
            for index, email in enumerate(emails):
                listbox.insert(index, email)

        def process_emails_async():
            threading.Thread(target=process_emails, daemon=True).start()

        process_emails_async()

        def export_data():
            try:
                filename = fd.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")])
                if filename:
                    with open(filename, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        for email in emails:
                            writer.writerow([email])
                    print("Data exported successfully to", filename)
                else:
                    print("Export canceled.")
            except Exception as e:
                print("Error exporting data:", e)

        # submit-button
        download_list = customtkinter.CTkButton(master=self, text="Download", width=220, height=40,
                                                command=export_data)
        download_list.place(relx=.5, rely=.8, anchor=tkinter.CENTER)


class TabView(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.toplevel_window = None
        self.another_toplevel_window = None
        self.notification_toplevel_window = None

        self.configure(width=400,
                       height=500)

        # create tabs
        self.add("Single")
        self.add("Multiple")
        self.add("Blacklist")
        self.add("Downloader")

        self.tab("Single").configure(height=200, width=200)

        def open_notification_toplevel(message, success):
            if self.notification_toplevel_window is None or not self.notification_toplevel_window.winfo_exists():
                self.notification_toplevel_window = NotificationTopLevelWindow(message, success)
            else:
                self.notification_toplevel_window.focus()

        # tab "Single":
        # headline
        singleLabel = customtkinter.CTkLabel(master=self.tab("Single"), text="Single-Validator", fg_color="transparent",
                                             font=("System", 20, "bold"))
        singleLabel.place(relx=.5, rely=.05, anchor=tkinter.CENTER)

        def mail_checker():
            global black_list
            try:
                errorMessageLabel.configure(text="")
                resolver = caching_resolver(timeout=10)
                email_info = validate_email(emailInput.get(), check_deliverability=True, dns_resolver=resolver)

                normalizedText.configure(text=email_info.normalized)
                domainText.configure(text=email_info.domain)
                localPartText.configure(text=email_info.local_part)

                is_in_blocklist = email_info.domain in blocklist or email_info.domain in blocklist

                if not is_in_blocklist:
                    try:
                        with open("blacklist.txt", "r") as f:
                            blacklist = f.read().splitlines()
                            is_in_blocklist = email_info.domain in blacklist
                    except FileNotFoundError:
                        print("Die Blacklist-Datei wurde nicht gefunden.")

                if is_in_blocklist is False:
                    validLabel.configure(text="The provided email address is valid!", text_color="green")
                else:
                    validLabel.configure(text="Email-Address found in blacklist!", text_color="red")

            except EmailNotValidError as e:

                normalizedText.configure(text="")
                domainText.configure(text="")
                localPartText.configure(text="")

                validLabel.configure(text="The provided email address is invalid!", text_color="red")
                errorMessageLabel.configure(text=str(e))

        def mail_checker_async():
            threading.Thread(target=mail_checker(), daemon=True).start()

        textbox = customtkinter.CTkTextbox(master=self.tab("Single"))
        textbox.insert("0.0", "new text to insert")  # insert at line 0 character 0

        emailInput = customtkinter.CTkEntry(master=self.tab("Single"), width=300, height=40,
                                            placeholder_text="Email for validation")
        emailInput.place(relx=.5, rely=.2, anchor=tkinter.CENTER)

        # Additional labels and fields for parameters in single tab
        normalizedLabel = customtkinter.CTkLabel(master=self.tab("Single"), text="Normalized:", fg_color="transparent",
                                                 font=("System", 12, "bold"))
        normalizedLabel.grid(row=0, column=0, padx=50, pady=(140, 0), sticky="w")

        normalizedText = customtkinter.CTkLabel(master=self.tab("Single"), text="...", font=("System", 12))
        normalizedText.grid(row=0, column=1, padx=5, pady=(140, 0), sticky="w")

        # domain label
        domainLabel = customtkinter.CTkLabel(master=self.tab("Single"), text="Domain:", font=("System", 12, "bold"))
        domainLabel.grid(row=1, column=0, padx=50, pady=0, sticky="w")

        domainText = customtkinter.CTkLabel(master=self.tab("Single"), text="...", font=("System", 12))
        domainText.grid(row=1, column=1, padx=5, pady=0, sticky="w")

        # localPart label
        localPartLabel = customtkinter.CTkLabel(master=self.tab("Single"), text="Local part:", fg_color="transparent",
                                                font=("System", 12, "bold"))
        localPartLabel.grid(row=2, column=0, padx=50, pady=0, sticky="w")

        localPartText = customtkinter.CTkLabel(master=self.tab("Single"), text="...", font=("System", 12))
        localPartText.grid(row=2, column=1, padx=5, pady=0, sticky="w")

        validLabel = customtkinter.CTkLabel(master=self.tab("Single"), text="", text_color="red",
                                            font=("System", 14, "bold"))
        validLabel.place(relx=.5, rely=.65, anchor=tkinter.CENTER)  # Place the button at the bottom

        errorMessageLabel = customtkinter.CTkLabel(master=self.tab("Single"), text="",
                                                   font=("System", 12))
        errorMessageLabel.place(relx=.5, rely=.72, anchor=tkinter.CENTER)  # Place the button at the bottom

        # submit-button
        button = customtkinter.CTkButton(master=self.tab("Single"), text="Validate", width=220, height=40,
                                         command=mail_checker_async)
        button.place(relx=.5, rely=.9, anchor=tkinter.CENTER)  # Place the button at the bottom

        def import_data_async():
            thread = threading.Thread(target=import_data, daemon=True)
            thread.start()

        # tab "Multiple":

        def openFileDialog():
            csvFilePathInput.delete(0, tkinter.END)

            filetypes = [("CSV files", "*.csv")]
            name = fd.askopenfilename(filetypes=filetypes)
            csvFilePathInput.insert(tkinter.END, name)

            print(csvFilePathInput.get())

        def get_domain(email):
            return email.split('@')[-1]

        def import_data():
            read_csv_file(csvFilePathInput.get())

        def read_csv_file(file_path):
            global email_list, queue_for_insert, thread_count, show_email_count

            queue_for_insert = queue.Queue()
            email_list = []

            if listbox:
                listbox.delete("0", tkinter.END)

            with open(file_path, 'r') as file:
                csv_reader = csv.reader(file, delimiter=';')

                # skip head
                next(csv_reader, None)

                csv_reader_list = list(csv_reader)

                # parse into set
                emails = list()

                for row in csv_reader_list:
                    if row:
                        emails.append(row[0])

                sorted_emails = sorted(emails, key=get_domain)

                # assign to global list
                email_list = split_into_chunks(sorted_emails, thread_count)

                if email_list:
                    open_notification_toplevel("Successfully imported emails!", True)
                else:
                    open_notification_toplevel("Error while handling the email-list!", False)

                # chunk emails that are rendered in the ui
                show_emails = emails[:show_email_count] if show_email_count < len(emails) else emails
                chunked_list = split_into_chunks(show_emails, thread_count)
                jobs = []

                for i in range(min(thread_count, len(chunked_list))):
                    thread = threading.Thread(target=insert_operation, args=(chunked_list[i], i + 1, queue_for_insert))
                    jobs.append(thread)

                for j in jobs:
                    j.start()

                for j in jobs:
                    j.join()

                # Retrieve items from the queue and insert them into the UI
                while not queue_for_insert.empty():
                    index, row = queue_for_insert.get()
                    listbox.insert(index, row)

                print("finished rendering values to listbox...")

        def insert_operation(emails, curr_list, queue_for_insert):
            for index, row in enumerate(emails):
                if row:
                    queue_for_insert.put((index + (len(emails) * curr_list), row))


        def split_into_chunks(lst, num_chunks):
            chunk_size = (len(lst) + num_chunks - 1) // num_chunks
            chunks = [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
            return chunks

        def show_value(selected_option):
            if self.toplevel_window and self.toplevel_window.winfo_exists():
                self.toplevel_window.destroy()
            self.toplevel_window = SingleMailToplevelWindow(email=selected_option)

        def run_validation_task():

            global email_list

            if email_list:
                validateAllButton.configure(text="...", state=tkinter.DISABLED)
                threading.Thread(target=validate_all, daemon=True).start()

        def stop_validation():
            validateAllButton.configure(text="Validate", state=tkinter.ACTIVE)
            global stop_validation_flag
            stop_validation_flag.set()

        def reset_stop_validation_flag():
            global stop_validation_flag
            stop_validation_flag.clear()

        def reset_lists():
            global invalid_emails, valid_emails, checked_domains, validated_count
            validated_count = 0
            valid_emails = []
            invalid_emails = []
            checked_domains = set()

        def validate_all():
            dns_check = switch.get()

            # Reset stop flag before starting validation
            reset_stop_validation_flag()

            global thread_count, email_list, black_list

            reset_lists()
            jobs = []

            try:
                with open("blacklist.txt", "r") as f:
                    black_list = f.read().splitlines()
            except FileNotFoundError:
                print("Die Blacklist-Datei wurde nicht gefunden.")

            for i in range(0, min(thread_count, len(email_list))):
                thread = threading.Thread(target=validate_chunked_list, args=(email_list[i], dns_check,))
                jobs.append(thread)

            for j in jobs:
                j.start()

            for j in jobs:
                j.join()

            update_ui()
            print(f"Valid: {len(valid_emails)}")
            print(f"Invalid: {len(invalid_emails)}")

        def update_ui():
            validateAllButton.configure(text="Validate", state=tkinter.ACTIVE)

            # check if windows exist and destroy if they do
            if self.toplevel_window and self.toplevel_window.winfo_exists():
                self.toplevel_window.destroy()

            if self.another_toplevel_window and self.another_toplevel_window.winfo_exists():
                self.another_toplevel_window.destroy()

            # open windows
            if valid_emails:
                self.toplevel_window = MailsListTopLevelWindow(emails=valid_emails, title="Valid Emails")
            if invalid_emails:
                self.another_toplevel_window = MailsListTopLevelWindow(emails=invalid_emails, title="Invalid Emails")

        def increase_validate_count():
            global validated_count

            validated_count = validated_count + 1
            validateAllButton.configure(text=validated_count)

        def validate_chunked_list(chunked_emails, check_dns):
            global black_list, checked_domains, invalid_emails, valid_emails

            if check_dns:
                for index, email in enumerate(chunked_emails):
                    if stop_validation_flag.is_set():
                        print("Validation stopped.")
                        break

                    email_domain = email.split('@')[-1]
                    # Check if the domain has been previously checked
                    if email_domain in checked_domains:
                        invalid_emails.append(email)
                        continue
                    else:
                        if email_domain in black_list:
                            invalid_emails.append(email)
                            checked_domains.add(email_domain)
                        else:
                            # Set resolver based on whether DNS check is enabled
                            resolver = caching_resolver(timeout=10)
                            try:
                                email_info = validate_email(email, check_deliverability=True, dns_resolver=resolver)
                                checked_domains.add(email_domain)
                                valid_emails.append(email_info.normalized)

                            except EmailNotValidError as e:
                                invalid_emails.append(email)
                                error_msg = str(e).lower()
                                # Handle specific error cases
                                if any(keyword in error_msg for keyword in
                                       ["deliverable", "dns", "unresolved", "not existing"]):
                                    checked_domains.add(email_domain)  # Add domain to blacklist
                    print(email)
            else:
                for index, email in enumerate(chunked_emails):
                    if stop_validation_flag.is_set():
                        print("Validation stopped.")
                        return
                    try:
                        email_info = validate_email(email, check_deliverability=False, dns_resolver=False)
                        if email_info.domain in blocklist or email_info.domain in black_list:
                            invalid_emails.append(email)
                        else:
                            valid_emails.append(email)
                    except EmailNotValidError as e:
                        invalid_emails.append(email)
                    print(f"{email}")

        # headline
        multipleLabel = customtkinter.CTkLabel(master=self.tab("Multiple"), text="Multiple-Validator",
                                               fg_color="transparent",
                                               font=("System", 20, "bold"))
        multipleLabel.place(relx=.5, rely=.05, anchor=tkinter.CENTER)

        # csvFilePath input field
        csvFilePathInput = customtkinter.CTkEntry(master=self.tab("Multiple"), height=30,
                                                  placeholder_text="CSV-Filepath")
        csvFilePathInput.grid(row=0, column=0, padx=(50, 10), pady=(50, 10), sticky="ew")

        # open filedialog button
        openFileDialog = customtkinter.CTkButton(master=self.tab("Multiple"), text="Open", command=openFileDialog,
                                                 font=("System", 12))
        openFileDialog.grid(row=0, column=1, padx=5, pady=(50, 10))

        switch = customtkinter.CTkSwitch(self.tab("Multiple"), text="DNS-Check",
                                         onvalue=True, offvalue=False)

        switch.grid(row=1, column=0, padx=15)

        listbox = CTkListbox(master=self.tab("Multiple"), command=show_value, height=180, width=50)
        listbox.grid(row=2, column=0, columnspan=2, padx=(50, 10), pady=10, sticky="nsew")

        # submit-button
        validateAllButton = customtkinter.CTkButton(master=self.tab("Multiple"), text="Validate",
                                                    command=run_validation_task)
        validateAllButton.grid(row=3, column=0, columnspan=1, padx=(50, 10), pady=5, sticky="nsew")

        stop_multiple_validation = customtkinter.CTkButton(master=self.tab("Multiple"), text="stop", width=40,
                                                           height=20,
                                                           fg_color="red",
                                                           hover_color="dark red",
                                                           command=stop_validation)
        stop_multiple_validation.grid(row=3, column=1, padx=(40, 10), pady=5, sticky="nsew")

        # submit-button
        buttonMultiple = customtkinter.CTkButton(master=self.tab("Multiple"), text="Import", width=220, height=40,
                                                 command=import_data_async)
        buttonMultiple.place(relx=.5, rely=.9, anchor=tkinter.CENTER)  # Place the button at the bottom

        # tab "Blacklist":

        def load_blacklist():
            try:
                with open("blacklist.txt", "r") as f:
                    blacklist_content = f.read()
                    blacklistTextbox.delete("1.0", "end")  # Clear existing content
                    blacklistTextbox.insert("1.0", blacklist_content)  # Insert content from file
            except FileNotFoundError:
                print("Die Blacklist-Datei wurde nicht gefunden.")

        def save_blacklist():
            blacklist_content = blacklistTextbox.get("1.0", "end-1c")  # Get all content except the trailing newline
            with open("blacklist.txt", "w") as f:
                f.write(blacklist_content)

        blacklistTextbox = customtkinter.CTkTextbox(master=self.tab("Blacklist"))
        blacklistTextbox = customtkinter.CTkTextbox(master=self.tab("Blacklist"), width=250, height=300)
        blacklistTextbox.place(relx=.5, rely=.4, anchor=tkinter.CENTER)

        loadButton = customtkinter.CTkButton(master=self.tab("Blacklist"), text="Load Blacklist",
                                             command=load_blacklist)
        loadButton.place(relx=.3, rely=.9, anchor=tkinter.CENTER)

        saveButton = customtkinter.CTkButton(master=self.tab("Blacklist"), text="Save Blacklist",
                                             command=save_blacklist)
        saveButton.place(relx=.7, rely=.9, anchor=tkinter.CENTER)
        
        # tab "Downloader":
        # Headline
        headline_label = customtkinter.CTkLabel(master=self.tab("Downloader"), text="Downloader", font=("System", 20, "bold"))
        headline_label.grid(row=0, column=1)

        # Email address
        email_label = customtkinter.CTkLabel(font=("System", 12), master=self.tab("Downloader"), text="Email Address:")
        email_label.grid(row=1, column=0, sticky="w")
        self.email_entry = customtkinter.CTkEntry(master=self.tab("Downloader"), width=30)
        self.email_entry.grid(row=1, column=1, sticky="ew")

        # Password
        password_label = customtkinter.CTkLabel(font=("System", 12), master=self.tab("Downloader"), text="Password:")
        password_label.grid(row=2, column=0, sticky="w")
        self.password_entry = customtkinter.CTkEntry(master=self.tab("Downloader"), show="*", width=30)
        self.password_entry.grid(row=2, column=1, sticky="ew")

        # IMAP server
        server_label = customtkinter.CTkLabel(font=("System", 12), master=self.tab("Downloader"), text="IMAP Server:")
        server_label.grid(row=3, column=0, sticky="w")
        self.server_entry = customtkinter.CTkEntry(master=self.tab("Downloader"), width=30)
        self.server_entry.grid(row=3, column=1, sticky="ew")

        # IMAP port
        port_label = customtkinter.CTkLabel(font=("System", 12), master=self.tab("Downloader"), text="IMAP Port:")
        port_label.grid(row=4, column=0, sticky="w")
        self.port_entry = customtkinter.CTkEntry(master=self.tab("Downloader"), width=10)
        self.port_entry.grid(row=4, column=1, sticky="ew")
        self.port_entry.insert(0, "993")

        # Save location
        filename_label = customtkinter.CTkLabel(font=("System", 12), master=self.tab("Downloader"), text="Save Location:")
        filename_label.grid(row=5, column=0, sticky="w")
        self.filename_entry = customtkinter.CTkEntry(master=self.tab("Downloader"), width=30)
        self.filename_entry.grid(row=5, column=1, sticky="ew")

        # Browse button
        self.browse_button = customtkinter.CTkButton(master=self.tab("Downloader"), text="Browse", command=self.browse)
        self.browse_button.grid(row=6, column=1, sticky="w")

        # Separator and format
        separator_label = customtkinter.CTkLabel(font=("System", 12), master=self.tab("Downloader"), text="Separator:")
        separator_label.grid(row=7, column=0, sticky="w")
        self.separator_var = tk.StringVar(value=";")
        separator_combobox = customtkinter.CTkOptionMenu(master=self.tab("Downloader"), values=[";", ","],
                                        state="readonly")
        separator_combobox.grid(row=7, column=1, sticky="ew")

        format_label = customtkinter.CTkLabel(font=("System", 12), master=self.tab("Downloader"), text="File Format:")
        format_label.grid(row=8, column=0, sticky="w")
        self.format_var = tk.StringVar(value="CSV")
        format_combobox = customtkinter.CTkOptionMenu(master=self.tab("Downloader"), values=["CSV", "TXT"],
                                    state="readonly")
        format_combobox.grid(row=8, column=1, sticky="ew")

        # Status
        self.status_var = tk.StringVar()
        self.status_label = customtkinter.CTkLabel(font=("System", 12), master=self.tab("Downloader"), textvariable=self.status_var)
        self.status_label.grid(row=9, column=1, sticky="ew", pady=(10, 0))

        # Download button
        self.download_button = customtkinter.CTkButton(master=self.tab("Downloader"), text="Start Download", command=self.start_download)
        self.download_button.grid(row=10, column=1, sticky="ew", pady=(10, 0))

        for child in self.tab("Downloader").winfo_children():
            child.grid_configure(pady=5, padx=10, sticky="ew")

    def browse(self):
        filetype = [('CSV files', '*.csv')] if self.format_var.get() == "CSV" else [('Text files', '*.txt')]
        filepath = fd.asksaveasfilename(defaultextension=filetype[0][1], filetypes=filetype)
        if filepath:
            self.filename_entry.delete(0, tk.END)
            self.filename_entry.insert(0, filepath)

    def update_status(self, message):
        self.status_var.set(message)
        self.update_idletasks()

    def start_download(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        server = self.server_entry.get()
        port = self.port_entry.get()
        filename = self.filename_entry.get()
        separator = self.separator_var.get()
        format = self.format_var.get()

        if not os.path.isabs(filename):
            messagebox.showerror("Error", "Please use a valid path!")
            return

        self.update_status("Connecting to Server...")

        try:
            email_addresses = set()
            mail = imaplib.IMAP4_SSL(server, port)
            mail.login(email, password)
            self.update_status("Connection to Server successful.")
            
            mail.select('inbox')
            self.update_status("Gatering E-Mail-Adresses...")

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

            self.update_status("Writing E-Mails into file...")
            with open(filename, 'w', encoding='utf-8') as file:
                for name, addr in sorted(email_addresses, key=lambda x: x[1]):  # Sortierung nach E-Mail
                    if format == "CSV":
                        line = f'"{name}"{separator}"{addr}"'
                    else:  # TXT-Format
                        line = f"{name}\t{addr}"
                    file.write(line + "\n")

            self.update_status("The E-Mails were successfully \ndownloaded and saved.")
            messagebox.showinfo("Success", "The E-Mails were successfully \ndownloaded and saved.")
        except Exception as e:
            self.update_status("An Error occured.")
            messagebox.showerror("Error", f"An Error occured: {e}")
        finally:
            if 'mail' in locals():
                mail.logout()
                
        # Reset fields
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.server_entry.delete(0, tk.END)
        self.filename_entry.delete(0, tk.END)



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mail-Eagle")
        self.geometry("500x600")

        self.maxsize(500, 600)
        self.minsize(500, 600)

        self.tab_view = TabView(master=self)
        self.tab_view.place(relx=.5, rely=.5, anchor=tkinter.CENTER)


app = App()
app.mainloop()
