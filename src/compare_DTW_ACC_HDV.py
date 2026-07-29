import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
import numpy as np

def load_and_process_data(datapath, DTWpath):
    """
    Load data from specified paths, merge, and classify data as ACC or HDV.
    
    Parameters:
    - datapath: Path to the corrected data files.
    - DTWpath: Path to the DTW files.
    
    Returns:
    - compile: A pandas DataFrame with the merged and processed data.
    """
    compile = pd.DataFrame()
    
    # Iterate through all files in the specified data directory
    for f in os.listdir(datapath):
        # Load the data and DTW files
        datadf = pd.read_csv(os.path.join(datapath, f))
        dtw_df = pd.read_csv(os.path.join(DTWpath, f))
        
        # Extract unique ACC IDs
        ACC_ids = pd.unique(datadf[datadf['ACC'] == 'Yes']['ID'])
        
        # Merge data on 'id' and 'time'
        dtw_df = pd.merge(dtw_df, datadf, left_on=['id', 'time'], right_on=['ID', 'time'])
        
        # Classify data as 'ACC' or 'HDV'
        dtw_df['type'] = ['ACC' if k in ACC_ids else 'HDV' for k in dtw_df['id']]
        
        # Concatenate the processed data into the compile DataFrame
        compile = pd.concat([compile, dtw_df])
    
    return compile

def filter_and_plot_data(compile):
    """
    Filter the compiled data and create plots for DTW string and speed-kf.
    
    Parameters:
    - compile: The merged and processed pandas DataFrame.
    """
    # Filter the data based on DTW string and speed criteria
    compile = compile[compile['DTW string'] < 1.5]
    compile = compile[compile['speed-kf'] < 25]
    
    # Plot DTW string values
    sns.boxplot(data=compile, x='type', y='DTW string', palette={'ACC': 'orange', 'HDV': 'blue'})
    plt.tight_layout()
    plt.title('DTW values, speed<25m/s')
    plt.show()
    
    # Plot speed-kf values
    sns.boxplot(data=compile, x='type', y='speed-kf', palette={'ACC': 'orange', 'HDV': 'blue'})
    plt.title('speed (truncated at speed 25m/s)')
    plt.tight_layout()
    plt.show()

def perform_statistical_tests(compile):
    """
    Perform Mann-Whitney U tests on the compiled data for DTW string and speed-kf.
    
    Parameters:
    - compile: The filtered pandas DataFrame containing 'type', 'DTW string', and 'speed-kf' columns.
    """
    # Perform Mann-Whitney U test for DTW string
    ACC_values = compile[compile['type'] == 'ACC']['DTW string']
    HDV_values = compile[compile['type'] == 'HDV']['DTW string']
    stat, p_value = mannwhitneyu(ACC_values, HDV_values, alternative='less')
    print(f"Test Mann-Whitney U unilatéral (DTW string): stat = {stat}, p = {p_value}")
    
    # Perform Mann-Whitney U test for speed-kf
    ACC_values = compile[compile['type'] == 'ACC']['speed-kf']
    HDV_values = compile[compile['type'] == 'HDV']['speed-kf']
    stat, p_value = mannwhitneyu(ACC_values, HDV_values, alternative='less')
    print(f"Test Mann-Whitney U unilatéral (speed-kf): stat = {stat}, p = {p_value}")

def compute_half_life(model_results):
    slope = model_results.params['duration']
    return -np.log(2)/slope