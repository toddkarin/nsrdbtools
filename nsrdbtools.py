
import numpy as np
import pandas as pd
import glob
import os

# import sys
# import matplotlib
# matplotlib.use('TkAgg')
# import matplotlib.pyplot as plt


def make_lat_long_grid(lat_lims=[25, 47], long_lims=[-124,-66], lat_step=1, long_step=1 ):
    """
    Make a lat/long grid pairs for the coordinates specified. Note that the
    end limit point is typically not included in the resultant grid.



    Example
        Make a latitude longitude grid:

        > make_lat_long_grid(lat_lims=[25, 47], long_lims=[-124,-66],
            lat_step=1, long_step=1)

        result:

        > {'lat': array([25., 25., 25., ..., 46., 46., 46.]), 'long': array([
        -124., -123., -122., ...,  -69.,  -68.,  -67.]), 'num': 1276}



    """

    lat_flat = np.arange( np.min(lat_lims), np.max(lat_lims), lat_step)
    long_flat = np.arange( np.min(long_lims), np.max(long_lims), long_step)


    lat = np.zeros(len(lat_flat)*len(long_flat))
    long = np.zeros(len(lat_flat) * len(long_flat))
    n=0
    for j in range(len(lat_flat)):
        for k in range(len(long_flat)):
            lat[n], long[n] = lat_flat[j], long_flat[k]
            n=n+1



    return {'lat':lat, 'long':long, 'num':len(lat)}




def inspect_database(root_path):
    """Build database for NSRDB files

    Build a lat/long and year list for NSRDB csv files in a data folder.
    Folders are searched recursively. Fast way to inspect a set of csv files
    and build a database of file path, latitude, longitude and year.

    Examples
    --------
    inspect_database('data_folder')


    Parameters
    ----------
    root_path

    Returns
    -------
    filedata
        pandas DataFrame containing information on files in the root_path..

    """

    import fnmatch
    import os

    # root_path = 'around_fairfield'
    pattern = '*.csv'


    filedata = pd.DataFrame(columns=['lat','long','year','filepath'])
    filename_list = []
    filename_fullpath = []
    location_id = []
    lat = []
    long = []
    year = []

    # Cycle through files in directory, extract info from filename without opening file.
    # Note this would break if NREL changed their naming scheme.
    for root, dirs, files in os.walk(root_path):
        for filename in fnmatch.filter(files, pattern):

            temp = filename.split('_')

            filename_list.append(filename)
            filename_fullpath.append(os.path.join(root, filename))
            location_id.append(temp[0])
            lat.append(temp[1])
            long.append(temp[2])
            year.append(temp[3][0:-4])

    # Create a DataFrame
    filedata = pd.DataFrame.from_dict({
        'location_id': location_id,
        'lat': lat,
        'long': long,
        'year': year,
        'filename': filename_list,
        'fullpath': filename_fullpath})


    filedata = filedata.sort_values(by='location_id')

    # Redefine the index.
    filedata.index = range(filedata.__len__())
    return filedata




def import_csv(filename):
    """Import an NSRDB csv file.

    The function (df,info) = import_csv(filename) imports an NSRDB formatted
    csv file

    Parameters
    ----------
    filename

    Returns
    -------
    df
        pandas dataframe of data
    info
        pandas dataframe of header data.
    """

    # filename = '1ad06643cad4eeb947f3de02e9a0d6d7/128364_38.29_-122.14_1998.csv'

    info = pd.read_csv(filename, nrows=1)
    # See metadata for specified properties, e.g., timezone and elevation
    # timezone, elevation = info['Local Time Zone'], info['Elevation']

    # Return all but first 2 lines of csv to get data:
    df = pd.read_csv(filename, skiprows=2)

    # Set the time index in the pandas dataframe:
    year=str(df['Year'][0])


    if np.diff(df[0:2].Minute) == 30:
        interval = '30'
        df = df.set_index(
          pd.date_range('1/1/{yr}'.format(yr=year), freq=interval + 'Min', periods=60*24*365 / int(interval)))
    elif df['Minute'][1] - df['Minute'][0]==0:
        interval = '60'
        df = df.set_index(
            pd.date_range('1/1/{yr}'.format(yr=year), freq=interval + 'Min', periods=60*24*365 / int(interval)))
    else:
        print('Interval not understood!')



    return (df, info)

# df, info = import_csv('nsrdb_1degree_uv/104_30.97_-83.22_tmy.csv')

def import_sequence(folder):
    """Import and append NSRDB files in a folder

    Import a sequence of NSRDB files, data is appended to a pandas dataframe.
    This is useful for importing all years of data from one folder.

    Parameters
    ----------
    folder
        directory containing files to import.

    Returns
    -------
    df
        pandas dataframe of data
    info
        pandas dataframe of header data for last file imported.
    """

    # Get all files.
    files = glob.glob(os.path.join(folder, '*.csv'))

    if len(files)==0:
        raise ValueError('No input files found in directory')
    files.sort()
    df = pd.DataFrame()
    for f in files:
        print(f)
        (df_temp,info) = import_csv(f)

        df = df.append(df_temp)

    return (df,info)


