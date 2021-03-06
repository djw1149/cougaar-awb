# Name:
# Purpose:
#
# Author:       D. Moore
#
# RCS-ID:       $Id: agentController.py,v 1.18 2006-08-30 20:45:57 damoore Exp $
#  <copyright>
#  Copyright 2002 BBN Technologies, LLC
#  under sponsorship of the Defense Advanced Research Projects Agency (DARPA).
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the Cougaar Open Source License as published by
#  DARPA on the Cougaar Open Source Website (www.cougaar.org).
#
#  THE COUGAAR SOFTWARE AND ANY DERIVATIVE SUPPLIED BY LICENSOR IS
#  PROVIDED 'AS IS' WITHOUT WARRANTIES OF ANY KIND, WHETHER EXPRESS OR
#  IMPLIED, INCLUDING (BUT NOT LIMITED TO) ALL IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, AND WITHOUT
#  ANY WARRANTIES AS TO NON-INFRINGEMENT.  IN NO EVENT SHALL COPYRIGHT
#  HOLDER BE LIABLE FOR ANY DIRECT, SPECIAL, INDIRECT OR CONSEQUENTIAL
#  DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE OF DATA OR PROFITS,
#  TORTIOUS CONDUCT, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
#  PERFORMANCE OF THE COUGAAR SOFTWARE.
# </copyright>
#

import sys
import re
import urllib
import random as r
import time
import os
import signal
import thread
import httplib

import wx
import wx.lib.ogl as ogl
import wx.lib.dialogs
# ----------------
# AWB Generic mods
from probeDLG import ProbeDlg
from ctrlDLG import CtrlDlg
from societyReader import SocietyReader
from agentCanvas import AgentCanvas
from informationPanel import InformationPanel
# -----------------
#~ from societyVisualModel import *
#~ from PollingServices.ServletDataReceiver import *
#~ from insertion_dialog import *
from csmarter_events import *
#from eventFactory import EventFactory

from servletProperties import ServletProperties
from globalConstants import *
import images
import zoomer as z


#---------------------------------------------------------------------
#~ GLOBAL VARS
CLOSE_SOCIETY_BTN_ID = 701
GLOBAL_WIDGET_ID_BASE = 10
#----------------------------------------------------------------------
# This creates some pens and brushes that the OGL library uses.



class AgentControllerViewer(wx.Panel):
    def __init__(self, parent, frame, log):
        wx.Panel.__init__(self, parent, -1)
        self.society = None
        self.hierarchy = None
        self.URL = None
        self.log = log
        self.frame = frame
        self.printData = wx.PrintData()
        self.printData.SetPaperId(wx.PAPER_LETTER)
        self.heatRange  = {50:"PURPLE", 100:"BLUE", 125:"SEA GREEN", 150:"ORANGE", 1000:"RED" }
        self.societyRunning = False
#--------
        self.box = wx.BoxSizer(wx.VERTICAL)
        self.canvas = AgentCanvas(self, frame, log)
        self.box.Add(self.canvas, 1, wx.GROW)
        subbox = wx.BoxSizer(wx.HORIZONTAL)

# ------
        self.ctrlSocietyButtonID =  GLOBAL_WIDGET_ID_BASE+1
        self.ctrlSocietyButton = wx.Button(self, self.ctrlSocietyButtonID , "Start")

        wx.EVT_BUTTON(self, self.ctrlSocietyButtonID, self.OnStartSociety)
        self.ctrlSocietyButton.SetBackgroundColour("BLACK")
        self.ctrlSocietyButton.SetForegroundColour("WHITE")
        #~ self.viewSocietyButton.SetDefault()
        subbox.Add(self.ctrlSocietyButton , flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, border=20)
        # ------
        self.viewSocietyButton = wx.Button(self, GLOBAL_WIDGET_ID_BASE+2, "View Agents")
        wx.EVT_BUTTON(self, GLOBAL_WIDGET_ID_BASE+2, self.OnViewSociety)
        self.viewSocietyButton.SetBackgroundColour("BLUE")
        self.viewSocietyButton.SetForegroundColour("YELLOW")
        #~ self.viewSocietyButton.SetDefault()
        subbox.Add(self.viewSocietyButton, flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, border=20)
        # ------
        self.Bind(EVT_AGENT_TASK_COUNT, self.AgentTaskCountUpdate)
        # ------
        self.ZoomPlusButton = wx.Button(self, GLOBAL_WIDGET_ID_BASE+3, "+")
        wx.EVT_BUTTON(self, GLOBAL_WIDGET_ID_BASE+3, self.OnZoomPlus)
        self.ZoomPlusButton.SetBackgroundColour(wx.GREEN)
        self.ZoomPlusButton.SetForegroundColour(wx.WHITE)

        subbox.Add(self.ZoomPlusButton, flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, border=20)

       # ------
        self.ZoomMinusButton = wx.Button(self, GLOBAL_WIDGET_ID_BASE+4, "-")
        wx.EVT_BUTTON(self, GLOBAL_WIDGET_ID_BASE+4, self.OnZoomMinus)
        self.ZoomMinusButton.SetBackgroundColour(wx.RED)
        self.ZoomMinusButton.SetForegroundColour(wx.WHITE)
        subbox.Add(self.ZoomMinusButton, flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, border=20)
       # ------
        #~ self.viewServletButton = wxButton(self, 15, "Servlet Options")
        #~ wx.EVT_BUTTON(self, 15, self.viewServletOptions)
        #~ self.viewServletButton.SetBackgroundColour(wxBLACK)
        #~ self.viewServletButton.SetForegroundColour(wxWHITE)
        #~ self.viewSocietyButton.SetDefault()
        #~ subbox.Add(self.viewServletButton, flag=wxALIGN_CENTER_VERTICAL | wxBOTTOM, border=20)

        # ------
        self.testServletButton = wx.Button(self, GLOBAL_WIDGET_ID_BASE+5, "Agent Probes")
        wx.EVT_BUTTON(self, GLOBAL_WIDGET_ID_BASE+5, self.AgentTaskCountUpdate)
        self.currTaskCount = None
        self.oldTaskCount = None
        self.testServletButton.SetBackgroundColour(wx.CYAN)
        self.testServletButton.SetForegroundColour(wx.BLACK)
        #~ self.viewSocietyButton.SetDefault()
        subbox.Add(self.testServletButton, flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, border=20)

        #~ wx.EVT_SOCIETYCONTROLLER_TEST(self, self.EventUpdate)
        self.box.Add(subbox, 0, wx.GROW)

        self.SetAutoLayout(True)
        self.SetSizer(self.box)
        self.bg_bmp = images.getGridBGBitmap()
        wx.EVT_ERASE_BACKGROUND(self, self.OnEraseBackground)
        wx.EVT_WINDOW_DESTROY(self, self.OnDestroy)
        ogl.OGLInitialize()

    def OnEraseBackground(self, evt):
        pass

    def AgentTaskCountUpdate(self, evt):
#            print >> sys.stdout, "AgentTaskCountUpdate"
            if self.societyReader is not None:
                self.oldTaskCount = self.currTaskCount
                self.currTaskCount = self.societyReader.readUniqueObjects(self.HOST, self.PORT)
                for o in self.currTaskCount.keys():
                    heat = 0
                    if self.oldTaskCount is None:
                      heat = self.currTaskCount[o]
                    elif self.oldTaskCount.get(o) is None:
                      heat = self.currTaskCount[o]
                    else:
                      heat = int(self.currTaskCount[o]) - int(self.oldTaskCount[o])
                    self.computeHeat(o, heat)
                #~ info = InformationPanel (140, 300, self.canvas, information=uniqueObjects)
                #~ self.canvas.addShape(info,     100, 100, wxBLACK_PEN, wxBrush("LIGHT STEEL BLUE", wxSOLID), '   unique Objects', "Yellow"  )
                #~ dc = wxClientDC(self.canvas)
                #~ self.canvas.PrepareDC(dc)
                #~ self.canvas.Redraw(dc)
            else: print >> sys.stdout, "WTF???"

    def OnZoomPlus(self, evt):
        if self.canvas.getSocietyStatus() == "active":
            z.setLevel(z.getLevel()   + 1)
            currentLevel = z.getLevel()
            self.canvas.OrganizeAgents(boxWidth=z.viewLevelData[currentLevel]["BOXWIDTH"],
            boxHeight=z.viewLevelData[currentLevel]["BOXHEIGHT"],
            pixelLevel=z.viewLevelData[currentLevel]["PIXELLEVEL"],
            fontSize=z.viewLevelData[currentLevel]["FONTSIZE"],
            theradius=z.viewLevelData[currentLevel]["RADIUS"])
        else:
            self.ErrorWindow()

    def OnZoomMinus(self, evt):
        if self.canvas.getSocietyStatus() == "active":
            z.setLevel(z.getLevel()-1)
            currentLevel = z.getLevel()
            self.canvas.OrganizeAgents(boxWidth=z.viewLevelData[currentLevel]["BOXWIDTH"],
            boxHeight=z.viewLevelData[currentLevel]["BOXHEIGHT"],
            pixelLevel=z.viewLevelData[currentLevel]["PIXELLEVEL"],
            fontSize=z.viewLevelData[currentLevel]["FONTSIZE"],
            theradius=z.viewLevelData[currentLevel]["RADIUS"])
        else:
            self.ErrorWindow()

    def OnStartSociety(self, evt):
        """
        We are limited to localhost currently!!!
        """
        self.NODE = None
        self.logfile = None
        win = CtrlDlg(self,wx.NewId(), self.log, "Start a Society", size=wx.Size(400, 300),style = wx.DEFAULT_DIALOG_STYLE)
        win.CenterOnScreen()
        val = win.ShowModal()
        if val != wx.ID_OK:
            return
        print "OK::", self.NODE
        rtn = self.startNode()
        if (rtn):
            self.societyRunning = True
            self.ctrlSocietyButton.SetBackgroundColour("WHITE")
            self.ctrlSocietyButton.SetForegroundColour("BLACK")
            self.ctrlSocietyButton.SetLabel("Stop")
            self.canvas.setSocietyActive()
            wx.EVT_BUTTON(self, self.ctrlSocietyButtonID, self.OnStopSociety)

    def OnStopSociety(self, evt):
        #~ signal.signal(signal.SIGINT|signal.SIG_DFL, self.spawnPID)
        if sys.platform[:3] in ('win', 'os2'):
            print 'must use WMI, Win32.all extensions'
        self.ctrlSocietyButton.SetBackgroundColour("BLACK")
        self.ctrlSocietyButton.SetForegroundColour("WHITE")
        self.ctrlSocietyButton.SetLabel("Start")
        wx.EVT_BUTTON(self, self.ctrlSocietyButtonID , self.OnStartSociety)

    def OnViewSociety(self, evt):
        agentList = []
        self.URL = None
        self.HOST = None
        self.PORT = None
        win = ProbeDlg(self,wx.NewId(), self.log, "Society Ping", size=wx.Size(400, 300),style = wx.DEFAULT_DIALOG_STYLE)
        win.CenterOnScreen()
        val = win.ShowModal()
        if val == wx.ID_OK:
            self.log.WriteText("URLDlg OK\n")
            self.log.WriteText(self.URL)
            #~ print "read...", self.URL, "host==", self.HOST,"port==", self.PORT
            societyreader = SocietyReader(self.URL)
            self.societyReader = societyreader
            #~ print "societyreader:", societyreader
            agentList = societyreader.readAgents()
            if agentList is None:
                dlg = wx.MessageDialog(self.frame, "Society not up as yet. Try again in a few seconds",
                          'Non-fatal Error', wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
            else:
                self.log.WriteText(str(agentList))
                self.canvas.CreateSociety(agentList)
                self.canvas.OrganizeAgents()

        else:
            self.log.WriteText("URLDlg Cancel\n")
        #~ print "Society Viewed"

    #~ def viewSociety(self, generator_file):
        """
        TODO
        """

        #~ print "creating society from  %s" % generator_file ### DEBUG -- remove this!
        #~ return ULHierarchy(uri='file:'+str(generator_file))
    def startNode(self):
        try:
            cip = os.environ['COUGAAR_INSTALL_PATH']
            execstring = cip+os.sep+'bin'+os.sep+'cougaar'
            print "EXEC STRING:", execstring, self.NODE
            args = None
            if self.logfile is not None:
                args = (execstring, self.NODE, "> "+self.logfile)
            else:
                args = (execstring, self.NODE)
            self.spawnPID = os.spawnv(os.P_NOWAIT,execstring, args);
            #~ print 'spawned...',execstring , ' ID=', self.spawnPID
        except KeyError:
            dlg = wx.MessageDialog(self.frame, "set 'COUGAAR_INSTALL_PATH' as an environmental variable",
                          'Fatal Error', wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True


    def computeHeat(self, agent, value):
        print "computeHeat:", agent, 'value:',value
        shape = self.canvas.shapeDict[str(agent)]
        # turn on the right color
        #~ color = self.computeColor(value)
        shape.SetBrush(wx.Brush(self.computeColor(value), wx.SOLID))
        dc = wx.ClientDC(self.canvas)
        self.canvas.PrepareDC(dc)
        self.canvas.Redraw(dc)

    def computeColor(self, agentValue):
        red = green = blue = 0
        agentValue = int(agentValue)
        agentValue = agentValue * 2
        if agentValue <= 0:
          red = green = blue = 40
        elif 0 <agentValue < 256:
            red = 0; green = agentValue; blue = 255 - agentValue
        elif  256 <= agentValue < 512:
            red = agentValue - 256; green = 255; blue = 0
        elif 512 <= agentValue  < 767:
            red = 255; green = 766 - agentValue; blue = 0
        else:
            red = 255; green = 0; blue = 0
        return wx.Colour(red, green, blue)

    def loadFromURL(self, aURL):
        file = urllib.urlopen(aURL)
        #~ self.log.WriteText(aURL+"\n\n")
        #~ for line in self.file.readlines():
            #~ self.log.WriteText(line)
        society =  SocietyFactory(uri='hierarchy.xml').parse()
        if society is not None:
            #~ print society
            self.hierarchy = MilitaryHierarchy(society)
            self.canvas.CreateSocieties(self.hierarchy)
            self.canvas.OrganizeAgents()



    def OnEraseBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
          dc = wx.ClientDC(self.GetClientWindow())

        # tile the background bitmap
        sz = self.GetClientSize()
        w = self.bg_bmp.GetWidth()
        h = self.bg_bmp.GetHeight()
        x = 0
        while x < sz.width:
            y = 0
            while y < sz.height:
                dc.DrawBitmap(self.bg_bmp, x, y)
                y = y + h
            x = x + w

    def OnDestroy(self, evt):
        # Do some cleanup
        print "agentController:OnDestroy - Check for running society and give option to terminate"
        if (self.societyRunning):
            dlg = wx.MessageDialog(self.frame, "A society is currently running.  Would you like AWB to stop it before you exit? " +
                                                                 "If you choose 'No' it will remain running in the background", 'Non-fatal Error', wx.YES_NO|wx.ICON_ERROR)
            val = dlg.ShowModal()
            if (val == wx.ID_YES):
                self.stopSociety()
            dlg.Destroy()
            
        
    def loadSociety(self, generator_file):
        """
        This wants to be nicely integrated with the GUI, such that
        When you select the file, an animation starts (similar to a busy watch cursor) and when the society is
        complete, an wxEvent is sent to the GUI. see exmaples in other parts of the application.
        use SocietyFactoryServer instead of SocietyFactory
        """
        m = re.compile('\.', re.IGNORECASE).split(str(generator_file))
        baseName = str(m[0])
        #~ print "creating society from  %s" % baseName ### DEBUG -- remove this!
        self.log.WriteText("file:" + generator_file)
        return SocietyFactory("file:" + generator_file).parse()
        
    def stopSociety(self):
        if (not self.societyRunning):
            return
        print "We still need code to stop a running society!"
        
#----------------------------------------------------------------------

    def OnCloseSociety(self,evt):
        if self.canvas.getSocietyStatus() == "active":
            self.canvas.MySocietyInit()
            print "Society Closed"
        else:
            self.ErrorWindow()
        #~ pass


    def viewServletOptions(self, evt):
        if self.canvas.getSocietyStatus() == "active":
            win = ServletProperties(self.canvas, -1, "Servlet Properties", size=wx.Size(300, 400),style = wx.DEFAULT_DIALOG_STYLE)
            win.CenterOnScreen()
            val = win.ShowModal()
        else:
            self.ErrorWindow()
        #~ pass
    def testServletPolling(self, evt):
        s = ServletDataReceiver("localhost", 8888)
        thread_id = thread.start_new_thread( s.serve, ())
        self.ServletPoller()
    def ServletPoller(self):
        agentMap = dict.fromkeys(self.hierarchy.getAgents(), -1)
        aPeer = xmlrpclib.Server('http://localhost:8888')
        data = aPeer.initServerMethods(agentMap)
        limit = 0
        for agent in agentMap.iterkeys():
                limit += 1
                if limit > 500: break
                tasks = aPeer.getGeneratedData(agent)
                #~ print "iteration:", limit, agent,  tasks
                evt = AgentTaskCountEvent((agent, tasks))
                wx.PostEvent(self, evt)


    def _ServletPoller(self):
            pass
    #~ def PlayRedraw(self, name):
        #~ shape = self.canvas.shapeDict[name]
        #~ shape.SetBrush(wxBrush(COLOURDB[r.randint(0, len(COLOURDB)) % len(COLOURDB )], wxCROSSDIAG_HATCH))
        #~ dc = wxClientDC(self.canvas)
        #~ self.canvas.PrepareDC(dc)
        #~ self.canvas.Redraw(dc)

    def ErrorWindow(self):
        #~ def __init__(self, parent, ID, title, pos=wxDefaultPosition, size=wxDefaultSize, style=wxDEFAULT_DIALOG_STYLE):
        win = ServerNotRunning(self.canvas, -1, "Server Inactive", pos=wx.DefaultPosition, size=wx.Size(500, 100), style = wx.DEFAULT_DIALOG_STYLE)
                         #style = wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME
        win.CenterOnScreen()
        val = win.ShowModal()



#----------------------------------------------------------------------



#----------------------------------------------------------------------
class RoundedRectangleShape(ogl.RectangleShape):
    def __init__(self, w=0.0, h=0.0):
        ogl.RectangleShape.__init__(self, w, h)
        self.SetCornerRadius(-0.3)

#----------------------------------------------------------------------
class MyEvtHandler(ogl.ShapeEvtHandler):
    def __init__(self, frame, log):
        ogl.ShapeEvtHandler.__init__(self)
        self.log = log
        self.statbarFrame = frame

    def OnLeftClick(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        print shape.__class__, shape.GetClassName()
        canvas = shape.GetCanvas()
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)

        if shape.Selected():
            shape.Select(False, dc)
            canvas.Redraw(dc)
            print shape.GetX(), shape.GetY()
        else:
            redraw = False
            shapeList = canvas.GetDiagram().GetShapeList()
            toUnselect = []
            for s in shapeList:
                if s.Selected():
                    # If we unselect it now then some of the objects in
                    # shapeList will become invalid (the control points are
                    # shapes too!) and bad things will happen...
                    toUnselect.append(s)

            shape.Select(True, dc)

            if toUnselect:
                for s in toUnselect:
                    s.Select(False, dc)
                canvas.Redraw(dc)

        #~ self.UpdateStatusBar(shape)

    def OnEndDragLeft(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        self.base_OnEndDragLeft(x, y, keys, attachment)
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)
        #~ self.UpdateStatusBar(shape)


    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):

        self.base_OnSizingEndDragLeft(pt, x, y, keys, attch)
        #~ self.UpdateStatusBar(self.GetShape())


    def OnMovePost(self, dc, x, y, oldX, oldY, display):

        self.base_OnMovePost(dc, x, y, oldX, oldY, display)
        #~ self.UpdateStatusBar(self.GetShape())

    def OnRightClick(self, x, y, keys = 0, attachment = 0):
        self.log.WriteText("RIGHTCLICK in Event Handler: %s\n" % self.GetShape())
        shape = self.GetShape()
        print shape.__class__, shape.GetClassName()
        # if it's an information panel, then delete it on right click...
        canvas = shape.GetCanvas()
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        FacetPropertiesID = shape.GetRegionName(0) + " Properties"

        win = FacetProperties(shape, canvas, -1, FacetPropertiesID, size=wx.Size(300, 400),style = wx.DEFAULT_DIALOG_STYLE)
                         #style = wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME

        win.CenterOnScreen()
        if win.ShowModal() == wx.ID_OK:
            self.log.WriteText("You pressed OK\n")
        else:
            self.log.WriteText("You pressed Cancel\n")


class ServerNotRunning(wx.Dialog):
    def __init__(self, parent, ID, title, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE):
        pre = wx.PreDialog()
        pre.Create(parent, ID, title, pos, size, style)
        self.this = pre.this

        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, -1, "The Society is inactive")
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        box = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(self, wx.ID_OK, " OK ")
        btn.SetDefault()
        btn.SetHelpText("The OK button completes the dialog")
        box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.AddSizer(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)
#----------------------------------------------------------------------

class __Cleanup:
    cleanup = ogl.OGLCleanUp()
    def __del__(self):
        self.cleanup()

# when this module gets cleaned up then wxOGLCleanUp() will get called
__cu = __Cleanup()

overview = """\
The Object Graphics Library is a library supporting the creation and
manipulation of simple and complex graphic images on a canvas.

"""
#----------------------------------------------------------------------

def runTest(frame, nb, log):
    win = AgentControllerViewer(nb,frame,  log)
    return win

if __name__ == '__main__':
    import sys,os
    import run
    run.main(['', os.path.basename(sys.argv[0])])