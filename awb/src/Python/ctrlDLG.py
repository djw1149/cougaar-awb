# CONVERTED2DOT5 = TRUE

import sys
import re
import os

import wx
from wxPython.help import *

import images
import pickle

#---------------------------------------------------------------------------


NODE_TXTCTRL_ID = 701

class CtrlDlg(wx.Dialog):
    def OnSetFocus(self, evt):
        print "OnSetFocus"
        evt.Skip()
    def OnKillFocus(self, evt):
        print "OnKillFocus"
        evt.Skip()

    def __init__(self, parent, ID, log, title, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE):
        pre = wx.PreDialog()
        pre.Create(parent, ID, title, pos, size, style)
        self.this = pre.this
        self.parent = parent
        self.log = log

 #~ ------------------------------
        nodeLbl = wx.StaticText(self, -1, "Node")
        default = "enter/select node to run"
        self.nodeTxtCtrl = wx.TextCtrl(self, NODE_TXTCTRL_ID, default, size=(300, -1), style=wx.TE_PROCESS_ENTER )

        wx.EVT_TEXT_ENTER(self, self.nodeTxtCtrl.GetId(), self.OnOk)

        self.bg_bmp = images.getGridBGBitmap()
        wx.EVT_ERASE_BACKGROUND(self, self.OnEraseBackground)
        #---------------------------------
        # button fixtures
        bBrowseID = wx.NewId()
        bBrowse = wx.Button(self, bBrowseID, "browse")
        bBrowse.SetBackgroundColour("BLACK")
        bBrowse.SetForegroundColour("WHITE")

        wx.EVT_BUTTON(self, bBrowse.GetId(), self.OnBrowse)

        bOk = wx.Button(self, wx.ID_OK, "OK")
        bOk.SetDefault()
        wx.EVT_BUTTON(self, bOk.GetId(), self.OnOk)
        bCan = wx.Button(self, wx.ID_CANCEL, "Cancel")
        wx.EVT_BUTTON(self, bCan.GetId(), self.OnCancel)

        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(bBrowse, 0, wx.GROW|wx.ALL, 4)
        bsizer.Add(bOk, 0, wx.GROW|wx.ALL, 4)
        bsizer.Add(bCan, 0, wx.GROW|wx.ALL, 4)

        sizer = wx.FlexGridSizer(cols=3, hgap=6, vgap=6)
        sizer.AddMany([nodeLbl, self.nodeTxtCtrl, (0,0),
                        (0,0),bsizer,(0,0),])
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(sizer, 0, wx.ALL, 25)



        self.SetSizer(border)
        self.SetAutoLayout(True)
# ----------------------------------------------


    def OnBrowse(self, evt):
        fileDialog = wx.FileDialog(self, message="Choose a node xml file", wildcard = "*.xml", style=wx.OPEN  )
        if fileDialog.ShowModal() == wx.ID_OK:
           self.nodeTxtCtrl.SetValue( fileDialog.GetPath())
        fileDialog.Destroy()

    def OnOk(self, evt):
        self.log.WriteText('OnOk: %s, %s\n' % (self.nodeTxtCtrl.GetValue(),  evt.GetId()))
        self.parent.NODE = self.nodeTxtCtrl.GetValue()
        self.SetReturnCode(wx.ID_OK)
        self.Destroy()


    def OnCancel(self, evt):
        self.SetReturnCode(wx.ID_CANCEL)
        self.Destroy()
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


#---------------------------------------------------------------------------

def runTest(frame, nb, log):
    win = URLDlg(nb, log)
    return win

if __name__ == '__main__':
    import sys,os
    import run
    run.main(['', os.path.basename(sys.argv[0])])