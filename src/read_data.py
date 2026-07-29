import pandas as pd
import numpy as np


def slice_data(df_path, path_out):
    '''Slice the dataframe into separate CSV files based on the 'run-index' column.

    Parameters:
    -----------
    df_path : str
        Path to the input CSV file.
    path_out : str
        Directory path to save the sliced CSV files.

    Returns:
    --------
    None
    '''
    df = pd.read_csv(df_path)
    for run in pd.unique(df['run-index']):
        out = df[df['run-index']==run]
        out.to_csv(path_out+run+'.csv')
    return

def detect_leader(df):
    '''Detects leaders for each vehicle in the dataframe.

    Parameters:
    -----------
    df : DataFrame
        Input dataframe containing vehicle data.

    Returns:
    --------
    DataFrame
        DataFrame with an additional column 'leader' indicating the ID of the leader for each vehicle.
    '''
    df_out = pd.DataFrame(columns = df.columns)
    df_out['leader'] = []
    df['r'] = np.sqrt(df['xloc-kf']**2 + df['yloc-kf']**2)
    df['theta'] = np.arctan2(df['yloc-kf'], df['xloc-kf'])
    lanes = pd.unique(df['lane-kf'])
    for t in pd.unique(df['time']):
        at_t = df[df['time']==t]
        for l in lanes : 
            lane_at_t = at_t[at_t['lane-kf']==l]
            lane_at_t.sort_values(by = 'r', ascending = False, inplace = True)
            lane_at_t = lane_at_t.reset_index()
            leader = [np.nan]
            for k in range(len(lane_at_t['ID'])-1):
                leader.append(lane_at_t['ID'][k])
            lane_at_t['leader']=leader
            df_out = pd.concat([df_out,lane_at_t])
    return df_out

def compute_DHW(df):
    '''Compute Distance Headway (DHW) and Time Headway (THW) for each vehicle in the dataframe.

    Parameters:
    -----------
    df : DataFrame
        Input dataframe containing vehicle data.

    Returns:
    --------
    DataFrame
        DataFrame with additional columns 'DHW' (Distance Headway) and 'THW' (Time Headway).
    '''
    df_out = pd.DataFrame(columns = df.columns)
    df_out['DHW'] = [] ; df_out['THW'] = []
    for t in pd.unique(df['time']):
        at_t = df[df['time']==t]
        for lane in pd.unique(at_t['lane-kf']):
            lane_at_t = at_t[at_t['lane-kf']==lane]
            lane_at_t.sort_values(by = 'r', ascending = True, inplace = True)
            lane_at_t = lane_at_t.reset_index()
            DHW,THW = [],[]
            for k in range(len(lane_at_t['ID'])):
                if lane_at_t['leader'][k]>0 :
                    lead_df = lane_at_t[lane_at_t['ID']==lane_at_t['leader'][k]]
                    ID_df = lane_at_t[lane_at_t['ID']==lane_at_t['ID'][k]]
                    DHW.append(np.sqrt((list(lead_df['xloc-kf'])[0]-list(ID_df['xloc-kf'])[0])**2+(list(lead_df['yloc-kf'])[0]-list(ID_df['yloc-kf'])[0])**2))
                    THW.append(DHW[-1]/lane_at_t['speed-kf'][k])
                else: 
                    DHW.append(np.nan)
                    THW.append(np.nan)
            lane_at_t['DHW']=DHW
            lane_at_t['THW']=THW
            df_out = pd.concat([df_out,lane_at_t])
    return df_out

def clean_data(df_path, path_out):
    '''Clean the dataframe by detecting leaders and computing Distance Headway (DHW) and Time Headway (THW).

    Parameters:
    -----------
    df_path : str
        Path to the input CSV file.
    path_out : str
        Directory path to save the cleaned CSV files.

    Returns:
    --------
    None
    '''
    df = pd.read_csv(df_path)
    for run in pd.unique(df['run-index']):
        out = df[df['run-index']==run]
        out = detect_leader(out)
        out = compute_DHW(out)
        out.to_csv(path_out+str(run)+'.csv')
    return