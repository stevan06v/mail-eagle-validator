import customtkinter
import os
from tkinter import filedialog as fd


def shorten_file_path(file_path, max_length=15, prefix_length=5):
    if len(file_path) > max_length:
        prefix = file_path[:prefix_length]
        suffix = file_path[-(max_length - len(prefix) - 3):]
        return f"{prefix}...{suffix}"
    else:
        return file_path

class MyTabView(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.configure(width=400,
                       height=400,)

        # create tabs
        self.add("Single")
        self.add("Multiple")

        self.tab("Single").configure(height=200, width=200)

        # tab "Single":
        def submit():
            print(emailEntry.get())

        emailLabel = customtkinter.CTkLabel(master=self.tab("Single"), text="Email Address:", fg_color="transparent")
        emailLabel.grid(row=0, column=0, padx=0, pady=10)

        emailEntry = customtkinter.CTkEntry(master=self.tab("Single"), placeholder_text="Email for validation")
        emailEntry.configure(width=200)
        emailEntry.grid(row=0, column=1, padx=0, pady=10)

        button = customtkinter.CTkButton(master=self.tab("Single"), text="Validate", command=submit)
        button.grid(row=1, column=0, padx=20, pady=20, sticky="s")  # Place the button at the bottom

        # tab "Multiple":
        def submitMultiple():
            print(emailEntry.get())

        def openFileDialog():
            name = fd.askopenfilename()
            csvFilePathLabel.configure(text=shorten_file_path(os.path.basename(name)))

        def optionmenuCallback(choice):
            print("optionmenu dropdown clicked:", choice)

        # filename
        csvFilePathLabel = customtkinter.CTkLabel(master=self.tab("Multiple"), text="CSV-File:", fg_color="transparent")
        csvFilePathLabel.grid(row=0, column=0, padx=0, pady=10)

        # open filedialog
        openFileDialog = customtkinter.CTkButton(master=self.tab("Multiple"), text="Open", command=openFileDialog)
        openFileDialog.grid(row=0, column=1, padx=0, pady=20)  # Place the button at the bottom

        # option menu
        optionMenuLabel = customtkinter.CTkLabel(master=self.tab("Multiple"), text="Delimiter:", fg_color="transparent")
        optionMenuLabel.grid(row=1, column=0, padx=0, pady=10)

        optionmenu = customtkinter.CTkOptionMenu(master=self.tab("Multiple"), values=[",", ";"],
                                                 command=optionmenuCallback)
        optionmenu.set(",")
        optionmenu.grid(row=1, column=1, padx=20, pady=20)  # Place the button at the bottom


        # submit button for multiple
        buttonMultiple = customtkinter.CTkButton(master=self.tab("Multiple"), text="Validate", command=submitMultiple)
        buttonMultiple.grid(row=2, column=0, padx=20, pady=20)  # Place the button at the bottom


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Email-Validator")
        self.geometry("500x500")

        self.maxsize(500, 500)
        self.minsize(500, 500)

        self.tab_view = MyTabView(master=self)
        self.tab_view.grid(row=0, column=0, padx=50, pady=30)


app = App()
app.mainloop()
