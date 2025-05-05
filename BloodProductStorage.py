class BloodProductStorage:

  # inventory is a list of tuples containing (# of units, days until experation, days until arrival)
  def __init__(self, inventory):
    self.inventory = inventory

  def add(self, NumUnits, Exp, Arrival):
    item = (NumUnits, Exp, Arrival)
    for i in range(len(self.inventory)):
      if item[1] < self.inventory[i][1]:
        self.inventory.insert(i, item)
        return
      elif item[1] == self.inventory[i][1] and item[2] < self.inventory[i][2]:
        self.inventory.insert(i, item)
        return
    self.inventory.append(item)

  def use(self, NumUnits):
    skips = 0
    while NumUnits > 0 and len(self.inventory) > skips:
      if self.inventory[skips][2] > 0:
        skips += 1
      elif self.inventory[skips][0] > NumUnits:
        self.inventory[skips] = [self.inventory[skips][0] - NumUnits, self.inventory[skips][1], self.inventory[skips][2]]
        NumUnits = 0
      else:
        NumUnits -= self.inventory[skips][0]
        self.inventory.pop(skips)
    return NumUnits

  def avail(self):
    return sum(i[0] for i in self.inventory if i[2] == 0)

  def export(self, need):
    found = []
    while need > 0:
      if self.inventory[0][0] > need:
        found.append((need, self.inventory[0][1], self.inventory[0][2]))
        self.inventory[0] = (self.inventory[0][0] - need, self.inventory[0][1], self.inventory[0][2])
        need = 0
      else:
        need -= self.inventory[0][0]
        found.append(self.inventory[0])
        self.inventory.pop(0)
    return found

  def timestep(self):
    self.inventory = [(i[0], i[1] - 1, max(i[2] - 1, 0)) for i in self.inventory]
    exp = 0
    while len(self.inventory) > 0 and self.inventory[0][1] <= 0:
      exp += self.inventory[0][0]
      self.inventory.pop(0)
    return exp

  def __str__(self):
    return 'Inventory: ' + str(self.inventory)

'''
##testing
def run_tests():
    print("Starting BloodProductStorage tests...\n")

    # Create a BloodProductStorage object with some initial inventory
    storage = BloodProductStorage([
        (5, 3, 0),  # 5 units, expires in 3 days, available now
        (10, 5, 0), # 10 units, expires in 5 days, available now
        (3, 2, 1)   # 3 units, expires in 2 days, arrives tomorrow
    ])

    print("Initial Inventory:", storage)

    # Test adding new inventory
    storage.add(4, 6, 0)
    print("\nAfter Adding (4,6,0):", storage)

    # Test using blood
    remaining = storage.use(8)
    print("\nAfter Using 8 Units (Remaining Unfulfilled:", remaining, "):", storage)

    # Test using more blood than available
    remaining = storage.use(20)
    print("\nAfter Trying to Use 20 More Units (Remaining Unfulfilled:", remaining, "):", storage)

    # Test available blood (should exclude items with arrival > 0)
    available_units = storage.avail()
    print("\nCurrently Available Units (should exclude pending arrivals):", available_units)

    # Test exporting blood
    exported_units = storage.export(7)
    print("\nExported 7 Units:", exported_units)
    print("After Exporting:", storage)

    # Test timestep (aging & expiration)
    expired_units = storage.timestep()
    print("\nAfter One Timestep (Expired Units:", expired_units, "):", storage)

    storage.timestep()
    print("\nAfter Another Timestep:", storage)

    print("\nAll tests completed!")


# Run the tests
run_tests()
'''