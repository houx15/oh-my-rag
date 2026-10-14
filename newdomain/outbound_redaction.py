"""Deterministic additional redaction; never weakens the existing outbound screen.

Preserve only institution literals already approved by the frozen policy.
All other exact denylist matches are replaced, including coincidental matches.
Original source/question records stay private and unchanged.
"""
import re
from newdomain.institution_fields import _CONTACT,_SECRET

class OutboundRedactor:
 def __init__(self,names,policy):
  if not isinstance(names,list)or any(not isinstance(x,str)or not x for x in names):raise ValueError('denylist')
  self.names=sorted(set(names),key=lambda x:(-len(x),x))
  self.approved=sorted({x['value']for x in policy['source_cells']},key=lambda x:(-len(x),x))
 def text(self,value):
  if _SECRET.search(value):raise ValueError('credential-like material must not enter benchmark')
  saved=[]
  for literal in self.approved:
   if literal in value:
    token='\x00APPROVED'+str(len(saved))+'\x00';value=value.replace(literal,token);saved.append((token,literal))
  for name in self.names:value=value.replace(name,'[已隐去姓名]')
  value=_CONTACT.sub('[已隐去联系信息]',value)
  for token,literal in saved:value=value.replace(token,literal)
  return value
 def value(self,obj):
  if isinstance(obj,str):return self.text(obj)
  if isinstance(obj,list):return [self.value(x)for x in obj]
  if isinstance(obj,dict):return {k:self.value(v)for k,v in obj.items()}
  return obj
