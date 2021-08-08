import math

brackets = {"Senior": [300000, 500000, 1000000, 1000001]}
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
            print("bigi=", bigi, "diff = ", diff)

            break
        else:
            bigi = len(brackets.get(bracket)) - 1
            diff = temp - brackets.get(bracket)[bigi]

    # Adding all taxes before that range
    for i in range(bigi):
        tax += helperb.get(bracket)[i]
        print("tax helper = ", tax)

    # Remaining taxable amount
    tax += diff * 0.01 * ratesb.get(bracket)[bigi]
    print("tax remain = ", tax, "rate=", ratesb.get(bracket)[bigi], diff)

    return tax


# bracket = "Senior"
# print("tax = ", itC(740500, bracket))

from datetime import date, datetime


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

    m1 = int(str((d2 - d1))[0:3]) // 30
    ob1 = nodInM(d1.year, d1.month)
    ob2 = nodInM(d2.year, d2.month)
    m2 = (ob1 - int(str(d1.day)) + 1) / ob1
    m3 = (ob2 - int(str(d2.day))) / ob1
    return m1 + m2 + m3, m1


d1 = date(2021, 4, 12)
d2 = date(2022, 2, 28)
# print(getMonths(d1, d2))


def monthlist_fast(dates):
    start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
    total_months = lambda dt: dt.month + 12 * dt.year
    mlist = []
    for tot_m in range(total_months(start) - 1, total_months(end)):
        y, m = divmod(tot_m, 12)
        mlist.append(datetime(y, m + 1, 1).strftime("%b-%y"))
    return mlist


def strd(d1):
    return f"{d1.year}-{d1.month}-{d1.day}"


ml = monthlist_fast([strd(d1), strd(d2)])
bracket = "Senior"
wrkM, fullM = getMonths(d1, d2)
ysal = 1200000
msal = 1200000 / 12
taxin = wrkM * ysal / 12
print(taxin, wrkM)
nettaxin = taxin - 50000
ity = itC(nettaxin, bracket)
itm = ity // fullM


ycess = 0.04 * ity
mcess = ycess // fullM

import pandas as pd

# TODO: Update for partial months
df = pd.DataFrame()
df["Months"] = ml
df["Honoraium"] = [msal for i in range(len(ml))]
df["Monthly IT"] = [itm for i in range(len(ml))]
df["Monthly Cess"] = [mcess for i in range(len(ml))]
df["Total M Tax"] = df["Monthly IT"] + df["Monthly Cess"]
df["Net Pay"] = df["Honoraium"] - df["Total M Tax"]

print(df)
