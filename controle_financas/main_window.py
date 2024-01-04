from datetime import date

from PySide6 import QtCore, QtGui, QtWidgets
from sqlalchemy import select

from controle_financas.consts import MONTHS
from controle_financas.database import Session
from controle_financas.models import Record


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, data, headers, *args):
        super().__init__(parent, *args)
        self._data = data
        self._headers = headers

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index=None):
        return len(self._data)

    def columnCount(self, index=None):
        return len(self._data[0])

    def headerData(self, column, orientation, role):
        if orientation == QtGui.Qt.Horizontal and role == QtGui.Qt.DisplayRole:
            return self._headers[column]
        return None


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 600)
        with open("styles.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.value_label = QtWidgets.QLabel("Valor")
        self.value_input = QtWidgets.QLineEdit()
        self.value_input.setValidator(
            QtGui.QRegularExpressionValidator(r"^\d+,\d{2}$|^\d+$")
        )
        self.value_layout = QtWidgets.QHBoxLayout()
        self.value_layout.addWidget(self.value_label)
        self.value_layout.addWidget(self.value_input)

        self.record_date_label = QtWidgets.QLabel(
            "Data", alignment=QtCore.Qt.AlignmentFlag.AlignCenter
        )
        self.record_date_calendar = QtWidgets.QCalendarWidget()
        self.record_date_layout = QtWidgets.QVBoxLayout()
        self.record_date_layout.addWidget(self.record_date_label)
        self.record_date_layout.addWidget(self.record_date_calendar)

        self.add_record_button = QtWidgets.QPushButton("Adicionar Registro")
        self.add_record_button.clicked.connect(self.add_record)

        self.inputs_layout = QtWidgets.QVBoxLayout()
        self.inputs_layout.addLayout(self.value_layout)
        self.inputs_layout.addLayout(self.record_date_layout)
        self.inputs_layout.addWidget(self.add_record_button)

        self.records_table_label = QtWidgets.QLabel(
            "Registros", alignment=QtCore.Qt.AlignmentFlag.AlignCenter
        )

        self.records_year_label = QtWidgets.QLabel("Ano")
        self.records_year_combobox = QtWidgets.QComboBox()
        self.update_records_year_combobox()
        self.records_year_layout = QtWidgets.QHBoxLayout()
        self.records_year_layout.addWidget(self.records_year_label, 1)
        self.records_year_layout.addWidget(self.records_year_combobox, 4)

        self.records_month_label = QtWidgets.QLabel("Mês")
        self.records_month_combobox = QtWidgets.QComboBox()
        self.update_records_month_combobox()
        self.records_month_layout = QtWidgets.QHBoxLayout()
        self.records_month_layout.addWidget(self.records_month_label, 1)
        self.records_month_layout.addWidget(self.records_month_combobox, 4)

        self.records_table = QtWidgets.QTableView()
        self.update_records_table()
        self.records_year_combobox.currentIndexChanged.connect(
            self.update_records_table
        )
        self.records_month_combobox.currentIndexChanged.connect(
            self.update_records_table
        )

        self.records_table_layout = QtWidgets.QVBoxLayout()
        self.records_table_layout.addWidget(self.records_table_label)
        self.records_table_layout.addLayout(self.records_year_layout)
        self.records_table_layout.addLayout(self.records_month_layout)
        self.records_table_layout.addWidget(self.records_table)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.addLayout(self.inputs_layout)
        self.main_layout.addLayout(self.records_table_layout)

    @QtCore.Slot()
    def add_record(self):
        with Session() as session:
            current_date = self.record_date_calendar.selectedDate().currentDate()
            record_date = date(
                year=current_date.year(),
                month=current_date.month(),
                day=current_date.day(),
            )
            record = Record(
                value=float(self.value_input.text().replace(",", ".")),
                record_date=record_date,
            )
            session.add(record)
            session.commit()
        self.value_input.setText("")
        self.update_records_table()
        self.message_box.setText("Registro Adicionado")
        self.message_box.show()

    def update_records_year_combobox(self):
        self.records_year_combobox.clear()
        with Session() as session:
            years = []
            for record in session.scalars(select(Record)).all():
                if record.record_date.year not in years:
                    years.append(str(record.record_date.year))
            if years:
                self.records_year_combobox.addItems(years)
            else:
                self.records_year_combobox.addItem(str(date.today().year))

    def update_records_month_combobox(self):
        if self.records_year_combobox.currentText():
            year = int(self.records_year_combobox.currentText())
            months = (
                MONTHS[: date.today().month] if date.today().year == year else MONTHS
            )
            self.records_month_combobox.clear()
            self.records_month_combobox.addItems(months)

    def update_records_table(self):
        headers = ["Valor", "Data"]
        data = []
        with Session() as session:
            for record in session.scalars(select(Record)).all():
                if (
                    str(record.record_date.year)
                    == self.records_year_combobox.currentText()
                    and record.record_date.month
                    == self.records_month_combobox.currentIndex()
                ):
                    data.append([record.value, record.record_date])
        if not data:
            data = [["" for _ in headers]]
        self.records_table.setModel(TableModel(self, data, headers))
