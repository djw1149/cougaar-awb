#Host.py
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
import types
from node import Node
from facet import Facet

class Host:

  def __init__(self, name=None, rule='BASE'):
    """Constructs a host with the optional name  """
    self.name = name
    self.society = None
    self.nodes = {}
    self.nodelist = [] # for testing iterators
    self.facets = []
    self.rule = str(rule)


  def __str__(self):
    return "Host:"+ self.name+":RULE:"+self.rule
    
    
  def add_entity(self, entity):  # currently, used only to add facets
    if type(entity) == types.ListType:  # will be a list of facet objects
      for each_thing in entity:
        self.add_facet(each_thing)
    else:
      raise Exception, "Attempting to add unknown Host attribute"
  
  def delete_entity(self):
    self.society.delete_host(self)
  
  def add_node(self, node):
    if isinstance(node, Node):
      node.host = self
      self.nodes[node.name] = node
      self.nodelist.append(node) # only for testing iterators
      return node
    if isinstance(node, types.StringType):
      newNode = Node(node)
      self.nodes[node] = newNode
      self.nodelist.append(newNode) # only for testing iterators     
      self.nodes[node].host = self
      return self.nodes[node]

  def delete_node(self, node):
    del self.nodes[node.name]
    self.nodelist.remove(node)
  
  def get_node(self, index):
    return self.nodelist[index]

  def add_nodes(self, nodes):
    if isinstance(nodes, types.ListType):
      for n in nodes: self.add_node(n)

  def each_facet(self):
    for facet in self.facets: # only for testing iterators
      yield facet

  def remove_facet(self, component_classname):
    print "Host::remove_facet() not implemented"

  def remove_all_facets(self):
    self.facets = []

  def delete_facet(self, facet):
    self.facets.remove(facet)

  def add_facet(self, facet):
    #facet arg could be either a Facet instance or a facet value string
    if isinstance(facet, Facet):
      facet.parent = self
      self.facets.append(facet)
    else:
      fac = Facet(facet)
      fac.parent = self
      self.facets.append(fac)

  def get_facet(self, index):
    return self.facets[index]

  def get_facet_value(self, key):
    for facet in self.facets:
      if facet.has_key(key):
        return facet[key]
    return None

  def set_rule(self, newRule):
        self.rule = str(newRule)

  def clone(self):
    host = Host(self.name)
    host.add_nodes(self.nodes)
    return host
    
  def to_xml(self):
    xml = "  <host name='"+ self.name + "'>\n"
    #for node in self.nodes.keys():
      #xml = xml + self.nodes[node].to_xml()
    for facet in self.facets:
      xml = xml + facet.to_xml()
    for node in self.nodelist:
      xml = xml + node.to_xml()
    xml = xml +  "  </host>\n"
    return xml

  def to_python(self):
    script = "host = Host('"+self.name+"')\n"
    script = script + "society.add_host(host)\n"
    for node in self.nodes.keys():
      script = script + self.nodes[node].to_python()   
    return script
    
    
  def each_node(self):
    for node in self.nodelist: # for testing iterators
      yield node


