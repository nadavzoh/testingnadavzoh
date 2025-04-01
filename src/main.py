import sys
from argparse import ArgumentParser
from PyQt5.QtWidgets import QApplication
from Lotus import Lotus

def parse_args():
    parser = ArgumentParser(description="Lotus GUI")
    parser.add_argument("-fub", "--fub", help="FUB name", required=True, type=str)
    parser.add_argument("-spice", "--spice", help="Path to SPICE file", required=True, type=str)

    parser.add_argument("-af", "--af", help="Path to AF DCFG file", required=True, type=str)
    parser.add_argument("-mutex", "--mutex", help="Path to mutex file", required=True, type=str)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    app = QApplication(sys.argv)
    main_window = Lotus(fub=args.fub, spice=args.spice, af=args.af, mutex=args.mutex)
    main_window.show()
    sys.exit(app.exec_())

