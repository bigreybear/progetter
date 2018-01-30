import xlwt
import pickle
import copy

class ExcelWriter:
    def __init__(self, src_file):
        self.coord_index = {}
        self.index_num = 0
        self.wbk = None
        self.sheet = None
        with open(src_file, "rb") as _f:
            self.src_list = copy.deepcopy(pickle.load(_f))
        if len(self.src_list) == 0:
            print "The list is too short, plz make sure you get right file."
        else:
            self.init_coordination()

    def init_coordination(self):
        first_dict = self.src_list[0]
        for key in first_dict:
            self.coord_index[key] = self.index_num
            self.index_num += 1

    def modify_coordination(self, new_key):
        self.coord_index[new_key] = self.index_num
        self.index_num += 1
        self.sheet.write(0, self.index_num-1, new_key)

    def write_excel(self, filename):
        self.wbk = xlwt.Workbook()
        row_count = 1
        self.sheet = self.wbk.add_sheet('sheet1')
        for old_key in self.coord_index:
            self.sheet.write(0, self.coord_index[old_key], old_key)

        for a_row in self.src_list:
            for a_key in a_row:
                if a_key not in self.coord_index:
                    self.modify_coordination(a_key)
                self.sheet.write(row_count, self.coord_index[a_key], a_row[a_key])
            row_count += 1
        self.wbk.save(filename)


if __name__ == '__main__':
    ew = ExcelWriter("1988-2018NAS.bin")
    ew.write_excel("NAS1988-2018.xls")