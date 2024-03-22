import tkinter
import customtkinter
import os
import threading
from tkinter import filedialog as fd

class MyTabView(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

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

        def submit():
            email = emailInput.get()
            print(email)

        emailInput = customtkinter.CTkEntry(master=self.tab("Single"), width=300, height=40,
                                            placeholder_text="Email for validation")
        emailInput.place(relx=.5, rely=.2, anchor=tkinter.CENTER)

        # submit-button
        button = customtkinter.CTkButton(master=self.tab("Single"), text="Validate", width=220, height=40,
                                         command=submit)
        button.place(relx=.5, rely=.9, anchor=tkinter.CENTER)  # Place the button at the bottom

        # tab "Multiple":
        def submitMultiple():
            print(emailInput.get())

        def openFileDialog():
            name = fd.askopenfilename()
            csvFilePathInput.insert(tkinter.END, name)

            print(csvFilePathInput.get())

        def optionmenuCallback(choice):
            print("optionmenu dropdown clicked:", choice)

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
                                                 command=optionmenuCallback, width=2, font=("System", 12))
        optionmenu.set(",")
        optionmenu.grid(row=1, column=1, padx=10, pady=5)

        # submit-button
        buttonMultiple = customtkinter.CTkButton(master=self.tab("Multiple"), text="Validate", width=220, height=40,
                                                 command=submitMultiple)
        buttonMultiple.place(relx=.5, rely=.9, anchor=tkinter.CENTER)  # Place the button at the bottom


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Email-Validator")
        self.geometry("500x500")

        self.maxsize(500, 500)
        self.minsize(500, 500)

        self.tab_view = MyTabView(master=self)
        self.tab_view.place(relx=.5, rely=.5, anchor=tkinter.CENTER)


app = App()
app.mainloop()
