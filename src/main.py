import sys
from argparse import ArgumentParser
from PyQt5.QtWidgets import QApplication
from Lotus import Lotus

def parse_args():
    parser = ArgumentParser(description="Lotus GUI")
    parser.add_argument("-fub", "--fub", help="FUB name", required=True, type=str)
    parser.add_argument("-spice", "--spice", help="Path to <FUB>.sp file", required=False, type=str)

    parser.add_argument("-af", "--af", help="Path to <FUB>.af.dcfg file", required=False, type=str)
    parser.add_argument("-mutex", "--mutex", help="Path to <FUB>.mutex.dcfg file", required=False, type=str)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    app = QApplication(sys.argv)
    main_window = Lotus()
    main_window.show()
    sys.exit(app.exec_())

