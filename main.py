import tkinter
import customtkinter
import csv
from CTkListbox import *
from tkinter import filedialog as fd
from email_validator import validate_email, caching_resolver, EmailNotValidError
from disposable_email_domains import blocklist


class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, email="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")
        self.maxsize(400, 300)
        self.minsize(400, 300)

        self.label_text = f"ToplevelWindow - Email: {email}"
        self.label = customtkinter.CTkLabel(self, text=self.label_text)
        self.label.pack(padx=20, pady=20)


class TabView(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.toplevel_window = None

        self.configure(width=400,
                       height=400)

        # create tabs
        self.add("Single")
        self.add("Multiple")

        self.tab("Single").configure(height=200, width=200)

        # tab "Single":

        # headline
        singleLabel = customtkinter.CTkLabel(master=self.tab("Single"), text="Single-Validator", fg_color="transparent",
                                             font=("System", 20, "bold"))
        singleLabel.place(relx=.5, rely=.05, anchor=tkinter.CENTER)

        def mail_checker():
            try:
                errorMessageLabel.configure(text="")
                resolver = caching_resolver(timeout=10)
                emailInfo = validate_email(emailInput.get(), check_deliverability=True, dns_resolver=resolver)

                normalizedText.configure(text=emailInfo.normalized)
                domainText.configure(text=emailInfo.domain)
                localPartText.configure(text=emailInfo.local_part)

                is_in_blocklist = emailInfo.domain in blocklist

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

        textbox = customtkinter.CTkTextbox(master=self.tab("Single"))
        textbox.insert("0.0", "new text to insert")  # insert at line 0 character 0

        emailInput = customtkinter.CTkEntry(master=self.tab("Single"), width=300, height=40,
                                            placeholder_text="Email for validation")
        emailInput.place(relx=.5, rely=.2, anchor=tkinter.CENTER)

        # Additional labels and fields for parameters in single tab
        normalizedLabel = customtkinter.CTkLabel(master=self.tab("Single"), text="Normalized:", fg_color="transparent",
                                                 font=("System", 12, "bold"))
        normalizedLabel.grid(row=0, column=0, padx=50, pady=(100, 0), sticky="w")

        normalizedText = customtkinter.CTkLabel(master=self.tab("Single"), text="...", font=("System", 12))
        normalizedText.grid(row=0, column=1, padx=5, pady=(100, 0), sticky="w")

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
                                         command=mail_checker)
        button.place(relx=.5, rely=.9, anchor=tkinter.CENTER)  # Place the button at the bottom

        # tab "Multiple":
        def submitMultiple():
            read_csv_file(csvFilePathInput.get(), optionmenu.get())

        def openFileDialog():
            csvFilePathInput.delete(0, tkinter.END)

            filetypes = [("CSV files", "*.csv")]
            name = fd.askopenfilename(filetypes=filetypes)
            csvFilePathInput.insert(tkinter.END, name)

            print(csvFilePathInput.get())

        def read_csv_file(file_path, delimiter):
            listbox.delete("all")

            with open(file_path, 'r') as file:
                csv_reader = csv.reader(file, delimiter=delimiter)
                for row in csv_reader:
                    for index, item in enumerate(row):
                        print(index, item)
                        listbox.insert(index, item)

        def show_value(selected_option):
            if self.toplevel_window and self.toplevel_window.winfo_exists():
                self.toplevel_window.destroy()

            self.toplevel_window = ToplevelWindow(email=selected_option)
            print(selected_option)

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

        # option menu label
        optionMenuLabel = customtkinter.CTkLabel(master=self.tab("Multiple"), text="Delimiter:", fg_color="transparent",
                                                 font=("System", 12))
        optionMenuLabel.grid(row=1, column=0, padx=10, pady=5)

        # option menu
        optionmenu = customtkinter.CTkOptionMenu(master=self.tab("Multiple"), values=[",", ";"],
                                                 width=2, font=("System", 12))
        optionmenu.set(",")
        optionmenu.grid(row=1, column=1, padx=10, pady=5)

        listbox = CTkListbox(master=self.tab("Multiple"), command=show_value, )
        listbox.grid(row=2, column=0, columnspan=2, padx=(50, 10), pady=20, sticky="nsew")

        # submit-button
        buttonMultiple = customtkinter.CTkButton(master=self.tab("Multiple"), text="Import", width=220, height=40,
                                                 command=submitMultiple)
        buttonMultiple.place(relx=.5, rely=.9, anchor=tkinter.CENTER)  # Place the button at the bottom


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Email-Validator")
        self.geometry("500x500")

        self.maxsize(500, 500)
        self.minsize(500, 500)

        self.tab_view = TabView(master=self)
        self.tab_view.place(relx=.5, rely=.5, anchor=tkinter.CENTER)


app = App()
app.mainloop()
