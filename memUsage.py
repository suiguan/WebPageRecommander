import psutil
import time

baseUsage = psutil.virtual_memory().percent
minUsage = None 
maxUsage = None
avgUsage = 0
counts = 0
sumUsage = 0

try:
   while True:
      usage = psutil.virtual_memory().percent - baseUsage
      if minUsage == None or usage < minUsage: minUsage = usage
      if maxUsage == None or usage > maxUsage: maxUsage = usage
      counts += 1
      sumUsage += usage
      avgUsage = sumUsage/counts
      time.sleep(0.01)
finally:
   print("baseUsage %.3f%% min %.3f%% max %.3f%% avg %.3f%%" % (baseUsage, minUsage, maxUsage, avgUsage))
