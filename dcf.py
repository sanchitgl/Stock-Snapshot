import pandas as pd
import numpy as np
import math

def compound(p,r):   
    amt = p * (1 + (r/100))
    return amt

def DCFvalue(x, gr1_3, gr4_6, gr7_9, ter_rate, discount):
    amt_1 = (x[-3]+x[-2]+x[-1])/3
    amt = (x[-3]+x[-2]+x[-1])/3
    rates = []
    #print(gr1_3)
    #print(amt)
    amts = []
    for x in range(0, 3):
        amt = compound(amt,gr1_3)
        amts.append(amt)
        rates.append(gr1_3)

    amt = amts[-1]

    for x in range(0, 3):
        amt = compound(amt,gr4_6)
        amts.append(amt)
        rates.append(gr4_6)

    amt = amts[-1]

    for x in range(0, 3):
        amt = compound(amt,gr7_9)
        amts.append(amt)
        rates.append(gr7_9)

    #print(amts)
    npv_values, npv = get_npv(discount,amts)
    
    ter_amt = amts[-1]*(1 + (ter_rate/100))
    #print(ter_amt)
    terminal_value = ter_amt/(discount- ter_rate/100)
    #print(terminal_value)

    total_npv = npv+terminal_value
    #total_npv = terminal_value
    return amt_1, amts, rates, npv_values, npv, terminal_value, total_npv

def get_npv(rate, values):
    #print(rate)
    values = np.asarray(values)
    npv_values = (values / (1+rate)**np.arange(1,len(values)+1))
    #print(npv_values)
    npv_sum = npv_values.sum(axis=0)
    return npv_values, npv_sum