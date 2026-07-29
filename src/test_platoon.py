import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme()
from dtaidistance import dtw
from dtaidistance.preprocessing import differencing
import os
import multiprocessing


def detect_string(trajs, df, threshold,dataframe_keys):
    '''
    Function to detect strings of car-following behavior using a defined threshold for DTW values 
    to determine if two trajectories are similar enough.
    ---
    Inputs:
    trajs : pandas.DataFrame
        The dataset containing trajectory information of vehicles, including lane and position (Xroad).
    df : pandas.DataFrame
        A DataFrame containing DTW analysis results, with columns such as 'time', 'DTW', and vehicle IDs.
    threshold : float
        The maximum allowable DTW value for two trajectories to be considered similar.
    dataframe_keys : list of str
        Keys to access the required columns in the dataframe. Expected order:
            - dataframe_keys[0]: Column name for vehicle ID
            - dataframe_keys[1]: Column name for leader vehicle ID
            - dataframe_keys[2]: Column name for timestamps or datetime
            - dataframe_keys[3]: Column name for X road coordinates.

    Outputs:
    out : pandas.DataFrame
        A DataFrame that includes the original information from `df` and `trajs`, along with two new columns:
            - 'leader_string': A sequence of leader vehicles representing detected car-following behavior over time.
            - 'init_DTW': The starting time for each detected following sequence.
    '''
    vehicle_id = 'ID'
    leader = 'leader'
    datetime = 'time'
    Xroad = 'r'

    dataframe_keys = [vehicle_id,leader,datetime,Xroad]
    vehicle_id,leader,datetime, Xroad = dataframe_keys[0],dataframe_keys[1],dataframe_keys[2],dataframe_keys[3]
    DTW_dataframe = pd.merge(df, trajs[[leader, datetime, 'lane',Xroad]], left_on=[leader, 'time'],right_on = [leader,datetime], how='inner')
    out = pd.DataFrame()
    for lane in pd.unique(DTW_dataframe['lane']):
        DTW_data = DTW_dataframe[DTW_dataframe['lane']==lane]
        DTW_data.sort_values(by = ['time',Xroad],inplace = True)
        DTW_data.reset_index(inplace = True, drop = True)
        leader_string = [DTW_data[leader][0]]
        time_init = [DTW_data['time'][0]]
        current_time= DTW_data['time'][0]
        current_leader = DTW_data[leader][0]
        previous_leaders = [current_leader]
        for k in range(1,len(DTW_data['DTW'])):
            if DTW_data['DTW'][k]<threshold and DTW_data[leader][k] not in previous_leaders:
                leader_string.append(current_leader)
                time_init.append(current_time)
            elif DTW_data['DTW'][k]>threshold:
                leader_string.append(np.nan)
                current_leader = DTW_data['id'][k]
                current_time = DTW_data['time'][k]
                time_init.append(np.nan)
            elif DTW_data[leader][k] in previous_leaders and DTW_data['DTW'][k]<threshold: 
                current_leader = DTW_data[leader][k]
                leader_string.append(current_leader)
                current_time = DTW_data['time'][k]
                time_init.append(current_time)
        DTW_data['leader_string'] = leader_string
        DTW_data['init_DTW'] = time_init
        out = pd.concat([out,DTW_data])
        return out


def compute_DTW_platoon(dtw_df,trajs,threshold,dataframe_keys):
    '''
    Function to compute Dynamic Time Warping (DTW) distances at platoon scale 
    based on initial DTW results

    ---
    Inputs:
    dtw_df : pandas.DataFrame
        A DataFrame containing DTW analysis results for car following
    trajs : pandas.DataFrame
        A DataFrame containing trajectory data
    threshold : float
        The maximum allowable DTW value for considering two trajectories as similar.
    dataframe_keys : list of str
        Keys to access the required columns in the dataframe. Expected order:
            - dataframe_keys[0]: Column name for vehicle ID
            - dataframe_keys[1]: Column name for leader vehicle ID
            - dataframe_keys[2]: Column name for timestamps or datetime
            - dataframe_keys[3]: Column name for X road coordinates.

    Outputs:
    string_df : pandas.DataFrame
        An updated DataFrame that includes:
            - 'DTW string': DTW within strings between most upstream vehicle and tested vehicle
            - All columns from the input `dtw_df` and results of `detect_string`.
    '''
    vehicle_id = 'ID'
    leader = 'leader'
    datetime = 'time'
    Xroad = 'r'

    dataframe_keys = [vehicle_id,leader,datetime,Xroad]
    vehicle_id,leader,datetime, Xroad = dataframe_keys[0],dataframe_keys[1],dataframe_keys[2],dataframe_keys[3]
    string_df = detect_string(trajs, dtw_df, threshold)
    DTW_string = [string_df['DTW'][0]]
    previous_Theta = [string_df['Theta'][0]]
    for k in range(1,len(string_df['id'])):
        id = string_df['id'][k]
        leader = string_df[leader][k]
        previous_Theta.append(string_df['Theta'][k])
        if leader>0:
            if leader == string_df[leader][k-1]:
                used_theta = np.sum(previous_Theta)
                tmin_lead = string_df['init_DTW'][k]
                tmin_follow = string_df['init_DTW'][k]+used_theta
                tmax_lead = tmin_lead + 30
                tmax_follow = tmin_follow + 30
            else : 
                used_theta = string_df['Theta'][k]
                previous_Theta = [used_theta]
                tmin_lead = string_df['init_DTW'][k]
                tmin_follow = string_df['init_DTW'][k]+used_theta
                tmax_lead = tmin_lead + 30
                tmax_follow = tmin_follow + 30
            try : 
                Xfollow = differencing(np.array(trajs[(trajs[datetime]>tmin_follow)&(trajs[datetime]<tmax_follow)&(trajs[vehicle_id]==id)][Xroad]), smooth=0.1)
                Xlead = differencing(np.array(trajs[(trajs[datetime]>tmin_lead)&(trajs[datetime]<tmax_lead)&(trajs[vehicle_id]==leader)][Xroad]), smooth=0.1)
                distance, paths = dtw.warping_paths(Xlead, Xfollow)
                DTW_string.append(distance)
            except Exception:
                DTW_string.append(np.nan)
        else : 
            DTW_string.append(np.nan)
            previous_Theta = []
            leader = id
    string_df['DTW string'] = DTW_string
    return string_df


def routine(files_info):
    file,dtw_path,trajpath,dtw_threshold = files_info
    trajs = pd.read_csv(os.path.join(trajpath, file))
    for dtw_file in os.listdir(dtw_path):
        if file in dtw_file:
            dtw_data = pd.read_csv(os.path.join(dtw_path, dtw_file))
    string_evaluation = compute_DTW_platoon(dtw_data,trajs,dtw_threshold)
    string_evaluation.to_csv(f'out/string_dtw/{file}')
    print(f"Processed {trajs}")
    return
def study_platoon_evolution(out):
    results = pd.DataFrame()
    for k in pd.unique(out['leader_string']):
        test = out[out['leader_string']==k]
        begin = min(test['time'])
        init = test[test['time'] == pd.unique(test['time'])[0]]
        if (init['DTW string'] ).all():
            duration = 30
            compo = pd.unique(init['id'])
        else :
            compo = []
        for t in pd.unique(test['time']):
            init = test[test['time'] == t]

            if len(compo)>0:
                if (init['DTW string'].values ).all()< 1.5 and len(pd.unique(init['id']))==len(compo):
                    duration += 5
                elif (init['DTW string'] ).all()< 1.5 and len(pd.unique(init['id']))<len(compo): 
                    results = pd.concat([results, pd.DataFrame({'leader' : k, 'compo': [compo],'DTW ': init['DTW string'], 'begin' : begin, 'duration': duration, 'reason' : 'extraction'})])
                    compo = pd.unique(init['id'])
                    begin = t
                    duration = 30
                elif  (init['DTW string'] < 1.5).all() and len(pd.unique(init['id']))>len(compo): 
                    results = pd.concat([results, pd.DataFrame({'leader' : k, 'compo': [compo],'DTW ': init['DTW string'], 'begin' : begin, 'duration': duration, 'reason' : 'insertion'})])
                    compo = pd.unique(init['id'])
                    begin = t
                    duration = 30
                else :
                    results = pd.concat([results, pd.DataFrame({'leader' : k, 'compo': [compo],'DTW ': init['DTW string'], 'begin' : begin, 'duration': duration, 'reason' : 'disengagement'})])
                    compo = []
            else : 
                if (init['DTW string'].values ).all()< 1.5:
                    compo = pd.unique(init['id'])
                    duration = 30
                    begin = t
    return results
