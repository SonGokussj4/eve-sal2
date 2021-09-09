#!/usr/bin/env python3

import re
import typing
from tabulate import tabulate
from pathlib import Path
from borb.pdf.document import Document
from borb.pdf.pdf import PDF
from borb.toolkit.text.simple_text_extraction import SimpleTextExtraction
from tqdm import tqdm
from pprint import pprint

import plotille
import numpy as np

# X = np.sort(np.random.normal(size=1000))
# fig = plotille.Figure()
# fig.width = 60
# fig.height = 30
# fig.set_x_limits(min_=-3, max_=3)
# fig.set_y_limits(min_=-1, max_=1)
# fig.color_mode = 'byte'
# fig.plot([-0.5, 1], [-1, 1], lc=25, label='First line')
# fig.scatter(X, np.sin(X), lc=100, label='sin')
# fig.scatter(X, (X+2)**2 , lc=200, label='square')
# print(fig.show(legend=True))

import plotext as plt
from sklearn.linear_model import LinearRegression


def has_numbers(inputString):
    # inputString = inputString.replace("/", "").replace("-", "")
    inputString = re.sub(r'[hd/.,+-]', '', inputString)
    return all(char.isdigit() for char in inputString)

def fix_key(key):
    key = key.replace(" ", "")
    if key == "*Daň.sleva": return "*Daň. sleva"
    elif key == "Vojenskázdravotnípojišťovna": return "Vojenská zdravotní pojišťovna"
    elif key == "PPVprac.poměr": return "PPV prac. poměr"
    elif key == "Měsíčnímzda": return "Měsíční mzda"
    elif key == "Mzdazapřesčas": return "Mzda za přesčas"
    elif key == "Prácepřesčas25%": return "Práce přesčas 25%"
    elif key == "Prácepřesčas50%": return "Práce přesčas 50%"
    elif key == "Měs.prémiezfondu": return "Měs. prémie z fondu"
    elif key == "Paušálníodměny": return "Paušální odměny"
    elif key == "Mimořádnéodměny": return "Mimořádné odměny"
    elif key == "Výkonnostníodměny": return "Výkonnostní odměny"
    elif key == "Ročníodměny4": return "Roční odměny"
    elif key == "Ročníodměny": return "Roční odměny"
    elif key == "Cestovnínáhrady": return "Cestovní náhrady"
    elif key == "Řádnádovolená": return "Řádná dovolená"
    elif key == "Překážkynastr.prac": return "Překážky na str. prac"
    elif key == "Prostoj(É)": return "Prostoj (É)"
    elif key == "Kapitálovéživ.poj.": return "Kapitálové živ. poj."
    elif key == "Příspěveknabydlení": return "Příspěvek na bydlení"
    elif key == "DPNnemoc": return "DPN nemoc"
    elif key == "***ZÁKL.SOC.POJ.": return "***ZÁKL. SOC. POJ."
    elif key == "***ZÁKL.ZDR.POJ.": return "***ZÁKL. ZDR. POJ."
    elif key == "***HRUBÁMZDA": return "***HRUBÁ MZDA"
    elif key == "Sociálnípojištění": return "Sociální pojištění"
    elif key == "Zdravotnípojištění": return "Zdravotní pojištění"
    elif key == "Stravenkovýpaušál": return "Stravenkový paušál"
    elif key == "***POJ.ORG.KDANI": return "***POJ. ORG. K DANI"
    elif key == "***DÍLČÍZÁKL.DANĚ": return "***DÍLČÍ ZÁKL. DANĚ"
    elif key == "*Sleva-Poplatník": return "*Sleva - Poplatník"
    elif key == "*Zvýh-Dítě": return "*Zvýh - Dítě"
    elif key == "***VYPOČT.ZÁLOHA": return "***VYPOČT. ZÁLOHA"
    elif key == "*Daň.sleva": return "*Daň. sleva"
    elif key == "*Daňovásleva": return "*Daňová sleva"
    elif key == "Daňzálohová": return "Daň zálohová"
    elif key == "Daňovýbonus": return "Daňový bonus"
    elif key == "Daň(ručníkorekce)": return "Daň (ruční korekce)"
    elif key == "Bonus(ručníkorekce)": return "Bonus (ruční korekce)"
    elif key == "***ČISTÁMZDA": return "***ČISTÁ MZDA"
    elif key == "Stravnéspříspěvkem": return "Stravné s příspěvkem"
    elif key == "Evidencepůjček(Celkem0)": return "Evidence půjček (Celkem)"
    elif key == "Kompenzacekapit.poj": return "Kompenzace kapit. poj"
    elif key == "Kompenzacepř.bydl.": return "Kompenzace př. bydl."
    elif key == "PRŮMĚR(dov.)": return "PRŮMĚR (dov.)"
    elif key == "DOVOLENÁ": return "DOVOLENÁ"
    elif key == "DOVOLENÁ-zůst.": return "DOVOLENÁ - zůst."
    elif key == "Bezhotovostně": return "Bezhotovostně"

    # return f"================{key}"
    return key


def main():

    # pdfs: list[Path] = Path('.').glob("VypL*2017_1[0-2].pdf")

    # pdfs: list[Path] = [obj for obj in Path('.').glob("VypL*20*_[0][0-9].pdf")]
    # pdfs.extend([obj for obj in Path('.').glob("VypL*20*_10*.pdf")])

    pdfs: list[Path] = [obj for obj in Path('.').glob("VypL*20*.pdf")]

    files: list[str] = sorted([pdf.name for pdf in pdfs])

    headers = [
        "Měsíc",
        "Hrubá",
        "Roční odměny",
        "Bez odměn",
        "Čistá",
        "Bezhotovostně",
    ]

    table = []
    for pdf in tqdm(files, unit=" pdf", leave=False):

        doc: typing.Optional[Document] = None
        l:SimpleTextExtraction = SimpleTextExtraction()

        with open(pdf, "rb") as in_file_handle:
            doc = PDF.loads(in_file_handle, [l])

        assert doc is not None
        lines = l.get_text_for_page(0).split("\n")

        mesic = '_'.join(pdf.split('_')[1:3]).replace(".pdf", "")
        hruba_mzda = ""
        odmeny = ""
        cista_mzda = ""
        bezhotovost = ""

        dc = {}

        for line in lines:
            key = " ".join([item for item in line.split() if not has_numbers(item) and item != ":"])
            key = fix_key(key)
            value = " ".join([item for item in line.split() if has_numbers(item) and item != ":"])
            dc[key] = value

        # pprint(dc)

        # Fill dict
        hruba_mzda = dc.get("***HRUBÁ MZDA")
        odmeny = dc.get("Roční odměny")
        cista_mzda = dc.get("***ČISTÁ MZDA")
        bezhotovost = dc.get("Bezhotovostně").split()[-1]
        bez_odmen = dc["***HRUBÁ MZDA"]

        # Ignore "Roční odměny"
        if "Roční odměny" in dc.keys():
            bez_odmen = str(int(dc["***HRUBÁ MZDA"]) - int(dc["Roční odměny"]))

        # Ignore "Přesčas"
        prescasy = {key: value for key, value in dc.items() if "přesčas" in key}
        if len(prescasy) != 0:
            for key, value in prescasy.items():
                print(f'bez_odmen [{bez_odmen}] - value [{value.split()[-1]}] = {int(bez_odmen) - int(value.split()[-1])}')
                bez_odmen = str(int(bez_odmen) - int(value.split()[-1]))


        # Fill table row
        table.append([mesic, hruba_mzda, odmeny, bez_odmen, cista_mzda, bezhotovost])

    # Print table
    print(tabulate(table, headers=headers, tablefmt="psql"))

    # Plot histogram
    months = [row[0].replace(".pdf", "") for row in table]

    # hrube = [int(row[1].replace(",", "")) for row in table]
    # ciste = [int(row[3].replace(",", "")) for row in table]
    # bezhotovosti = [int(row[4].replace(",", "")) for row in table]
    bez_odmen = [int(row[3].replace(",", "")) for row in table]

    # x = np.array(range(len(months))).reshape((-1, 1))
    # y = np.array(bez_odmen)
    # model = LinearRegression().fit(x, y)
    # y_pred = model.intercept_ + model.coef_ * x

    # print(f'model.intercept_: {model.intercept_}')
    # print(f'model.coef_: {model.coef_}')

    # plt.bar(months, hrube, label="hruba")
    # plt.bar(months, ciste, label="cista")
    # plt.bar(months, bezhotovosti, label="bezhotovost")
    plt.bar(months, bez_odmen, label="bez odmen")

    # predikce = [int(row[0]) for row in y_pred]
    # print(predikce)
    # plt.plot(x, predikce, label = "predikce")

    plt.plotsize(130, 30)
    plt.title("Finance")
    plt.xlabel("Month")
    plt.ylabel("Hruba [Kč]")
    # plt.colorless()
    plt.show()




if __name__ == "__main__":
    main()

