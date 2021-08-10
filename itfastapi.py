from fastapi import FastAPI
from pydantic import BaseModel

# To Run server
# uvicorn itfastapi:app --reload

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Details(BaseModel):
    msal: int
    d1: str
    d2: str
    cat: int


@app.post("/ITC/")
async def root(details: Details):
    msal = details.msal
    d1 = details.d1[4:15]
    d2 = details.d2[4:15]
    cat = details.cat
    ds = datetime.strptime(d1, "%b %d %Y").date()
    de = datetime.strptime(d2, "%b %d %Y").date()
    tm, wm, mh1, mh2, ml = getMonths(ds, de)
    taxin = tm * msal
    nettaxin = taxin - 50000
    stddec = 50000
    honoC = honmon(msal, tm).to_html()
    # Taxable Income and Standard Deduction Chart
    taxin_stdC = taxin_stddec(taxin, stddec, nettaxin).to_html()

    ity, dfIT = itC(nettaxin, taxslab[cat])

    # Tax Slabs Chart
    tax_slabC = dfIT.to_html()

    itm = round(ity / wm)
    ycess = 0.04 * ity
    mcess = round(ycess / wm)

    cessC = f"<p>Health and Education CESS @4% on IT {round(ycess)}</p>"

    disC = distribute(msal, itm, mcess, ml, mh1, mh2).to_html()

    return honoC + taxin_stdC + tax_slabC + cessC + disC


import pandas as pd
from datetime import date, datetime
import math

taxslab = ["Senior"]
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
