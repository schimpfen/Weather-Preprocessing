from sklearn.preprocessing import MinMaxScaler
from netCDF4 import Dataset
import numpy as np
import os


def main():

    sample_file = 'F:/Aircraft-Data/Weather Cubes/2018-11-01/Flight_Plan_KJFK_KLAX_AAL1.nc'
    PATH_PROJ = '/'.join(os.path.abspath('.').split('\\')[:-1])
    PATH_FP = os.path.join(PATH_PROJ, 'Data/IFF_Flight_Plans/Sorted')
    PATH_TP = os.path.join(PATH_PROJ, 'Data/IFF_Track_Points/Sorted')
    PATH_WC = 'F:/Aircraft-Data/Weather Cubes/'

    nda_minmax = np.empty((6,0))
    # For every Weather Cube, Log the Minimum/Maximum latitude, longitude, echo top
    wc_dates = [x for x in os.listdir(PATH_WC) if os.path.isdir(os.path.join(PATH_WC, x))]
    for dir in wc_dates:
        print('Reading Weather Cubes form {}'.format(dir))
        files = [y for y in os.listdir(os.path.join(PATH_WC, dir)) if y.__contains__('.nc')]
        for wc in files:
            wc_abspath = os.path.join(PATH_WC, dir, wc)
            grp = Dataset(wc_abspath, 'r', format='netCDF4')
            if len(grp['Latitude']) > 0:
                nda_tmp = np.array([grp['Latitude'][:].min(), grp['Latitude'][:].max(), grp['Longitude'][:].min(),
                               grp['Longitude'][:].max(), grp['Echo_Top'][:].min(), grp['Echo_Top'][:].max()])
                nda_tmp = nda_tmp.reshape((6,1))
                nda_minmax = np.hstack((nda_minmax, nda_tmp))
            grp.close()


    # for every flight plan, Log the Minimum/Maximum latitude, longitude, altitude
    fp_dates = [x for x in os.listdir(PATH_FP) if os.path.isdir(os.path.join(PATH_FP, x))]
    for dir in fp_dates:
        print('Reading Flight Plans from {}'.format(dir))
        files = [y for y in os.listdir(os.path.join(PATH_FP, dir)) if y.__contains__('.txt')]
        for fp in files:
            fp_abspath = os.path.join(PATH_FP, dir, fp)
            nda_fp = np.genfromtxt(fp_abspath, delimiter=',')
            if len(nda_fp[:,0]) > 0:
                nda_tmp = np.array([nda_fp[:,1].min(), nda_fp[:,1].max(), nda_fp[:,2].min(),
                                 nda_fp[:,2].max(), nda_fp[:,3].min(), nda_fp[:,3].max()])
                nda_tmp = nda_tmp.reshape((6, 1))
                nda_minmax = np.hstack((nda_minmax, nda_tmp))


    # for every flight track, Log the Minimum/Maximum latitude, longitude, altitude
    tp_dates = [x for x in os.listdir(PATH_TP) if os.path.isdir(os.path.join(PATH_TP, x))]
    for dir in tp_dates:
        print('Reading Trajectories from {}'.format(dir))
        files = [y for y in os.listdir(os.path.join(PATH_TP, dir)) if y.__contains__('.txt')]
        for tp in files:
            tp_abspath = os.path.join(PATH_TP, dir, tp)
            nda_tp = np.genfromtxt(tp_abspath, delimiter=',')
            if len(nda_tp) > 0:
                nda_tmp = np.array([nda_tp[:, 1].min(), nda_tp[:, 1].max(), nda_tp[:, 2].min(),
                                 nda_tp[:, 2].max(), nda_tp[:, 3].min(), nda_tp[:, 3].max()])
                nda_tmp = nda_tmp.reshape((6, 1))
                nda_minmax = np.hstack((nda_minmax, nda_tmp))


    print('Generating MinMaxScalers')

    # Save log and identify overall min/max latitude, longitude, altitude
    nda_minmax.tofile(os.path.join(os.path.abspath('.'), 'Data_MinMax.csv'), sep=',')
    lat_min, lon_min, alt_min = nda_minmax[0,:].min(),nda_minmax[1,:].min(), nda_minmax[2,:].min()
    lat_max, lon_max, alt_max = nda_minmax[0,:].max(), nda_minmax[1,:].max(), nda_minmax[2,:].max()


    # Create MinMax Scaler using overall parameters
    lat_scaler = MinMaxScaler(feature_range=[lat_min, lat_max])
    lon_scaler = MinMaxScaler(feature_range=[lon_min, lon_max])
    alt_scaler = MinMaxScaler(feature_range=[alt_min, alt_max])


    # Scale every Weather Cube
    wc_dates = [x for x in os.listdir(PATH_WC) if os.path.isdir(x)]
    for dir in wc_dates:
        print('Scaling Weather Cubes from {}'.format(dir))
        files = [y for y in os.listdir(os.path.join(PATH_WC, dir)) if y.__contains__('.nc')]
        for wc in files:
            wc_abspath = os.path.join(PATH_WC, dir, wc)
            grp = Dataset(wc_abspath, 'r+', format='netCDF4')
            if len(grp['Latitude']) > 0:
                grp['Latitude'][:] = lat_scaler.transform(grp['Latitude'][:])
                grp['Longitude'][:] = lon_scaler.transform(grp['Longitude'][:])
                grp['Echo_Top'][:] = alt_scaler.transform(grp['Echo_Top'][:])
            grp.close()


    # Scale every Flight Plan
    fp_dates = [x for x in os.listdir(PATH_FP) if os.path.isdir(x)]
    for dir in fp_dates:
        print('Scaling Flight Plans from {}'.format(dir))
        files = [y for y in os.listdir(os.path.join(PATH_FP, dir)) if y.__contains__('.txt')]
        for fp in files:
            fp_abspath = os.path.join(PATH_FP, dir, fp)
            nda_fp = np.genfromtxt(fp_abspath, delimiter=',')
            if len(nda_fp[:,0]) > 0:
                nda_fp[:,1] = lat_scaler.transform(nda_fp[:,1])
                nda_fp[:,2] = lon_scaler.transform(nda_fp[:,2])
                nda_fp[:,3] = alt_scaler.transform(nda_fp[:,3])


    # Scale every Flight Track
    tp_dates = [x for x in os.listdir(PATH_TP) if os.path.isdir(x)]
    for dir in tp_dates:
        print('Scaling Trajectories from {}'.format(dir))
        files = [y for y in os.listdir(os.path.join(PATH_TP, dir)) if y.__contains__('.txt')]
        for tp in files:
            tp_abspath = os.path.join(PATH_TP, dir, tp)
            nda_tp = np.genfromtxt(tp_abspath, delimiter=',')
            if len(nda_tp[:,0]) > 0:
                nda_tp[:,1] = lat_scaler.transform(nda_tp[:,1])
                nda_tp[:,2] = lon_scaler.transform(nda_tp[:,2])
                nda_tp[:,3] = alt_scaler.transform(nda_tp[:,3])

    print('Done')


if __name__ == '__main__':
    main()