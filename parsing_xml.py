import xml.etree.ElementTree as ET
import pandas as pd
import re
import sys
import nltk 

#Shortcut to set default to empty string instead Nonetype
empty_if_none = lambda s: s if s else ''


def text1(root, ns=None):
    '''
    gets the text out of the definitions
    This functions only takes the text, formulas are ignored
    Replace newlines with a blank space.
    '''
    def_str = empty_if_none(root.text)

    for d in list(root):
        def_str += empty_if_none(d.text)
        #If d has a <Math> child then search for tails
        math_elements = d.findall('latexml:Math', ns)
        for m in math_elements:
            def_str += empty_if_none(m.tail)
        def_str += empty_if_none(d.tail)
    return def_str.lower().replace('\n', ' ')

def recutext1(root, nsstr='{http://dlmf.nist.gov/LaTeXML}'):
    ret_str = '' #empty_if_none(root.text)
    for el in list(root):
        if el.tag != (nsstr + 'Math'):
            ret_str += empty_if_none(el.text)
            ret_str += empty_if_none(el.tail)
            ret_str += recutext1(el, nsstr)
        else:
            ret_str += empty_if_none(el.tail)
    return ret_str.lower().replace('\n', ' ')



class DefinitionsXML(object):
    def __init__(self, file_path):
        '''
        Read an xml file and parse it
        '''
        try:
            self.exml = ET.parse(file_path)
        except ET.ParseError:
            raise ET.ParseError('Could not parse file %s'%file_path)

        self.ns = {'latexml': 'http://dlmf.nist.gov/LaTeXML' }
        self.def_lst = []

    def find_definitions(self):
        '''
        finds all definitions in the parsed xml
        and returns a list of them
        '''
        for e in self.exml.iter():
            att_class = e.attrib.get('class', None)
            if att_class:
                if re.match(r'ltx_theorem_[definto]+$', att_class):
                    self.def_lst.append(e)
        return self.def_lst

    def para_p(self, root):
        '''
        The xml format for a definition is as follows:
        <theorem class="ltx_theorem_defn">
        <title>  </title>
        <para>
          <p>
          Here goes the text of the definition
          </p>
          </para>
        </theorem>
        This function gets a theorem root and returns the p tag
        '''
        #return root.findall('./latexml:para/latexml:p', self.ns)[0]
        return root.findall('.//latexml:para', self.ns)[0]

    def get_def_text(self, method=recutext1):
        '''
        uses the method specified to get the text from 
        the definitions in self.def_lst
        '''
        if self.def_lst:
            pass
        else:
            self.find_definitions()
        return [method(self.para_p(r)) for r in self.def_lst]

    def write_defs(self, path):
        '''
        Append the list of found definitions to the text file at path
        '''
        with open(path,'a') as text_file:
            for d in self.get_def_text():
                text_file.write(d+'\n')
        return 0


if __name__ == "__main__":
    '''
    Usage: python parsing_xml.py fileList FileToStoreDefs
    '''
    allfiles = sys.argv[1:-1]
    defs_file = sys.argv[-1]
    for f in allfiles:
        try:
            DD = DefinitionsXML(f)
            print('writing file: %s'%f, end='\r')
            DD.write_defs(defs_file)
        except ET.ParseError:
            print('Error parsing file: %s'%f, end='\n')

