import os
import csv
import yaml
import datetime
from os import chdir

class Evaluation:
    
    def __init__(
            self,
            author="God",
            metadata_file = "meta_data.yml",
            working_dir = os.getcwd(),
            target_dir = os.getcwd(),
            title = "Evaluation",
            eval_date = datetime.date.today())
            
            self.working_dir = working_dir
            
            self.metadata_file = metadata_file
            
            try:
                metadata = self.load_metadata(self.metadata_file)
            except:
                print("no metadata-file found. Care to write one and try again?
                        You find and example in the repository")
            # specific only to layered materials and solid-state.
            gated = gated if metadata["experiment"]["gated"] == True else ''
            self.title = metadata["experiment"]["type"] + ' '
                       + "of" + ' '
                       + gated + ' '
                       + metadata["experiment"]["material"] + ' '
                       + metadata["experiment"]["material_info"]
            
            date_start = metadata["general"]["date_start"]
            self.date_start = datetime.date(date_start[:4],
                                            date_start[4:6],
                                            date_start[6:])

            date_end = metadata["general"]["date_end"]
            self.date_end = datetime.date(date_end[:4],
                                            date_end[4:6],
                                            date_end[6:])
            
            self.eval_data = eval_date

            setup = ''
            if "setup_optical" in metadata["general"]:
                self.setup.append(metadata["general"]["setup_optical"]+' ')
            if "setup_cryo" in metadata["general"]:
                self.setup.append(metadata["general"]["setup_cryo"]+' ')
            self.setup = ''.join(setup)
            
            self.laser = metadata["experiment"]["laser"]
            self.temperature = metadata["experiment"]["temperature"]
            self.notes = metadata["experiment"]["notes"]
            
            self.gate = metadata["experiment"]["gate"] if gated == True else None
                

    def latex_header(self):
        '''Creates header for the LaTeX-file. Fixes layout, font and so on.'''
        with open(self.working_dir+"\\"+self.metadata_file, 'wb') as texfile:
            texfile.write("\\documentclass[english]{scrartcl}\n")
            texfile.write("\\usepackage{babel, fontspec, amsmath}\n")
            texfile.write("\\usepackage{graphicx, float}\n")
            texfile.write("\\setmainfont[Numbers=OldStyle]{Linux Libertine O}\n")


    def load_metadata(metadata_file="meta_data.yml"):
        '''Loads meta-data yaml-file and reads it to dict.'''
        try:
            with open(self.working_dir+"\\"+metadata_file, 'r') as metadata_file:
                metadata = yaml.load(metadata_file)
        except IOError:
            print("No metadata found. I quit!")

        return(metadata)


    def data_header(self):
        '''creates header, related to the data.'''
        with open(self.working_dir+"\\"+self.metadata_file, 'wb') as texfile:
            texfile.write("\\title{"+self.title+"}\n")
            # preliminary
            texfile.write("\\date{\\today}")
            texfile.write("\\author{"+self.author+"}\\n")

