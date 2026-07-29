import pandas as pd
import os
import seaborn as sns
sns.set_theme()
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import statsmodels.api as sm
import ast

test = pd.DataFrame()
for f in os.listdir('out/platoons/'):
    df = pd.read_csv('out/platoons/'+f)
    df['run'] = [f for k in range(len(df['time']))]
    test = pd.concat([test,df])

def Eddie_area(dataframe,xmin,xmax,frame_min,frame_max):
    return dataframe[(dataframe['r'] < xmax )
                       & (dataframe['r'] > xmin )
                       &(dataframe['time'] > frame_min )
                       &(dataframe['time'] < frame_max)]

def compute_FD(data,xmin,xmax,frame_min,frame_max):
    Q,K = [],[]
    eddie_test = Eddie_area(data,xmin,xmax,frame_min,frame_max)
    Area = np.abs(xmin-xmax)*np.abs(frame_min-frame_max)
    distance = 0
    time = 0
    for k in pd.unique(eddie_test['ID']):
        test_local = eddie_test[eddie_test['ID']==k]
        distance+=max(test_local['r'])-min(test_local['r'])
        time+=max(test_local['time'])-min(test_local['time'])
    Q = distance/Area
    K = time/Area
    return Q, K

def compute_LC_density(data,xmin,xmax,frame_min,frame_max):
    eddie_test = Eddie_area(data,xmin,xmax,frame_min,frame_max)
    Area = np.abs(xmin-xmax)*np.abs(frame_min-frame_max)
    LC = 0
    for k in pd.unique(eddie_test['ID']):
        test_local = eddie_test[eddie_test['ID']==k]
        test = test_local.reset_index(drop = True)
        for l in range(1,len(test['lane-kf'])):
            if test['lane-kf'][l-1]!=test['lane-kf'][l]:
                LC+=1
    return LC/Area

def compute_indicators(dtw_df,trajs_df,speed_limit):
    dtw_df = dtw_df.reset_index(drop = True)
    speed = []
    percentage_speed_limit = []
    has_heavy = []
    Flow = []
    Density = []
    LC_density = []
    for k in range(len(dtw_df['platoon compo'])):
        loc_speed = []
        loc_type = []
        for id in dtw_df['platoon compo'][k]:
            traj_id = trajs_df[(trajs_df['ID']==id)&(trajs_df['time']>dtw_df['time'][k])&(trajs_df['time']<dtw_df['time'][k]+dtw_df['duration'][k])]
            loc_speed.append(np.mean(traj_id['speed-kf']))
            try : 
                loc_type.append(np.array(traj_id['type-most-common'])[0])
            except Exception: 
                loc_type.append(np.nan)
        if 'large-vehicle' in loc_type : 
            has_heavy.append(1)
        else :
            has_heavy.append(0)
        try : 
            Q, k = compute_FD(trajs_df,min(traj_id['r']),max(traj_id['r']),min(traj_id['time']),max(traj_id['time']))
            LC_density.append(compute_LC_density(trajs_df,min(traj_id['r']),max(traj_id['r']),min(traj_id['time']),max(traj_id['time'])))
            Flow.append(Q)
            Density.append(k)
            speed.append(np.mean(loc_speed))
            percentage_speed_limit.append(np.mean(loc_speed)/speed_limit)
        except Exception:
            LC_density.append(np.nan)
            Flow.append(np.nan)
            Density.append(np.nan)
            speed.append(np.nan)
            percentage_speed_limit.append(np.nan)
    dtw_df['heavy in platoon'] = has_heavy
    dtw_df['mean speed'] = speed
    dtw_df['Flow'] = Flow
    dtw_df['Density'] = Density
    dtw_df['LC Density'] = LC_density
    return dtw_df


def duration(series):
    return 30 +5*len(series)

test ['duration'] = test['time']+25
test['platoon compo'] = test['platoon compo'].apply(ast.literal_eval)
test['string compo'] = test['string compo'].apply(ast.literal_eval)
test['ACC'] = test['ACC'].apply(ast.literal_eval)
test['platoon DTW'] = test['platoon DTW'].apply(ast.literal_eval)

test['lenght'] = [len(k) for k in test['platoon compo']]
DTW_for_model = pd.DataFrame()
for run in pd.unique(test['run']):
    data = test[test['run']==run]
    trajs = pd.read_csv('data/by_run/corrected/'+run)
    data = compute_indicators(data,trajs,30)
    DTW_for_model = pd.concat([DTW_for_model,data])

DTW_for_model.to_csv('out/DTW_platoon_summary.csv')
