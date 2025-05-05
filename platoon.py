import numpy as np
from BloodProductStorage import BloodProductStorage
from BloodInventoryUnit import BloodInventoryUnit
np.random.seed(2443563274)
class Platoon:
  """ Class representing medical platton that is serviced by some Medical Logisstics Company
      Attributes :
      location - location is defined as time in days in which transport with speed 1 can deliver supplies
      FWBInventoryArray - BloodProductStorage object containing current inventory of Fresh Whole Blood availiable to platoon
      PlasmaInventoryArray - BloodProductStorage object containing current inventory of Plasma availiable to platoon
      combatLevelList - probabilities with which platoon is engaged in combat of certain intensity """
  def __init__(self, loc, FWBinventory: BloodProductStorage, Plasmainventory: BloodProductStorage, cl, avgInterval, maxInterval, targetInv):
    self.location = loc #time to deliver to platoon in days
    self.FWBinventory = FWBinventory
    self.Plasmainventory = Plasmainventory
    self.combatLevelList = cl #list of combat level probabilities, must sum to 1
    self.targetInv = targetInv #target inventory levels of the form [FWB target, Plasma target]
    p = np.random.random()
    cumulative_cl = np.cumsum(cl)
    self.combatLevel = np.searchsorted(cumulative_cl, p) #The combat level on the current day sampled from
    minInterval = max(1, avgInterval - (maxInterval - avgInterval))
    self.orderCountDown = round(np.random.triangular(minInterval, avgInterval, maxInterval))
    self.runningDemand = [0,0] #resets when an order is placed
    self.avgOrderInterval = avgInterval
    self.maxOrderInterval = maxInterval


  def updateCombatLevel(self):
    """ Method that updates the combat level based on combatLevelList for each new day"""
    p = np.random.random()
    cumulative_cl = np.cumsum(self.combatLevelList)
    self.combatLevel = np.searchsorted(cumulative_cl, p)


  def timeStep(self):
     """ Method that represents a day passing for the simulation. Updates the combat level, inentory, and order shipments

     """
     self.updateCombatLevel()
     expiredFWB = self.FWBinventory.timestep()
     expiredPlasma = self.Plasmainventory.timestep()

     unMet, Demand = self.usage()
     self.runningDemand[0] += Demand[0]
     self.runningDemand[1] += Demand[1]
     self.orderCountDown -= 1

     orderDemand = None
     if self.orderCountDown == 0:
       orderDemand = self.placeOrder()
       minInterval = max(1, self.avgOrderInterval - (self.maxOrderInterval - self.avgOrderInterval))
       self.orderCountDown = round(np.random.triangular(minInterval, self.avgOrderInterval, self.maxOrderInterval))

     return orderDemand, unMet[0], unMet[1], expiredFWB, expiredPlasma


  def addInventory(self, productType: str, quantity, expires, arrival):
    """ Method used to add blood-products to platoons's inventory
        Args :
        order - order represented as BloodInventory unit type object that represents product added
         Returns:
          an error if product added has invalid type"""
    if productType == 'FWB':
       self.FWBinventory.add(quantity, expires, arrival)
       return
    if productType == 'Plasma':
      self.Plasmainventory.add(quantity, expires, arrival)
      return


  def usage(self):
    """Method that represents usage of blood in 1 day of simulation. This method must be run together with timestep method.
        Returns :
        List of unmet demand for that day as a list with values for FWB and Plasma. If all demand is met the value is 0.
    """
    FWBDemand, PlasmaDemand = PlatoonDemand(self)
    FWBDemand = round(FWBDemand)
    PlasmaDemand = round(PlasmaDemand)
    Demand = [FWBDemand, PlasmaDemand]
    unMetFWB = self.FWBinventory.use(FWBDemand)
    unMetPlasma = self.Plasmainventory.use(PlasmaDemand)
    return [unMetFWB, unMetPlasma], Demand


  def totalInventory(self):
    """ Method that computes total inventory availiable to the platoon.
      Returns :
        inventory in FWB and Palsma quantities as a list."""
    return [self.FWBinventory.avail(), self.Plasmainventory.avail()]


  def placeOrder(self):
    """ Method that etermines if an order needs to be placed by determining if the current inventory is below the given threshold.
        Returns :
        If an order is needed the order placement variable is updated to place this order.
    """
    avail = self.totalInventory()
    orderDemand = [max(a - b, 0) for a, b in zip(self.targetInv, avail)]
    self.runningDemand = [0, 0]
    return orderDemand

  def print(self):
    print('Location: ' + str(self.location) + ' FWB Inventory: ' + str(self.FWBinventory) + ' Plasma Inventory: ' + str(self.Plasmainventory)
    + ' Combat Level: ' + str(self.combatLevel) + ' Time to Order: ' + str(self.orderCountDown)
    + ' Running Demand: ' + str(self.runningDemand))


##
# Randomly samples the demand(in pints) for a given platoon
# Input the platoon that demand is needed for
# Output the Whole blood/red blood cell demand, plamsa demand
##
def PlatoonDemand(platoon):
  """ Function used to randomly sample demand for some platoon.
     Args :
     platoon - platoon for which demand is to be sampled
     Returns :
     Quantities of FWB and Plasma demanded.
  """
  numCasualities = 0
  if platoon.combatLevel == 0:
    numCasualities =  max(0,np.random.normal(platoon.combatLevel,platoon.combatLevel*0.5))
  elif platoon.combatLevel == 1:
    numCasualities =  max(0,np.random.normal(platoon.combatLevel,platoon.combatLevel*0.5))
  else:
    numCasualities =  max(0,np.random.normal(platoon.combatLevel,platoon.combatLevel*0.5))
  TransfusionsDemand = numCasualities * 0.2 * np.random.exponential(0.1116)*4815
  plasmaDemand = TransfusionsDemand * 0.02
  return TransfusionsDemand - plasmaDemand, plasmaDemand

