from datetime import date, datetime
from pathlib import Path

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


class KeyPressFilter(QtCore.QObject):
    def eventFilter(self, widget, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == 16777220:
                self.parent().add_record_button.click()
        return False


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 600)
        self.setWindowTitle('Controle finanças')
        with open(Path(__file__).parent.parent / 'styles.qss', 'r') as f:
            self.setStyleSheet(f.read())

        self.message_box = QtWidgets.QMessageBox()

        self.value_label = QtWidgets.QLabel('Valor R$')
        self.value_input = QtWidgets.QLineEdit()
        self.value_input.eventFilter = KeyPressFilter(self)
        self.value_input.installEventFilter(self.value_input.eventFilter)
        self.value_input.setValidator(
            QtGui.QRegularExpressionValidator(r'^\d+,\d{2}$|^\d+$')
        )
        self.value_layout = QtWidgets.QHBoxLayout()
        self.value_layout.addWidget(self.value_label)
        self.value_layout.addWidget(self.value_input)

        self.record_date_label = QtWidgets.QLabel(
            'Data', alignment=QtCore.Qt.AlignmentFlag.AlignCenter
        )
        self.record_date_calendar = QtWidgets.QCalendarWidget()
        self.record_date_calendar.setVerticalHeaderFormat(
            QtWidgets.QCalendarWidget.NoVerticalHeader
        )
        self.record_date_layout = QtWidgets.QVBoxLayout()
        self.record_date_layout.addWidget(self.record_date_label)
        self.record_date_layout.addWidget(self.record_date_calendar)

        self.add_record_button = QtWidgets.QPushButton('Adicionar Registro')
        self.add_record_button.clicked.connect(self.add_record)

        self.inputs_layout = QtWidgets.QVBoxLayout()
        self.inputs_layout.addLayout(self.value_layout)
        self.inputs_layout.addLayout(self.record_date_layout)
        self.inputs_layout.addWidget(self.add_record_button)

        self.records_table_label = QtWidgets.QLabel(
            'Registros', alignment=QtCore.Qt.AlignmentFlag.AlignCenter
        )

        self.records_year_label = QtWidgets.QLabel('Ano')
        self.records_year_combobox = QtWidgets.QComboBox()
        self.update_records_year_combobox()
        self.records_year_layout = QtWidgets.QHBoxLayout()
        self.records_year_layout.addWidget(self.records_year_label, 1)
        self.records_year_layout.addWidget(self.records_year_combobox, 4)

        self.records_month_label = QtWidgets.QLabel('Mês')
        self.records_month_combobox = QtWidgets.QComboBox()
        self.update_records_month_combobox()
        self.records_month_layout = QtWidgets.QHBoxLayout()
        self.records_month_layout.addWidget(self.records_month_label, 1)
        self.records_month_layout.addWidget(self.records_month_combobox, 4)

        self.records_table = QtWidgets.QTableView()
        self.update_records_table()
        self.records_table.setColumnHidden(0, True)
        self.records_year_combobox.currentIndexChanged.connect(
            self.update_records_table
        )
        self.records_month_combobox.currentIndexChanged.connect(
            self.update_records_table
        )

        self.total_label = QtWidgets.QLabel(
            'Total: ', alignment=QtCore.Qt.AlignmentFlag.AlignCenter
        )
        self.total_label.setStyleSheet('font-weight: bold;')
        self.update_total_label()

        self.mean_label = QtWidgets.QLabel(
            'Média: ', alignment=QtCore.Qt.AlignmentFlag.AlignCenter
        )
        self.mean_label.setStyleSheet('font-weight: bold;')
        self.update_mean_label()

        self.records_table_data_labels_layout = QtWidgets.QHBoxLayout()
        self.records_table_data_labels_layout.addWidget(self.total_label)
        self.records_table_data_labels_layout.addWidget(self.mean_label)

        self.remove_record_button = QtWidgets.QPushButton('Remover Registros')
        self.remove_record_button.clicked.connect(self.remove_records)

        self.records_table_layout = QtWidgets.QVBoxLayout()
        self.records_table_layout.addWidget(self.records_table_label)
        self.records_table_layout.addLayout(self.records_year_layout)
        self.records_table_layout.addLayout(self.records_month_layout)
        self.records_table_layout.addWidget(self.records_table)
        self.records_table_layout.addLayout(self.records_table_data_labels_layout)
        self.records_table_layout.addWidget(self.remove_record_button)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.addLayout(self.inputs_layout)
        self.main_layout.addLayout(self.records_table_layout)

    @QtCore.Slot()
    def add_record(self):
        if self.value_input.text():
            with Session() as session:
                current_date = self.record_date_calendar.selectedDate()
                record_date = date(
                    year=current_date.year(),
                    month=current_date.month(),
                    day=current_date.day(),
                )
                record = Record(
                    value=float(self.value_input.text().replace(',', '.')),
                    record_date=record_date,
                )
                session.add(record)
                session.commit()
            self.value_input.setText('')
            self.update_records_year_combobox()
            self.update_records_month_combobox()
            self.update_records_table()
            self.update_total_label()
            self.update_mean_label()
            self.message_box.setText('Registro Adicionado')
        else:
            self.message_box.setText('Preencha o Valor')
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

    def update_records_month_combobox(self):
        self.records_month_combobox.clear()
        if self.records_year_combobox.currentText():
            year = int(self.records_year_combobox.currentText())
            months = []
            with Session() as session:
                for record in session.scalars(select(Record)).all():
                    if (
                        record.record_date.year == year
                        and MONTHS[record.record_date.month - 1] not in months
                    ):
                        months.append(MONTHS[record.record_date.month - 1])
            self.records_month_combobox.clear()
            self.records_month_combobox.addItems(months)

    def update_records_table(self):
        headers = ['ID', 'Valor', 'Data']
        data = []
        with Session() as session:
            for record in session.scalars(select(Record)).all():
                if (
                    str(record.record_date.year)
                    == self.records_year_combobox.currentText()
                    and MONTHS[record.record_date.month - 1]
                    == self.records_month_combobox.currentText()
                ):
                    data.append(
                        [
                            record.id,
                            f'R$ {record.value:.2f}'.replace('.', ','),
                            record.record_date.strftime('%d/%m/%Y'),
                        ]
                    )
        if not data:
            data = [['' for _ in headers]]
        else:
            data.sort(key=lambda r: datetime.strptime(r[2], '%d/%m/%Y'))
        self.records_table.setModel(TableModel(self, data, headers))

    def update_total_label(self):
        total = 0
        with Session() as session:
            for row in self.records_table.model()._data:
                try:
                    record = session.get(Record, int(row[0]))
                    total += record.value
                except ValueError:
                    continue
        self.total_label.setText(f'Total: R$ {total:.2f}'.replace('.', ','))

    def update_mean_label(self):
        values = []
        with Session() as session:
            for row in self.records_table.model()._data:
                try:
                    record = session.get(Record, int(row[0]))
                    values.append(record.value)
                except ValueError:
                    continue
        try:
            self.mean_label.setText(f'Média: R$ {sum(values) / date.today().day:.2f}'.replace('.', ','))
        except ZeroDivisionError:
            self.mean_label.setText(f'Média: R$ 0,00')

    @QtCore.Slot()
    def remove_records(self):
        with Session() as session:
            for index in self.records_table.selectedIndexes():
                record = session.get(
                    Record, self.records_table.model()._data[index.row()][0]
                )
                if record:
                    session.delete(record)
                    session.commit()
        self.update_records_year_combobox()
        self.update_records_month_combobox()
        self.update_records_table()
        self.update_total_label()
        self.update_mean_label()
        self.message_box.setText('Registro(s) Removido(s)')
        self.message_box.show()
