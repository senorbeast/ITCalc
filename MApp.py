import pandas as pd
from datetime import date, datetime
import math

brackets = {"Senior": [300000, 500000, 1000000, 1000001]}
bracname = {
    "Senior": [
        "Upto 300000/-",
        "3,00,001 to 5,00,000/-",
        "5,00,001 to 10,00,000/-",
        "above 10,00,001/-",
    ]
}
helperb = {"Senior": [0, 10000, 100000]}
ratesb = {"Senior": [0, 5, 20, 30]}


def itC(amount, bracket):
    tax = 0
    temp = amount
    bigi = 0
    diff = 0
    # Determining the range
    for i in range(len(brackets.get(bracket))):
        if temp <= brackets.get(bracket)[i]:
            bigi = i
            diff = temp - brackets.get(bracket)[max(i - 1, 0)]
            # print("bigi=", bigi, "diff = ", diff)

            break
        else:
            bigi = len(brackets.get(bracket)) - 1
            diff = temp - brackets.get(bracket)[bigi]

    # Adding all taxes before that range
    for i in range(bigi):
        tax += helperb.get(bracket)[i]
    # print("Tax from helper = ", tax)

    # Remaining taxable amount
    remtax = diff * 0.01 * ratesb.get(bracket)[bigi]
    tax += remtax

    # bigi is the i on the range of amount
    # print(
    #     "Yearly Tax =",
    #     round(tax),
    #     "rate =",
    #     ratesb.get(bracket)[bigi],
    #     " That remain tax =",
    #     diff * 0.01 * ratesb.get(bracket)[bigi],
    # )
    # print(
    #     bigi,
    #     ratesb.get(bracket)[bigi],
    #     print([ratesb.get(bracket)[i] for i in range(bigi)]),
    #     "bigi",
    # )
    data = [
        {
            "1": f"{brackets.get(bracket)[i]} - {brackets.get(bracket)[i-1]}"
            if (ratesb.get(bracket)[i])
            else "",
            "2": brackets.get(bracket)[i] - brackets.get(bracket)[i - 1]
            if (ratesb.get(bracket)[i])
            else "",
            "3": helperb.get(bracket)[i],
        }
        for i in range(bigi)
    ]
    # Last Row of Tax Slabs Calc
    data2 = [
        {
            "1": f"{round(amount)} - {brackets.get(bracket)[bigi - 1]}"
            if (ratesb.get(bracket)[i] > 0)
            else f"{round(amount)}",
            "2": math.ceil(diff)
            if (ratesb.get(bracket)[i] > 0)
            else f"{round(amount)}",
            "3": round(remtax),
        }
    ]
    # 1st column of Tax Slabs
    ind = [f"{bracname.get(bracket)[i]}" for i in range(bigi + 1)]
    df = pd.DataFrame(data + data2, index=ind)

    df.insert(0, "Rates", value=[f"{ratesb.get(bracket)[i]}%" for i in range(bigi + 1)])

    df.loc[len(df.index)] = [
        "",
        "",
        "",
        sum(df["3"]),
    ]

    df.index = ind + ["Income Tax"]
    return tax, df


def getMonths(d1, d2):
    def nodInM(y, m):
        leap = 0
        if y % 400 == 0:
            leap = 1
        elif y % 100 == 0:
            leap = 0
        elif y % 4 == 0:
            leap = 1
        if m == 2:
            return 28 + leap
        list = [1, 3, 5, 7, 8, 10, 12]
        if m in list:
            return 31
        return 30

    def monthlist_fast(dates):
        start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
        total_months = lambda dt: dt.month + 12 * dt.year
        mlist = []
        for tot_m in range(total_months(start) - 1, total_months(end)):
            y, m = divmod(tot_m, 12)
            mlist.append(datetime(y, m + 1, 1).strftime("%b-%y"))
        return mlist

    def strd(d):
        return f"{d.year}-{d.month}-{d.day}"

    ml = monthlist_fast([strd(d1), strd(d2)])
    wmm = len(ml) - 2
    ob1 = nodInM(d1.year, d1.month)
    ob2 = nodInM(d2.year, d2.month)
    mh1 = (ob1 - int(str(d1.day)) + 1) / ob1
    mh2 = (int(str(d2.day))) / ob2
    wm2 = 0
    # print("Half month1 =", mh1, "Half month2 =", mh2)
    if int(mh1) == 1:
        wm2 += 1
    if int(mh2) == 1:
        wm2 += 1
    # print(
    #     "Total WM =",
    #     wmm + mh1 + mh2,
    #     "Whole Middle Months =",
    #     wmm,
    #     "Whole Months =",
    #     wmm + wm2,
    # )
    return (
        wmm + mh1 + mh2,
        wmm + wm2,
        [mh1, d1.month, d1.year],
        [mh2, d2.month, d2.year],
        ml,
    )


def distribute(msal, itm, mcess, ml, mh1, mh2):
    df = pd.DataFrame()
    df["Months"] = ml
    df["Honorarium"] = [msal for i in range(len(ml))]
    df["Monthly IT"] = [itm for i in range(len(ml))]
    df["Monthly Cess"] = [mcess for i in range(len(ml))]
    df["Total M Tax"] = df["Monthly IT"] + df["Monthly Cess"]
    df["Net Pay"] = df["Honorarium"] - df["Total M Tax"]

    # TODO: Update for partial months
    if mh1[0] > 0 and mh1[0] < 1:
        df.loc[
            df.index[
                df["Months"] == (f"{datetime(mh1[2], mh1[1], 1).strftime('%b-%y')}")
            ]
        ] = [
            f"{datetime(mh1[2], mh1[1], 1).strftime('%b-%y')}",
            round(mh1[0] * msal),
            0,
            0,
            0,
            round(mh1[0] * msal),
        ]
    if mh2[0] > 0 and mh2[0] < 1:
        df.loc[
            df.index[
                df["Months"] == (f"{datetime(mh2[2], mh2[1], 1).strftime('%b-%y')}")
            ]
        ] = [
            f"{datetime(mh2[2], mh2[1], 1).strftime('%b-%y')}",
            round(mh2[0] * msal),
            0,
            0,
            0,
            round(mh2[0] * msal),
        ]

    # Total Row (the bottom row)
    df.loc[len(df.index)] = [
        "Total",
        sum(df["Honorarium"]),
        sum(df["Monthly IT"]),
        sum(df["Monthly Cess"]),
        sum(df["Total M Tax"]),
        sum(df["Net Pay"]),
    ]
    df.index = [x + 1 for x in range(len(df.index))]
    return df


def honmon(msal, tm):
    fractional, whole = math.modf(tm)

    data = [
        {"1": msal, "2": msal},
        {"1": whole, "2": round(fractional, 2)},
        {"1": whole * msal, "2": round(fractional * msal, 2)},
    ]
    df = pd.DataFrame(
        data,
        index=[
            f"Honorarium Rs.{msal}/- pm",
            "No. of months and days(in m)",
            f"Honorarium per month @{msal}",
        ],
    )

    return df


def taxin_stddec(taxin, stddec, nettaxin):
    data = [
        {"1": round(taxin)},
        {"1": round(stddec)},
        {"1": round(nettaxin)},
    ]
    df = pd.DataFrame(
        data,
        index=[
            "Taxable Income",
            "(-) Standard Deduction",
            "Net Taxable Income",
        ],
    )
    return df


def pdtolisttup(df):
    honrow = df.to_records(index=True)
    rows = list(honrow)
    cols = list(df.columns.values)
    return rows, cols


# But in kv file root should be used, to refer root object
KV = """
ScreenManager:
    MainScreen:
        name: 'main_screen'
    DTScreen:
        name: 'dt_screen'
<MainScreen>:
    # adaptive_height: True
    # adaptive_size: True
    #md_bg_color: app.theme_cls.primary_color
    MDToolbar:
        title: "IT Calculator"
        type:"top"
    ScrollView:
        height: root.height
        spacing:20
        MDList:
            padding: [25, 80, 25, 25] 
            halign: "center"
            valign: "center"
            spacing:40
            MDTextField:
                id:input
                hint_text: "Monthly Salary"
                helper_text: "No Commas Please"
                helper_text_mode: "on_focus"
                text: "100000"
                on_text: app.process()
            MDGridLayout:
                cols:3
                MDLabel:
                    text: "Dates:"
                MDLabel:
                    text: app.startd
                MDLabel:
                    text: app.endd
            MDGridLayout:
                cols:3
                MDRaisedButton:
                    text: "Start Date"
                    # pos_hint: {'center_x': .5, 'center_y': .5}
                    on_release: app.show_date_pickerS()
                MDRaisedButton:
                    text: "Last Date"
                    # pos_hint: {'center_x': .5, 'center_y': .5}
                    on_release: app.show_date_pickerE()

            MDGridLayout:
                cols:2
                spacing:20
                MDRaisedButton:
                    id: button
                    text: "Select Tax Slab"
                    # pos_hint: {"center_x": .5, "center_y": .5}
                    on_release: app.menu.open()
                    
                MDLabel:
                    text: app.taxslab
            MDLabel:
                text: " "
            MDGridLayout:
                cols:1
                spacing:60
                MDFillRoundFlatIconButton:
                    md_bg_color: 0, 0.3, 0.3, 1
                    halign: "center"
                    valign: "center"
                    spacing: 80 
                    icon: "android"
                    text: "Calculate Everthing Income Tax, Distribution"
                    on_press: 
                        app.itcalc()
                        root.manager.transition.direction = 'left'
                        root.manager.current = 'dt_screen'
<DTScreen>:
    MDGridLayout:
        cols:1
        MDRaisedButton:
            text: "Edit Options"
            # background_color : 1, 0, 0, 1
            on_press:
                root.manager.transition.direction = 'right'
                root.manager.current = 'main_screen'
        ScrollView:
            do_scroll_x: True
            do_scroll_y: True
            MDLabel:
                valign: 'center'
                halign: 'center'
                size_hint_y: None
                size_hint_x: None
                text_size: 900, 1500
                height: 1500
                width: 900
                text: app.calcd

"""

from kivy.lang import Builder
from kivymd.uix.picker import MDDatePicker
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import StringProperty, NumericProperty
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import (
    ScreenManager,
    Screen,
    NoTransition,
    SlideTransition,
    CardTransition,
    SwapTransition,
    FadeTransition,
    WipeTransition,
    FallOutTransition,
    RiseInTransition,
)


class DTScreen(Screen):
    pass


class MainScreen(Screen):
    pass


class MainApp(MDApp):
    startd = StringProperty()
    endd = StringProperty()
    calcd = StringProperty()
    monsal = NumericProperty()
    taxslab = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calcd = "Enter data"
        self.startd = str(date(2021, 1, 1))
        self.endd = str(date(2022, 1, 1))
        self.manager = Builder.load_string(KV)
        self.monsal = 100000
        self.taxslab = "Senior"
        menu_items = [
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.menu_callback(x),
            }
            for i in ["Senior"]
        ]
        # Needed to use self.manager as we are in __init__ and self.root is defined after init
        self.menu = MDDropdownMenu(
            caller=self.manager.get_screen("main_screen").ids.button,
            items=menu_items,
            width_mult=4,
        )

    # def on_start(self):
    #     self.fps_monitor_start()

    def menu_callback(self, text_item):
        self.taxslab = text_item

    def on_saveS(self, instance, value, date_range):
        # print(date_range)
        self.startd = str(value)

    def on_cancelS(self, instance, value):
        """Events called when the "CANCEL" dialog box button is clicked."""
        self.startd = self.startd or str(date(2021, 1, 1))

    def on_saveE(self, instance, value, date_range):
        # print(date_range)
        self.endd = str(value)

    def on_cancelE(self, instance, value):
        """Events called when the "CANCEL" dialog box button is clicked."""
        self.endd = self.endd or str(date(2022, 1, 1))

    def show_date_pickerS(self):
        date_dialog = MDDatePicker(
            min_year=2020, max_year=2030, year=2021, month=1, day=1
        )
        date_dialog.bind(on_save=self.on_saveS, on_cancel=self.on_cancelS)
        date_dialog.open()

    def show_date_pickerE(self):
        date_dialog = MDDatePicker(
            min_year=2020, max_year=2030, year=2022, month=1, day=1
        )
        date_dialog.bind(on_save=self.on_saveE, on_cancel=self.on_cancelE)
        date_dialog.open()

    def itcalc(self):
        d1 = datetime.strptime(self.startd, "%Y-%m-%d").date() or date(2021, 1, 1)
        d2 = datetime.strptime(self.endd, "%Y-%m-%d").date() or date(2022, 1, 1)
        tm, wm, mh1, mh2, ml = getMonths(d1, d2)
        msal = self.monsal or 0
        self.calcd = f"The dates are {self.startd} to {self.endd}\n\n"
        self.calcd += "\n\n"
        self.calcd += f"Monthly salary={self.monsal}\n\n"
        self.calcd += "\n\n"
        self.calcd += honmon(msal, tm).to_string(col_space=25)
        taxin = tm * msal
        nettaxin = taxin - 50000
        stddec = 50000
        # Taxable Income and Standard Deduction Chart
        self.calcd += "\n\n"
        self.calcd += "\n\n"
        self.calcd += taxin_stddec(taxin, stddec, nettaxin).to_string(col_space=25)
        ity, dfIT = itC(nettaxin, self.taxslab)
        self.calcd += "\n\n"
        self.calcd += "\n\n"
        # Tax Slabs Chart
        self.calcd += dfIT.to_string(col_space=25)
        itm = round(ity / wm)
        ycess = 0.04 * ity
        mcess = round(ycess / wm)
        self.calcd += "\n\n"
        self.calcd += "\n\n"
        self.calcd += f"Health and Education CESS @4% on IT {round(ycess)}"
        self.calcd += "\n\n"
        self.calcd += "\n\n"
        self.calcd += distribute(msal, itm, mcess, ml, mh1, mh2).to_string(col_space=25)
        self.calcd += "\n\n"
        self.calcd += "\n\n"

    def process(self):
        # here self.manager and self.root both work as
        # its after __init__ (intialization)
        # self.root is defined
        self.monsal = self.root.get_screen("main_screen").ids.input.text

    def build(self):
        return self.manager


if __name__ == "__main__":
    MainApp().run()
