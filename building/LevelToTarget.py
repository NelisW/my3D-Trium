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

docoptstring = """Usage: zprobestats.py (--filename=<filename>) [-s]   [--xtarget=<xtarget>] [--ytarget=<ytarget>] [--ztarget=<ztarget>]  
       zprobestats.py  (-h | --help)

The zprobestats.py reads the Repetier host log file output and processes
the z probe statistics to calculate how the screws must be turned to level the bed.

If the bed is pefectly flat, set the target values to equal values. If the bed is 
not perfectly flat set each of the target values to the required z-height.

Set the zprobe offset for your printer.

Arguments:
    If no filename is supplied nothing happens

Options:

    -h, --help  [optional] help information. 
    -s  [optional] show all results.
    --filename=<filename> is the name of the input file with bed tower heights.
    --xtarget=<xtarget>  [optional] defines the target height on the X measurement point
    --ytarget=<xtarget>  [optional] defines the target height on the Y measurement point
    --ztarget=<xtarget>  [optional] defines the target height on the Z measurement point
"""
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
        return row['zp'] - xtarget
    if row['Tower'] == 'Y':
        return row['zp'] -  ytarget
    if row['Tower'] == 'Z':
        return row['zp'] - ztarget
    return np.nan


################################################################################
# process one bed tower sample set
def processBedTower(filename,zProbeOffset, xtarget,ytarget,ztarget,showall=False):
    """Reads and analyse a file with four measured bed heights (near towers and in centre).

    The probe trigger z value (not the actual height) is determined by moving the hot end 
    slowly down and noting the z value where the probe triggers. The distance from the 
    nozzle tip to the probe trigger height is zProbeOffset.


    The function calculates the number of screw turns required (on M3 screw). This save us 
    a little arithmetic and removes the confusion of which direction to move. .  

          Args:
              | zProbeOffset (float): the the z value when the probe triggers. 
              | xtarget (float): the required z value at the X tower probe point
              | ytarget (float): the required z value at the Y tower probe point
              | ztarget (float): the required z value at the Z tower probe point

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
    df = pd.DataFrame(validlines,columns=['x','y','zp'])

    #name the towers
    df['Tower'] = df.apply(label_tower,axis=1)
    df['zptarget'] =  df.apply(target_tower, args=(xtarget,ytarget,ztarget),axis=1)
    df['cnt'] = 1.

    # correct for probe offset to get to metal
    df['zp'] = df['zp'] - zProbeOffset
    # get height at screw
    df['screw'] = df['zp'] * 158.6 / (52.85 + np.sqrt(df['x']**2 + df['y']**2))

    # now calc offsets to move to target
    df['dzp'] = df['zp'] - ztarget 
    df['dzp'] =  df.apply(delta_tower, args=(xtarget,ytarget,ztarget),axis=1)

    df['dscrew'] = df['dzp'] * 158.6 / (52.85 + np.sqrt(df['x']**2 + df['y']**2))
    # get required turn magnitude
    df['Trns(deg)'] = 360. * df['dscrew'] / 0.5
    df['Trns/0.25'] = (df['dscrew'] / 0.5) / 0.25

    # from now on work with aggregates
    dfg = df.groupby(['Tower'])
    dfr = dfg.aggregate(np.mean)
    dfr['Std dev'] = dfg.aggregate(np.std)['screw']
    dfr['Spread'] = dfg.aggregate(np.ptp)['screw']
    dfr['Sample count'] = dfg.aggregate(np.count_nonzero)['cnt']

     # centre does not require slant correction
    dfr['screw'].ix['C'] = dfr['zp'].ix['C']

    # remove value for C outputs
    dfr.ix['C']['Trns(deg)'] = np.nan
    dfr.ix['C']['Trns/0.25'] =  np.nan
    # dfr.ix['C']['screw'] =  np.nan
    dfr.ix['C']['dscrew'] =  np.nan
    dfr.ix['C']['dzp'] =  np.nan

    if 'Xm' in dfr.index:
        dfprt = dfr.drop(['screw','Spread','Std dev','Sample count','cnt'],axis=1)
        if not showall:
            dfprt = dfprt.drop(['Xm','Ym','Zm'],axis=0)
        print(dfprt)
    else:
        print(dfr.drop(['screw','Spread','Std dev','Sample count','cnt'],axis=1))

    print('\nMeasurement statistics')

    if 'Xm' in dfr.index:
        dfprt = dfr.drop(['x','y','zp','zptarget','dzp','screw','dscrew','Trns(deg)','Trns/0.25','cnt'],axis=1)
        if not showall:
            dfprt = dfprt.drop(['Xm','Ym','Zm'],axis=0)
        print(dfprt)
    else:
        print(dfr.drop(['x','y','zp','zptarget','dzp','screw','dscrew','Trns(deg)','Trns/0.25','cnt'],axis=1))


################################################################################
################################################################################
args = docopt.docopt(docoptstring)

filename = args['--filename']
xtarget = float(args['--xtarget']) if args['--xtarget'] else 0
ytarget = float(args['--ytarget']) if args['--ytarget'] else 0
ztarget = float(args['--ztarget']) if args['--ztarget'] else 0
showall = True if args['-s'] else False

if filename:
    processBedTower(filename,xtarget=xtarget,ytarget=ytarget,ztarget=ztarget,zProbeOffset=0.79,showall=showall)

print('\nfini!')
