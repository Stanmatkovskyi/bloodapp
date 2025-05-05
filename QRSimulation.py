import numpy as np
from BloodInventoryUnit import BloodInventoryUnit
from QRPlatoon import Platoon
from QRCompany import Company
from skopt import gp_minimize

T = 100 #Number of days simulated
n = 2 #Number of Platoons
l = [3, 2] #List of length n of the Locations of each platoon as an integer number of days from company location
I = [[[10, 'FWB', 750], [300, 'Plasma', 30]], [[20, 'Plasma', 40], [5, 'FWB', 300], [20, 'FWB', 800]]] #List of length n with an entry for each platoon. Each entry is the platoon current inventory represented by a list of lists of format
# [Days until Expired, Type of blood, number of units]
CLMatrix = [[0.5, 0.2, 0.1, 0.05, 0.05], [0.7, 0.2, 0.05, 0.03, 0.02]] #List of length n of a list of the probability of being at each combat level 0 to 4 for each platoon. Probabilities must add to 1.
QR = [[[400, 1800], [5, 30]], [[500, 1000], [5, 20]]] # List of length n with an entry for each platoon. Each entry is the Q and R values to be tested for said platoon given by a list with an entry for each
#blood category of the form [R, Q]. Q + R must be less than the platoon's storage capacity.
SC = [2500, 2000] #list of length n of the storage capacity in units for each platoon

def sim(inputs):
  simQR = [[[inputs[0], inputs[1]], [inputs[2], inputs[3]]], [[inputs[4], inputs[5]], [inputs[6], inputs[7]]]]
  platoons = []
  for i in range(n):
    FWBInv = []
    PlasmaInv = []
    for j in I[i]:
      if j[1] == 'FWB':
       FWBInv.append(BloodInventoryUnit(j[0], j[1], j[2]))
      if j[1] == 'Plasma':
        PlasmaInv.append(BloodInventoryUnit(j[0], j[1], j[2]))
    platoons.append(Platoon(l[i], FWBInv, PlasmaInv, CLMatrix[i], simQR[i]))

  Company1 = Company([], [], [], platoons)
  result = []
  for i in range(T):
    output = Company1.timeStep()
    result.append(output)

  result = np.array(result).T
  k = 10
  rawScore = 0
  maxUnmet = 0
  for i in result:
    rawScore += sum(i[0]) + sum(i[1])
    for j in i[0]:
      if j > maxUnmet:
        maxUnmet = j
    for j in i[1]:
      if j > maxUnmet:
        maxUnmet = j
  rawScore += maxUnmet * k
  normalizeScore = rawScore / (n*T)
  return normalizeScore

def QRsim():
    bounds = [(200, 800), (500, 2000), (0, 15), (10, 50), (200, 800), (500, 2000), (0, 15), (10, 50)]

    result = gp_minimize(sim, bounds, n_calls=100)
    print(f"Best configuration: {result.x} with score: {result.fun}")
