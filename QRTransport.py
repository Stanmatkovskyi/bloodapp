import numpy as np

class Transport :
  def __init__(self,sp,cap,count,iu=0):
    self.speed = sp # speed 1 means it takes exactly loc number of days to deliver , speed 2 -> ceil(loc/2) and so on
    self.capacity = cap # capacity in pint
    self.availcount = count # days till tranport is usable again
    self.inuse = iu # 0 not in use, 1 in use
    

def getTime(trans, platoon):
    return np.ceil(platoon.location / trans.speed)  # Fixed 'platoon.loc'

def capCheck(trans,shipment) : # checks if transport can carry blood loaded
  count = 0
  for i in shipment :
    count += i.quantity
  if count > trans.capacity :
    return False
  else :
    return True

def availUpdate(transport) : #updates transport object so that it can be used again
  if transport.availcount == 0 :
    transport.inuse = 0


def useTrans (transport, platoon) :  # essesntially makes transport unavailiable
  transport.availcount += getTime(transport, platoon)*2
  transport.inuse = 1
  transport.cacc += transport.cost
