# -*- encoding: utf8 -*-

import tkinter.messagebox
from tkinter import *
from tkinter.ttk import *
import datetime
import pickle

NUM_OF_ITEMS=1
is_dealt = [0] * NUM_OF_ITEMS

def pickCodeFromItems(set_items_info):
    return

class ElocationGUI:
    def __init__(self):
        self.window = Tk()
        self.window.title("E-location")
        self.window.resizable(0, 0)

        frame1 = Frame(self.window)
        frame1.pack(padx=10, pady=10)

        Label(frame1, text="Input sync file DIR:", width=20, justify=CENTER).grid(
            row=1, column=1, padx=5, pady=5)
        Label(frame1, text="Prime", width=8, justify=CENTER).grid(
            row=1, column=2, padx=5, pady=5)
        Label(frame1, text="", width=8, justify=CENTER).grid(
            row=1, column=3, padx=5, pady=5)

        self.rows = NUM_OF_ITEMS
        self.cols = 2

        self.variable = []
        for row in range(self.rows):
            self.variable.append([])
            for col in range(self.cols):
                self.variable[row].append(StringVar())

        for row in range(self.rows):
            Entry(frame1, textvariable=self.variable[row][0],
                  width=50).grid(row=row + 2, column=1, padx=5, pady=5)
            Entry(frame1, textvariable=self.variable[row][1],
                  width=10).grid(row=row + 2, column=2, padx=5, pady=5)
        frame3 = Frame(self.window)
        frame3.pack(padx=10, pady=10)
        self.confirm_bt=Button(frame3, text='Confirm', command=self.save).pack(side=LEFT)
        self.start_bt = Button(frame3, text="Sync", command=self.start)
        self.start_bt.pack(side=LEFT)
        self.set_bt = Button(frame3, text='Cancel', command=self.setFlags)
        self.set_bt.pack(side=LEFT)
        Button(frame3, text="History", command=self.displayHisRecords).pack(side=LEFT)
        self.load_bt = Button(frame3, text='Open', command=self.load)
        self.load_bt.pack(side=LEFT)
        self.window.protocol(name="WM_DELETE_WINDOW", func=self.close)
        self.window.after(100, self.updateControls)
        self.window.mainloop()

    def displayHisRecords(self):
        """
        显示历史信息
        """
        global consignation_info
        tp = Toplevel()
        tp.title('History Records')
        tp.resizable(0, 1)
        scrollbar = Scrollbar(tp)
        scrollbar.pack(side=RIGHT, fill=Y)
        col_name = ['Date', 'Time', 'Barms', 'CO', 'SN', 'location', 'prime', 'comment','others']
        tree = Treeview(
            tp, show='headings', columns=col_name, height=30, yscrollcommand=scrollbar.set)
        tree.pack(expand=1, fill=Y)
        scrollbar.config(command=tree.yview)
        for name in col_name:
            tree.heading(name, text=name)
            tree.column(name, width=70, anchor=CENTER)

        for msg in consignation_info:
            tree.insert('', 0, values=msg)

    def save(self):
        """
        保存设置
        """
        global set_items_info, consignation_info
        self.getItems()
        with open('itemInfo.dat', 'wb') as fp:
            pickle.dump(set_items_info, fp)
            pickle.dump(consignation_info, fp)

    def load(self):
        """
        载入设置
        """
        global set_items_info, consignation_info
        try:
            with open('itemInfo.dat', 'rb') as fp:
                set_items_info = pickle.load(fp)
                consignation_info = pickle.load(fp)
        except FileNotFoundError as error:
            tkinter.messagebox.showerror('错误', error)

        for row in range(self.rows):
            for col in range(self.cols):
                if col == 0:
                    self.variable[row][col].set(set_items_info[row][0])
                elif col == 3:
                    self.variable[row][col].set(set_items_info[row][1])
                elif col == 4:
                    self.variable[row][col].set(set_items_info[row][2])
                elif col == 5:
                    self.variable[row][col].set(set_items_info[row][3])
                elif col == 6:
                    self.variable[row][col].set(set_items_info[row][4])
                elif col == 7:
                    temp = set_items_info[row][5].strftime('%X')
                    if temp == '01:00:00':
                        self.variable[row][col].set('')
                    else:
                        self.variable[row][col].set(temp)

    def setFlags(self):
        """
        重置标志
        """
        global is_start, is_ordered
        if is_start is False:
            is_ordered = [1] * NUM_OF_ITEMS
    
    def sellAll(self):
        return

    def updateControls(self):
        """
        更新状态信息
        """
        global actual_items_info, is_start
        if is_start:
            for row, (actual_code, actual_name, actual_price,is_great_drop) in enumerate(actual_items_info):
                if actual_code:
                    self.variable[row][1].set(actual_name)
                    self.variable[row][2].set(str(actual_price))
                    if is_ordered[row] == 1:
                        self.variable[row][8].set('监控中')
                    elif is_ordered[row] == 0:
                        self.variable[row][8].set('已委托')
                    self.variable[row][9].set(str(is_dealt[row]))
                else:
                    self.variable[row][1].set('')
                    self.variable[row][2].set('')
                    self.variable[row][8].set('')
                    self.variable[row][9].set('')

        self.window.after(3000, self.updateControls)

    def start(self):
        """
        启动停止
        """
        global is_start, item_codes, set_items_info
        if is_start is False:
            is_start = True
        else:
            is_start = False

        if is_start:
            self.getItems()
            item_codes = pickCodeFromItems(set_items_info)
            self.start_bt['text'] = '停止'
            self.set_bt['state'] = DISABLED
            self.load_bt['state'] = DISABLED
        else:
            self.start_bt['text'] = '开始'
            self.set_bt['state'] = NORMAL
            self.load_bt['state'] = NORMAL

    def close(self):
        """
        关闭程序时，停止线程
        """
        global is_monitor
        is_monitor = False
        self.window.quit()

    def getItems(self):
        """
        获取UI上用户输入的各项数据，
        """
        global set_items_info
        set_items_info = []

        # 获取买卖价格数量输入项等
        for row in range(self.rows):
            set_items_info.append([])
            for col in range(self.cols):
                temp = self.variable[row][col].get().strip()
                if col == 0:
                    if len(temp) == 6 and temp.isdigit():  # 判断股票代码是否为6位数
                        set_items_info[row].append(temp)
                    else:
                        set_items_info[row].append('')
                elif col == 3:
                    if temp in ('>', '<'):
                        set_items_info[row].append(temp)
                    else:
                        set_items_info[row].append('')
                elif col == 4:
                    try:
                        price = float(temp)
                        if price > 0:
                            set_items_info[row].append(price)  # 把价格转为数字
                        else:
                            set_items_info[row].append(0)
                    except ValueError:
                        set_items_info[row].append(0)
                elif col == 5:
                    if temp in ('B', 'S'):
                        set_items_info[row].append(temp)
                    else:
                        set_items_info[row].append('')
                elif col == 6:
                    if temp.isdigit() and int(temp) >= 0:
                        set_items_info[row].append(str(int(temp) // 100 * 100))
                    else:
                        set_items_info[row].append('')
                elif col == 7:
                    try:
                        set_items_info[row].append(datetime.datetime.strptime(temp, '%H:%M:%S').time())
                    except ValueError:
                        set_items_info[row].append(datetime.datetime.strptime('1:00:00', '%H:%M:%S').time())


ElocationGUI()