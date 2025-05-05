from Company import Company
from transport import Transport
from BloodProductStorage import BloodProductStorage
from platoon import Platoon
import numpy as np
import pandas as pd

def TFSim(T, n, l, avgOrderInterval, maxOrderInterval, TargetInv, PI, CI, CLMatrix):
    
    platoons = []
    for i in range(n):
        p = Platoon(l[i], BloodProductStorage([]), BloodProductStorage([]), CLMatrix[i], avgOrderInterval[i], maxOrderInterval[i], TargetInv[i])
        for item in PI[i]:
            p.addInventory(item[0], item[1], item[2], 0)
        platoons.append(p)

    company1 = Company(BloodProductStorage([]), BloodProductStorage([]), [], platoons)
    company1.addTransport(Transport(1, 10000, 'Platoon1T1'))
    company1.addTransport(Transport(1, 10000, 'Platoon2T1'))

    for item in CI:
        company1.addInventory(item[0], item[1], item[2])

    result = []
    for i in range(T):
        output = company1.timeStep()
        print(output)
        result.append(output)
        company1.print()

    result = np.array(result).T
    resultDF = toDF(result)
    print(resultDF)
    return resultDF

def toDF(result):
    df = pd.DataFrame()
    for i in range(len(result)):
        df['Platoon'+str(i+1)+'_TransDays'] = result[i][0]
        df['Platoon'+str(i+1)+'_TransSpace'] = result[i][1]
        df['Platoon'+str(i+1)+'_FWBUnmet'] = result[i][2]
        df['Platoon'+str(i+1)+'_PlasmaUnmet'] = result[i][3]
        df['Platoon'+str(i+1)+'_FWBExpired'] = result[i][4]
        df['Platoon'+str(i+1)+'_PlasmaExpired'] = result[i][5]

    df['Company_TransDays'] = df.iloc[:, 0::6].sum(axis=1)
    df['Company_TransSpace'] = df.iloc[:, 1::6].sum(axis=1)
    df['Company_FWBUnmet'] = df.iloc[:, 2::6].sum(axis=1)
    df['Company_PlasmaUnmet'] = df.iloc[:, 3::6].sum(axis=1)
    df['Company_FWBExpired'] = df.iloc[:, 4::6].sum(axis=1)
    df['Company_PlasmaExpired'] = df.iloc[:, 5::6].sum(axis=1)

    return df
    

    
