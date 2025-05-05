class Transport:
  """ Class representing transport capabilities availiable for medicla logistics company
        Attributes :
          Speed - how fast can ttransport get to location 1 distance unit away in days
          Capacity - availiable cargo capacity in pints
          departureCount - days till the transport departs
          Name - Name of transport capability
          Cost - per usage opportunity cost associated with transport capabilty
          Cacc - accumulated cost of transport capabilty"""

  def __init__(self,sp,cap, name):
    self.speed = sp # speed 1 means it takes exactly loc number of days to deliver , speed 2 -> ceil(loc/2) and so on
    self.capacity = cap # capacity in pint
    self.name = name

  def __str__(self):
    return f"Name: {self.name}. Speed: {self.speed}. Capacity: {self.capacity}"

  def __repr__(self):
    return f"Name: {self.name}. Speed: {self.speed}. Capacity: {self.capacity}"
