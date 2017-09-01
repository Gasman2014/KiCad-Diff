
import deepdiff, sys, pprint
from deepdiff import DeepDiff  # For Deep Difference of 2 objects
from deepdiff import DeepSearch
from pprint import *


t1 = {"for life": "vegan", "ingredients": ["no meat", "no eggs", "no dairy"]}
t2 = {"for life": "vegan", "ingredients": ["veggies", "tofu", "soy sauce"]}
#print (DeepDiff(t1, t2, exclude_paths={"root['ingredients']"}))
print (DeepDiff(t1, t2))
'''
t1 = '((module Mounting_Holes:MountingHole_5.5mm) (layer F.Cu) (tedit 56D1B4CB) (tstamp 598A07F7)(at 112.28 125.28)(descr "Mounting Hole 5.5mm, no annular"))'
t2= '((module Mounting_Holes:MountingHole_5.5mm) (layer F.Cu) (tedit 56D1B4CB) (tstamp 598A07F7)(at 112.28 125.26)(descr "Mounting Hole 5.5mm, no annular"))'
'''
t1 = "'module': 'Mounting_Holes_MountingHole_5.5mm', 'layer': 'F.Cu', 'tedit': '56D1B4CB', 'tstamp': '598A07F7', 'location': '112.28_125.28', 'descr': 'Mounting Hole 5.5mm no annular'"
t2 = "'module': 'Mounting_Holes_MountingHole_5.5mm', 'layer': 'F.Cu', 'tedit': '56D1B4CB', 'tstamp': '598A07F7', 'location': '112.28_125.28', 'descr': 'Mounting Hole 3.5mm no annular'"


def clean(s):
    s = s.replace(")",  "]")
    s = s.replace("(", "[")
    s = s.replace(" [", ", [")
    s = s.replace("][", "], [")
    s = s[1:]
    print(s)
    return(s)
'''
def clean(s):
    s = s.replace("(",  "*(")
    s = s.replace(")",  ")*")
    s = s.replace(" ",  "_")
    s = s.replace("*_*",  ", ")
    s = s.replace("_*(",  ", (")
    s = s.replace("**(",  ", (")
    s = s.replace("*(",  "(")
    s = s.replace(")*",  ")")
    print(s)
    return(s)

t1 = clean(t1)
t2 = clean(t2)
'''


ddiff = DeepDiff(t1, t2, ignore_order=False)
print("DeepDiff")
pprint(ddiff, indent=6)

ddiff_verbose0 = DeepDiff(t1, t2, verbose_level=0, view='tree')
print("DeepDiff_Verbose_0")
print(ddiff_verbose0)

ddiff_verbose1 = DeepDiff(t1, t2, verbose_level=1, view='tree')
print("DeepDiff_Verbose_1")
print(ddiff_verbose1)

ddiff_verbose1 = DeepDiff(t1, t2, verbose_level=2, view='tree')
print("DeepDiff_Verbose_2")
print(ddiff_verbose1)

set_of_values_changed = ddiff_verbose1['values_changed']
print("DeepDiff_Set")
print(set_of_values_changed)

(changed,) = set_of_values_changed
print("DeepDiff_Set_Changed1")
print(changed)
print("DeepDiff_Set_Changed_T1")
pprint(changed.t1)
print("DeepDiff_Set_Changed_T2")
print(changed.t2)
print("DeepDiff_Set_Changed_UP")
pprint(changed.up)
