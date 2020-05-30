#!/usr/bin/python

from .colors import *
from .. import __version__

def banner():
    banner = """%s%s

 oooo                                .o8                      .o8  oooo    
 `888                               "888                     "888  `888    
  888  oooo    ooo ooo. .oo.    .oooo888   .oooo.        .oooo888   888    
%s%s  888   `88.  .8'  `888P"Y88b  d88' `888  `P  )88b      d88' `888   888%s%s    
%s%s  888    `88..8'    888   888  888   888   .oP"888 8888 888   888   888%s%s    
  888     `888'     888   888  888   888  d8(  888      888   888   888    
 o888o     .8'     o888o o888o `Y8bod88P" `Y888""8o     `Y8bod88P" o888o   
       .o..P'                                                                  
       `Y8P'\t\t\t\t%s%sLYNDA %s%s%s\n\t\t\t\t\t%s%sLYNDA %s%s LYNDA \n\t\t\t\t\t%s%sLYNDA %s%sLYNDA


""" % (fc, sb, fm, sb, fc, sb, fm, sb, fc, sb, fy,sb, fg, sd, __version__, fy,sb, fg, sd, fy,sb, fg, sd)
    return banner
