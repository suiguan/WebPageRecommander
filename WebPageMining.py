import numpy as np
import sys
import time

MINSUP = (1.0/3)

class FreqWebPageSetFinder:
   def __init__(self, weblog):
      self.total_web_pages, self.num_users = self.get_total_pages(weblog) #first db scan get total number of webpages
      self.minsup = int(MINSUP * self.num_users)
      print("total web pages = %d, total users = %d, minsup = %d" % (self.total_web_pages, self.num_users, self.minsup))
      self.wb_table, self.vi_list0, self.hi_counter0 = self.get_web_table(weblog) #second db scan to set up Level-0 VI-List, HI-Counter 
      #print(self.wb_table)
      #print(self.vi_list0)
      #print(self.hi_counter0)

   #return a dict of list of frequent itemsets at each level
   def find_freq_sets(self):
      self.fs = {}
      level0 = []
      #find frequent singleton from hi-counter
      for i in range(0, self.hi_counter0.shape[0]):
         if self.hi_counter0[i] >= self.minsup: level0.append([i,])
      self.fs[0] = level0

      #3, continue the to next level for each row of the VI-list
      for cidx in self.vi_list0.keys():
         self.find_next_level([cidx,], self.vi_list0[cidx])

      return self.fs

   def find_next_level(self, col_indices, row_indices): 
      level = len(col_indices)

      #1, create the projected WB-table
      wb = self.wb_table[row_indices]

      #2, create HI-counter
      hi_counter = np.sum(wb, axis=0) 
      #set non-relevant colum to 0
      for col in col_indices: hi_counter[col] = 0

      #find frequent non-singleton from hi-counter
      has_next_level = False
      for c in range(0, hi_counter.shape[0]):
         if hi_counter[c] >= self.minsup:
            has_next_level = True
            s = col_indices + [c,]
            if level in self.fs.keys(): self.fs[level].append(s)
            else: self.fs[level] = [s, ]

      #if all values in the hi_counter is non-frequent, we don't continue the next level (Apriori)
      if not has_next_level: return

      #3, create VI-list for this level,
      vi_list = {} 
      columns = range(0, self.total_web_pages)
      for c in col_indices: columns.remove(c)
      for i in range(0, wb.shape[0]):
         for c in columns:
            if wb[i][c] == 1:
               r = row_indices[i]
               if c in vi_list.keys(): vi_list[c].append(r)
               else: vi_list[c] = [r,]
               break

      #, and continue the to next level for each row of the VI-list
      for cc in vi_list.keys():
         self.find_next_level(col_indices+[cc,], vi_list[cc])


   def get_total_pages(self, weblog):
      f = open(weblog)
      table = {}
      num_users = 0
      for line in f:
         num_users += 1
         webpages = line.split(',')
         for webpage in webpages:
            w = int(webpage)
            if not w in table.keys(): table[w] = 1
      f.close()
      return len(table.keys()), num_users

   def get_web_table(self, weblog):
      wb_table = np.zeros((self.num_users, self.total_web_pages), dtype=np.uint8) 
      vi_list = {}
      f = open(weblog)
      user = 0
      for line in f:
         webpages = line.split(',')
         first_occurrence_col = None
         for webpage in webpages:
            w = int(webpage)
            if first_occurrence_col == None: first_occurrence_col = w
            elif w < first_occurrence_col: first_occurrence_col = w
	    wb_table[user][w] = 1
         if first_occurrence_col in vi_list: vi_list[first_occurrence_col].append(user)
         else: vi_list[first_occurrence_col] = [user,]
	 user += 1
      f.close()
      return wb_table, vi_list, np.sum(wb_table, axis=0) 



def usage(prog):
   print("Usage: python %s <weblog file>" % prog)
   print("       where in <weblog file>, each line is a user's web access log,")
   print("       the web pages are separted by comma, and identified by 0 to N-1, where N = total number of web pages")
   sys.exit(-1);

def main(argv):
   if len(argv) != 2: usage(argv[0])
   finder = FreqWebPageSetFinder(argv[1])
   all_sets = finder.find_freq_sets()
   for level in all_sets.keys():
      s = all_sets[level]
      print("level %d has %d freqent sets: %s" % (level, len(s), s))

if __name__ == "__main__":
   main(sys.argv)
