'''
GUI for schmuxi. Uses Tkinter.

SchmuxI - Hmm Refreshing!
'''

from tkinter import Tk, BOTH, Text, TOP, X, N, LEFT
from tkinter.ttk import Frame, Button, Style, Label, Entry
from spec_evaluation import Experiment
import os
from subprocess import call

config_source = "spec_config.yml"

class control_panel(Frame):
    '''Main GUI-window'''

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        
        self.master.title("Schmuxi - Hmm refreshing")
        self.pack(fill=BOTH, expand=1)
        
        frame1 = Frame(self)
        frame1.pack(fill=X)

        temperature_label = Label(frame1, text="Temperature", width=15)
        temperature_label.pack(side=LEFT, padx=5, pady=5)
        
        temperature_entry = Entry(frame1, text="4", width = 15)
        temperature_entry.pack(fill=X, padx=5, expand=True)
        
        config_btn = Button(self, text="Edit config",
                command=self.edit_config(config_source))
        config_btn.place(x=50,y=50)

    def edit_config(self, config_source):
        
        EDITOR = os.environ.get('EDITOR','vim')
        call([EDITOR, config_source])

def main():

    root = Tk()
    root.geometry("500x300+300+300")
    app = control_panel()
    root.mainloop()

if __name__ == '__main__':
    main()
