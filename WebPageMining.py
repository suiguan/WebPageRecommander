import numpy as np
import sys
import time
import operator

MINSUP = (1.0/3)
#MINSUP = (1.0/10)

class FreqWebPageSetFinder:
   def __init__(self, weblog):
      self.total_web_pages, self.num_users, self.wb_table, self.hi_counter0 = self.get_web_table(weblog) #db scan to set up Level-0 VI-List, HI-Counter 
      self.minsup = int(MINSUP * self.num_users)
      print("total web pages = %d, total users = %d, minsup = %d" % (self.total_web_pages, self.num_users, self.minsup))
      #print(self.wb_table)
      #print(self.hi_counter0)

   #implementation of the paper "Web Page Recommdation Based on Bitwise Frequent Pattern Mining"
   #return a dict of list of frequent itemsets at each level
   def BW_mine(self):
      self.fs = {}
      level0 = set([])
      #find frequent singleton from hi-counter
      for i in range(0, self.hi_counter0.shape[0]):
         if self.hi_counter0[i] >= self.minsup: level0.add(frozenset([i,]))
      self.fs[0] = level0

      #3, continue the to next level for each row of the VI-list
      for col_idx in range(0, self.total_web_pages):
	  #create vi_list entry for col_idx
          if self.hi_counter0[col_idx] < self.minsup: continue
	  col_arr = self.wb_table[:,col_idx]
	  row_indices = []
	  for r in range(0, col_arr.shape[0]):
             if col_arr[r] == 1: row_indices.append(r)

          #find next level for this vi_list entry
          self.find_next_level([col_idx,], row_indices, col_idx + 1)

      #return the FS
      return self.fs

   #implementation of the paper "Frequent Itemsets Mining Using Vertical Index List"
   #by using the BW_table other than the proposed VIL 
   #return a dict of list of frequent itemsets at each level
   def SL_mine(self):
      self.fs = {}
      sl_table = {} # ("webpage" : "support") key-value pair

      #find frequent singleton from hi-counter & create SL table
      level0 = set([])
      for i in range(0, self.hi_counter0.shape[0]):
         if self.hi_counter0[i] >= self.minsup: 
            level0.add(frozenset([i,]))
            sl_table[i] = self.hi_counter0[i]
      self.fs[0] = level0

      #sort the SL table based on support value
      self.sorted_sl = sorted(sl_table.items(), key=operator.itemgetter(1)) #sort by value

      #use the key (webpage) in the sorted_sl as the control order to find all frequent itemsets
      for idx in range(0, len(self.sorted_sl)): 
         nextIdx = idx + 1
         while nextIdx < len(self.sorted_sl):
            self.check_high_level([self.sorted_sl[idx][0],], nextIdx)
            nextIdx += 1

      #return the FS
      return self.fs

   def check_high_level(self, webpages, nextIdx):
      if nextIdx >= len(self.sorted_sl): return
      itemset = webpages + [self.sorted_sl[nextIdx][0],]
      level = len(itemset) - 1
      #calculate the support of the itemset from the BW_table  
      #there should be at lease 2 webpages in the itemset
      r = self.wb_table[:,itemset[0]] & self.wb_table[:,itemset[1]] #access by column 
      for webp in itemset[2:]: 
         r = r & self.wb_table[:,webp] #access by column
      sup = np.sum(r)
      if sup >= self.minsup:
         #add the itemset to the FS
         s = frozenset(itemset)
         if level in self.fs.keys(): self.fs[level].add(s)
         else: self.fs[level] = set([s,])
         #continue to check higher level
         for idx in range(nextIdx+1, len(self.sorted_sl)):
            self.check_high_level(itemset, idx)


   def find_next_level(self, col_indices, row_indices, next_col_idx): 
      level = len(col_indices)
      #print("at level %d, col_indices = %s" % (level, col_indices))

      #1, create the projected WB-table
      wb = self.wb_table[row_indices]

      #2, create HI-counter
      hi_counter = np.sum(wb, axis=0) 
      #print("finding at level %d, col indices %s, row indices %s, next col idx %d" % (level, col_indices, row_indices, next_col_idx))
      #print(hi_counter)

      #find frequent non-singleton from hi-counter
      has_next_level = False
      for c in range(next_col_idx, hi_counter.shape[0]):
         if hi_counter[c] >= self.minsup:
            has_next_level = True
            s = frozenset(col_indices + [c,])
            if level in self.fs.keys(): self.fs[level].add(s)
            else: self.fs[level] = set([s,])

      #if all values in the hi_counter is non-frequent, we don't continue the next level (Apriori)
      if not has_next_level: 
         #print("no next level")
         return

      #3, create VI-list entry for this level,
      for col_idx in range(next_col_idx, self.total_web_pages):
         if hi_counter[col_idx] < self.minsup: continue
         col_arr = self.wb_table[:,col_idx]
         rows = []
         for r in row_indices:
            if col_arr[r] == 1: rows.append(r)
         self.find_next_level(col_indices + [col_idx,], rows, col_idx + 1)


   def get_web_table(self, weblog):
      f = open(weblog)
      firstline = f.readline()
      tokens = firstline.split(',')
      total_web_pages = int(tokens[0])
      total_users = int(tokens[1]) 
      wb_table = np.zeros((total_users, total_web_pages), dtype=np.uint8) 
      user = 0
      for line in f:
	 #error checking:
	 if user >= total_users: raise Exception("Too many user access log, number of lines >= total user count %d" % total_users) 
         webpages = line.split(',')
         first_occurrence_col = None
         for webpage in webpages:
            w = int(webpage)
	    #error checking:
	    if w < 0 or w >= total_web_pages: raise Exception("Invalid web page number %d, total web page count %d" % (w, total_web_pages))
	    wb_table[user][w] = 1
	 user += 1
      f.close()
      return total_web_pages, total_users, wb_table, np.sum(wb_table, axis=0) 



def usage(prog):
   print("Usage: python %s <BW/SL> <weblog file> <output file name>" % prog)
   print("       where in <BW/SL>, BW means using BW_mine and SL means using SL_mine")
   print("       where in <weblog file>, the first line is comma seperated two number, the first number is total number of web pages,")
   print("                               the second number is total number of users, then following each line is a user's web access log,")
   print("                               the web pages are separted by comma, and identified by 0 to N-1, where N = total number of web pages")
   sys.exit(-1);

def main(argv):
   if len(argv) != 4: usage(argv[0])
   outf = open(argv[3], "w")

   before = int(time.time())
   all_sets = None
   if argv[1] == "BW":
      finder = FreqWebPageSetFinder(argv[2])
      all_sets = finder.BW_mine()
   elif argv[1] == "SL":
      finder = FreqWebPageSetFinder(argv[2])
      all_sets = finder.SL_mine()
   if all_sets == None:
      print("Unsupported Mining method %s, only BW/SL is current supported" % argv[1])
      sys.exit(-1);
   after = int(time.time())
   print("Take %d seconds to find all frequent item sets" % (after - before))
   outf.write("Take %d seconds to find all frequent item sets\n" % (after - before))

   for level in all_sets.keys():
      ss = all_sets[level]
      line = "Level %d has %d frequent sets: " % (level, len(ss))
      for s in ss:
         line += "%s," % list(s)
      line += "\n"
      outf.write(line)
   outf.close()

if __name__ == "__main__":
   main(sys.argv)
