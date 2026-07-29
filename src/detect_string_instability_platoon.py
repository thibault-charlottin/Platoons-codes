import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast
import os

def retieve_3_ACC_platoon(platoon_df, trajs_df):
    ACC_ids = pd.unique(trajs_df[trajs_df['ACC'] == 'Yes']['ID'])
    platoon_df['platoon with 3 ACC'] = ((platoon_df['ACC'].str.contains('True,True')) & (platoon_df['leader'].isin(ACC_ids))) | (platoon_df['ACC'].str.contains('True,True,True'))
    platoon_df['platoon with 2 ACC'] = ((platoon_df['ACC'].str.contains('True')) & (platoon_df['leader'].isin(ACC_ids))) | (platoon_df['ACC'].str.contains('True,True')) & (platoon_df['platoon with 3 ACC'] == False)
    platoon_df['platoon with 1 ACC'] = (platoon_df['ACC'].str.contains('True')) & (platoon_df['platoon with 2 ACC'] == False) & (platoon_df['platoon with 3 ACC'] == False)
    return platoon_df

def create_string_instability_test_vectors(platoon_compo, t_min, t_max, trajs_df):
    num_platoon = len(platoon_compo)
    num_timepoints = int((t_max + 30 - t_min) * 10)
    speed_vector = np.full((num_platoon, num_timepoints), np.nan)
    
    for k in range(num_platoon):
        vehicle_data = trajs_df[(trajs_df['time'] > t_min) & (trajs_df['time'] < t_max) & (trajs_df['ID'] == platoon_compo[k])]
        vehicle_data = vehicle_data.sort_values(by='time')
        num_data_points = len(vehicle_data)
        if num_data_points > 0:
            speed_vector[k, :num_data_points] = vehicle_data['speed-kf'].values[:num_data_points]
    
    return speed_vector

def truncate_speed_vectors(speed_vectors):
    valid_lengths = np.apply_along_axis(lambda col: np.max(np.where(~np.isnan(col))) + 1 if not np.all(np.isnan(col)) else 0, axis=1, arr=speed_vectors)
    max_valid_length = np.max(valid_lengths)
    speed_vectors_truncated = speed_vectors[:, :max_valid_length]
    
    return speed_vectors_truncated

def calculate_p_norms(speed_vectors):
    diff_vectors = np.diff(speed_vectors, axis=0)
    norm_2 = np.linalg.norm(diff_vectors, axis=1)  # 2-norm
    norm_inf = np.linalg.norm(diff_vectors, ord=np.inf, axis=1)  # infinity norm
    return norm_2, norm_inf

def string_stability_test(speed_vectors):
    speed_vectors_truncated = truncate_speed_vectors(speed_vectors)
    norm_2, norm_inf = calculate_p_norms(speed_vectors_truncated)
    strict_stability  = 'Stable'
    weak_stability = 'Stable'
    for k in range(1,len(norm_2)):
        if  norm_inf[k] / norm_inf[k-1] < 1:
            strict_stability = 'Unstable'
        if norm_inf[k] / norm_inf[0] < 1:
            weak_stability = 'Unstable'
    return weak_stability, strict_stability

def add_stability_information(trajs_df, platoon_df):
    platoon_df['platoon compo'] = platoon_df['platoon compo'].apply(ast.literal_eval)
    strict_stability = []
    weak_stability = []
    for k in range(len(platoon_df['platoon compo'])):
        platoon_compo = [platoon_df['leader'][k]] + platoon_df['platoon compo'][k]
        tmin = platoon_df['time'][k]
        tmax = tmin + 30
        speed_vectors = create_string_instability_test_vectors(platoon_compo, tmin, tmax, trajs_df)
        strict, weak = string_stability_test(speed_vectors)
        strict_stability.append(strict)
        weak_stability.append(weak)
    platoon_df['strict stability'] = strict_stability
    platoon_df['weak stability'] = weak_stability
    return platoon_df

def routine(path_platoon, path_trajs):
    files = os.listdir(path_platoon)
    for f in files:
        platoon_df = pd.read_csv(os.path.join(path_platoon, f))
        trajs_df = pd.read_csv(os.path.join(path_trajs, f))
        platoon_df = add_stability_information(trajs_df, platoon_df)
        platoon_df = retieve_3_ACC_platoon(platoon_df, trajs_df)
        platoon_df.to_csv(os.path.join(path_platoon, f))


