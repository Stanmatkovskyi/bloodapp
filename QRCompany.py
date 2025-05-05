#Object represent a medical logistics company that services a number of medical platoons
import numpy as np
from QRTransport import *
class Company:
  def __init__(self, FWBinventory, Plasmainventory, transport, platoons):
    self.FWBinventoryArray = FWBinventory #List of BloodInventoryUnit with the productType 'FWB' that the Company has on hand
    self.PlasmainventoryArray = Plasmainventory #List of BloodInventoryUnit with the productType 'Plasma' that the Company has on hand
    self.transportCapabilities = transport #List of Transport objects that provide the transport available to the company for BloodInventoryUnit delivery
    self.platoonList = platoons #List of medical platoons that the company services

  # fucntion that represents a day passsing for the simulation.
  #Returns 4 lists with an entry for each platoon for the day which are unmet FWB demand, unmet Plasma demand, FWB inventory, and Plasma inventory.
  def timeStep(self):
    for unit in self.transportCapabilities:
      unit.availcount = np.max(unit.availcount-1,0)
      availUpdate(unit)
    for unit in self.FWBinventoryArray:
      unit.hold()
    for unit in self.PlasmainventoryArray:
      unit.hold()
    FWBInventory = []
    PlasmaInventory = []
    unMetFWBDemand = []
    unMetPlasmaDemand = []
    for platoon in self.platoonList:
      unMet = platoon.usage()
      platoon.timeStep()
      platoon.placeOrderCheck()
      FWBInventory.append(platoon.totalInventory()[0])
      PlasmaInventory.append(platoon.totalInventory()[1])
      unMetFWBDemand.append(unMet[0])
      unMetPlasmaDemand.append(unMet[1])
    return [unMetFWBDemand, unMetPlasmaDemand, FWBInventory, PlasmaInventory]
