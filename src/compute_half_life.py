import pandas as pd
import statsmodels.api as sm
import numpy as np
import ast
import matplotlib.pyplot as plt
from scipy.stats import shapiro
import seaborn as sns
import os
sns.set_theme()
sns.set(font_scale=1.5)

def import_platoons(platoonspath):
    """
    Import all platoon data from the specified path.
    
    Parameters:
    - platoonspath: Path to the platoon data files.
    
    Returns:
    - alldata: A pandas DataFrame containing all concatenated platoon data.
    """
    alldata = pd.DataFrame()
    for f in os.listdir(platoonspath):
        df = pd.read_csv(os.path.join(platoonspath, f))
        df['ACC'] = df['ACC'].apply(ast.literal_eval)
        alldata = pd.concat([alldata, df])
    
    alldata['has_ACC'] = alldata['ACC'].apply(lambda k: True in k)
    return alldata.reset_index()


def count_platoons_per_duration(data_platoons):
    """
    Count the number of platoons for each duration.
    
    Parameters:
    - data_platoons: A pandas DataFrame with platoon data and durations.
    
    Returns:
    - A DataFrame with the number of platoons and their corresponding durations.
    """
    platoon_duration = 30
    duration_list= [30]
    data_platoons.sort_values(by='platoon compo')
    data_platoons.reset_index(inplace =True,drop = True)
    for i in range(1,len(data_platoons['platoon compo'])):
        if data_platoons['platoon compo'][i] == data_platoons['platoon compo'][i-1]:
            platoon_duration+=5
            duration_list.append(platoon_duration)
        else :
            platoon_duration = 30
            duration_list.append(platoon_duration)
    data_platoons['duration'] = duration_list
    number = []
    duration = []
    for t in pd.unique(data_platoons['duration']):
        test = data_platoons[data_platoons['duration'] >= t]
        number.append(len(test['duration']))
        duration.append(t)
    return pd.DataFrame({'number of platoons': number, 'duration': duration}).sort_values(by='duration', ascending=True)

def perform_statistical_analysis(data, label):
    """
    Perform OLS regression and Shapiro-Wilk test on the data.
    
    Parameters:
    - data: A pandas DataFrame with the data for analysis.
    - label: A string label for identifying the type of data (e.g., 'ACC', 'No ACC').
    
    Returns:
    - The OLS model summary and Shapiro-Wilk test results.
    """
    x = sm.add_constant(data['duration'])
    y = data['log_remaining_platoons']
    model = sm.OLS(y, x).fit()
    residuals = model.resid
    
    print(f'{label} Analysis')
    stat, p = shapiro(residuals)
    print('Shapiro-Wilk Statistic:', stat)
    print('Shapiro-Wilk p-value:', p)
    print(model.summary())
    
    return model

def plot_results(data_ACC, data_no_ACC, intercept, slope_ACC, conf_int_ACC):
    """
    Plot the results of the platoon duration analysis.
    
    Parameters:
    - data_ACC: DataFrame for platoons with ACC.
    - data_no_ACC: DataFrame for platoons without ACC.
    - intercept: The intercept of the regression line.
    - slope_ACC: The slope of the regression line.
    - conf_int_ACC: Confidence interval for the slope.
    """
    x_line = np.linspace(0, max(data_ACC['duration']), 100)
    y_line = np.exp(slope_ACC * x_line + intercept)
    
    plt.figure(figsize=(8, 5))
    plt.scatter(data_ACC['duration'], data_ACC['number of platoons'], color='blue', label='All platoons')
    plt.scatter(data_no_ACC['duration'], data_no_ACC['number of platoons'], color='orange', label='HDV platoons')
    
    plt.xlabel('Duration [s]')
    plt.ylabel('Number of Platoons')
    plt.legend()
    plt.tight_layout()
    plt.savefig('remaining_TGSIM_L1_platoons.pdf')
    plt.show()
