import numpy as np 
import docopt
import sys
import os
import os.path
import fnmatch
import pandas as pd


pd.set_option('precision', 3)

docoptstring = """Usage: zprobestats.py [<filename>]  [--ref=<tower>]
       zprobestats.py  (-h | --help)

The zprobestats.py reads the Repetier host log file output and processes
the z probe statistics

Arguments:
    filename [optional] is the name of the input file.
    If no input filename is supplied, all .txt files in current directory
    will be processed. 

Options:

  -h, --help  [optional] help information.
  --ref=<tower>  [optional] selects the reference tower, others to match this one.

"""


################################################################################
#lists the files in a directory and subdirectories (from Python Cookbook)
def listFiles(root, patterns='*', recurse=1, return_folders=0):
    """lists the files in a directory and subdirectories (from Python Cookbook)

    Extensively reworked for Python 3.
    """
    # Expand patterns from semicolon-separated string to list
    pattern_list = patterns.split(';')
    filenames = []
    filertn = []

    if int(sys.version[0]) < 3:

        # Collect input and output arguments into one bunch
        class Bunch(object):
            def __init__(self, **kwds): self.__dict__.update(kwds)
        arg = Bunch(recurse=recurse, pattern_list=pattern_list,
            return_folders=return_folders, results=[])

        def visit(arg, dirname, files):
            # Append to arg.results all relevant files (and perhaps folders)
            for name in files:
                fullname = os.path.normpath(os.path.join(dirname, name))
                if arg.return_folders or os.path.isfile(fullname):
                    for pattern in arg.pattern_list:
                        if fnmatch.fnmatch(name, pattern):
                            arg.results.append(fullname)
                            break
            # Block recursion if recursion was disallowed
            if not arg.recurse: files[:]=[]
        os.path.walk(root, visit, arg)
        return arg.results

    else:
        for dirpath,dirnames,files in os.walk(root):
            if dirpath==root or recurse:
                for filen in files:
                    filenames.append(os.path.abspath(os.path.join(os.getcwd(),dirpath,filen)))
                if return_folders:
                    for dirn in dirnames:
                        filenames.append(os.path.abspath(os.path.join(os.getcwd(),dirpath,dirn)))
        for name in filenames:
            if return_folders or os.path.isfile(name):
                for pattern in pattern_list:
                    if fnmatch.fnmatch(name, pattern):
                        filertn.append(name)
                        break

    return filertn


################################################################################
# here we get a list of all the input
def getInfileNames(infile):

    infiles = []

    if infile is not None:
        infiles.append(infile)
    else:
        # no input filename supplied, get all
        files = listFiles('.', patterns='*.txt', recurse=0, return_folders=0)
        for file in files:
            file = os.path.basename(file)
            infiles.append(file)

    return infiles


################################################################################
# label the towers
def label_tower (row):
   if row['x'] < -80. :
      return 'X'
   if row['y'] > 80. :
      return 'Z'
   if row['x'] > 60. :
      return 'Y'
   return 'C'


################################################################################
# process one sample set
def processOneFile(filename,zProbeTrigger,shimThickness,reftower=None,locmarg=0.05):
    print('{}\n{}\n\n'.format(79*'-',filename))
    validlines = []
    tdone = False
    with open(filename,'r') as fin:
        lines = fin.readlines()
        for line in lines:
            line = line.strip()
            lstl = line.split(' ')
            # only use lines with Bed X: in them for dataframe
            if 'Bed X:' in line:
                # remove unwanted clutter, keep only x,y,z
                validlines.append([float(lstl[i]) for i in [4,6,8]])
            # if temperature lines, get values
            if not tdone and 'ok' in line and 'T:' in line and 'B:' in line:
                print('Time {} '.format(lstl[0]))
                print('Bed temperature is {} deg C'.format(lstl[5].split(':')[1]))
                print('Nozzle temperature is {} deg C'.format(lstl[3].split(':')[1]))
                tdone = True

    # make pandas dataframe
    df = pd.DataFrame(validlines,columns=['x','y','z'])
    # correct for probe offset and friction shim to get to metal
    df['z'] = df['z'] - (zProbeTrigger - shimThickness)
    # get height at screw
    df['S'] = df['z'] * 158.6 / (52.85 + np.sqrt(df['x']**2 + df['y']**2))
    #name the towers
    df['Tower'] = df.apply(label_tower,axis=1)
    # get required turn magnitude
    df['Trns(deg)'] = 360. * df['S'] / 0.5
    df['Trns/0.25'] = (df['S'] / 0.5) / 0.25


    # from now on work with aggregates
    dfg = df.groupby(['Tower'])
    dfr = dfg.aggregate(np.mean)
    dfr['Std dev'] = dfg.aggregate(np.std)['S']
    dfr['Spread'] = dfg.aggregate(np.max)['S'] - dfg.aggregate(np.min)['S']
     # centre does not require slant correction
    dfr['S'].ix['C'] = dfr['z'].ix['C']

    # if a reference tower is given, calc turn offset for other towers
    if reftower:
        reftower = reftower.upper()
        print("All turns to set other towers' S equal to {} tower S".format(reftower))
        # for t in ['X','Y','Z']:
        dfr['Trns(deg)R'] = dfr['Trns(deg)'] - dfr.ix[reftower]['Trns(deg)']
        dfr['Trns/0.25R'] = dfr['Trns/0.25'] - dfr.ix[reftower]['Trns/0.25']
        dfr['Trns(deg)'] = dfr['Trns(deg)R'] 
        dfr['Trns/0.25'] = dfr['Trns/0.25R']
        dfr.drop(['Trns(deg)R','Trns/0.25R'],axis=1,inplace=True)
    else:
        print("All turns to set towers' S equal to zero")

    # remove value for C turns
    dfr.ix['C']['Trns(deg)'] = np.nan
    dfr.ix['C']['Trns/0.25'] =  np.nan

    print(dfr)
    print('')

    # get mean, min and max of the tower averages
    bedMean = np.mean((dfr['S']).T[['X','Y','Z']])
    bedMin = np.min((dfr['S']).T[['X','Y','Z']])
    bedMax = np.max((dfr['S']).T[['X','Y','Z']])
    print('Mean bed height is {:.3f} mm'.format(bedMean))
    print('Bed min={:.3f}, max={:.3f}, spread={:.3f} mm'.format(bedMin,bedMax,bedMax-bedMin))
    # if level to within margin calc the convex/concave
    if bedMax-bedMin < locmarg:
        convex = bedMean - dfr.ix['C']['S']
        direc = 'mountian' if convex < 0 else 'valley'
        print('Bed level to within {} mm: print locus convexity {:.3f} mm ({})'.format(
            locmarg,convex,direc))
    print('\n')



def deltaRadius(R,C):
    r = (0 - C[0]) * (R[1]-R[0]) / (C[1]-C[0]) + R[0]
    print('required radius is {}'.format(r))
    print('delta from R[0] is {}'.format(r - R[0]))


################################################################################
################################################################################
# args = docopt.docopt(__doc__)
args = docopt.docopt(docoptstring)

# print(args)

infile = args['<filename>']
reftower = args['--ref']


# see if only one input file, or perhaps many
infiles = getInfileNames(infile)

#process the list of files found in spec
for infile in infiles:
    processOneFile(infile, reftower=reftower, zProbeTrigger=0.7,shimThickness=0.1)

print('\nfini!')


# R = np.asarray([147.3, 148.3])
# C = np.asarray([0.075,-0.196])
# deltaRadius(R,C)
