# society_factory.py
#
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

from __future__ import generators
import os, sys, traceback
from wxPython.wx import *
from xml.dom import minidom
from Ft.Xml.Domlette import Print, PrettyPrint
from Ft.Xml.Domlette import NonvalidatingReader

from society import *
from host import *
from node import *
from agent import *
from facet import *
from component import *
from argument import *
from parameter import *
import types

class SocietyFactory:

  def __init__(self, uri=None, xmlString=None):
    global doc
    if uri is not None:
      doc = NonvalidatingReader.parseUri(uri)
    elif xmlString is not None:
      uri = 'file:bogusFile.txt' # Required by Domlette or it issues a warning.
      doc = NonvalidatingReader.parseString(xmlString, uri)

  def parse(self):
    societyElement = doc.childNodes[0]
    society = Society(societyElement.getAttributeNS(None, "name"))
    #~ print 'Society==>', society.name
    if societyElement.hasChildNodes():
      societyElements = societyElement.childNodes
      for societyElem in societyElements:
        if societyElem.nodeType == minidom.Node.ELEMENT_NODE:
          #~ print societyElem.nodeName, societyElem.nodeValue, societyElem.nodeType
          if societyElem.nodeName == 'facet':
            #~ print "Facet value ==>", self.attributeDict(societyElem)
            society.add_facet(self.attributeDict(societyElem))
          elif societyElem.nodeName == 'host':
            newHost = Host(str(societyElem.getAttributeNS(None, "name")))
            society_host = society.add_host(newHost)
            if society_host is None:
              raise Exception, "Parsing failed due to duplicate host: " + newHost.name
            newHost.parent = society
            #~ print "Host Name: ", society_host.name
            if societyElem.hasChildNodes():
              hostElements = societyElem.childNodes
              # note we need to reflect facets too  differentiate between facets and nodes in the node.nodeValue
              for xmlNode in hostElements:
                if xmlNode.nodeType == minidom.Node.ELEMENT_NODE:
                  #~ print xmlNode.nodeName, xmlNode.nodeValue, xmlNode.nodeType
                  if xmlNode.nodeName == 'facet':
                    newHost.add_facet(self.attributeDict(xmlNode))
                  elif xmlNode.nodeName == 'node':
                    nodename = xmlNode.getAttributeNS(None, "name")
                    #~ print "Node name ==>", nodename
                    newNode = newHost.add_node(str(xmlNode.getAttributeNS(None, "name")))
                    if newNode is None:
                      raise Exception, "Parsing failed due to duplicate node: " + nodename
                    if xmlNode.hasChildNodes():
                      nodeElements = xmlNode.childNodes
                      self.populateNodeElements(newNode, nodeElements)
    return society

  def attributeDict(self, this):
    d = {}
    attributes = this.attributes
    values = attributes.values()
    for v in values:
      d[str(v.name)] = str(v.value)
    return d

  def populateNodeElements(self, thisNode, xmlNodes):
    for xmlNode in xmlNodes:
      if xmlNode.nodeName == 'facet':
        thisNode.add_facet(self.attributeDict(xmlNode))
      elif xmlNode.nodeName == 'vm_parameter':
        thisNode.add_vm_parameter( VMParameter(value=xmlNode.childNodes[0].data.strip()) )
        #~ print 'vm_parameter:', xmlNode.childNodes[0].data.strip()
      elif xmlNode.nodeName == 'env_parameter':
        thisNode.add_env_parameter( EnvParameter(value=xmlNode.childNodes[0].data.strip()) )
        #~ print 'env_parameter:', xmlNode.childNodes[0].data.strip()
      elif xmlNode.nodeName == 'prog_parameter':
        thisNode.add_prog_parameter( ProgParameter(value=xmlNode.childNodes[0].data.strip()) )
        #~ print 'prog_parameter:', xmlNode.childNodes[0].data.strip()
      elif xmlNode.nodeName == 'class':
        thisNode.klass = xmlNode.childNodes[0].data.strip()
        #~ print 'class:', xmlNode.childNodes[0].data.strip()
      elif xmlNode.nodeName == 'agent':
        agentDict = self.attributeDict(xmlNode)
        newAgent = thisNode.add_agent(agentDict['name'])
        if newAgent is None:
          raise Exception, "Parsing failed due to duplicate agent: " + agentDict['name']
        if agentDict.has_key('class'):
          newAgent.klass = agentDict['class']
        #~ print 'AGENT:', newAgent
        self.populateAgentElements(newAgent, xmlNode.childNodes)
      elif xmlNode.nodeName == 'component':
        compAttrs = self.attributeDict(xmlNode)
        component = Component(compAttrs.get('name'), compAttrs['class'], compAttrs.get('priority'), compAttrs.get('insertionpoint'))
        thisNode.add_component(component)
        #~ print 'NODE COMPONENT:', component
      else:
        if xmlNode.nodeType == minidom.Node.ELEMENT_NODE:
          print 'UNKNOWN NODE TYPE:', xmlNode.nodeName

  def populateAgentElements(self, thisAgent, xmlNodes):
    for xmlNode in xmlNodes:
      if xmlNode.nodeName == 'facet':
        thisAgent.add_facet(self.attributeDict(xmlNode))
      elif xmlNode.nodeName == 'component':
        compAttrs = self.attributeDict(xmlNode)
        #~ print "component name :", compAttrs['name'], " class :",  compAttrs['class'], " priority :",  compAttrs['priority'], " ip:",  compAttrs['insertionpoint']
        component = Component(compAttrs.get('name'), compAttrs['class'], compAttrs.get('priority'), compAttrs.get('insertionpoint'))
        thisAgent.add_component(component)
        if xmlNode.hasChildNodes():
          argNodes = xmlNode.childNodes
          for argNode in argNodes:
            if argNode.nodeType == minidom.Node.ELEMENT_NODE:
              #~ print "argument:", argNode.childNodes[0].data.strip()
              component.add_argument(str(argNode.childNodes[0].data.strip()))

def society_from_python(filename):
  globals = {}
  locals = {}
  execfile(filename, globals, locals)
  society = locals['society']
  return society


class TransformationRule:
  def __init__(self, name):
    global society
    self.name = name
    self.fire_count = 0
    self.rule = None
    self.fired = False
    self.society = None
    #~ self.isRubyRule = False

  def set_rule(self, ruleText):
    self.rule = str(ruleText.rule)
    #~ self.isRubyRule = ruleText.isRubyRule

  def fire(self):
    self.fire_count += 1
    self.fired = True

  def reset(self):
    self.fired = False

  def has_fired(self):
    return self.fired

  def execute(self, society):
    #~ wxLogMessage("Running rule '"+ str(self.name)+ "' on society "+ str(society.name))
    print "Running rule '"+ str(self.name)+ "' on society "+ str(society.name)
    try:
      #ugly ugly replacement to get around stray CR's that can 
      #be introduced when editing on multiple  platforms
      self.rule = self.rule.replace(chr(13), '')
      exec self.rule
    except Exception, args:
      print "exec self.rule exception"
      print str(args)


class TransformationEngine:
  def __init__(self, society, parent, max_loop=300):
    self.MAXLOOP = max_loop
    self.society = society
    self.rules = []
    self.parent = parent

  def add_rule(self, rule):
    if isinstance(rule, TransformationRule): self.rules.append(rule)

  def transform(self):
    loop = True
    count =0
    while loop is True and count < self.MAXLOOP:
      loop = False
      for rule in self.rules:
        try:
          rule.execute(self.society)
        except Exception, args:
          print "ERROR transforming the Society."
          traceback.print_exc()
          self.log.WriteText("Transformation failed.\n")
          self.log.WriteText("%s\n" % str(args))

        if rule.fired == True:  # if rule fired, we'll fire it again...until it doesn't fire any longer
          rule.reset()
          loop = True
      count = count + 1
      print "loop ", count
    for rule in self.rules:
      # Sending the following msg to the log file seems to cause Linux to hang, perhaps
      # because this is running in a separate thread and a deadlock occurs (see wxPython bug 496697).
      #~ wxLogMessage("Rule '" + rule.name + "' fired " + str(rule.fire_count) + " times.")
      print "Rule '" + rule.name + "' fired " + str(rule.fire_count) + " times."
    if count == self.MAXLOOP:
      msg = '''The transformation ran to the loop limit.  This may indicate there was an error and the
transformation did not complete correctly.'''
      dlg = wxMessageDialog(self.parent, msg, style = wxCAPTION | wxOK |  wxTHICK_FRAME | wxICON_EXCLAMATION)
      val = dlg.ShowModal()
      dlg.Destroy()
    return self.society



def main():
  #factory = SocietyFactory('tiny.xml')
  factory = QikSocietyFactory('SB-1AD-STRIPPED_TEST.xml')
  factory.parse()

if __name__ == "__main__":
  main()
