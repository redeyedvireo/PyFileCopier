# Holds global values for copying.  Copy groups can override some of these.

class GlobalCopyParams:
  def __init__(self):
    self.destinationDir = None
    self.dateRoot = False