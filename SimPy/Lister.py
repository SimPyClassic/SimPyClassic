#!/usr/bin/env python
# $Revision: 1.1.1.15 $ $Date: 2008/03/03 13:56:37 $ kgm
"""Lister 1.9.1
Pretty-printer for SimPy class objects
"""
__version__ = '1.9.1 $Revision: 1.1.1.15 $ $Date: 2008/03/03 13:56:37 $'

class Lister(object):
    indent=0
    def __str__(self):
        Lister.indent+=1
        result= ("<Instance of %s, id %s:\n%s"%(self.__class__.__name__,
                                               id(self),self.attrnames()))+"\t"*(Lister.indent-1)+">"
        Lister.indent-=1
        return result
    
    def attrnames(self):
        result=''
        for attr in self.__dict__.keys():
            if attr[:2] == "__": #builtin
                pass
            elif attr[0]=="_": #private
                pass
            else:
                result=result+"\t"*Lister.indent+".%s=%s\n" %(attr,self.__dict__[attr])
        return result
    def __repr__(self):
        Lister.indent+=1
        result= ("<Instance of %s, id %s:\n%s"%(self.__class__.__name__,
                                               id(self),self.attrnames()))+"\t"*(Lister.indent-1)+">"
        Lister.indent-=1
        return result

