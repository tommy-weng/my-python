from excel_proxy import Excel

class Recorder:
    def __init__(self, fname):
        self.excel = Excel(fname)
        self.line = 0

    def __del__(self):
        self.excel.close()

    def write(self, contents):
        for i in range(0, len(contents)):
            self.excel.write(i, self.line, contents[i])
        self.line += 1
