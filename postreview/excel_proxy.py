from openpyxl import Workbook

class Excel:
  def __init__(self, fname):
    self.workbook = Workbook()
    self.worksheet = self.workbook.active
    self.fname = fname
  def write(self, col, row, content):
    self.worksheet[chr(ord('A') + col) + str(row + 1)] = content
  def close(self):
    self.workbook.save(self.fname)
