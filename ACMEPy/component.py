#Component.py
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
from argument import Argument

class Component:
   # Construct a plugin
   #
   # data:: [String] the plugin data
   #
  def __init__(self, name=None, klass=None, priority = None, insertionpoint=None, rule='BASE'):
    self.name = name
    self.klass = klass
    self.priority = priority
    self.insertionpoint = insertionpoint
    self.arguments = []
    self.rule = str(rule)
    self.parent = None
    self.prev_parent = None
    
  def set_attribute(self, attribute, value):
    # both args must be strings
    if attribute.lower() == 'name':
      self.name = value
    elif attribute.lower() == 'klass':
      self.klass = value
    elif attribute.lower() == 'priority':
      self.priority = value
    elif attribute.lower() == 'insertionpoint':
      self.insertionpoint = value
    elif attribute.lower() == 'rule':
      self.rule = value
    else:
      raise Exception, "Attempting to set unknown Component attribute: " + attribute.lower()
    self.parent.society.isDirty = True

  def delete_entity(self):
    '''Deletes itself from component list of parent node or agent.'''
    self.parent.delete_component(self)
  
  def delete_from_prev_parent(self):
    if self.prev_parent is not None:
      self.prev_parent.delete_component(self)
    else:
      self.delete_entity()
  
  def has_changed_parent(self):
    return self.parent != self.prev_parent
  
  def delete_argument(self, argument):
    self.arguments.remove(argument)
    del argument
    self.parent.society.isDirty = True
  
  def add_entity(self, entity):
    if isinstance(entity, Argument):
      entity.prev_parent = entity.parent
      self.add_argument(entity)
    else:
      raise Exception, "Attempting to add unknown Component attribute"

  def add_argument(self, argument):
    if isinstance(argument, Argument):
      self.arguments.append(argument)
      argument.parent = self
      self.parent.society.isDirty = True
    elif type(argument) == types.StringType:  # must be a string
      arg = Argument(argument)
      self.add_argument(arg)
    else:
      raise Exception, "Attempting to add invalid Argument type"
  
  def get_argument(self, index):
    return self.arguments[index]
  
  def each_argument(self):
    for argument in self.arguments: # only for testing iterators
      yield argument
  
  def has_argument(self, argValue):
    for argument in self.arguments:
      if argument.name == argValue:
        return True
    return False
  
  def __str__(self):
    return "Component:"+self.name+":RULE:"+self.rule
  
  def set_rule(self, newRule):
    self.rule = str(newRule)
    self.parent.society.isDirty = True
  
  def getStrippedName(self):
    index = self.name.find('|')
    if index > -1 and self.parent is not None and self.name[:index] == self.parent.name:
      return self.name[index+1:]
    else:
      return self.name
  
  def rename(self, newName):
    self.name = newName
    self.parent.society.isDirty = True
    return self.name
  
  def clone(self):
    component = Component(self.name, self.klass, self.priority, self.insertionpoint, self.rule)
    for arg in self.arguments:
      new_arg = arg.clone()
      component.add_argument(new_arg)
      new_arg.component = component
    return component
  
  def to_xml(self):
    xml =  "        <component name='"+str(self.name)+"' class='"+str(self.klass)+"' priority='"+str(self.priority)+"' insertionpoint='"+str(self.insertionpoint)+"'>\n"
    for a in self.arguments[:]:
      xml = xml + a.to_xml()
    xml = xml + "        </component>\n"
    return xml
    
  def to_python(self):
    script = "component = Component(name='"+self.name+"', klass='"+self.klass+"', priority='"+str(self.priority)+"', insertionpoint='"+self.insertionpoint+"')\n"
    script = script + "agent.add_component(component)\n"
    for a in self.arguments:
      script = script + a.to_python()
    return script
  
  def to_ruby(self, numTabs):
    if self.parent.isNodeAgent():
      # it's a component of a node
      script = "      node.agent.add_component('" + self.name + "') do |c|\n"
    else:
      #it's a component of an agent
      script = "        agent.add_component('" + self.name + "') do |c|\n"
    indent = "  " * numTabs
    script = script + indent + "c.classname = '" + self.klass + "'\n"
    script = script + indent + "c.priority = '" + self.priority + "'\n"
    script = script + indent + "c.insertionpoint = '" + self.insertionpoint + "'\n"
    for a in self.arguments:
      script = script + a.to_ruby(numTabs)
    indent = "  " * (numTabs - 1)
    script = script + indent + "end\n"
    return script
