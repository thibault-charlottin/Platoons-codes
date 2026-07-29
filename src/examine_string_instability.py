import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast
import statsmodels.stats.multicomp as mc

sns.set_theme()
sns.set(font_scale = 1.2)


def import_platoons(path):
    files = os.listdir(path)
    dataplatoons = pd.DataFrame()
    for f in files : 
        df = pd.read_csv(path+f)
        dataplatoons = pd.concat([dataplatoons,df])
    return dataplatoons



def calculate_num_acc(row):
    if row['platoon with 3 ACC']:
        return 3
    elif row['platoon with 2 ACC']:
        return 2
    else:
        return 0  # Aucun ACC

def plot_stability(df):
    df['num_ACC'] = df.apply(calculate_num_acc, axis=1)
    df['strict_stable'] = df['strict stability'].apply(lambda x: 1 if x == 'Stable' else 0)
    df['weak_stable'] = df['weak stability'].apply(lambda x: 1 if x == 'Stable' else 0)

    stability_counts = df.groupby('num_ACC').agg(
        strict_stability_percentage=('strict_stable', 'mean'),
        weak_stability_percentage=('weak_stable', 'mean')
    )

    stability_counts['strict_stability_percentage'] *= 100
    stability_counts['weak_stability_percentage'] *= 100
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(8, 6), sharey=True)

    sns.barplot(x=stability_counts.index, y='strict_stability_percentage', data=stability_counts, ax=ax1, palette=['#1F77B4'])
    ax1.set_ylabel('Percentage of Strict Stability')
    ax1.set_xlabel('') 
    ax1.set_yticks([0,25,50,75,100])

    sns.barplot(x=stability_counts.index, y='weak_stability_percentage', data=stability_counts, ax=ax2, palette=['#FF7F0E'])
    ax2.set_ylabel('Percentage of Weak Stability')
    ax2.set_yticks([0,25,50,75,100])

    plt.xlabel('Number of ACC in the Platoon')

    plt.tight_layout()
    plt.savefig('out/images/string_stability_compa.pdf',dpi=300)
    plt.show()

def examine_stats_instability(df):
    comp = mc.MultiComparison(df['strict_stable'], df['num_ACC'])
    post_hoc_res = comp.tukeyhsd()
        
    print("\nPost-hoc Results:")
    print(post_hoc_res.summary())


    comp = mc.MultiComparison(df['weak_stable'], df['num_ACC'])
    post_hoc_res = comp.tukeyhsd()
        
    print("\nPost-hoc Results:")
    print(post_hoc_res.summary())
