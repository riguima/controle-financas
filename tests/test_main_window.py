from datetime import date

import pytest
from PySide6 import QtCore
from sqlalchemy import select

from controle_financas.database import Session, db
from controle_financas.main_window import MainWindow
from controle_financas.models import Base, Record


@pytest.fixture(scope='function')
def session():
    Base.metadata.drop_all(db)
    Base.metadata.create_all(db)
    return Session()


def test_add_record(qtbot, session):
    widget = MainWindow()
    qtbot.addWidget(widget)
    widget.value_input.setText('50,00')
    widget.add_record_button.click()
    record = session.scalars(select(Record)).first()
    assert record.value == 50
    assert record.record_date == date.today()
    assert widget.message_box.isVisible()


def test_add_record_with_another_date(qtbot, session):
    widget = MainWindow()
    qtbot.addWidget(widget)
    widget.value_input.setText('100,50')
    widget.record_date_calendar.setSelectedDate(QtCore.QDate(2023, 4, 15))
    widget.add_record_button.click()
    record = session.scalars(select(Record)).first()
    assert record.value == 100.50
    assert record.record_date == date(year=2023, month=4, day=15)
    assert widget.message_box.isVisible()


def test_add_record_with_empty_value(qtbot, session):
    widget = MainWindow()
    qtbot.addWidget(widget)
    widget.add_record_button.click()
    assert not session.scalars(select(Record)).all()
    assert widget.message_box.isVisible()


def test_records_comboboxes(qtbot, session):
    widget = MainWindow()
    qtbot.addWidget(widget)
    assert widget.records_year_combobox.count() == 0
    assert widget.records_month_combobox.count() == 0


def test_records_comboboxes_with_record(qtbot, session):
    widget = MainWindow()
    qtbot.addWidget(widget)
    widget.value_input.setText('25')
    widget.record_date_calendar.setSelectedDate(QtCore.QDate(2023, 12, 12))
    widget.add_record_button.click()
    years = [
        widget.records_year_combobox.itemText(index)
        for index in range(widget.records_year_combobox.count())
    ]
    months = [
        widget.records_month_combobox.itemText(index)
        for index in range(widget.records_month_combobox.count())
    ]
    assert years == ['2023']
    assert months == ['Dezembro']


def test_records_table(qtbot, session):
    widget = MainWindow()
    qtbot.addWidget(widget)
    assert widget.records_table.model()._data == [
        ['' for _ in widget.records_table.model()._headers]
    ]


def test_records_table_with_records(qtbot, session):
    widget = MainWindow()
    qtbot.addWidget(widget)
    widget.value_input.setText('100,50')
    widget.record_date_calendar.setSelectedDate(QtCore.QDate(2023, 4, 15))
    widget.add_record_button.click()
    widget.value_input.setText('25')
    widget.record_date_calendar.setSelectedDate(QtCore.QDate(2023, 4, 12))
    widget.add_record_button.click()
    assert widget.records_table.model()._data == [
        [2, 'R$ 25,00', '12/04/2023'],
        [1, 'R$ 100,50', '15/04/2023'],
    ]


def test_remove_records(qtbot, session):
    widget = MainWindow()
    qtbot.addWidget(widget)
    widget.value_input.setText('100,50')
    widget.record_date_calendar.setSelectedDate(QtCore.QDate(2023, 4, 15))
    widget.add_record_button.click()
    widget.value_input.setText('25')
    widget.record_date_calendar.setSelectedDate(QtCore.QDate(2023, 4, 12))
    widget.add_record_button.click()
    widget.records_table.selectRow(1)
    widget.remove_record_button.click()
    assert widget.records_table.model()._data == [
        [2, 'R$ 25,00', '12/04/2023'],
    ]
    assert widget.message_box.isVisible()
    widget.records_table.selectRow(0)
    widget.remove_record_button.click()
    assert widget.records_table.model()._data == [
        ['' for _ in widget.records_table.model()._headers]
    ]
    assert widget.message_box.isVisible()


def test_total_label(qtbot, session):
    widget = MainWindow()
    qtbot.addWidget(widget)
    assert widget.total_label.text() == 'Total: R$ 0,00'
    widget.value_input.setText('100,50')
    widget.add_record_button.click()
    assert widget.total_label.text() == 'Total: R$ 100,50'
    widget.records_table.selectRow(0)
    widget.remove_record_button.click()
    assert widget.total_label.text() == 'Total: R$ 0,00'


def test_mean_label(qtbot, session):
    widget = MainWindow()
    qtbot.addWidget(widget)
    assert widget.mean_label.text() == 'Média: R$ 0,00'
    widget.value_input.setText('100,50')
    widget.add_record_button.click()
    widget.value_input.setText('57,00')
    widget.add_record_button.click()
    assert widget.mean_label.text() == 'Média: R$ 78,75'
