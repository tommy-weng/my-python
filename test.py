# -*- coding: utf-8 -*-

def choose_cores_for_tti_trace_gathering_for_both_directions(cell_number=1, is_nb_iot=0):

    if not isinstance(cell_number, list):
        cell_number = range(cell_number)
    result = {}
    print cell_number
    for cell in cell_number:
        cell= int(cell)
        print cell
        #tti_trace_core_num = self.ta_dev_wro1.get_cpu_address_for_tti_traces(cell, "both", is_nb_iot)
        #result[cell] = tti_trace_core_num

    return result

if __name__ == '__main__':
    print choose_cores_for_tti_trace_gathering_for_both_directions(2,0)