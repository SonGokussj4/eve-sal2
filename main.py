#!/usr/bin/env python3

import typing
from tabulate import tabulate
from pathlib import Path
from borb.pdf.document import Document
from borb.pdf.pdf import PDF
from borb.toolkit.text.simple_text_extraction import SimpleTextExtraction


def main():

    pdfs: list[str] = Path('.').glob("VypL*2017*[0][1-3].pdf")
    files = sorted([pdf.name for pdf in pdfs])

    headers = [
        "Měsíc",
        "Hrubá",
        "Čistá",
        "Bezhotovostně",
    ]

    table = []
    for pdf in files:
        doc: typing.Optional[Document] = None
        l:SimpleTextExtraction = SimpleTextExtraction()

        with open(pdf, "rb") as in_file_handle:
            doc = PDF.loads(in_file_handle, [l])

        assert doc is not None
        lines = l.get_text_for_page(0).split("\n")

        mesic = '_'.join(pdf.split('_')[1:3])
        hruba_mzda = ""
        cista_mzda = ""
        bezhotovost = ""

        for line in lines:

            if "***HR" in line:
                hruba_mzda = int(line.split()[-2])
                hruba_mzda = f"{hruba_mzda:,d}"

            if "***ČI" in line:
                cista_mzda = int(line.split()[-2])
                cista_mzda = f"{cista_mzda:,d}"

            if "Bezhotovost" in line:
                bezhotovost = int(line.split()[-2])
                bezhotovost = f"{bezhotovost:,d}",

        # print(f"{'_'.join(pdf.split('_')[1:3])} -> {hruba_mzda:,d} {cista_mzda:,d} {bezhotovost:,d}")
        # print(f"{'_'.join(pdf.split('_')[1:3])} -> ")

        table.append([mesic, hruba_mzda, cista_mzda, bezhotovost])

    # Print table
    print(tabulate(table, headers=headers, tablefmt="psql"))





if __name__ == "__main__":
    main()

