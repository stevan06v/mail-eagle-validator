import queue
import threading
import time
import tkinter
import customtkinter
import csv
from CTkListbox import *
from tkinter import filedialog as fd
from email_validator import validate_email, caching_resolver, EmailNotValidError
from disposable_email_domains import blocklist
import os


cores = os.cpu_count()
email_list = []
invalid_emails = []
valid_emails = []
black_list = list()
checked_domains = []
thread_count = cores * 2
show_email_count = 500
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

        def split_into_chunks(lst, num_chunks):
            chunk_size = (len(lst) + num_chunks - 1) // num_chunks
            chunks = [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
            return chunks

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

        # tab "Multiple":
        def import_data():
            read_csv_file(csvFilePathInput.get())

        def openFileDialog():
            csvFilePathInput.delete(0, tkinter.END)

            filetypes = [("CSV files", "*.csv")]
            name = fd.askopenfilename(filetypes=filetypes)
            csvFilePathInput.insert(tkinter.END, name)

            print(csvFilePathInput.get())

        def read_csv_file(file_path):

            global email_list
            global thread_count
            global show_email_count

            email_list = []
            listbox.delete("all")

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

                # assign to global list
                email_list = split_into_chunks(emails, thread_count)

                if email_list:
                    open_notification_toplevel("Successfully imported emails!", True)
                else:
                    open_notification_toplevel("Error while handling the email-list!", False)

                # chunk emails that are rendered in the ui
                show_emails = emails[:show_email_count]

                chunked_list = split_into_chunks(show_emails, thread_count)

                queue_for_insert = queue.Queue()
                jobs = []

                for i in range(0, thread_count):
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
            global invalid_emails, valid_emails, checked_domains
            valid_emails = []
            invalid_emails = []

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

            for i in range(0, thread_count):
                thread = threading.Thread(target=validate_chunked_list,
                                          args=(email_list[i], dns_check,))
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
                print("valid opened")
                self.toplevel_window = MailsListTopLevelWindow(emails=valid_emails, title="Valid Emails")
            if invalid_emails:
                print("invalid opened")
                self.another_toplevel_window = MailsListTopLevelWindow(emails=invalid_emails, title="Invalid Emails")

        def validate_chunked_list(chunked_emails, check_dns):
            global black_list, checked_domains, invalid_emails, valid_emails

            if check_dns:
                for index, email in enumerate(chunked_emails):
                    if stop_validation_flag.is_set():
                        print("Validation stopped.")
                        return
                    # Set resolver based on whether the domain has been checked previously
                    resolver = caching_resolver(timeout=10) if check_dns and email.split('@')[
                        -1] not in checked_domains else False

                    if email.split('@')[-1] in black_list:
                        invalid_emails.append(email)
                        return
                    try:
                        email_info = validate_email(email, check_deliverability=True, dns_resolver=resolver)
                        # Add the email domain to the checked domains set if resolver is True
                        if resolver:
                            checked_domains.append(email_info.domain)

                        if email_info.domain in black_list:
                            invalid_emails.append(email)
                        else:
                            valid_emails.append(email)
                    except EmailNotValidError as e:
                        invalid_emails.append(email)
                        if "deliverable" in str(e).lower() or "dns" in str(e).lower() or "unresolved" in str(
                                e).lower() or "not existing" in str(e).lower():
                            black_list.append(
                                email.split('@')[
                                    -1])  # Add domain to blacklist if delivery failure or DNS-related error
                    print(f"{email}")
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
                                                 command=import_data)
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


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Email-Validator")
        self.geometry("500x600")

        self.maxsize(500, 600)
        self.minsize(500, 600)

        self.tab_view = TabView(master=self)
        self.tab_view.place(relx=.5, rely=.5, anchor=tkinter.CENTER)


app = App()
app.mainloop()
