import math
from transport import Transport
from BloodInventoryUnit import BloodInventoryUnit
from BloodProductStorage import BloodProductStorage
from platoon import Platoon

class Company:
  """ Class representing Medical Logistics Company
  Attributes :
  FWBinentory - BloodProductStorage objects representing current Fresh Whole Blood inventory of the company
  Plasmainentory - BloodProductStorage object representing current Plasma inventory of the company
  transportCapabilities - list of Transport objects representing transport capabilities availiable to company
  platoonList - list of platoons that is serviced by the company
   """
  def __init__(self, FWBinventory: BloodProductStorage, Plasmainventory: BloodProductStorage, transport, platoons):
    self.FWBinventory = FWBinventory
    self.Plasmainventory = Plasmainventory
    self.transportCapabilities = transport #List of Transport objects that provide the transport available to the company for BloodInventoryUnit delivery
    self.platoonList = platoons #List of medical platoons that the company services


  def timeStep(self):
    """function that represents passing of 1 day in the simulation
      Returns : list with entries for that time step of
      [[Transport Days Used by  platoon], [Transport Space Used by platoon], [FWB unmet demand by platoon], [Plasma unmet demand by platoon], [Expired FWB by platoon], [Expired Plasma by platoon]] """
    
    self.FWBinventory.timestep()
    self.Plasmainventory.timestep()

    FWBUnmet = []
    PlasmaUnmet = []
    ExpiredFWB = []
    ExpiredPlasma = []
    transportDays = []
    transportSpace = []
    for i in range(len(self.platoonList)):
      demand, FWBU, PlasmaU, FWBE, PlasmaE = self.platoonList[i].timeStep()
      FWBUnmet.append(FWBU)
      PlasmaUnmet.append(PlasmaU)
      ExpiredFWB.append(FWBE)
      ExpiredPlasma.append(PlasmaE)
      tDays, tSpace = self.orderPlanning(demand, i)
      transportDays.append(tDays)
      transportSpace.append(tSpace)
      
    return [transportDays, transportSpace, FWBUnmet, PlasmaUnmet, ExpiredFWB, ExpiredPlasma]

  def orderPlanning(self, demand, platoonIndex):
    if demand == None:
      return 0, 0
    FWBonHand, PlasmaOnHand = self.findInventory(demand[0], demand[1])
    transport = self.transportCapabilities[platoonIndex]
    cap = transport.capacity
    if cap >= demand[0] + demand[1]:
      for j in FWBonHand:
        self.platoonList[platoonIndex].addInventory('FWB', j[0], j[1], math.ceil(self.platoonList[platoonIndex].location / self.transportCapabilities[platoonIndex].speed))
      for j in PlasmaOnHand:
        self.platoonList[platoonIndex].addInventory('Plasma', j[0], j[1], math.ceil(self.platoonList[platoonIndex].location / self.transportCapabilities[platoonIndex].speed))
      return math.ceil(self.platoonList[platoonIndex].location / self.transportCapabilities[platoonIndex].speed), demand[0] + demand[1]
    while cap > 0:
      if demand[0] > 0:
        if FWBonHand[0][0] < cap:
          self.platoonList[platoonIndex].addInventory('FWB', FWBonHand[0][0], FWBonHand[0][1], math.ceil(self.platoonList[platoonIndex].location / self.transportCapabilities[platoonIndex].speed))
          demand[0] -= FWBonHand[0][0]
          cap -= FWBonHand[0][0]
          FWBonHand.pop(0)
        else:
          self.platoonList[platoonIndex].addInventory('FWB', cap, FWBonHand[0][1], math.ceil(self.platoonList[platoonIndex].location / self.transportCapabilities[platoonIndex].speed))
          demand[0] -= cap
          cap = 0
      if demand[1] > 0:
        if PlasmaOnHand[0][0] < cap:
          self.platoonList[platoonIndex].addInventory('Plasma', PlasmaOnHand[0][0], PlasmaOnHand[0][1], math.ceil(self.platoonList[platoonIndex].location / self.transportCapabilities[platoonIndex].speed))
          demand[1] -= PlasmaOnHand[0][0]
          cap -= PlasmaOnHand[0][0]
          PlasmaOnHand.pop(0)
        else:
          self.platoonList[platoonIndex].addInventory('Plasma', cap, PlasmaOnHand[0][1], math.ceil(self.platoonList[platoonIndex].location / self.transportCapabilities[platoonIndex].speed))
          demand[1] -= cap
          cap = 0
    for j in FWBonHand:
      self.addInventory('FWB', j[0], j[1])
    for j in PlasmaOnHand:
      self.addInventory('Plasma', j[0], j[1])
    return math.ceil(self.platoonList[platoonIndex].location / self.transportCapabilities[platoonIndex].speed), transport.capacity

  def findInventory(self, FWBNeed, PlasmaNeed):
    """ method used to find units of inventory that can be used to satisfy demand
        Args :
        FWBNeed - demand for FWB
        PlasmaNeed - demand for Plasma
        Returns :
        Arrays of FWB and Plasma inventory units that can be used to satisfy demand
     """
    FWB = self.FWBinventory.export(FWBNeed)
    Plasma = self.Plasmainventory.export(PlasmaNeed)
    return FWB, Plasma

  def addInventory(self, productType: str, quantity, expires):
    """ Method used to add blood-products to company's inventory
        Args :
        order - order represented as BloodInventory unit type object that represents product added"""
    if productType == 'FWB':
       self.FWBinventory.add(quantity, expires, 0)
       return
    if productType == 'Plasma':
      self.Plasmainventory.add(quantity, expires, 0)
      return
    
  def addTransport(self, transport: Transport):
    """ Method that adds transport capabilities to list of those availiable to company
        Args:
        transport - Transport object that represents transport capability to be added """
    self.transportCapabilities.append(transport)

  def print(self):
    print('FWB Inventory: ' + str(self.FWBinventory))
    print('Plasma Inventory: ' + str(self.Plasmainventory))
    print('Transport Capabilities: ' + str(self.transportCapabilities))
    print('Platoons: ')
    for i in self.platoonList:
      i.print()



