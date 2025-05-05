import numpy as np
from BloodInventoryUnit import BloodInventoryUnit

#Object representing a medical platoon
class Platoon:
  def __init__(self, loc, FWBinventory, Plasmainventory, cl, QR):
    self.location = loc #time to deliver to platoon in days
    self.FWBinventoryArray = FWBinventory # array of BloodInventoryUnit objects with the productType 'FWB' available to the platoon
    self.PlasmainventoryArray = Plasmainventory # array of BloodInventoryUnit objects with the productType 'Plasma' available to the platoon
    self.combatLevelList = cl #list of combat level probabilities, must sum to 1
    p = np.random.random()
    cumulative_cl = np.cumsum(cl)
    self.combatLevel = np.searchsorted(cumulative_cl, p) #The combat level on the current day sampled fro
    self.OrderPlacement = [[], []] #[[Days until order arrives] entry for each order empty if no orders, BloodInventoryUnit order]
    self.R_FWB = QR[0][0]
    self.Q_FWB = QR[0][1]
    self.R_Plasma = QR[1][0]
    self.Q_Plasma = QR[1][1]

  # function that updates the combat level based on combatLevelList for each new day
  def updateCombatLevel(self):
    p = np.random.random()
    cumulative_cl = np.cumsum(self.combatLevelList)
    self.combatLevel = np.searchsorted(cumulative_cl, p)

  # function that represents a day passing for the simulation. Updates the combat level, inentory, and order shipments
  def timeStep(self):
     self.updateCombatLevel()
     for unit in self.FWBinventoryArray:
      unit.hold()
     for unit in self.PlasmainventoryArray:
       unit.hold()
     self.FWBinventoryArray = [item for item in self.FWBinventoryArray if item.ageUsable > 0]
     self.PlasmainventoryArray = [item for item in self.PlasmainventoryArray if item.ageUsable > 0]
     popIndex = []
     for i in range(len(self.OrderPlacement[0])):
      if self.OrderPlacement[0][i] == 0:
        self.addInventory(self.OrderPlacement[1][i])
        popIndex.append(i)
      else:
        self.OrderPlacement[0][i] -= 1
     numPops = 0
     for i in popIndex:
      self.OrderPlacement[0].pop(i - numPops)
      self.OrderPlacement[1].pop(i - numPops)
      numPops += 1

  # function that takes a BloodInventoryUnit object as input and adds that object to the correct inventory array for the platoon.
  # returns an error if the BloodInventoryUnit productType is not stored by the platoon
  def addInventory(self, order: BloodInventoryUnit):
    if order.productType == 'FWB':
       for i in range(len(self.FWBinventoryArray)):
         if order.ageUsable < self.FWBinventoryArray[i].ageUsable:
           self.FWBinventoryArray.insert(i, order)
           return
       self.FWBinventoryArray.append(order)
       return
    if order.productType == 'Plasma':
      for i in range(len(self.PlasmainventoryArray)):
       if order.ageUsable < self.PlasmainventoryArray[i].ageUsable:
          self.PlasmainventoryArray.insert(i, order)
          return
      self.PlasmainventoryArray.append(order)
      return

  #function that goes through the usage of blood for the platoon for a day of simulation. It must be run with time step for every simulated day
  #return the unmet demand for that day as a list with values for FWB and Plasma. If all demand is met the value is 0.
  def usage(self):
    FWBDemand, PlasmaDemand = PlatoonDemand(self)
    FWBDemand = round(FWBDemand)
    PlasmaDemand = round(PlasmaDemand)
    unMet = [0, 0]

    # Process FWB Demand
    totalFWB = sum(unit.quantity for unit in self.FWBinventoryArray)
    if FWBDemand > totalFWB:
        unMet[0] = FWBDemand - totalFWB
        self.FWBinventoryArray.clear()
    else:
        remaining_demand = FWBDemand
        new_inventory = []
        for unit in self.FWBinventoryArray:
            if remaining_demand > 0:
                if unit.quantity > remaining_demand:
                    unit.quantity -= remaining_demand
                    new_inventory.append(unit)
                    remaining_demand = 0
                else:
                    remaining_demand -= unit.quantity
            else:
                new_inventory.append(unit)
        self.FWBinventoryArray = new_inventory

    # Process Plasma Demand (Similar Logic)
    totalPlasma = sum(unit.quantity for unit in self.PlasmainventoryArray)
    if PlasmaDemand > totalPlasma:
        unMet[1] = PlasmaDemand - totalPlasma
        self.PlasmainventoryArray.clear()
    else:
        remaining_demand = PlasmaDemand
        new_inventory = []
        for unit in self.PlasmainventoryArray:
            if remaining_demand > 0:
                if unit.quantity > remaining_demand:
                    unit.quantity -= remaining_demand
                    new_inventory.append(unit)
                    remaining_demand = 0
                else:
                    remaining_demand -= unit.quantity
            else:
                new_inventory.append(unit)
        self.PlasmainventoryArray = new_inventory

    return unMet


  #computes the total inventory available for the platoon. returns the inventory in FWB and Palsma as a list.
  def totalInventory(self):
    FWB = 0
    Plasma = 0
    for i in self.FWBinventoryArray:
      FWB += i.quantity
    for i in self.PlasmainventoryArray:
      Plasma += i.quantity
    return [FWB, Plasma]

  # function that determines if an order needs to be places by determining if the current inventory is below the given threshold.
  # If an order is needed the order placement variable is updated to place this order
  def placeOrderCheck(self):
    if self.totalInventory()[0] < self.R_FWB:
      orderIn = False
      for i in self.OrderPlacement[1]:
        if i.productType == 'FWB':
          orderIn = True
      if not orderIn:
        self.OrderPlacement[0].append(self.location)
        self.OrderPlacement[1].append(BloodInventoryUnit(30, 'FWB', self.Q_FWB))
    if self.totalInventory()[1] < self.R_Plasma:
      orderIn = False
      for i in self.OrderPlacement[1]:
        if i.productType == 'Plasma':
          orderIn = True
      if not orderIn:
        self.OrderPlacement[0].append(self.location)
        self.OrderPlacement[1].append(BloodInventoryUnit(300, 'Plasma', self.Q_Plasma))

  def print(self):
    return 'Location: ' + str(self.location) + ' FWB Inventory: ' + str(self.FWBinventoryArray) + ' Plasma Inventory: ' + str(self.PlasmainventoryArray) + ' Combat Level: ' + str(self.combatLevel) + ' Order Placement: ' + str(self.OrderPlacement)



##
# Randomly samples the demand(in pints) for a given platoon
# Input the platoon that demand is needed for
# Output the Whole blood/red blood cell demand, plamsa demand
##
def PlatoonDemand(platoon):
  numCasualities =  max(0,np.random.normal(platoon.combatLevel,platoon.combatLevel*0.5))
  TransfusionsDemand = numCasualities * 0.2 * np.random.exponential(0.1116)*4815
  plasmaDemand = TransfusionsDemand * 0.02
  return TransfusionsDemand - plasmaDemand, plasmaDemand
