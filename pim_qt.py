def main_gui():
    app = QApplication(sys.argv)

    w = QWidget(flags=0)
    w.resize(1000, 600)
    w.move(100, 100)
    w.setWindowTitle('Simple')
    w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main_gui()
