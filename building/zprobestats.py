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

docoptstring = """Usage: zprobestats.py [--bedtower=<bedtower>] [--bedmesh=<bedmesh>]  [--reftower=<reftower>]
       zprobestats.py  (-h | --help)

The zprobestats.py reads the Repetier host log file output and processes
the z probe statistics

Arguments:
    If no options are supplied nothing happens

Options:

  -h, --help  [optional] help information.
    --bedtower=<bedtower> [optional] is the name of the input file with bed tower heights.
    --bedmesh=<bedmesh> [optional] is the name of the bed mesh input file.
    --reftower=<reftower>  [optional] selects the reference tower, others to match this one.

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
   if row['x'] <-72. :
      return 'X'
   if row['y'] > 80. :
      return 'Z'
   if row['x'] > 60. :
      return 'Y'
   return 'C'


################################################################################
# process one bed tower sample set
def processBedTower(filename,zProbeTrigger,shimThickness,reftower=None,locmarg=0.02):
    """Reads and analyse a file with four measured bed heights (near towers and in centre).

    The probe trigger z value (not the actual height) is determined by moving the hot end 
    slowly down and noting the z value where the probe triggers. The distance from the 
    nozzle tip to the probe trigger height is zProbeTrigger + shimThickness.


    The function calculates the number of screw turns required (on M3 screw) to move the 
    bed to z=0 or to the z value of one of the towers as indicated in reftower. This save us 
    a little arithmetic and removes the confusion of which direction to move. If reftower
    is X the movement on the Y and Z towers will bring the bed to the same height as X.  

          Args:
              | zProbeTrigger (float): the the z value when the probe triggers. 
              | shimThickness (float):  is the thickness of the paper/shim when doing the nozzle 
                friction test in mm.
              | reftower (string):  tells the code to calculate the corrective turn magnitudes 
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
        print("All screw turns to set other towers' S equal to {} tower S".format(reftower))
        # for t in ['X','Y','Z']:
        dfr['Trns(deg)R'] = dfr['Trns(deg)'] - dfr.ix[reftower]['Trns(deg)']
        dfr['Trns/0.25R'] = dfr['Trns/0.25'] - dfr.ix[reftower]['Trns/0.25']
        dfr['Trns(deg)'] = dfr['Trns(deg)R'] 
        dfr['Trns/0.25'] = dfr['Trns/0.25R']
        dfr.drop(['Trns(deg)R','Trns/0.25R'],axis=1,inplace=True)
    else:
        print("All screw turns to set towers' S equal to zero")

    # remove value for C turns
    dfr.ix['C']['Trns(deg)'] = np.nan
    dfr.ix['C']['Trns/0.25'] =  np.nan

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

    print(dfr)
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


def deltaRadius(R,C):
    r = (0 - C[0]) * (R[1]-R[0]) / (C[1]-C[0]) + R[0]
    print('required radius is {}'.format(r))
    print('delta from R[0] is {}'.format(r - R[0]))

################################################################################
# process one bed mesh sample set
def processBedMesh(filename):

    print(filename)
      #define MESH_X_DIST ((MESH_MAX_X - (MESH_MIN_X))/(MESH_NUM_X_POINTS - 1))
      #define MESH_Y_DIST ((MESH_MAX_Y - (MESH_MIN_Y))/(MESH_NUM_Y_POINTS - 1))
  #define MESH_MIN_X (X_MIN_POS + MESH_INSET)
  #define MESH_MAX_X (X_MAX_POS - (MESH_INSET))
  #define MESH_MIN_Y (Y_MIN_POS + MESH_INSET)
  #define MESH_MAX_Y (Y_MAX_POS - (MESH_INSET))
  #define MESH_INSET 10        // Mesh inset margin on print area
  #define MESH_NUM_X_POINTS 3  // Don't use more than 7 points per axis, implementation limited.
  #define MESH_NUM_Y_POINTS 3


   #define DELTA_PROBEABLE_RADIUS (DELTA_PRINTABLE_RADIUS - 40)
    #define LEFT_PROBE_BED_POSITION -(DELTA_PROBEABLE_RADIUS)
    #define RIGHT_PROBE_BED_POSITION DELTA_PROBEABLE_RADIUS
    #define FRONT_PROBE_BED_POSITION -(DELTA_PROBEABLE_RADIUS)
    #define BACK_PROBE_BED_POSITION DELTA_PROBEABLE_RADIUS

    #define MIN_PROBE_EDGE 40 // The Z probe minimum square sides can be no smaller than this.
    #define AUTO_BED_LEVELING_GRID_POINTS 10


    DELTA_PRINTABLE_RADIUS = 110.0
    DELTA_PROBEABLE_RADIUS = DELTA_PRINTABLE_RADIUS - 40.
    print(DELTA_PROBEABLE_RADIUS)

    for px in [-80, 80]:
        for py in [-80, 80]:
            print(px+33.5,py+5.)

    mesh = np.loadtxt(filename,usecols=[i for i in range(2,11+1)])
    print(mesh)
    mesh = mesh - np.min(mesh)
    x = np.linspace(-DELTA_PROBEABLE_RADIUS,DELTA_PROBEABLE_RADIUS,mesh.shape[0])
    y = np.linspace(-DELTA_PROBEABLE_RADIUS,DELTA_PROBEABLE_RADIUS,mesh.shape[1])
    xx,yy = np.meshgrid(x,y)
    p = ryplot.Plotter(1,1,2,figsize=(16,6))
    p.meshContour(1,xx,yy,mesh,contLabel=True,cbarshow=True)
    p.mesh3D(2,xx,yy,mesh,cbarshow=True)
    p.saveFig('xxx.png')

################################################################################
################################################################################
# args = docopt.docopt(__doc__)
args = docopt.docopt(docoptstring)

# print(args)

bedtower = args['--bedtower']
bedmesh = args['--bedmesh']
reftower = args['--reftower']

#process the list of files found in spec
if bedtower:
    processBedTower(bedtower, reftower=reftower, zProbeTrigger=0.7,shimThickness=0.1)

if bedmesh:
    processBedMesh(bedmesh)


print('\nfini!')


# R = np.asarray([147.3, 148.3])
# C = np.asarray([0.075,-0.196])
# deltaRadius(R,C)
