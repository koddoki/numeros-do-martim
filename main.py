import argparse
import cv2
import numpy as np
import os

def lade_bild(bild_pfad):
    bild = cv2.imread(bild_pfad, cv2.IMREAD_UNCHANGED)
    if bild is None:
        raise ValueError(f"Fehler: Bild konnte nicht von {bild_pfad} geladen werden")
    return bild

def teile_in_quadranten(bild):
    höhe, breite = bild.shape[:2]
    mitte_x, mitte_y = breite // 2, höhe // 2
    return [
        bild[0:mitte_y, 0:mitte_x],
        bild[0:mitte_y, mitte_x:breite],
        bild[mitte_y:höhe, 0:mitte_x],
        bild[mitte_y:höhe, mitte_x:breite]
    ]

def spiegele_quadranten(quadranten):
    return [
        cv2.flip(quadranten[0], 1),
        quadranten[1],
        cv2.flip(quadranten[2], -1),
        cv2.flip(quadranten[3], 0)
    ]


def vergleiche_bilder(bild1, bild2, schwelle=30):
    if bild1.shape != bild2.shape:
        return False
    beschnittenes_bild1 = bild1[:, 3:]
    beschnittenes_bild2 = bild2[:, 3:]
    unterschied = cv2.absdiff(beschnittenes_bild1, beschnittenes_bild2)
    _, thresh = cv2.threshold(unterschied, schwelle, 255, cv2.THRESH_BINARY)
    return np.count_nonzero(thresh) == 0


def finde_passenden_quadranten(bild_pfad, basis_ordner):
    bild = lade_bild(bild_pfad)
    quadranten = teile_in_quadranten(bild)
    gespiegelte_quadranten = spiegele_quadranten(quadranten)

    basis_bilder = []
    for dateiname in os.listdir(basis_ordner):
        basis_bild_pfad = os.path.join(basis_ordner, dateiname)
        basis_bild = lade_bild(basis_bild_pfad)
        wert = int(os.path.splitext(dateiname)[0].split('_')[1])
        basis_bilder.append((basis_bild, wert))

    gesamt_summe = 0
    quadranten_werte = [10, 1, 1000, 100]

    for i, quadrant in enumerate(gespiegelte_quadranten):
        for basis_bild, basis_wert in basis_bilder:
            if vergleiche_bilder(quadrant, basis_bild):
                gesamt_summe += basis_wert * quadranten_werte[i]

    print(f"Gesamtsumme: {gesamt_summe}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verarbeitet ein Cistercian-Zahlenbild.")
    parser.add_argument("bild_pfad", type=str, help="Pfad zum Cistercian-Zahlenbild")

    basis_ordner = 'bilde'

    args = parser.parse_args()

    finde_passenden_quadranten(args.bild_pfad, basis_ordner)
