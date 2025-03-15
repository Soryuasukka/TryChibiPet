import sys
from PyQt5.QtWidgets import QApplication
from pet_widget import DesktopPet

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec_())