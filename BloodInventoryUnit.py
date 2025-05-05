class BloodInventoryUnit:
  def __init__(self, exp, prod, quant):
    self.ageUsable = exp #Days until the inventory expires
    self.productType = prod #The type of blood product
    self.quantity = quant #quantity in pints

  def hold(self): #transition function
    self.ageUsable -= 1

  def merge(self, other):
    if (self.ageUsable == other.ageUsable) and (self.productType == other.productType):
        self.quantity += other.quantity
        other = None

  def __str__(self):
    return 'Age Usable: ' + str(self.ageUsable) + ' Product Type: ' + self.productType + ' Quantity: ' + str(self.quantity)
