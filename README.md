




Descriptions of classes, methods and functions (defo not copypaste fr ong)


class Transport:
  """ Class representing transport capabilities availiable for medicla logistics company
        Attributes :
          Speed - how fast can ttransport get to location 1 distance unit away in days
          Capacity - availiable cargo capacity in pints
          departureCount - days till the transport departs
          Name - Name of transport capability"""


class BloodInventoryUnit:
""" This class represents units of Class VIIIB suplies thta can be stored and transported by company/platoon
      Attributes :
       ageUsable - amount of days left until product can no longer be used
       productType - specific type of product e.g. blood, plasma,etc.
       quantity - quantity in pints """

method hold
 """
    This method represents holding blood inentory for 1 day,
   reducing ageUsable by 1
    """

method merge
 """ This method merges two entries for inventory units of same type and age,
      adding up their quantities. For instance, it can be used when platoon receives
      supplies of same trype and age they already hold.
    """


class Company:
  """ Class representing Medical Logistics Company
  Attributes :
  FWBinentoryArray - list of BloodInventoryUnit objects rpresenting current Fresh Whole Blood inventory of the company
  FWBinentoryArray - list of BloodInventoryUnit objects rpresenting current Plasma inventory of the company
  transportCapabilities - list of Transport objects representing transport capabilities availiable to company
  platoonList - list of platoons that is serviced by the company
   """


method timeStep:
    """function that represents passing of 1 day in the simulation
      Returns : list with entries for that time step of
      [Transports used, [FWB unmet demand by platoon], [Plasma unmet demand by platoon], [Expired FWB by platoon], [Expired Plasma by platoon]] """



function orderPlanning:
    """function that counts transports used
       Args :
       orders - array of orders by platoons
       Returns :
       Number of transports used"""


method findInventory:
    """ method used to find units of inventory that can be used to satisfy demand
        Args :
        FWBNeed - demand for FWB
        PlasmaNeed - demand for Plasma
        Returns :
        Arrays of FWB and Plasma inventory units that can be used to satisfy demand
     """

method addInventory:
    """ Method used to add blood-products to company's inventory
        Args :
        order - order represented as BloodInventory unit type object that represents product added"""


method addTransport:
    """ Method that adds transport capabilities to list of those availiable to company
        Args:
        transport - Transport object that represents transport capability to be added """

class Platoon:
  """ Class representing medical platton that is serviced by some Medical Logisstics Company
      Attributes :
      location - location is defined as time in days in which transport with speed 1 can deliver supplies
      FWBInventoryArray - array representing current inventory of Fresh Whole Blood availiable to platoon
      PlasmaInventoryArray - array representing current inventory of Plasma availiable to platoon
      combatLevelList - probabilities with which platoon is engaged in combat of certain intensity """

method updateCombatLevel:
    """ Method that updates the combat level based on combatLevelList for each new day"""


method timeStep:
     """ Method that represents a day passing for the simulation. Updates the combat level, inentory, and order shipments

     """

method  addInventory:
    """ Method used to add blood-products to platoons's inventory
        Args :
        order - order represented as BloodInventory unit type object that represents product added
         Returns:
          an error if product added has invalid type"""

method totalInventory:
    """ Method that computes total inventory availiable to the platoon.
      Returns :
        inventory in FWB and Palsma quantities as a list."""

method placeOrder:
    """ Method that etermines if an order needs to be placed by determining if the current inventory is below the given threshold.
        Returns :
        If an order is needed the order placement variable is updated to place this order.
    """

function  PlatoonDemand:
  """ Function used to randomly sample demand for some platoon.
     Args :
     platoon - platoon for which demand is to be sampled
     Returns :
     Quantities of FWB and Plasma demanded.
  """
