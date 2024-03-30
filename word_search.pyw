#!/usr/bin/env python3
#Word Search program puzzle generator v 2.3.1
#Solo Deo gloria, amen.

#Import modules
import random
from tkinter import *
from tkinter import messagebox as mb

#Coordinates start at top left, and are positive right down

DIRECTIONS=[(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)] #Directions in the form of (dx, dy)
EASY_DIRECTIONS=DIRECTIONS[:3] #Easy mode directions
SIZE_FAC_OPTIONS=tuple(range(2, 10)) #Ratio of total characters in puzzle to characters that are actually words
SIZE_FAC_DEFAULT=4
ALL_CHARS="ABCDEFGHIJKLMNOPQRSTUVWXYZ" #Filling characters and limiter for input words (modify this to allow for punctuation)

class Generator(object):
    def get_puzzle_dim(self, words, size_fac):
        """Calculate puzzle dimension by word list (returns one side of a square)"""
        #Count all the letters
        total = 0
        for word in words:
            for letter in word:
                total += 1

        #Return either the side of a square large enough for all the characters times size_fac, or the length of the longest word
        return max((int((total * size_fac) ** 0.5), len(max(words, key=len))))

    def create_empty_table(self, dim):
        #Create the empty 2D table to build the puzzle. referenced by table[y][x]=" "
        table = []
        for y in range(dim):
            table.append([])
            for x in range(dim):
                table[-1].append(" ")
        return table
    
    def copy_table(self, table):
        """Independently duplicate table data"""
        return eval(str(table)) #um, hehe?
        
        #Jumped code in case previous is buggy
        copy=[]
        for row in table:
            copy.append([])
            for column in row:
                copy[-1].append(column[:]) #Duplicate each character independently
        return copy   

    def create_blank_tried_pos(self, words):
        """Create a new tried positions dictionary"""
        dictionary={}
        for word in words:
            dictionary[word]=[]
        return dictionary

    def all_random_coords(self, dim):
        xlist=list(range(dim))
        random.shuffle(xlist)
        ylist=list(range(dim))
        random.shuffle(ylist)
        return xlist, ylist

    def gen_word_search(self, words, directions = None, size_fac=2):
        """Generate a word search puzzle. Returns a 2D list table
    with empty spaces to be filled with random characters.
    Directions defaults to DIRECTIONS[:]"""

        #Default to all directions
        if not directions:
            directions = DIRECTIONS[:]

        dim=self.get_puzzle_dim(words, size_fac) #Generate puzzle dimension
        table=self.create_empty_table(dim)
        table_history={}

        #Dict of positions for each word that have been tried but hurt future words. Future word values should ALWAYS be empty.
        tried_positions=self.create_blank_tried_pos(words)

        current_index=0
        while current_index<len(words): #place every word

            word=words[current_index]

            table_history[word]=self.copy_table(table) #Record previous table state

            #Randomly shuffle all coordinate possibilities
            xlist, ylist=self.all_random_coords(dim)

            #For all possible positions (randomized)...
            for x in xlist:
                for y in ylist:

                    #For all possible directions (randomized)...
                    random.shuffle(directions)
                    
                    success = False #If all directions for this positionare used, this will be the default value
                    
                    for direction in directions:
                        
                        if (x, y, direction) in tried_positions[word]:
                            continue #We already tried this direction
                        
                        tcopy = self.copy_table(table) #Copy the table
                        pos = [x, y] #Current position in the word. To be incremented forward by direction for each letter
                        success = True #Assume that the letter placing loop will succeed ;-D
                        
                        for letter in word: #Move forward in the word
                            try: #check that the index is valid. REMEMBER: table must be indexed [y][x]
                                if pos[0] < 0 or pos[1] < 0:
                                    raise IndexError
                                tcopy[pos[1]][pos[0]]
                            except IndexError: #Position does not exist
                                success = False
                                break

                            #Try placing the letter...
                            if tcopy[pos[1]][pos[0]] == " ": #Letter successfully placed
                                tcopy[pos[1]][pos[0]] = letter
                                
                            elif tcopy[pos[1]][pos[0]] == letter: #Position was assigned, but is already this letter. Okay :-)
                                continue
                            
                            else: #Position is occupied by a different letter. Try again...
                                success = False
                                break

                            #Step the position forward by direction
                            pos[0] += direction[0]
                            pos[1] += direction[1]
                            
                        if success: #Word successfully placed at this orientation
                            break
                    if success: #...and at this Y position
                        break
                if success: #...and at this X position
                    break
            if success: #...So, write changes to the table
                table=self.copy_table(tcopy)
                tried_positions[word].append((x, y, direction)) #Record the tried position for potential FUTURE use
                current_index+=1
                
            else: #No position or orientation worked, so backtrack
                current_index-=1
                tried_positions[word]=[] #If we're backing up in the word list, any previously tried placing positions for this word are now invalid
                table=self.copy_table(table_history[word])
                
                if current_index<0: #Nothing worked all the way back through the first word, the puzzle is too small
                    dim+=1
                    table=self.create_empty_table(dim)
                    table_history={} #May be no reason to clear this
                    current_index=0
            
        return table #All finished :-D


#root=Tk()
#root.geometry("200x70")

class Window(Tk):
    def __init__(self):
        """Word Search Generator GUI"""
        super(Window, self).__init__()
        self.title("Word Search Gen")
        self.build()
        self.mainloop()
        
    def build(self):

        #Checkbutton for using hard directions
        self.use_hard=BooleanVar()
        self.use_hard.set(True)
        Checkbutton(self, text="Use upward/leftward directions", variable=self.use_hard, command=self.configure_directs).grid(row=0, sticky=N+E+W)
        self.configure_directs()

        #Number area for size_fac
        self.sf_frame=Frame(self)
        self.sf_frame.grid(row=1, sticky=E+W)
        
        Label(self.sf_frame, text="Size factor:").grid(row=0, column=0, sticky=E+N)
        
        self.sf_spinbox=Spinbox(self.sf_frame, values=SIZE_FAC_OPTIONS, command=self.configure_size_fac)
        self.sf_spinbox.grid(row=0, column=1, sticky=E+W+N)
        self.configure_size_fac() #Create the size_fac variable and set the spinbox to the default
        
        self.sf_frame.columnconfigure(1, weight=1) #Resize size factor frame around the column with the spinbox.
        

        #Entry area for the words, and a scrollbar
        self.entry_frame=Frame(self)
        self.entry_frame.grid(row=2, sticky=N+S+E+W)
        self.text=Text(self.entry_frame, width=30, height=20, wrap="word") #Text object
        self.scrollbar=Scrollbar(self.entry_frame) #Scrollbar object
        
        self.scrollbar["command"]=self.text.yview #Connect scrollbar to text
        self.text.configure(yscrollcommand=self.scrollbar.set) #Connect text to scrollbar
        
        self.scrollbar.grid(row=0, column=1, sticky=N+S+E) #pack the scrollbar
        self.text.grid(row=0, column=0, sticky=N+S+E+W) #pack the text
        self.text.insert(0.0, "Delete this text, then enter one word per line.")

        #Resize the entry frame around the text box
        self.entry_frame.rowconfigure(0, weight=1)
        self.entry_frame.columnconfigure(0, weight=1)

        #Go button
        Button(self, text="Generate", command=self.generate_puzzle).grid(row=3, sticky=S+E+W)

        #Resize GUI about entry frame
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

    def configure_directs(self):
        """Set up directions to use"""
        if self.use_hard.get():
            self.directions=DIRECTIONS[:]
        else:
            self.directions=EASY_DIRECTIONS[:]

    def configure_size_fac(self):
        """Configure the size factor"""

        #If size_fac is not set yet, set to default and alter spinbox
        if not hasattr(self, "size_fac"):
            self.size_fac=SIZE_FAC_DEFAULT*1
            self.clear_sf_spinbox()
            return

        inp_value=self.sf_spinbox.get()
        try:
            self.size_fac=int(inp_value) #Try assigning the new size_fac

            if self.size_fac<1: #Is size fac invalid?
                raise ValueError
            
            if str(self.size_fac)!=inp_value: #If we turned 4.0 into 4, alter the spinbox to match the interpretation
                self.clear_sf_spinbox()
                
        except ValueError: #Entry was invalid, clear to existing size_fac value
            self.clear_sf_spinbox()

    def clear_sf_spinbox(self):
        """set the SF spinbox to whatever the current size_fac is"""
        self.sf_spinbox.delete(0, END)
        self.sf_spinbox.insert(0, str(self.size_fac))

    def generate_puzzle(self):
        """Generate a puzzle from the input words"""
        self.configure_size_fac()
        
        words_raw = self.text.get(0.0, END).upper() #Read the entry area for words

        #Checkpoint against invalid characters
        for l in words_raw:
            if l not in ALL_CHARS + "\n":
                mb.showerror("Invalid text", "Enter one word per line with no punctuation.")
                return

        #Heal double-spacing
        while "\n\n" in words_raw:
            words_raw=words_raw.replace("\n\n", "\n")

        #Generate the puzzle
        words=words_raw.splitlines()
        try:
            table=Generator().gen_word_search(words, directions=self.directions[:], size_fac=self.size_fac*1)
            
        except NotImplementedError: #The algorithm could not place a word, so it raised NotImplementedError. Try again...
            mb.showerror("Generation failed", "The algorithm could not place a word. Try it again. If the problem persists, try more commonly lettered words.")
            return

        #Prepare the returned puzzle table for use (turn into text and fill with random characters)
        text=""
        for row in table:
            for letter in row:
                if letter == " ":
                    text+=random.choice(ALL_CHARS)
                else:
                    text+=letter
                text+=" " #Space out the characters to make it square
            text = text[:-1] + "\n" #Remove the trailing space, and add a new line
        text=text[:-1] #remove the trailing newline

        #Copy the finished puzzle to the Tkinter/system clipboard
        self.clipboard_clear()
        self.clipboard_append(text)
        mb.showinfo("Generation complete", "The puzzle was copied to the clipboard. :-)\nPaste into a word processor set for a monospaced font BEFORE closing this program.")

#If this program was not imported, call the GUI
if __name__ == "__main__":
    Window()
    
#HalleluJAH!!!
