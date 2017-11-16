import os
import csv
import yaml
import datetime
from os import chdir
from glob import glob

class Evaluation:
    
    def __init__(
            self,
            author="God",
            metadata_file = "meta_data.yml",
            working_dir = os.getcwd(),
            target_dir = os.getcwd(),
            title = "Evaluation",
            eval_date = datetime.date.today()):
            
            self.working_dir = working_dir
            
            self.metadata_file = metadata_file
            print(self.metadata_file)
            try:
                metadata = self.load_metadata(self.metadata_file)
            except:
                print("no metadata-file found. Care to write one and try again? You find and example in the repository")
            # specific only to layered materials and solid-state.
            gated = "gated" if (metadata["experiment"]["gated"] == True) else ''
            self.title = (metadata["experiment"]["type"] + ' '
                       + "of" + ' '
                       + gated + ' '
                       + metadata["experiment"]["material"] + ' '
                       + metadata["experiment"]["material_info"])
            
            date_start = str(metadata["general"]["date_start"])
            self.date_start = datetime.date(int(date_start[:4]),
                                            int(date_start[4:6]),
                                            int(date_start[6:]))

            date_end = str(metadata["general"]["date_end"])
            self.date_end = datetime.date(int(date_end[:4]),
                                            int(date_end[4:6]),
                                            int(date_end[6:]))
            
            self.eval_date = eval_date

            self.setup = ''
            if "setup_optical" in metadata["general"]:
                self.setup += (metadata["general"]["setup_optical"]+' ')
            if "setup_cryo" in metadata["general"]:
                self.setup += (metadata["general"]["setup_cryo"]+' ')
            
            self.laser = metadata["experiment"]["laser"]
            self.temperature = metadata["experiment"]["temperature"]
            self.notes = metadata["experiment"]["notes"]
            self.author = metadata["general"]["author"]
            self.gate = metadata["experiment"]["gate"] if gated == True else None
            
            self.content = ''


    def latex_header(self):
        '''Creates header for the LaTeX-file. Fixes layout, font and so on.'''
        latex_header = ''
        latex_header += "\\documentclass[english]{scrartcl}\n"
        latex_header += "\\usepackage{babel, fontspec, amsmath}\n"
        latex_header += "\\usepackage{graphicx, float}\n"
        latex_header += "\\usepackage{datetime2}\n"
        latex_header += "\\setmainfont[Numbers=OldStyle]{Linux Libertine O}\n"
        latex_header += "\\setkomafont{sectioning}{\\rmfamily}\n"
        self.content += latex_header


    def load_metadata(self, metadata_file="meta_data.yml"):
        '''Loads meta-data yaml-file and reads it to dict.'''
        print("I was here bitch!")
        try:
            with open(self.working_dir+"\\"+metadata_file, 'r') as metadata_file:
                metadata = yaml.load(metadata_file)
        except IOError:
            print("No metadata found. I quit!")

        return(metadata)


    def data_header(self):
        '''creates header, related to the data.'''
        data_header = ''
        data_header += "\\title{"+self.title+"}\n"
        data_header += "\\usepackage{graphicx, float}\n"
        data_header += "\\author{"+self.author+"}\n"
        data_header += (
                        "\\date{\\DTMdate{"
                        + str(self.eval_date.year)+"-"
                        + str(self.eval_date.month)+"-"
                        + str(self.eval_date.day)+"}}\n")
        
        self.content += data_header
    

    def maketitle(self):
        '''write title in the document'''
        title_section = ''
        title_section += "\\maketitle\n"
        title_section += "\\centering{Experiment performed on:}\\\\\n"
        start =("\\DTMdate{"
                    +str(self.date_start.year)+"-"
                    +str(self.date_start.month)+"-"
                    +str(self.date_start.day)+"}")
        end =("\\DTMdate{"
                    +str(self.date_end.year)+"-"
                    +str(self.date_end.month)+"-"
                    +str(self.date_end.day)+"}")
        title_section += "\\centering{"+start+" -- "+end+"}\n"

        self.content += title_section
    

    def include_plot(self, plot_file):
        '''includes image-file of a plot into the tex-file content.'''
        self.content += "\\begin{figure}[h]\n"
        
        self.content += ("\\includegraphics[width=0.4\\textwidth]{"
                        + plot_file + "}\n")
        self.content += "\\caption{This is a picture. Really!!!}\n"
        self.content += "\\end{figure}\n"
    
    def begin_document(self):
        self.content += "\\begin{document}\n"


    def end_document(self):
        self.content += "\\end{document}\n"


    def compose(self):
        '''composes the content of the .tex-file'''
        self.latex_header()
        self.data_header()
        self.begin_document()
        self.maketitle()
        images = glob('*.png') + glob('*.jpg')
        for image in images:
            self.include_plot(image)
        self.end_document()
        return(self.content)
    
    def write_tex(self):
        with open("Evaluation.tex","w") as texfile:
            texfile.write(self.content)

# test-routine
if __name__ == '__main__':
    document = Evaluation()
    print(document.compose())
    document.write_tex()
