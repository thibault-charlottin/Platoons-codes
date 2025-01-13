import pandas as pd
import numpy as np
from dtaidistance import dtw
from dtaidistance.preprocessing import differencing
import os
import multiprocessing

print('define vehicle ID key')
vehicle_id = input()
print('define leader ID key')
leader = input()
print('define time key')
datetime = input()
print('define X road coordinates key')
Xroad = input()

dataframe_keys = [vehicle_id,leader,datetime,Xroad]

def test_car_following_by_time(data,lead,follow,tau_list,window,step,dataframe_keys):
    """
    Function that compares over time the trajectory of a leader and a follower vehicle.
    It calculates the Dynamic Time Warping (DTW) distance between the trajectories of 
    the lead and follower vehicles for various time shifts (taus).
    ---
    Inputs:
    data : pandas.DataFrame
        The dataset containing trajectories of vehicles, including spatial and temporal 
        information.
    lead : int or str
        Identifier for the leader vehicle.
    follow : int or str
        Identifier for the follower vehicle.
    tau_list : list of float
        A list of time-shift values (taus) to test between the leader and follower trajectories.
    window : float
        The time window over which to compute the DTW distance at each step.
    step : float
        The step size for sliding the time window forward.
    dataframe_keys : list of str
        Keys to access the required columns in the dataframe. Expected order:
            - dataframe_keys[0]: Column name for vehicle ID
            - dataframe_keys[1]: Column name for leader vehicle ID
            - dataframe_keys[2]: Column name for timestamps or datetime
            - dataframe_keys[3]: Column name for X road coordinates.

    Outputs:
    time : list of float
        List of timestamps corresponding to the start of each time window.
    DTW : list of float
        List of DTW distances for the optimal tau at each time window.
    tau_out : list of float
        List of taus (time shifts) that resulted in the minimum DTW distance for each time window.
    """
    vehicle_id,leader,datetime, Xroad = dataframe_keys[0],dataframe_keys[1],dataframe_keys[2],dataframe_keys[3]
    x1 = data[data[vehicle_id]==lead]
    x2 = data[(data[vehicle_id]==follow)]
    T = x2[x2[leader]==lead][datetime]
    DTW = []
    time = []
    tau_out = []
    k = min(T)
    if max(T)-min(T)<window:
        window = max(T)-min(T)
    while k<max(T):
        DTW_loc = []
        for tau in tau_list:
            tmin_lead = int(k)
            tmax_lead = min(int(k+(window)),max(T))
            tmin_follow = k+tau
            tmax_follow = k+window+tau
            try : 
                X1 = differencing(np.array(x1[(x1[datetime]<=tmax_lead)&(x1[datetime]>=tmin_lead)][Xroad]), smooth=0.1)
                X2 = differencing(np.array(x2[(x2[datetime]<=tmax_follow)&(x2[datetime]>=tmin_follow)][Xroad]), smooth =0.1)
                distance, paths = dtw.warping_paths(X1, X2)
                DTW_loc.append(distance)
            except Exception :
                DTW_loc = 100000 #insane value to drop this outlier
        min_index = DTW_loc.index(min(DTW_loc))
        DTW.append(DTW_loc[min_index])
        tau_out.append(tau_list[min_index])
        time.append(k)
        k=k + step
    return time,DTW, tau_out

def create_dtw_by_time_df(data,tau_list,window,step,dataframe_keys):
    """
    Function to compute Dynamic Time Warping (DTW) distances over time for all leader-follower 
    vehicle pairs in the dataset and compile the results into a DataFrame.

    ---
    Inputs:
    data : pandas.DataFrame
        The dataset containing trajectories of vehicles, including spatial and temporal 
        information.
    tau_list : list of float
        A list of time-shift values (taus) to test between leader and follower trajectories.
    window : float
        The time window over which to compute the DTW distance at each step.
    step : float
        The step size for sliding the time window forward.
    dataframe_keys : list of str
        Keys to access the required columns in the dataframe. Expected order:
            - dataframe_keys[0]: Column name for vehicle ID
            - dataframe_keys[1]: Column name for leader vehicle ID
            - dataframe_keys[2]: Column name for timestamps or datetime
            - dataframe_keys[3]: Column name for X road coordinates.

    Outputs:
    df_out : pandas.DataFrame
        A DataFrame containing the following columns:
            - 'id': Follower vehicle IDs
            - 'leader': Leader vehicle IDs
            - 'time': Timestamps corresponding to the start of each time window
            - 'DTW': DTW distances for the optimal tau at each time window
            - 'Theta': The tau (time shift) that resulted in the minimum DTW distance
    """
    vehicle_id,leader,datetime = dataframe_keys[0],dataframe_keys[1],dataframe_keys[2],dataframe_keys[3]
    time_list,id_list,leader_list,DTW_list,Tau_list = [], [],[],[],[]
    df_lead_follow_pairs = data[[leader, vehicle_id]].drop_duplicates()
    df_lead_follow_pairs.dropna(inplace=True)
    df_lead_follow_pairs.reset_index(inplace=True)
    for k in range (len(df_lead_follow_pairs[vehicle_id])):
        leader = df_lead_follow_pairs[leader][k]
        id = df_lead_follow_pairs[vehicle_id][k]
        time,DTW, Tau = test_car_following_by_time(data,leader,id,tau_list,window,step,dataframe_keys)
        id_list+= [id for k in range(len(time))]
        leader_list+= [leader for k in range(len(time))]
        time_list+=time
        DTW_list+=DTW
        Tau_list+=Tau
        print(id,leader,' done', k)
    df_out = pd.DataFrame({'id':id_list,'leader':leader_list,'time':time_list,'DTW':DTW_list, 'Theta': Tau_list})
    return df_out


def process_file(file_info):
    file, path, tau_values, window, step = file_info
    df = pd.read_csv(os.path.join(path, file))
    DTW_df = create_dtw_by_time_df(df, tau_values, window, step)
    DTW_df.to_csv(f'out/DTW_CF_{file}')
    print(f"Processed {file}")

# Main part of the code
if __name__ == "__main__":
    print('declare path of the trajectory data')
    path = input()
    window = 30
    step = 5
    tau_values = [0.6 + 0.1 * k for k in range(0, 14)]
    
    # Prepare the list of files to process
    files = [(file, path, tau_values, window, step) for file in os.listdir(path)]

    # Set up multiprocessing pool
    num_workers = multiprocessing.cpu_count()  # You can adjust the number of workers
    with multiprocessing.Pool(processes=num_workers) as pool:
        pool.map(process_file, files)