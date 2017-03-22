import numpy as np 
import docopt
import sys
import os
import os.path
import fnmatch
import pandas as pd
from sympy import Plane, Point3D,N,sympify,Line3D
from sympy.matrices import Matrix
import math
import pyradi.ryplot as ryplot

pd.set_option('precision', 3)

docoptstring = """Usage: zprobestats.py [--bedtower=<bedtower>] [--bedmesh=<bedmesh>] [--xtarget=<xtarget>] [--ytarget=<ytarget>] [--ztarget=<ztarget>] 
       zprobestats.py  (-h | --help)

The zprobestats.py reads the Repetier host log file output and processes
the z probe statistics

Arguments:
    If no options are supplied nothing happens

Options:

  -h, --help  [optional] help information.
    --bedtower=<bedtower> [optional] is the name of the input file with bed tower heights.
    --bedmesh=<bedmesh> [optional] is the name of the bed mesh input file.
    --xtarget=<xtarget>  [optional] defines the target height on the X measurement point
    --ytarget=<xtarget>  [optional] defines the target height on the Y measurement point
    --ztarget=<xtarget>  [optional] defines the target height on the Z measurement point

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
    # near X tower
    if row['x'] <-72.:
        if row['y'] < 0:
            return 'X'
        else:
            return 'Xm'
    # near Y tower
    if row['x'] > 60. :
        if row['y'] < 0:
            return 'Y'
        else:
            return 'Ym'
    # near Z tower
    if row['y'] > 80. :
      return 'Z'
    if row['y'] < -80. :
      return 'Zm'
    return 'C'


################################################################################
# label the towers
def target_tower (row, xtarget,ytarget,ztarget):
    # near X tower
    if row['Tower'] == 'X':
        return xtarget
    if row['Tower'] == 'Y':
        return ytarget
    if row['Tower'] == 'Z':
        return ztarget
    return np.nan

################################################################################
# label the towers
def delta_tower (row, xtarget,ytarget,ztarget):
    # near X tower
    if row['Tower'] == 'X':
        return row['z'] - xtarget
    if row['Tower'] == 'Y':
        return row['z'] -  ytarget
    if row['Tower'] == 'Z':
        return row['z'] - ztarget
    return np.nan


################################################################################
# process one bed tower sample set
def processBedTower(filename,zProbeOffset, xtarget,ytarget,ztarget,locmarg=0.02):
    """Reads and analyse a file with four measured bed heights (near towers and in centre).

    The probe trigger z value (not the actual height) is determined by moving the hot end 
    slowly down and noting the z value where the probe triggers. The distance from the 
    nozzle tip to the probe trigger height is zProbeOffset.


    The function calculates the number of screw turns required (on M3 screw). This save us 
    a little arithmetic and removes the confusion of which direction to move. .  

          Args:
              | zProbeOffset (float): the the z value when the probe triggers. 
               friction test in mm.
                relative to one of the towers, X, Y or Z. B(default: `None`).
              | locmarg (float):  issues a bed titl warning above this threshold

          Returns:
              | the axis object for the plot

          Raises:
              | No exception is raised.




    """
    print('{}\n{}\n\n'.format(79*'-',filename))
    validlines = []
    tdone = False
    with open(filename,'r') as fin:
        lines = fin.readlines()
        for line in lines:
            if len(line) > 2:
                line = line.strip()
                if '>' in line[0] or '<' in line[0]:
                    line = line[2:]
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

    #name the towers
    df['Tower'] = df.apply(label_tower,axis=1)
    df['Target'] =  df.apply(target_tower, args=(xtarget,ytarget,ztarget),axis=1)

    # correct for probe offset to get to metal
    df['z'] = df['z'] - zProbeOffset
    # get height at screw
    df['S'] = df['z'] * 158.6 / (52.85 + np.sqrt(df['x']**2 + df['y']**2))

    # now calc offsets to move to target
    df['dz'] = df['z'] - ztarget 
    df['dz'] =  df.apply(delta_tower, args=(xtarget,ytarget,ztarget),axis=1)

    df['dS'] = df['dz'] * 158.6 / (52.85 + np.sqrt(df['x']**2 + df['y']**2))
    # get required turn magnitude
    df['Trns(deg)'] = 360. * df['dS'] / 0.5
    df['Trns/0.25'] = (df['dS'] / 0.5) / 0.25


    # from now on work with aggregates
    dfg = df.groupby(['Tower'])
    dfr = dfg.aggregate(np.mean)
    dfr['Std dev'] = dfg.aggregate(np.std)['S']
    dfr['Spread'] = dfg.aggregate(np.max)['S'] - dfg.aggregate(np.min)['S']
     # centre does not require slant correction
    dfr['S'].ix['C'] = dfr['z'].ix['C']

    # remove value for C outputs
    dfr.ix['C']['Trns(deg)'] = np.nan
    dfr.ix['C']['Trns/0.25'] =  np.nan
    dfr.ix['C']['S'] =  np.nan
    dfr.ix['C']['dS'] =  np.nan
    dfr.ix['C']['dz'] =  np.nan

    if 'Xm' in dfr.index:
        print(dfr.drop(['Xm','Ym','Zm'],axis=0))
    else:
        print(dfr)
    print('')

    # get mean, min and max of the tower averages and tpower and centre
    twrMean = np.mean((dfr['S']).T[['X','Y','Z']])
    twrMin = np.min((dfr['S']).T[['X','Y','Z',]])
    twrMax = np.max((dfr['S']).T[['X','Y','Z']])
    twrSpread = twrMax-twrMin
    bedMean = np.mean((dfr['S']).T[['X','Y','Z','C']])
    bedMin = np.min((dfr['S']).T[['X','Y','Z','C']])
    bedMax = np.max((dfr['S']).T[['X','Y','Z','C']])
    bedSpread = bedMax-bedMin

    print('            Towers      Full bed')
    print('          (SX,SY,SZ)  (SX,SY,SZ,SC)')
    print('mean         {:.3f}        {:.3f} '.format(twrMean,bedMean))
    print('min          {:.3f}        {:.3f} '.format(twrMin,bedMin))
    print('max          {:.3f}        {:.3f} '.format(twrMax,bedMax))
    print('spread       {:.3f}        {:.3f} '.format(twrMax-twrMin,bedSpread))

    # calculate the plane through the three screws
    bedplane = Plane(
        Point3D(dfr.ix['X']['x'], dfr.ix['X']['y'], dfr.ix['X']['z']),
        Point3D(dfr.ix['Y']['x'], dfr.ix['Y']['y'], dfr.ix['Y']['z']),
        Point3D(dfr.ix['Z']['x'], dfr.ix['Z']['y'], dfr.ix['Z']['z']) , evaluate=False )

    # process bed normal vector
    bednormal = Matrix(bedplane.normal_vector).normalized()
    bnx = float(N(bednormal[0]))
    bny = float(N(bednormal[1]))
    bnz = float(N(bednormal[2]))
    ang = np.arctan2(bny,bnx)
    norm = np.sqrt(bnx*bnx+bny*bny)
    print('\nBed normal vector ({:.3e},{:.3e},{:.3e})'.format(bnx,bny,bnz))
    print('  projection onto z=0 plane: radius={:.1f} um angle={:.1f} deg'.format(1e6*norm,180*ang/np.pi))


    print('\nPrint locus:')
    print('Plane through SX, SY, and SZ:  {}'.format(N(bedplane.equation())))
    # measured bed centre
    bedcentre = Point3D(dfr.ix['C']['x'], dfr.ix['C']['y'], dfr.ix['C']['z'])
    # displacement between plane at (0,0) and measured z
    convex = N((N(bedplane.projection(Point3D(0,0))) - bedcentre).z)
    # apparent bed direction as seen by printer
    direc = 'mountain' if convex < 0. else 'valley'
    slant = 'on a tilted bed' if twrSpread>locmarg else ''
    print('Print locus convexity [plane(0,0) - SC] is {:.3f} mm'.format(convex))
    print('The printer perceives the bed as a {} {}'.format(direc,slant))
    if twrSpread>locmarg:
        print('\n********  WARNING: bed tilt in z {:.3f} mm exceeds {:.3f} mm, {}'.format(
            twrSpread,locmarg,'consider levelling'))



################################################################################
################################################################################
# args = docopt.docopt(__doc__)
args = docopt.docopt(docoptstring)

# print(args)

bedtower = args['--bedtower']
bedmesh = args['--bedmesh']
xtarget = float(args['--xtarget']) if args['--xtarget'] else -0.048
ytarget = float(args['--ytarget']) if args['--ytarget'] else 0.
ztarget = float(args['--ztarget']) if args['--ztarget'] else -0.032


#process the list of files found in spec
if bedtower:
    processBedTower(bedtower,xtarget=xtarget,ytarget=ytarget,ztarget=ztarget,zProbeOffset=-0.79)

if bedmesh:
    processBedMesh(bedmesh)


print('\nfini!')


# R = np.asarray([147.3, 148.3])
# C = np.asarray([0.075,-0.196])
# deltaRadius(R,C)
