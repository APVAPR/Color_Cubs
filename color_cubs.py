import gettext
import tkinter as tk
import random
from texttable import Texttable
from tkinter.messagebox import askquestion, showinfo
from database import show_all_results, insert_result
from tkinter.simpledialog import askstring


rgb_to_color = {'#000000': 'black', '#eb3734': 'red',
                '#3499eb': 'blue', '#4fbd70': 'green',
                '#bd79ad': 'pink', '#d9d780': 'yellow',
                '#36856e': 'darkgreen'}
colors_to_rgb = {v: k for k, v in rgb_to_color.items()}

with open('rules.txt', 'r') as file:
    rules = file.read()


class My_Button(tk.Button):

    def __init__(self, master, x, y):
        random_color = My_Button.color_rand()
        super().__init__(master, height=1, width=1, bg=f'{random_color}')
        self.master = master
        self.x = x
        self.y = y
        self._color = rgb_to_color[random_color]

    def __str__(self):
        return rgb_to_color[self['bg']]

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, col):
        if col[0] == '#':
            self['bg'] = col
            self._color = rgb_to_color[self['bg']]
        else:
            self['bg'] = colors_to_rgb[col]
            self._color = col

    @staticmethod
    def color_rand():
        colors = ['#eb3734', '#3499eb', '#4fbd70', '#bd79ad', '#d9d780', '#36856e']
        return random.choice(colors)


class Main_window:
    ROW = 10
    COLUMN = 10
    buttons = []
    scores = 0
    moves = 0

    def __init__(self):
        self.scores_label = None
        self.win = tk.Tk()
        self.win.title('Color Cubs')
        self.win.resizable(False, False)
        self.win.config(bg='black')
        self.geometry_set()
        self.first_start_game()

    def geometry_set(self):
        s = self.win.geometry()
        s = s.split('+')
        s = s[0].split('x')
        width_win = int(s[0])
        height_win = int(s[1])
        w = self.win.winfo_screenwidth()
        h = self.win.winfo_screenheight()
        w = w // 2
        h = h // 2
        w = (w - width_win) // 2
        h = (h - height_win) // 2
        self.win.geometry(f'+{w}+{h}')

    def make_game_buttons_list(self):
        for row in range(self.ROW + 2):
            temp = []
            for col in range(self.COLUMN + 2):
                btn = My_Button(self.win, x=row, y=col)
                btn.config(command=lambda button=btn: self.button_push(button))
                temp.append(btn)
                btn.grid(row=row, column=col)
                if col == 0 or col == self.COLUMN + 1 or row == 0 or row == self.ROW + 1:
                    btn.color = '#000000'
                    btn.config(state=tk.DISABLED)
            self.buttons.append(temp)
        if self.check_lonely_button():
            self.reload_game()

    def show_scores_label(self):
        self.scores_label = tk.Label(self.win, text=f'Scores: {self.scores}', font='Arial')
        self.scores_label.grid(row=self.ROW + 3, column=self.COLUMN // 2, columnspan=500)

    def button_push(self, clicked_button: My_Button):
        same_color_btn = self.check_around(clicked_button.x, clicked_button.y, [])
        if len(same_color_btn) > 1:
            self.iterate_same_btn_lst(same_color_btn, self.change_color_column)
            black_column = self.check_low_row()
            if black_column:
                self.shift_column(black_column)
            self.change_button_state()
            self.counter_scores(same_color_btn)
            self.moves += 1
        self.show_in_console()
        self.scores_label.config(text=f'Moves: {self.moves} Scores: {self.scores}')
        self.is_finish_game()

    def check_around(self, x, y, some_btn_lst=None):
        """
        Checks whether adjacent buttons have the same color as button[x][y].
        Adds a tuple with the coordinates of such buttons to the list.
        Recursively checks the color of adjacent buttons of the same buttons
        Returns a list with coordinates of the same color buttons pressed

        """
        if some_btn_lst is None:
            some_btn_lst = []
        count = 0
        if not (x, y) in some_btn_lst:
            some_btn_lst.append((x, y))
            count += 1
        center_btn = self.buttons[x][y]
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                btn = self.buttons[x + i][y + j]
                if btn.color == center_btn.color and (x + i, y + j) not in some_btn_lst:
                    some_btn_lst.append((x + i, y + j))
                    count += 1
        if count == 0:
            return some_btn_lst

        for row, col in some_btn_lst:
            if self.buttons[row][col].color == self.buttons[x][y].color:
                if not (row == x and col == y):
                    self.check_around(row, col, some_btn_lst)
        return some_btn_lst

    def check_lonely_button(self):
        btns = []
        for row in self.buttons:
            for button in row:
                btns.append(button)
        btns = sorted(btns, key=lambda x: x.color)
        btns = [i.color for i in btns if i.color != 'black']
        for i in btns:
            if btns.count(i) < 2:
                print('Lonely button')
                return True
        return False

    def change_button_state(self):
        for row in self.buttons:
            for button in row:
                if button.color == 'black' and button['state'] != 'disabled':
                    button['state'] = tk.DISABLED
                elif button.color != 'black' and button['state'] == 'disabled':
                    button['state'] = tk.NORMAL

    def change_color_column(self, row, col):
        """
        функция изменяет цвет по всей колонке.

        """
        for i in range(row, -1, -1):
            btn = self.buttons[i][col]
            btn2 = self.buttons[i - 1][col]
            if btn2.color == 'black':
                btn.color = 'black'
            else:
                btn2.color, btn.color = btn.color, btn2.color

    @staticmethod
    def iterate_same_btn_lst(same_color_list, func):
        same_color_list = sorted(same_color_list, key=lambda x: (x[0], x[1]))
        for r, c in same_color_list:
            func(r, c)

    def check_low_row(self):
        empty_column_list = []
        for col in range(1, self.COLUMN):
            btn = self.buttons[self.ROW][col]
            if btn.color == 'black':
                empty_column_list.append(col)
        return empty_column_list

    def shift_column(self, black_col_list):
        for black_column in black_col_list:
            for row in range(self.ROW, -1, -1):
                for col in range(black_column, 0, -1):
                    btn1 = self.buttons[row][col]
                    btn2 = self.buttons[row][col - 1]
                    btn1.color, btn2.color = btn2.color, btn1.color

    def counter_scores(self, same_btns):
        self.scores += len(same_btns) ** 2

    def create_menu(self):
        menubar = tk.Menu(self.win)
        self.win.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Game', command=self.reload_game)
        file_menu.add_command(label='Settings', command=self.create_settings_menu)
        file_menu.add_command(label='Show results', command=Table.show_winner_table)
        file_menu.add_command(label='Rules', command=lambda: showinfo('Rules', rules))
        file_menu.add_command(label='Quit', command=self.win.destroy)
        menubar.add_cascade(label='File', menu=file_menu)

    def create_settings_menu(self):
        setting_menu = tk.Toplevel(self.win)
        setting_menu.wm_title('Settings')
        tk.Label(setting_menu, text='Rows count:').grid(row=0, column=0)
        tk.Label(setting_menu, text='Column count:').grid(row=1, column=0)
        row_entry = tk.Entry(setting_menu)
        row_entry.insert(0, self.ROW)
        row_entry.grid(row=0, column=1)
        column_entry = tk.Entry(setting_menu)
        column_entry.insert(0, self.COLUMN)
        column_entry.grid(row=1, column=1)
        btn = tk.Button(setting_menu, text='Confirm', command=lambda: self.change_settings(row_entry, column_entry))
        btn.grid(row=2, column=0, columnspan=2)

    def change_settings(self, row: tk.Entry, column: tk.Entry):
        self.ROW = int(row.get())
        self.COLUMN = int(column.get())
        self.reload_game()

    def show_in_console(self):
        table = Texttable()
        for i in self.buttons:
            table.add_row(i)

        score_row = ['' for _ in range(len(i))]
        score_row[-1] = self.scores
        score_row[-2] = 'Score is:'
        table.add_row(score_row)
        print(table.draw())

    def splash_screen(self):
        text = 'COLOR\nCUBS\n\n\nclick\nto start\nthe game'
        label1 = tk.Button(self.win, text=text,
                           bg='white',
                           font=('Cube font', 50, 'bold'),
                           command=lambda: self.reload_game())
        label1.grid(row=0, column=0)

    def first_start_game(self):
        self.splash_screen()

    def reload_game(self):
        self.buttons.clear()
        [child.destroy() for child in self.win.winfo_children()]
        self.scores = self.moves = 0
        self.create_menu()
        self.make_game_buttons_list()
        self.show_scores_label()

    def is_all_buttons_black(self):
        for row in self.buttons:
            for button in row:
                if button.color != 'black':
                    return False
        return True

    def is_same_button_around(self, row, col):
        center_btn = self.buttons[row][col]
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                btn = self.buttons[row + i][col + j]
                if btn.color == center_btn.color and (btn is not center_btn):
                    return True
        return False

    def is_has_moves(self):
        for row in self.buttons[1: self.ROW + 1]:
            for button in row[1: self.COLUMN + 1]:
                if button['state'] != 'disabled':
                    if self.is_same_button_around(button.x, button.y):
                        return True
        return False

    def off_all_buttons(self):
        for row in self.buttons:
            for button in row:
                if button['state'] != 'disabled':
                    button['state'] = tk.DISABLED

    def is_finish_game(self):
        is_finish = False
        title = 'Game over!'

        if self.is_all_buttons_black():
            title = 'You win!!!'
            text = f'Congratulation!!! You win!!! Your score is: {self.scores}. Start new game?'
            is_finish = True
            Table.gamer = askstring('Name', 'What is your name?')
            if Table.gamer:
                Table.add_result(self.scores, self.moves)

        elif self.check_lonely_button():
            text = f'Game over. There is a fireproof cube on the field. Start a new game?'
            is_finish = True

        elif not self.is_has_moves():
            text = f'Game over, no more moves. Start a new game?'
            is_finish = True

        if is_finish:
            self.off_all_buttons()
            if askquestion(title, text) == 'yes':
                self.reload_game()
            print(text)


class Table:
    winners_list = show_all_results()
    _GAMER = None

    def __init__(self):
        self.win_win = tk.Toplevel()
        self.win_win.title('Winner list!')
        self.win_win.geometry('+500+10')

    @property
    def gamer(self):
        return Table._GAMER

    @gamer.setter
    def gamer(self, name):
        if not Table._GAMER:
            Table._GAMER = name

    @gamer.deleter
    def gamer(self):
        if Table._GAMER:
            Table._GAMER = None

    def create_top_line(self):
        top_table = ['№', 'Name', 'Scores', 'Moves']

        for i in range(4):
            tk.Label(self.win_win, text=top_table[i],
                     bg='LightSteelBlue',
                     fg='Black',
                     font=('Arial', 16, 'bold')).grid(row=0, column=i)

    def filling_table(self):
        i = 1
        for index, data in enumerate(Table.winners_list, 1):
            name, scores, moves = data
            print(name, scores, moves)
            tk.Label(self.win_win, text=index).grid(row=i, column=0)
            tk.Label(self.win_win, text=name).grid(row=i, column=1)
            tk.Label(self.win_win, text=scores).grid(row=i, column=2)
            tk.Label(self.win_win, text=moves).grid(row=i, column=3)
            i += 1

    @staticmethod
    def show_winner_table():
        tab = Table()
        tab.create_top_line()
        tab.filling_table()
        print(tab.winners_list)

    @staticmethod
    def add_result(scores, moves):
        insert_result(Table.gamer, scores, moves)


def main():

    a = Main_window()
    a.win.mainloop()


if __name__ == '__main__':
    main()
