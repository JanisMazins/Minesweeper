import random 
import numpy as np
import tkinter as tk
import sys
import time
from datetime import datetime
import csv 
# All tile coordinate tuples are written: (x,y), but to access the according coordinate in a numpy.ndarray, you take matrix[y][x].
FRAMEWIDTH = 30
FRAMEHEIGHT = 30
# Heights and widths of the mine field squares.

class BoardKey:
    def __init__(self, size_x, size_y, mines, no_mine_tile):
        self.size_y = size_y 
        self.size_x = size_x 
        self.mines = mines 
        matrix = np.zeros((size_y, size_x), dtype = bool)
        locations = []
        mine_locations = []
        for i in range(0, size_x*size_y):
            locations.append(i) 
        no_mine_tile = size_x*(no_mine_tile[1]) + no_mine_tile[0] 
        del locations[no_mine_tile]
        for i in range(mines): 
            mine_index = random.randint(0, len(locations)-1) 
            mine_locations.append(locations.pop(mine_index)) 
        np.put(matrix, mine_locations, True) 
        self.matrix = matrix
        # Creates a random truth matrix depending on the user's input.

    def check_matrix_key(self, tile: tuple=(int,int)):
        return self.matrix[tile[1], tile[0]]
        # Checks if a certain tile has a mine.

    def adjecent_tiles(self, tile: tuple=(int,int)):
        tiles = []
        for y in range(
            tile[1] - 1 if tile[1] != 0 
            else 0, 
            tile[1] + 2 if tile[1] != self.size_y - 1 
            else self.size_y 
            ): 
            for x in range(
                tile[0] - 1 if tile[0] != 0 
                else 0, 
                tile[0] + 2 if tile[0] != self.size_x - 1 
                else self.size_x 
                ): 
                    if (x,y) != tile:
                        tiles.append((x,y))
        return tiles
        # Checks what tiles are around a tile. The ranges look confusing because we need to consider\
        # the mines on the border of the field.

    def adjecent_mines(self, tile: tuple=(int,int)):
        adjecent = 0
        for index, value in enumerate(self.adjecent_tiles(tile)):
            x = self.adjecent_tiles(tile)[index][0]
            y = self.adjecent_tiles(tile)[index][1]
            if self.matrix[y,x]:
                adjecent += 1
        return adjecent
        # Counts the amount of mines adjecent to a specified tile.

    def __str__(self):
        return str(self.matrix)
        # Returns the "truth matrix".

class UserInfoDump:
    def __init__(self, user_matrix, mines=0, mine_label=tk.Label, flag_button=tk.Button, menu_frame=tk.Frame, grid_frame=tk.Frame):
        self.user_matrix = user_matrix
        self.vic_con = 0
        self.start_time = 0 # Placeholder value.
        self.first = True
        self.flag_mode = False
        "-------------------------------------" # The values below are only used for the GUI.
        self.mines = mines
        self.mine_label = mine_label
        self.flag_button = flag_button
        self.menu_frame = menu_frame
        self.grid_frame = grid_frame
        self.elapsed_time = 0 # Placeholder value.
# A class that saves a bunch of information.

def zero_tile(answer_key: BoardKey, tile: tuple=(int,int), revealed_tiles = [], tiles_to_check = []):
    revealed_tiles.append(tile)
    if answer_key.adjecent_mines(tile) == 0:
        for element in answer_key.adjecent_tiles(tile):
            if element not in tiles_to_check and element not in revealed_tiles:
                tiles_to_check.append(element)
    if tiles_to_check == []:
        return revealed_tiles
    else:
        return zero_tile(answer_key, tile=tiles_to_check.pop(0), revealed_tiles=revealed_tiles, tiles_to_check=tiles_to_check)
# Reveals all tiles around a tile with zero adjecent mines. Repeats this if there is another such tile adjecent. Returns a list.

def highscores_write(name, measured_skill, difficulty):
    date = datetime.now().date()
    new_record = [measured_skill, date, name]

    with open(file=f"highscores/{difficulty}_highscores.csv", mode="r") as file:
        reader = csv.reader(file)
        reader_list = list(reader)
        if len(reader_list) == 0:
            new_reader_list = [new_record]
        else:
            reader_list.insert(0, new_record)
            new_reader_list = sort_highscores(reader_list)

    with open(file=f"highscores/{difficulty}_highscores.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(new_reader_list)
# Takes data for a new record and puts it into the list. Makes sure that the records are sorted according to their measured skill.

def sort_highscores(lists):
    i = 0
    while True:
        try:
            if float(lists[i][0]) > float(lists[i+1][0]): # **
                lists[i], lists[i+1] = lists[i+1], lists[i]
                i += 1
            elif float(lists[i][0]) <= float(lists[i+1][0]): # *
                return lists
        except IndexError:
            return lists
# Sorts lists according to the size of their first elements. To sort high->low: change (*) '<=' -> '>=' and (**) '>' -> '<'.

def check_difficulty(size_x, size_y, mines, time):
    difficulty_dict = {(4,4,3):"beginner",
                       (7,7,7):"easy",
                       (15,15,35):"normal",
                       (22,22,100):"hard"}
    if (size_x,size_y,mines) in difficulty_dict:
        measured_skill = round(time, 2)
        difficulty = difficulty_dict[(size_x,size_y,mines)]
    else:
        try:
            measured_skill = round(100*((size_x*size_y*time)**(1/2)) / mines**2, 2) 
            if size_x*size_y - 1 == mines: 
                raise ZeroDivisionError
        except ZeroDivisionError: 
            measured_skill = float("inf")
        difficulty = "adjusted"
    return measured_skill, difficulty
# Checks what difficulty the game was. Returns the measured skill and difficulty in a list.
"-----------------------------------------------------------------------------------------------------------------------"
"the functions and classes above this line are used in both the terminal UI and the GUI. The things below are related to the terminal"
def highscore_collect_input_T(size_x, size_y, mines, time):
    while True:
        confirm = input("Vill du spara ditt resultat? (y/n)")
        if confirm == "y":
            name = input("Ange ditt namn:")
            measured_skill, difficulty = check_difficulty(size_x, size_y, mines, time)
            highscores_write(name, measured_skill, difficulty)
            break
        elif confirm == "n":
            break
    return main_T()
# Collects the measured skill of the run and saves it.

def read_T(difficulty):
    with open(file=f"highscores/{difficulty}_highscores.csv", mode="r") as file:
        reader = csv.reader(file)
        reader_list = list(reader)
        print("-"*40)
        if len(reader_list) == 0:
            print("Det finns inga rekord än!")
        else:
            print("De tio bästa resultaten (Lägre är bättre):")
            for i in range(10):
                try:
                    print(f"{i+1}. {reader_list[i][2]} ({reader_list[i][1]}): {reader_list[i][0]}\
 {'poäng' if difficulty == 'adjusted' else 'sekunder'}.")
                except:
                    break
        print("-"*40)
# Reads the scoreboard for the selected highscores and prints them out in the terminal.

def coords(coords: str):
    x_coord = letter_to_number(coords[0])
    y_coord = int(coords[1:]) - 1
    new_coords = (x_coord, y_coord)
    return new_coords
# Converts user coordinates (ex: "A1") to usable coordinates for an BoardKey object (ex: (0,1)).

def letter_to_number(letter: str):
    for index, value in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ"):
        if value == letter:
            return index
# Converts a letter to the correct index.

def check_input(input: str, size_x: int, size_y: int, first_check: bool):
    try:
        input = input.upper()
        if input == "M" and not first_check:
            return True, input
        elif 3 <= len(input) <= 4 and letter_to_number(input[0]) < size_x and 0 < int(input[1:-1]) <= size_y \
            and input[-1] == "M" and not first_check:
            return True, input
        elif 2 <= len(input) <= 3 and letter_to_number(input[0]) < size_x and 0 < int(input[1:]) <= size_y:
            return True, input
        else:
            return False, input
    except:
        return False, input
# Checks if the input is in the correct format and size. If it is, then it returns a list with [True, "corrected input"]. Otherwise just [False].

def check_max_input(variable, user_input, size_x, size_y):
    maxdict = {"spelplanens bredd":29,
                   "spelplanens höjd":99,
                   "antal minor":size_x * size_y - 1}
    if variable == "antal minor" and 0 <= user_input <= maxdict[variable]:
        return True
    elif 1 <= user_input <= maxdict[variable]:
        return True
    else:
        return False
# Stores and checks the maximum values for the field's input variables.

def display_board_T(user_matrix):
    templist = []
    for row_index, row_value in enumerate(user_matrix):
        for column_index, column_value in enumerate(user_matrix[row_index]):
            templist.append("| " + f"{column_value} ")
        templist.append("|")
        print("".join(templist))
        print("|----+" + (len(user_matrix[0])-2)*"---+" + "---|")
        templist.clear()
# Writes out the field in the terminal based on what the user_matrix that the user currently sees.

def initial_user_layout(x_input, y_input):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ"
    user_matrix = np.full((y_input + 1, x_input + 1), "\u2588", dtype='<U2')
    user_matrix[0][0] = "  "
    for index, value in enumerate(alphabet[0:x_input]):
        user_matrix[0][index+1] = value
    
    for index in range(0, y_input):
        user_matrix[index+1][0] = str(index+1) + " " if len(str(index)) == 1 else index+1
    
    return user_matrix
# Creates a matrix with the information which is initially visible for the user.
# A BoardKey object resides in user_matrix[i][j], where i>=1 and j>=1.

def change_user_matrix(user_matrix, content, tile: tuple=(int,int)):
    user_matrix[tile[1]+1][tile[0]+1] = content
    return user_matrix
# Help function that changes the content of a tile in user_matrix.

def flag_logic(user_info_dump: UserInfoDump, tile):
    if user_info_dump.user_matrix[tile[1]+1][tile[0]+1] not in "⚐\u2588":
        print("Du kan inte flagga avslöjade rutor!!!")
        return user_info_dump
    elif user_info_dump.user_matrix[tile[1]+1][tile[0]+1] == "⚐":
        user_info_dump.user_matrix = change_user_matrix(user_info_dump.user_matrix, "\u2588", tile)
    else:
        user_info_dump.user_matrix = change_user_matrix(user_info_dump.user_matrix, "⚐", tile)
    return user_info_dump
# Help function that determines how a flag should be placed.

def reveal_board(answer_key: BoardKey, user_matrix):
    for row_index, row_value in enumerate(answer_key.matrix):
        for column_index, column_value in enumerate(answer_key.matrix[row_index]):
            if answer_key.check_matrix_key((column_index, row_index)):
                user_matrix = change_user_matrix(user_matrix, "⚐", (column_index, row_index))
            else:
                user_matrix = change_user_matrix(user_matrix, answer_key.adjecent_mines((column_index, row_index)), (column_index, row_index))
    return user_matrix
# Reveals the entire user_matrix with a BoardKey object as a guide.

def input_helper(size_x, size_y, user_matrix, first_check = False): 
    while True:
        display_board_T(user_matrix)
        temp_tile = input("ange ruta:")
        if temp_tile == "":
            while True:
                confirmation = input("Är du säker på att du vill avsluta spelet? (y/n)")
                if confirmation == "y":
                    return False
                elif confirmation == "n":
                    break
        usable, corrected_input = check_input(temp_tile, size_x, size_y, first_check)
        if usable: 
            return corrected_input
        print("Ange en giltig ruta!!!")
# Checks if the input is correct or not. Also makes sure that 

def play_reveal_tile_helper(answer_key: BoardKey, user_info_dump: UserInfoDump, tile):
    if answer_key.adjecent_mines(tile) != 0 and user_info_dump.user_matrix[tile[1] + 1][tile[0] + 1] == "\u2588": # When revealing a tile with adjecent mines.
        user_info_dump.user_matrix = change_user_matrix(user_info_dump.user_matrix, answer_key.adjecent_mines(tile), tile)
        user_info_dump.vic_con += 1
    elif user_info_dump.user_matrix[tile[1] + 1][tile[0] + 1] == "\u2588": # When revealing a tile with no adjecent mines.
        revealed_tiles = zero_tile(answer_key, tile, revealed_tiles=[], tiles_to_check=[])
        for revealed_tile in revealed_tiles:
            if user_info_dump.user_matrix[revealed_tile[1] + 1][revealed_tile[0] + 1] == "\u2588":
                user_info_dump.user_matrix = change_user_matrix(user_info_dump.user_matrix, answer_key.adjecent_mines(revealed_tile), revealed_tile)
                user_info_dump.vic_con += 1
    return user_info_dump 
# Decides what changes are made to the user_matrix depending on how many adjecent tiles there are. 

def play(answer_key: BoardKey, user_info_dump: UserInfoDump, first_input = str):
    if user_info_dump.vic_con == answer_key.size_x * answer_key.size_y - answer_key.mines: # Victory condition.
        display_board_T(reveal_board(answer_key, user_info_dump.user_matrix))
        end_time = time.time() 
        elapsed_time = end_time - user_info_dump.start_time
        print("VICTORY")
        return highscore_collect_input_T(answer_key.size_x, answer_key.size_y, answer_key.mines, elapsed_time)
    
    if user_info_dump.first: 
        user_info_dump.first = False
        temp_tile = first_input
        user_info_dump.start_time = time.time()
    else:
        temp_tile = input_helper(answer_key.size_x, answer_key.size_y, user_info_dump.user_matrix)
        if temp_tile == False:
            return

    if temp_tile[-1] == "M":
        if len(temp_tile) == 1: 
            user_info_dump.flag_mode = not user_info_dump.flag_mode 
            return play(answer_key, user_info_dump)     
        else:
            tile = coords(temp_tile[:-1])
            return play(answer_key, flag_logic(user_info_dump, tile))

    if user_info_dump.flag_mode:
        flagged_tile = coords(temp_tile)
        return play(answer_key, flag_logic(user_info_dump, flagged_tile))

    tile = coords(temp_tile)

    if user_info_dump.user_matrix[tile[1]+1][tile[0]+1] == "⚐":
        print("Du kan inte röja en ruta med en flagga på!!!")
        return play(answer_key, user_info_dump)

    if answer_key.check_matrix_key(tile):
        display_board_T(reveal_board(answer_key, user_info_dump.user_matrix))
        print("GAME OVER")
        return main_T()
    else: 
        user_info_dump = play_reveal_tile_helper(answer_key, user_info_dump, tile) 
    return play(answer_key, user_info_dump)
# play() controls the logic of the game and interprets how the user inputs should be handled. This is where the game is played.

def terminal_menu():
    while True:
        choice = input("MINESWEEPER \n\n 1. Spela \n 2. Topplista \n 3. Hjälp \n 4. Avsluta \n\n Välj ett alternativ:")
        if choice == "1":
            break
        elif choice == "2":
            difficulty_dict = {"1":"beginner", "2":"easy", "3":"normal", "4":"hard", "5":"adjusted"}
            while True:
                user_input = input("-"*90 + "\n" + "1: Nybörjare\n2: Lätt\n3: Normal\n4: Svår\n5: Anpassad\n\nAnge kategori:")
                if user_input in difficulty_dict:
                    read_T(difficulty_dict[user_input])
                    break
        elif choice == "3":
            print("-"*90 + "\n" + """Minesweeper går ut på att röja ett spelfält med minor. Ifall du väljer en ruta med 
en mina förlorar du. Antalet avgränsande minor hos en ruta anges på rutan. 
   -För att avslöja en ruta, skriv: [bokstav][siffra] (T.ex: C5). 
   -För att sätta ut en flagga på en ruta skriver man ut koordinaten enligt föregående 
   instruktion och skriver ut ett 'M' efter detta (T.ex: C5M).
   -Skriv 'M' för att gå in i 'flaggläge'. I detta läge behöver man inte skriva ut 'M' 
   efter varje koordinat. Skriv 'M' åter en gång för att gå ur 'flaggläge'.
Man vinner när alla tomma rutor är avslöjade. Lycka till!""" + "\n" + "-"*90)
        elif choice == "4":
            return True
        else:
            print("Ange ett giltigt alternativ!")
    print("-"*90)
    return False
# Creates the menu in the terminal. You can either see highscores, get help, leave or continue and play the game. 

def main_T():
    if terminal_menu():
        return
    inputs = [[0, "spelplanens bredd", "en giltig bredd!!! (min: 1, max: 29)"], \
              [0, "spelplanens höjd", "en giltig höjd!!! (min: 1, max: 99)"], \
              [0, "antal minor", "ett giltigt antal minor!!! (får inte överstiga spelplanens storlek)"]] 
              # The zeros are just placeholder values. 
    for index, max_list in enumerate(inputs):
        while True:
            try:
                temp = int(input(f"Ange {inputs[index][1]}:"))
            except:
                print(f"Ange {inputs[index][2]}")
                continue
            if check_max_input(inputs[index][1], temp, inputs[0][0], inputs[1][0]):
                inputs[index][0] = temp
                break
            print(f"Ange {inputs[index][2]}")
    # Makes sure the user types in a usable input. Asks again if the input was incorrect.

    x_input = inputs[0][0]
    y_input = inputs[1][0]
    mines_input = inputs[2][0]
    user_matrix = initial_user_layout(x_input, y_input)
    user_info_dump = UserInfoDump(user_matrix)

    first_input = input_helper(x_input, y_input, user_info_dump.user_matrix, first_check=True)
    if first_input == False:
        return
    print("Tryck 'Enter' för att avsluta.")
    answer_key = BoardKey(x_input, y_input, mines_input, coords(first_input))
    play(answer_key, user_info_dump, first_input=first_input) # The game begins here.
"-----------------------------------------------------------------------------------------------------------------------"
"All classes and functions below this line relate to the GUI."
class EntryButton:
    def __init__(self, root, entry_list: list, button_text:str, function):
        self.entry_list = entry_list
        self.button = tk.Button(master=root, text=button_text, relief=tk.RAISED, font=("", 14), command=lambda: self.get_info())
        self.button.pack()
        self.function = function
        self.result_list = []

    def get_info(self):
        self.result_list.clear()
        for entry in self.entry_list:
            self.result_list.append(entry.get())
        self.function()
# An object of this class is a tk.Button which saves the data of a tk.Entry when pressed and executes some chosen function.

def create_main_frame(root):
    menu_frame = tk.Frame(master=root)
    menu_frame.pack()
    return menu_frame
# Creates the main frame for a menu.

def next_menu(old_menu, new_menu):
    old_menu.destroy()
    new_menu()
# Deletes all widget in the frame which you want to leave and calls a function to create the next menu.

def graphic_change_matrix(answer_key: BoardKey, user_info_dump: UserInfoDump, tile):
    for widget in user_info_dump.user_matrix[tile[1]][tile[0]].winfo_children(): 
        widget.destroy() 
    if answer_key.check_matrix_key(tile):
        tk.Label(master=user_info_dump.user_matrix[tile[1]][tile[0]], text="✱").pack()
    else:
        color_dict = {0:["", "#ffffff"],
                    1:["1", "#0000ff"],
                    2:["2", "#018001"],
                    3:["3", "#ff0100"],
                    4:["4", "#020280"],
                    5:["5", "#7e0100"],
                    6:["6", "#008281"],
                    7:["7", "#000000"],
                    8:["8", "#808080"],
                    9:["9", "#fefefe"]}
        number_of_mines = answer_key.adjecent_mines(tile)
        tk.Label(master=user_info_dump.user_matrix[tile[1]][tile[0]], text=color_dict[number_of_mines][0], fg=color_dict[number_of_mines][1], height=FRAMEHEIGHT, width=FRAMEWIDTH).pack()
# Changes the user_matrix with an answer_key as a guide.

def win_lose(win_or_lose: str, answer_key: BoardKey, user_info_dump: UserInfoDump, return_menu):
    tk.Label(master=user_info_dump.menu_frame, text=win_or_lose, fg="red", font=("", 20, "bold")).pack(side="top")
    tk.Button(master=user_info_dump.menu_frame, text="Tillbaka", command=lambda: [next_menu(user_info_dump.menu_frame, return_menu), user_info_dump.grid_frame.destroy()]).pack() 
    for row_index, row in enumerate(user_info_dump.user_matrix):
        for column_index, column in enumerate(user_info_dump.user_matrix[row_index]):
            graphic_change_matrix(answer_key, user_info_dump, (column_index, row_index))
# Determines the logic for when the game ends. Used for both wins and losses.

def flag_mode_on_off(user_info_dump: UserInfoDump):
    flag_button = user_info_dump.flag_button
    if flag_button.cget("text") == "✱":
        flag_button.config(text="⚐")
    else:
        flag_button.config(text="✱")
    user_info_dump.flag_mode = not user_info_dump.flag_mode
# Changes flag_mode when called.

def flag_mode_helper(button, mine_label):
    if button.cget("text") == "⚐":
        button.config(text="")
        new_mines = int(mine_label.cget("text")) + 1
    else:
        button.config(text="⚐")
        new_mines = int(mine_label.cget("text")) - 1
    mine_label.config(text=new_mines)

def create_answer_key(user_info_dump: UserInfoDump, tile):
    answer_key = BoardKey(len(user_info_dump.user_matrix[0]), len(user_info_dump.user_matrix), user_info_dump.mines, tile)
    for row_index, row in enumerate(user_info_dump.user_matrix):
        for column_index, column in enumerate(user_info_dump.user_matrix[row_index]):
            button = user_info_dump.user_matrix[row_index][column_index].winfo_children()[0]
            button.config(command=lambda x = column_index, y = row_index: \
minesweeper_output(user_info_dump, (x,y), answer_key=answer_key))
    return answer_key
# Creates an answer key and assigns it as a parameter for every button in the user_matrix.

def minesweeper_output(user_info_dump: UserInfoDump, tile, answer_key = BoardKey):
    button = user_info_dump.user_matrix[tile[1]][tile[0]].winfo_children()[0] 
    if user_info_dump.first: 
        user_info_dump.start_time = time.time()
        user_info_dump.first = False 
        answer_key = create_answer_key(user_info_dump, tile) 

    if user_info_dump.flag_mode:
        flag_mode_helper(button, user_info_dump.mine_label)
        return

    if button.cget("text") == "⚐":
        return
    
    if answer_key.check_matrix_key(tile): 
        win_lose("GAME OVER", answer_key, user_info_dump, lambda: main_menu(user_info_dump.menu_frame.master))
        return
    elif answer_key.adjecent_mines(tile) != 0 and type(button) == tk.Button: 
        graphic_change_matrix(answer_key, user_info_dump, tile)
        user_info_dump.vic_con += 1
    else:
        total_tiles = zero_tile(answer_key, tile, revealed_tiles=[], tiles_to_check=[])
        for revealed_tile in total_tiles:
            if type(user_info_dump.user_matrix[revealed_tile[1]][revealed_tile[0]].winfo_children()[0]) == tk.Button:
                graphic_change_matrix(answer_key, user_info_dump, revealed_tile)
                user_info_dump.vic_con += 1

    if user_info_dump.vic_con == answer_key.size_x*answer_key.size_y - answer_key.mines: # Victory condition.
        end_time = time.time()
        user_info_dump.elapsed_time = end_time - user_info_dump.start_time
        win_lose("VICTORY", answer_key, user_info_dump, lambda: save_score_menu(user_info_dump.menu_frame.master, user_info_dump))
        user_info_dump.mine_label.config(text="0")
        return
    # This function is called everytime a tile is clicked on by the player. The logic of the game is controlled from here. 

def graphic_check_input(menu_frame, entry_button: EntryButton):
    error_label = tk.Label(master=menu_frame, fg="red")
    error_label.pack(side="bottom")
    try:
        width = int(entry_button.result_list[0])
        height = int(entry_button.result_list[1])
        mines = int(entry_button.result_list[2])
        if 1 <= width <= 22 and 1 <= height <= 22 and mines <= width*height - 1:
            next_menu(menu_frame, lambda: minefield(menu_frame.master, width, height, mines))
        else:
            error_label.config(text="Fel input! (max. bredd: 22, max. höjd: 22, det kan inte finnas fler minor än rutor på spelplanet.)")
    except:
        error_label.config(text="Fel input! Skriv in siffor i alla fält.")
    error_label.after(10000, lambda:error_label.destroy())


# Checks the input to custom_minesweeper_menu(). If the input is good then the corresponding mine field is created.
"-----------------------------------------------------------------------------------------------------------------------"
"The following functions create menu layouts."
def main_menu(root):
    menu_frame = create_main_frame(root)
    tk.Label(master=menu_frame, text="Minesweeper", fg="red", font=("", 30, "bold")).pack()
    button_dict = {1:["Spela", lambda: next_menu(menu_frame, lambda: standard_minesweeper_menu(root))], 
                  2:["Highscores", lambda: next_menu(menu_frame, lambda: highscores_main_menu(root))], 
                  3:["Hjälp", lambda: next_menu(menu_frame, lambda: help_menu(root))], 
                  4:["Avsluta", lambda: next_menu(menu_frame, lambda: root.destroy())]} 
    for i in range(1,5):
        tk.Button(master=menu_frame, text=button_dict[i][0], relief=tk.RAISED, font=("", 14), width=13, command=button_dict[i][1]).pack()
# Creates the widgets for the main menu.

def help_menu(root):
    menu_frame = create_main_frame(root)
    tk.Label(master=menu_frame, font=("", 12), justify="left", text="\n" + \
"""Minesweeper går ut på att röja ett spelfält med minor. Ifall du väljer en ruta med
en mina förlorar du. Antalet avgränsande minor hos en ruta anges på rutan.
    -För att avslöja en ruta kan man trycka på en ruta.
    -Klicka på flaggsymbolen för att gå in i 'flaggläge'. I detta läge kan man vänsterklicka för att sätta ut flaggor. 
Man vinner när alla tomma rutor är avslöjade. Lycka till!""").pack()
    tk.Button(master=menu_frame, text="Tillbaka", command=lambda: next_menu(menu_frame, lambda: main_menu(root))).pack()
# Displays a help screen.

def standard_minesweeper_menu(root):
    menu_frame = create_main_frame(root)
    button_dict = {1:["Nybörjare", lambda: next_menu(menu_frame, lambda:minefield(root, 4, 4, 3))],
                   2:["Lätt", lambda: next_menu(menu_frame, lambda: minefield(root, 7, 7, 7))], 
                   3:["Normal", lambda: next_menu(menu_frame, lambda: minefield(root, 15, 15, 35))], 
                   4:["Svår", lambda: next_menu(menu_frame, lambda: minefield(root, 22, 22, 100))], 
                   5:["Anpassad...", lambda: next_menu(menu_frame, lambda: custom_minesweeper_menu(root))]} 
    # Change the corresponding dictionary entry in check_difficulty() when changing the settings above.
    tk.Label(master=menu_frame, text="Välj svårighetsgrad:", font=("", 18)).pack() 
    for i in range(1,6):
        button = tk.Button(master=menu_frame, text=button_dict[i][0], relief=tk.RAISED, font=("", 14), width=13, command=button_dict[i][1]).pack()
# Displays a selection menu for standard mine fields.

def custom_minesweeper_menu(root):
    menu_frame = create_main_frame(root)
    entry_list = []
    label_dict = {1:"Spelplanens bredd (max=22):", 
                  2:"Spelplanens höjd (max=22):", 
                  3:"Antal minor:"} 
    for i in range(1,4):
        tk.Label(master=menu_frame, text=label_dict[i]).pack()
        entry = tk.Entry(master=menu_frame)
        entry.pack()
        entry_list.append(entry)
    confirm = EntryButton(menu_frame, entry_list, "Bekräfta val", lambda: graphic_check_input(menu_frame, confirm))
# Displays a custom selection screen where the user can select a custom size.

def minefield(root, width, height, mines):
    menu_frame = create_main_frame(root) 
    grid_frame = create_main_frame(root) 

    mine_label = tk.Label(master=menu_frame, text=mines, bg="black", fg="red", font=("", 14)) 
    mine_label.pack(side="right") 

    flag_button = tk.Button(master=menu_frame, text="✱") 
    flag_button.pack(side="right")

    tk.Label(master=menu_frame, width=round(width*3)).pack()

    user_matrix = np.full((height, width), None)
    user_info_dump = UserInfoDump(user_matrix, mines, mine_label, flag_button, menu_frame, grid_frame)

    flag_button.config(command=lambda: flag_mode_on_off(user_info_dump))
    for matrix_row in range(height): 
        for matrix_column in range(width):
            frame = tk.Frame(master=grid_frame, height=FRAMEHEIGHT, width=FRAMEWIDTH)
            frame.pack_propagate(False)
            frame.grid(row=matrix_row, column=matrix_column)
            button = tk.Button(master=frame, relief=tk.RAISED, height=FRAMEHEIGHT, width=FRAMEWIDTH,\
command=lambda x = matrix_column, y = matrix_row: minesweeper_output(user_info_dump, (x,y), answer_key = BoardKey))
            button.pack()
            user_info_dump.user_matrix[matrix_row][matrix_column] = frame
# Creates a grid with frames that have buttons in them. Each button sends its position as an argument to minesweeper_output().
# Also creates a flag button and a mine counter label.

def save_score_menu(root, user_info_dump: UserInfoDump):
    menu_frame = create_main_frame(root)

    width = len(user_info_dump.user_matrix[0])
    height = len(user_info_dump.user_matrix)
    mines = user_info_dump.mines
    time = user_info_dump.elapsed_time

    measured_skill, difficulty = check_difficulty(width, height, mines, time)

    tk.Label(master=menu_frame, text="Skriv in ditt namn för att spara rekordet:").pack()

    entry = tk.Entry(master=menu_frame)
    entry.pack()

    confirm = EntryButton(menu_frame, [entry], "Bekräfta", \
lambda: [next_menu(menu_frame, lambda: main_menu(root)), highscores_write(confirm.result_list[0], measured_skill, difficulty)])
    tk.Button(master=menu_frame, text="Tillbaka", command=lambda: next_menu(menu_frame, lambda: main_menu(root))).pack()
# Menu where the user can enter their name to save their score. The score is sent to highscores_write() which logs the scores.

def highscores_main_menu(root):
    menu_frame = create_main_frame(root)
    button_dict = {1:["Nybörjare", lambda: next_menu(menu_frame, lambda: view_highscores(root, "beginner"))], 
                    2:["Lätt", lambda: next_menu(menu_frame, lambda: view_highscores(root, "easy"))],
                    3:["Normal", lambda: next_menu(menu_frame, lambda: view_highscores(root, "normal"))], 
                    4:["Svår", lambda: next_menu(menu_frame, lambda: view_highscores(root, "hard"))], 
                    5:["Anpassad...", lambda: next_menu(menu_frame, lambda: view_highscores(root, "adjusted"))]} 
    tk.Label(master=menu_frame, text="Välj kategori:", font=("", 18)).pack() 
    for i in range(1,6):
        tk.Button(master=menu_frame, text=button_dict[i][0], relief=tk.RAISED, font=("", 14), width=13, command=button_dict[i][1]).pack()
    tk.Button(master=menu_frame, text="Tillbaka", command=lambda: next_menu(menu_frame, lambda: main_menu(root))).pack()
# Selection menu for highscores.

def view_highscores(root, difficulty):
    main_frame = create_main_frame(root)
    with open(file=f"highscores/{difficulty}_highscores.csv", mode="r") as file:
        reader = csv.reader(file)
        reader_list = list(reader)
        if len(reader_list) == 0:
            tk.Label(master=main_frame, text="Det finns inga rekord än!").pack() 
        else:
            tk.Label(master=main_frame, text=f"Rekord (lägre {'poäng' if difficulty == 'adjusted' else 'tid'} är bättre):").pack()
            for i in range(10):
                try:
                    tk.Label(master=main_frame, text=f"{i+1}. {reader_list[i][2]} ({reader_list[i][1]}): {reader_list[i][0]} \
 {'poäng' if difficulty == 'adjusted' else 'sekunder'}.").pack()
                except:
                     break
                
    tk.Button(master=main_frame, text="Tillbaka", command=lambda: next_menu(main_frame, lambda: highscores_main_menu(root))).pack()

# Begins execution here.
def main(): 
    try: 
        if sys.argv[1] == "-t":
            main_T() 
    except: 
        window = tk.Tk()
        window.attributes("-fullscreen", True)
        main_menu(window) 
        window.mainloop()
# Plays the game in the terminal if an argument "-t" is received when starting the program. Otherwise it defaults to the GUI.

if __name__ == "__main__":
    main()