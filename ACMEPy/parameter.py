#Parameter.py
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
from agent import Agent


class Parameter:
  def __init__(self, value=None, type="Parameter", rule='BASE'):
    self.type = str(type)
    self.value = str(value)
    self.rule = rule
    
  def __str__(self):
    return (self.type+":"+self.value)


class VMParameter(Parameter):
  def __init__(self, value=None, type="VMParameter"):
    Parameter.__init__(self, value=value, type=type)
  def to_xml(self):
    return "<vm_parameter>" + self.value +"</vm_parameter>\n"    
    
class ProgParameter(Parameter):
  def __init__(self, value=None, type="ProgParameter"):
    Parameter.__init__(self, value=value, type=type)
  def to_xml(self):
    return "<prog_parameter>" + self.value +"</prog_parameter>\n"
    
class EnvParameter(Parameter):
  def __init__(self, value=None, type="EnvParameter"):
    Parameter.__init__(self, value=value, type=type)
  def to_xml(self):
    return "<env_parameter>" + self.value +"</env_parameter>\n"    
  
def unitTest():
  p = Parameter(value='Test-Parameter')
  v = VMParameter(value='-Dorg.cougaar.node.name=1AD_TINY')
  e = EnvParameter(value='DISPLAY=AD:0.0')
  
  print v
  print p
  print e
if __name__ == '__main__':
  unitTest()
