import sys

class Weblog_Parser:
   def __init__(self, input_weblog):
      self.weblog = input_weblog
      self.next_web_id = 0 
      self.web_id_table = {}
      self.user_access_log_table = {}

   def get_web_id(self, webpage):
      if not webpage in self.web_id_table: 
         self.web_id_table[webpage] = self.next_web_id
         self.next_web_id += 1
      return self.web_id_table[webpage]

   def add_user_access(self, user, webpage):
      wid = self.get_web_id(webpage)
      if not user in self.user_access_log_table:
         self.user_access_log_table[user] = set([])
      self.user_access_log_table[user].add(wid) 

   def dump_forrmated_log(self):
      for user in self.user_access_log_table.keys():
         line = ""
         for web in self.user_access_log_table[user]:
            line += "%d," % web
         line = line[:-1] + "\n"
         self.formated_weblog.write(line)

   def dump_web_id_table(self):
      for web in self.web_id_table.keys():
         self.weblog_id_lookup.write("%d --- %s\n" % (self.web_id_table[web], web))

   def parse(self, out_formatted_log, out_id_lookup):
      #open all files
      self.input_weblog = open(self.weblog, "r")
      self.formated_weblog = open(out_formatted_log, "w")
      self.weblog_id_lookup = open(out_id_lookup, "w")

      #start parsing
      #an example of weblog: 
      #199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "GET /history/apollo/ HTTP/1.0" 200 6245
      for line in self.input_weblog:
         try:
            tokens = line.split()
            user = tokens[0]
            resp_code = int(tokens[-2])
            web_req = line.split('"')[1]
            web_req_tokens = web_req.split()

            if len(web_req_tokens) < 2: continue #ignore request that doesn't have valid HTTP request method
            webpage = web_req.split()[1]
            if (resp_code >= 200 and resp_code <= 299): #only record valid http response code
               self.add_user_access(user, webpage)

            #TODO: also consider if URL belongs to the same webpage previously seen)

         except Exception, e:
            print("ignore invalid formatted line: %s" % line)
            #print(e)
            continue

      #the first line of the formatted web log contain two number seperated by comma,
      #the first is total number of webpages in the domain
      #the second is the total number of users
      self.formated_weblog.write("%d,%d\n" % (len(self.web_id_table.keys()), len(self.user_access_log_table.keys())))

      #save outputs
      self.dump_forrmated_log()
      self.dump_web_id_table()

      #close all files
      self.input_weblog.close()
      self.formated_weblog.close()
      self.weblog_id_lookup.close()

def usage(prog):
   print("Usage: python %s <weblog file> <formatted web log output filename> <web id lookup filename>" % prog)
   print("       where in <weblog>, each line has the format: host - timestamp - request -HTTP reply code - bytes in the reply")
   print("             in <formatted web log>, first line is <number of web pages>,<number of users>, then following each line indicates the web has been access by the user (user id hidden)")
   print("             in <web id lookup file>, we can find out which id means which web page")
   sys.exit(-1);

def main(argv):
   if len(argv) != 4: usage(argv[0])
   parser = Weblog_Parser(argv[1])
   parser.parse(argv[2], argv[3])

if __name__ == "__main__":
   main(sys.argv)
