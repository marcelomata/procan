#!/usr/bin/env python
# web page procan plugin
# Written by:  Matthew W. Jones <matburt@oss-institute.org>
# Plugin Version: 0.1 (6/26/2006)
#
# **Note** This does NOT look pretty right now.
#
# - Pass no options to send page to stdout
# - or pass a first parameter as the full path to a web file that will be created
#   and written to.
#
#   Future:  -s: Suppress the stdout output for this plugin
#
##Plot data into a window, keep the window open and update it whenever we get
##new data.
import os
import sys
import string
import time
from Numeric import *

class pp_WebPlugin:
    def __init__(self, optpath=""):
        self.opt = optpath
        self.history = {}
        self.graphrange = {}
        for i in range(0,24):
            self.graphrange[i] = time.localtime()[3]+i
            if self.graphrange[i] > 23:
                self.graphrange[i] = self.graphrange[i]-(time.localtime()[3]+1)


    ##Process input from procan on stdin
    def runLoop(self):
        while 1:
            redir = sys.stdin.readline()
            self.updateFile(sys.stdin.readline())
            print redir

    ##Redraw the gnuplot display with our current data.
    def updateFile(self, line):
        self.processLine(line)
        self.procs = {}
        #could eliminate this whole block by revising processLine
        for hour in self.history.keys():
            for proc in self.history[hour].keys():
                if not self.procs.has_key(proc):
                    self.procs[proc] = {}
                self.procs[proc][hour] = self.history[hour][proc]
        
        missing = []
        for proc in self.procs.keys():
            for i in range(0,len(self.procs[proc])-1):
                for j in range(0,int(self.procs.keys()[i+1]) - int(self.procs.keys()[i])):
                    missing.append(self.procs.keys()[i]+j)
            for misshour in missing:
                self.procs[proc][misshour] = {}

        self.html = "<html><title>ProcAn Status</title><b><i>Interesting Processes:</i></b>\n"
        for proc in self.procs.keys():
            self.html+="<h3>"+proc+"</h3>"
            self.html+="<i>Hour</i><br>"
            for hour in self.procs[proc].keys():
                self.html+=" " + str(self.keyfromval(hour,self.graphrange))+":"
                pt = 0
                for point in range(0, int(self.procs[proc][hour][1])):
                    self.html+="*"
                    pt = point
                self.html+=" ("+str(pt)+")<br>"
                
            self.html+="<br>"
        self.html+="<center><small><i>Generated by "
        self.html+="<a href='http://matburt.net/projects/procan'>ProcAn</a>"
        self.html+="</center></i></small>"
        self.html+="</html>\n"
        if self.opt != "":
            wfile = open(self.opt,'w')
            wfile.write(self.html)
            wfile.close()
        else:
            print self.html

    ##Parse the line recieved from ProcAn
    def processLine(self, line):
        if line[0] != "[":
            return
        s_line = string.split(line,",")
        s_line[0] = s_line[0][1:len(s_line[0])]
        s_line[len(s_line)-1] = s_line[len(s_line)-1][0:len(s_line[len(s_line)-1])-1]
        if not self.history.has_key(time.localtime()[3]):
            self.history[time.localtime()[3]] = {}
        if self.history[time.localtime()[3]].has_key(s_line[1]):
            self.history[time.localtime()[3]][s_line[1]][0] = int(self.history[time.localtime()[3]][s_line[1]][0])+1
            self.history[time.localtime()[3]][s_line[1]][1] = int(s_line[5][0:len(s_line[5])-1])
        else:
            self.history[time.localtime()[3]][s_line[1]] = [1,int(s_line[5][0:len(s_line[5])-1])]

    ##Helper method to retrieve a key
    def keyfromval(self,val,dict):
        for key in dict.keys():
            if dict[key] == val:
                return key
        return ""
    
class pp_WebPluginNew(object):
    def __init__(self, optpath=''):
        self.opt = optpath
        self.history = {}
        self.graphrange = {}
        this_hour = time.localtime().tm_hour
        for hour in range(24):
            entry = this_hour + hour
            if entry > 23:
                entry -= this_hour + 1
            self.graphrange[hour] = entry

    # Process input from procan on stdin
    def runLoop(self):
        while True:
            #redir = sys.stdin.readline()
            #self.updateFile(sys.stdin.readline())
            #print redir
            line = sys.stdin.readline()
            self.updateFile(line)
            print line
            
    # Redraw the gnuplot display with our current data
    def updateFile(self, line):
        self.processLine(line)
        self.procs = {}
        for hour, procs in self.history.items():
            for proc in procs.keys():
                if not self.procs.has_key(proc):
                    self.procs[proc] = {}
                self.procs[proc][hour] = self.history[hour][proc]
        missing = []
        #procs = self.procs.keys()
        #procs.sort()
        #for proc in procs:
        #    for i in range(len(self.procs[proc]) - 1):
        #        for j in range(int(self.procs.keys())):
        #            print i, j
        self.html =  "<html><title>ProcAn Status</title><b><i>Interesting Processes:</i></b>\n"
        print self.procs
        for proc in self.procs.keys():
            self.html += '<h3>%s</h3><i>Hour</i><br>' % proc
            for hour in self.procs[proc].keys():
                self.html += ' %s:' % str(self.keyfromval(hour, self.graphrange))
                points = int(self.procs[proc][hour][1])
                self.html += '*' * points
                self.html += ' (%d)<br>' % points - 1
            self.html += '<br>'
        self.html+="<center><small><i>Generated by "
        self.html+="<a href='http://matburt.net/projects/procan'>ProcAn</a>"
        self.html+="</center></i></small>"
        self.html+="</html>\n"
        if self.opt:
            wfile = file(self.opt, 'w')
            wfile.write(self.html)
            wfile.close()
        else:
            #print self.html
            sys.stdout.write(self.html)


    def processLine(self, line):
        line = line.strip()
        if not (line.startswith('[') and line.endswith(']')):
            return
        hour = time.localtime().tm_hour
        unbracketed = line[1:-1]
        print 'unbracketed', unbracketed
        # pulled these variable names from analyzer.c and renamed type to ptype
        ptype, cmd, lastpid, movement, score, niterests = unbracketed.split(',')
        if not self.history.has_key(hour):
            self.history[hour] = {}
        if self.history[hour].has_key(cmd):
            print 'history, hour, cmd', self.history[hour][cmd]
            cdict = self.history[hour][cmd]
            cdict[0] = int(cdict[0]) + 1
            cdict[1] = int(niterests[:len(niterests) - 1])
        else:
            print 'niterests', niterests
            if int(niterests):
                self.history[hour][cmd] = [1, int(niterests[:len(niterests) - 1])]

        print 'in processLine', self.history

    def keyfromval(self, val, dict):
        for key, value in dict.items():
            if value == val:
                return key
        return ''
    
            
if __name__ == '__main__':
    # Handle Arguments
    if len(sys.argv) > 1:
        print "Writing Web file: " + str(sys.argv[1])
        cp = pp_WebPluginNew(sys.argv[1])
        cp.runLoop()
    else:
        cp = pp_WebPluginNew()
        cp.runLoop()
