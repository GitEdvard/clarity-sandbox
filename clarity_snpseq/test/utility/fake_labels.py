from collections import namedtuple


class FakeLabelPrinter(object):
    def __init__(self):
        self.cache = list()

    def print_bar_code_for_container(self, name=None, barcode=None):
        printout = LabelPrintout(name=name, barcode=barcode)
        self.cache.append(printout)


class LabelPrintout(namedtuple('LabelPrintout', ['name', 'barcode'])):
    pass


class LabelPrinterService(object):
    @staticmethod
    def create():
        pass


label_printer = FakeLabelPrinter()
