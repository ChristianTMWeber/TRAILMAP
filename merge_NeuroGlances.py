# Merge two or more neuroglancer urls, 
# such that the image contents from all the URLs 
# are accessible from a single URL, 
# and shown there as different layers
#


import urllib.parse

import re


import argparse # to parse command line options


def initilizeArgParser( parser = argparse.ArgumentParser(
    description="") ):

    parser.add_argument("NeuroGlancerURLs", type=str,nargs='*',
        help="List of Neuglancer urls that we want to merge" )

    args = parser.parse_args()

    return args


def ensureURLType( URL: "string or list(str)") -> "list(str)":

    if len(URL) == 1 :
        URL = URL[0].split() # split the string at the white space


    assert "!" in URL[0], \
    "Arguments to 'merge_NeuroGlances.py' have to be passed in single 'quotation marks', so that the exclamation mark '!' is preserved "

    return URL

def getNeuroGlancerLayers( URLsNoQuote : "list(str)", brackets = ("\\[","\\]")) -> "list(str)":
    # content within a given URL is listed between rectangular brackets.
    # so let's find everything within rectangular bracket

    # find 0 or more of any character (except new line):    .*
    # find everything after a '[':       (?<=\\[).* 
    # find everything before a ']':    .*(?=\\])


    regexPattern_stuffBetweenBrackets = "(?<=%s).*(?=%s)" % (brackets[0],brackets[1])

    layerContents = []

    for URL in URLsNoQuote:

        layerContents.append(  re.search(regexPattern_stuffBetweenBrackets ,URL).group() )

    return layerContents


def makeMergedLayerURL( URLsQuotationMarks : "list(str)", 
    brackets = (urllib.parse.quote("["), urllib.parse.quote("]")) ) -> "str":
    # get the various URLs
    # find out the layer definitions
    # and provide a single URL containing all the layers


    URLsNoQuote = [urllib.parse.unquote(URL) for URL in  URLsQuotationMarks]

    layerDefinitions = getNeuroGlancerLayers(URLsQuotationMarks, brackets = brackets)


    URL_preamble = re.search( ".*%s" %brackets[0], URLsQuotationMarks[0] ).group()

    URL_postamble = re.search( "%s.*"%brackets[1], URLsQuotationMarks[0] ).group()

    mergedLayerURL = URL_preamble + ",".join(layerDefinitions) + URL_postamble

    #mergedLayerURLQuotes = urllib.parse.quote(mergedLayerURL)

    return mergedLayerURL




if __name__ == '__main__':

    args = initilizeArgParser()


    NeuroGlancerURLs = ensureURLType( args.NeuroGlancerURLs )

    mergedURL = makeMergedLayerURL( NeuroGlancerURLs )

    #import pdb; pdb.set_trace() # import the debugger and instruct it to stop here

    print("")
    print(mergedURL)
