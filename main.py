from TransportFeedbackSim import TFSim
from QRSimulation import QRsim

simType = 'TF' #Type of simulation to run. 'QR' or 'TF'

#inputs, eventually generated view UI into json
T = 15 #Number of days simulated
n = 2 #Number of Platoons
l = [3, 2] #List of length n of the Locations of each platoon as an integer number of days from company location
avgOrderInterval = [3, 4] # List of length n of the time between reorders for each platoon as an integer number of days
maxOrderInterval = [5, 7] # List of length n of the maximum time between reorders for each platoon as an integer number of days
TargetInv = [[1000, 40], [1000, 40]] # List of length n of the target inventory levels for each platoon in the form [FWB target, Plasma target]
PI = [[['FWB',750, 10], ['Plasma', 30, 300]], [['Plasma', 40, 20], ['FWB', 300, 5], ['FWB', 800, 20]]] #List of length n with an entry for each platoon. Each entry is the platoon current inventory represented by a list of lists of format
CI = [['FWB', 2000, 40], ['Plasma', 2000, 300], ['FWB', 15000, 10], ['FWB', 10000, 15]]
# [Type of blood, number of units, Days until expired]
CLMatrix = [[0.5, 0.2, 0.1, 0.05, 0.05], [0.7, 0.2, 0.05, 0.03, 0.02]] #List of length n of a list of the probability of being at each combat level 0 to 4 for each platoon. Probabilities must add to 1.


if simType == 'QR':
    QRsim()
elif simType == 'TF':
    TFSim(T, n, l, avgOrderInterval, maxOrderInterval, TargetInv, PI, CI, CLMatrix)