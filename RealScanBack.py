import sqlite3
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msg
from dateutil.relativedelta import *
import sys
import os
import datetime

ENTER_TEXT = "Enter information"
MAIN_TABLE = "Patients"
TOP_REL_HIGH = 0.1
BOTTOM_REL_HIGH = 0.9
FONT = ("Courier", 16)
COLUMNS_NAMES = ( "Date", "Age", "Weight", "Height", 'Scoliosis', 'Kyphosis', 'Lordosis', 'Posture', 'Markers')
PATIENT_FIELDS = {'id_num': 'ID:', 'name': 'Name:', 'surname': 'Surname:', 'DoB': 'Date of birth:', 'gender': 'Gender:',
                  'Height': 'Height', 'Weight': 'Weight:',
                  'Scoliosis' :'Scoliosis:', 'Kyphosis':'Kyphosis:', 'Lordosis':'Lordosis:',
                  'Posture':'Posture:', 'Markers': 'Markers:'}
MAIN_COLS = """(id_num text NOT NULL PRIMARY KEY, name text, surname text, DoB text, gender text, Height text,
              Weight text, Scoliosis text, Kyphosis text, Lordosis text, Posture text, Markers text)"""
PAT_COL_INDEX = {'id_num': 0, 'name': 1, 'surname': 2, 'DoB': 3, 'gender': 4,
                  'Height': 5, 'Weight': 6,
                 'Scoliosis' : 7, 'Kyphosis': 8, 'Lordosis':9, 'Posture':10, 'Markers': 11}
PATIENT_COLS = """(date text, age REAL, Weight REAL, Height REAL, Scoliosis text, Kyphosis text,
 Lordosis text, Posture text, Markers text)"""
PAT_DICT = {"Date": "data", "Age":'age', "Weight": 'Weight', "Height":'Height', 'Scoliosis' :'Scoliosis',
            'Kyphosis':'Kyphosis', 'Lordosis':'Lordosis',
                  'Posture':'Posture', 'Markers': 'Markers'}
PAT_TABLE_NAME = "Patient_{rowid}"
CHOOSE_FIELDS = {'Scoliosis' : ['Yes','No'], 'Kyphosis': ['Yes','No'], 'Lordosis': ['Yes','No'],
                  'Posture': ["Upright stomding", "Neck flexion", "Vertebral column flexion"], 'Markers': ['Yes','No']}



class Entr:
    def __init__(self, parent, row, col, text, var, default=""):
        self.label = Entry(parent, textvariable=var)
        self.label.grid(row=row, column=col + 1, sticky=W, padx=5, pady=10 , in_=parent)
        chanel_num_label = Label(parent, text=text,  bg='gray85', font=("Courier", 16))
        chanel_num_label.grid(row=row, column=col, sticky=W, padx=5, in_=parent)
        self.label.insert(0, default)

    def bind(self, key, command):
        self.label.bind(key, command)

    def get_data(self):
        return float(self.label.get())

    def get_str(self):
        return str(self.label.get())


class CBox:
    def __init__(self, parent, row, col, text, var, values, default=""):
        self.label = ttk.Combobox(parent, textvariable=var, values=values)
        self.label.grid(row=row, column=col + 1, sticky=W, padx=5, pady=10, in_=parent)
        chanel_num_label = Label(parent, text=text, bg='gray85', font=("Courier", 16))
        chanel_num_label.grid(row=row, column=col, sticky=W, padx=5, in_=parent)
        self.label.insert(0, default)

    def get_data(self):
        return float(self.label.get())

    def get_str(self):
        return str(self.label.get())


class Screen:
    def __init__(self, parent):
        self.parent = parent
        self.data_path = os.path.dirname(sys.argv[0])
        self.tab_parent = ttk.Notebook(parent)
        self.entr = dict()
        self.MedText = dict()
        style = ttk.Style()
        self.cur_rowid = 0
        self.cur_patient = dict()
        for field in PATIENT_FIELDS:
            self.cur_patient[field] = StringVar()
        style.theme_create("MyStyle", parent="alt", settings={
            "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0]}},
            "TNotebook.Tab": {"configure": {"padding": [10, 10]}, }})
        style.theme_use("MyStyle")
        self.make_menu()
        self.patient_page()
        self.his_page()
        self.meas_page()
        self.db = Database()
        self.cur_meas = {col : '' for col in COLUMNS_NAMES}

    def search(self, event=None):
        cur_id = self.cur_patient['id_num'].get()
        patient = self.db.get_data(MAIN_TABLE, 'id_num', cur_id, MAIN_COLS)
        self.db.commit()
        if patient:
            self.new_pat()
            self.cur_rowid = self.db.get_rowid(MAIN_TABLE, cur_id, MAIN_COLS)
            path = os.path.join(self.data_path, "Patient_" + str(self.cur_rowid))
            for key, var in self.cur_patient.items():
                var.set(patient[0][PAT_COL_INDEX[key]])
            for key, item in self.MedText.items():
                cur_path = os.path.join(path, f"{self.cur_rowid}_{key}.txt")
                item.read_file(cur_path)
            for index, meas in enumerate(self.db.get_all_tab(PAT_TABLE_NAME.format(rowid=self.cur_rowid))):
                self.his_table.insert(meas)
        else:
            msg.showerror("Search Error", "Patient not found ):")
            return

        self.parent.update()

    def make_text_files(self, dir_path, rowid):
        for key, item in self.MedText.items():
            cur_path = os.path.join(dir_path, f"{rowid}_{key}.txt")
            file = open(cur_path, "w+")
            file.close()
            item.read_file(cur_path)

    def save(self):
        cur_id = self.cur_patient['id_num'].get()
        new_pat = [var.get() for var in self.cur_patient.values()]
        if self.db.get_data(MAIN_TABLE, 'id_num', cur_id, MAIN_COLS):
            msg.showerror("Save Error", f"Already exist patient with same id: {cur_id}")
            return
        self.db.insert(tuple(new_pat), MAIN_TABLE, MAIN_COLS)
        rowid = self.db.get_rowid(MAIN_TABLE, cur_id, MAIN_COLS)
        new_dir = os.path.join(self.data_path, "Patient_" + str(rowid))
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
            self.make_text_files(new_dir, rowid)
        else:
            msg.showerror("Save Error", f"cannot make dir")
            return
        self.db.create_table(PAT_TABLE_NAME.format(rowid=rowid), PATIENT_COLS)
        msg.showinfo(message="Save complete")
        self.cur_rowid = rowid
        self.db.commit()

    def new_pat(self):
        for var in self.cur_patient.values():
            var.set('')
        for medText in self.MedText.values():
            medText.clear()
        self.his_table.delete()
        self.cur_rowid = 0

    def edit(self):
        if self.cur_rowid == 0:
            msg.showerror("Error", f"Editing available only after uploading patient")
        for key, var in self.cur_patient.items():
            self.db.update(MAIN_TABLE, key, var.get(), self.cur_rowid)
        msg.showinfo(message="Update complete")

    def make_menu(self):
        self.patient = ttk.Frame(self.tab_parent)
        self.tab_parent.add(self.patient, text="Patient")

        self.meas_his = ttk.Frame(self.tab_parent)
        self.tab_parent.add(self.meas_his, text="Measurements history")

        self.meas = ttk.Frame(self.tab_parent)
        self.tab_parent.add(self.meas, text="Measurement")

        self.tech = ttk.Frame(self.tab_parent)
        self.tab_parent.add(self.tech, text="Technician")

        self.end = ttk.Frame(self.tab_parent)
        self.tab_parent.add(self.end, text="Exit")

        self.tab_parent.pack(expand=1, fill='both')

    def patient_page(self):
        #top frame
        self.top = Frame(self.patient, bg='gray85')
        self.top.grid(row=0, column=0, rowspan=1, columnspan=12, pady=20, padx=20)
        self.entr['id_num'] = Entr(self.top, 0, 0, "ID Number:", self.cur_patient['id_num'])
        self.entr['id_num'].bind('<Return>', self.search)
        self.entr['name'] = Entr(self.top, 0, 2, "Name:", self.cur_patient['name'])
        self.entr['surname'] = Entr(self.top, 0, 4, "Surname:", self.cur_patient['surname'])
        Button(self.top, text="Search", width=10, height=2, command=self.search).grid(row=0, column=6, rowspan=2, padx=6)


        #left frame
        left_frame = LabelFrame(self.patient,  bg='gray85', text='info')
        left_frame.grid(row=1, column=0, rowspan=4, columnspan=6, pady=5, padx=5)
        self.entr['DoB'] = Date(left_frame, 0, 0)
        self.cur_patient['DoB'] = self.entr['DoB']
        self.entr['gender'] = CBox(left_frame, 1, 0, "Sex:", self.cur_patient['gender'], ["F", "M"])
        counter = 2
        for key, name in PATIENT_FIELDS.items():
            if key[0] in {'H', 'W'}:
                self.entr[key] = Entr(left_frame, counter, 0, name, self.cur_patient[key])
                counter += 1
        for key, values in CHOOSE_FIELDS.items():
            self.entr[key] = CBox(left_frame, counter, 0, PATIENT_FIELDS[key], self.cur_patient[key], values)
            counter += 1



        #right_frame
        right_frame = LabelFrame(self.patient,  bg='gray85', text='info')
        right_frame.grid(row=1, column=6, rowspan=10, columnspan=10, pady=5, padx=5, sticky=NW)
        self.MedText['Med_bg'] = MedText(right_frame, "Medical background:", 0, 0)
        self.MedText['fam_his'] = MedText(right_frame, "Family history:", 3, 0)
        self.MedText['other'] = MedText(right_frame, 'Other:', 0, 1)


        #low_frame
        low_frame = LabelFrame(self.patient,  bg='gray85', text='options')
        low_frame.grid(row=12, column=0, rowspan=10, columnspan=10, pady=5, padx=5, sticky=NW)
        Button(low_frame, text="Clear patient\ndata", width=15, height=4, font=FONT, command=self.new_pat)\
            .grid(row=0, column=0, pady=5, padx=15)
        Button(low_frame, text="Edit patient\ninfo", width=15, height=4, font=FONT, command=self.edit)\
            .grid(row=0, column=1, pady=5, padx=15)
        Button(low_frame, text="Save new\npatient", width=15, height=4, font=FONT, command=self.save).grid\
            (row=0, column=2, pady=5, padx=15)
        Button(low_frame, text="Cancel", width=15, height=4, font=FONT).grid(row=0, column=3, pady=5, padx=15)
        Button(low_frame, text="Print", width=15, height=4, font=FONT).grid(row=0, column=4, pady=5, padx=15)

    def his_page(self):
        # top frame
        top_frame = Frame(self.meas_his, bg='gray85')
        top_frame.grid(row=0, column=0, rowspan=1, columnspan=12, pady=20, padx=20)
        Label(top_frame, text="ID Number:",  bg='gray85', font=FONT).grid(row=0, column=0, pady=5, padx=5, sticky=W)
        Label(top_frame, text="Name:",  bg='gray85', font=FONT).grid(row=0, column=2, pady=5, padx=5, sticky=W)
        Label(top_frame, text="Surname:",  bg='gray85', font=FONT).grid(row=0, column=4, pady=5, padx=5, sticky=W)
        Label(top_frame, textvariable=self.cur_patient['id_num'], width=15).grid(row=0, column=1, pady=5, padx=5, sticky=W)
        Label(top_frame, textvariable=self.cur_patient['name'], width=15).grid(row=0, column=3, pady=5, padx=5, sticky=W)
        Label(top_frame, textvariable=self.cur_patient['surname'], width=15).grid(row=0, column=5, pady=5, padx=5, sticky=W)
        # make table
        self.his_table = Table(self.meas_his, COLUMNS_NAMES, 1, 0)

    def meas_page(self):
        top_frame = Frame(self.meas, bg='gray85')
        top_frame.grid(row=0, column=0, rowspan=1, columnspan=12, pady=20, padx=20)
        Label(top_frame, text="ID Number:", bg='gray85', font=FONT).grid(row=0, column=0, pady=5, padx=5, sticky=W)
        Label(top_frame, text="Name:", bg='gray85', font=FONT).grid(row=0, column=2, pady=5, padx=5, sticky=W)
        Label(top_frame, text="Surname:", bg='gray85', font=FONT).grid(row=0, column=4, pady=5, padx=5, sticky=W)
        Label(top_frame, textvariable=self.cur_patient['id_num'], width=15).grid(row=0, column=1, pady=5, padx=5,
                                                                                 sticky=W)
        Label(top_frame, textvariable=self.cur_patient['name'], width=15).grid(row=0, column=3, pady=5, padx=5,
                                                                               sticky=W)
        Label(top_frame, textvariable=self.cur_patient['surname'], width=15).grid(row=0, column=5, pady=5, padx=5,
                                                                                  sticky=W)

        Button(self.meas, text="Save new measurement", width=20, height=4, command=self.save_meas).grid(row=1, column=0)

    def save_meas(self):
        self.cur_meas["Date"] = str(datetime.date.today())
        self.cur_meas["Age"] = self.entr['DoB'].get_age()
        for field in COLUMNS_NAMES:
            if field not in ["Date", "Age"]:
                self.cur_meas[field] = self.cur_patient[field].get()
        self.db.insert(tuple(self.cur_meas.values()), PAT_TABLE_NAME.format(rowid=self.cur_rowid),
                       PATIENT_COLS)
        rowid = len(self.db.get_all_tab(PAT_TABLE_NAME.format(rowid=self.cur_rowid)))
        self.his_table.insert(tuple(self.cur_meas.values()))
        new_dir = os.path.join(self.data_path, "Patient_" + str(self.cur_rowid), f"{str(datetime.date.today())}_{rowid}")
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)


class Table:
    def __init__(self, parent, columns, row, col):
        self.columns = columns
        self.parent = parent
        frame = Frame(parent)
        frame.grid(row=row, column=col)
        self.listBoxs = dict()
        self.vsb = Scrollbar(frame, orient="vertical", command=self.OnVsb)
        self.vsb.grid(row=1, column=0)
        for index, column in enumerate(columns):
            Button(frame, text=column, width=10).grid(row=0, column=index + 1)
            self.listBoxs[column] = Listbox(frame, width=10, yscrollcommand=self.vsb.set)
            self.listBoxs[column].grid(row=1, column=index + 1, padx=0)

    def insert(self, values):
        for index, key in enumerate(self.listBoxs):
            if key == 'BMI':
                self.listBoxs[key].insert(END, str(values[index])[:8])
                continue
            self.listBoxs[key].insert(END, values[index])

    def delete(self):
        for lb in self.listBoxs.values():
            lb.delete(0, END)

    def OnVsb(self, *args):
        for list in self.listBoxs.values():
            list.yview(*args)


    def OnMouseWheel(self, event):
        for list in self.listBoxs.values():
            list.yview("scroll", event.delta, "units")
        # this prevents default bindings from firing, which
        # would end up scrolling the widget twice
        return "break"


class MedText:
    def __init__(self, parent, text, row, col, width=30, height=10):
        self.new_line = StringVar()
        Label(parent, text=text, bg='gray85', font=FONT).grid(row=row, column=col)
        frame = Frame(parent)
        frame.grid(row=row + 1, column=col, sticky=W)
        self.entry = Entry(frame, textvariable=self.new_line, width=width)
        self.entry.grid(row=0, column=0, sticky=W)
        self.new_line.set(ENTER_TEXT)
        self.lb = Listbox(parent, width=width + 10, height=height, bd=3, highlightbackground='gray')
        self.lb.grid(row=row + 2, column=col, sticky=W)
        self.file_path = ""
        self.entry.bind("<FocusIn>", self.clear_search)
        self.entry.bind("<FocusOut>", self.re_clear)
        self.entry.bind('<Return>', self.insert_new_line)
        Button(frame, text="Save", command=self.insert_new_line, width=9).grid(row=0, column=1)

    def read_file(self, file_path):
        file = open(file_path, 'r')
        lines = file.readlines()
        for line in lines:
            self.lb.insert(END, line)
        self.file_path = file_path
        file.close()

    def insert_new_line(self, event=None):
        if self.file_path:
            new_line = self.new_line.get()
            if new_line and new_line != ENTER_TEXT:
                file = open(self.file_path, "a")
                file.write(new_line + "\n")
                file.close()
                self.lb.insert(END, new_line)
                self.new_line.set("")

    def re_clear(self, event):
        self.new_line.set(ENTER_TEXT)

    def clear(self):
        self.file_path = ""
        self.new_line.set(ENTER_TEXT)
        self.lb.delete(0, END)

    def clear_search(self, event):
        self.new_line.set("")

class Date:
    def __init__(self, parent, row, col):
        Label(parent, text="Date of birth:", font=FONT, bg='gray85').grid(row=row, column=col)
        Date_frame = Frame(parent)
        Date_frame.grid(row=row, column=col + 1)
        self.day = ttk.Combobox(Date_frame, values=[i for i in range(1,32)], width=5)
        self.day.insert(0, "Day")
        self.day.grid(row=0, column=0, sticky=W)
        self.month = ttk.Combobox(Date_frame, values=[i for i in range(1, 13)], width=5)
        self.month.insert(0, "Month")
        self.month.grid(row=0, column=1, sticky=W)
        self.year = ttk.Combobox(Date_frame, values=[i for i in range(1980, datetime.date.today().year + 1)], width=5)
        self.year.insert(0, "Year")
        self.year.grid(row=0, column=2, sticky=W)

    def get(self):
        return f"{self.day.get()}/{self.month.get()}/{self.year.get()}"

    def set(self, text):
        self.day.delete(0, END)
        self.month.delete(0, END)
        self.year.delete(0, END)
        if not text:
            self.day.insert(0, "Day")
            self.month.insert(0, "Month")
            self.year.insert(0, "Year")
            return
        else:
            date = text.split('/')
            if len(date) == 3:
                self.day.insert(0, date[0])
                self.month.insert(0, date[1])
                self.year.insert(0, date[2])
            else:
                self.day.insert(0, "Day")
                self.month.insert(0, "Month")
                self.year.insert(0, "Year")

    def get_age(self):
        birth = datetime.date(int(self.year.get()), int(self.month.get()), int(self.day.get()))
        today = datetime.date.today()
        age = relativedelta(today, birth)
        return f"{age.years}.{age.months}"

class Database:
    """sqlite3 database class that holds testers jobs"""
    DB_LOCATION = os.path.join(os.path.dirname(__file__), "BackScN.db")

    def __init__(self):
        """Initialize db class variables"""

        self.connection = sqlite3.connect(Database.DB_LOCATION)
        self.cur = self.connection.cursor()

    def close(self):
        """close sqlite3 connection"""
        self.connection.close()

    def insert(self, new_data, table_name, columns_tup):
        """execute a row of data to current cursor"""
        self.create_table(table_name, columns_tup)
        self.cur.execute(f"Insert Into {table_name} VALUES {new_data}")

    def insertMany(self, many_new_data, name, col_num, columns_tup):
        """add many new data to database in one go"""
        self.create_table(name, columns_tup)
        form = self.make_form(col_num)
        self.cur.executemany("Insert Into " + name + ' VALUES' + form, many_new_data)

    def create_table(self, name, columns_tup):
        """create a database table if it does not exist already"""
        self.cur.execute('''CREATE TABLE IF NOT EXISTS ''' + name + columns_tup)
        self.commit()

    def execute(self, new_data):
        """execute a row of data to current cursor"""
        self.cur.execute(new_data)

    def commit(self):
        """commit changes to database"""
        self.connection.commit()

    def get_all_tab(self, tab_name):
        self.cur.execute("SELECT * FROM " + tab_name)
        return self.cur.fetchall()

    def get_data(self, table, col, buffer, columns_tup):
        self.create_table(table, columns_tup)
        self.cur.execute(f"SELECT * FROM {table} WHERE {col} = '{buffer}'")
        return self.cur.fetchall()

    def get_rowid(self, table, id_num, col_tup):
        self.create_table(table, col_tup)
        self.cur.execute(f"SELECT rowid FROM {table} WHERE id_num = '{id_num}'")
        return self.cur.fetchone()[0]

    def make_form(self, num):
        form = '('
        for i in range(0, num - 1):
            form += '?, '
        form += '?)'
        return form

    def update(self, table, col, new_data, rowid):
        self.cur.execute(f"UPDATE  {table} SET {col} = '{new_data}' WHERE rowid = '{rowid}'")
        self.commit()

    def __del__(self):
        self.commit()
        self.close()


if __name__ == '__main__':
    root = Tk()
    root.title("BackScn")
    img = Image("photo", file="/Users/guyfilo/PycharmProjects/ad-or/icon.png")
    root.tk.call('wm', 'iconphoto', root._w, img)
    root.geometry('{}x{}'.format(1200, 800))
    Screen(root)
    root.mainloop()