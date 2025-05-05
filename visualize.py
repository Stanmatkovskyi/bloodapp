import matplotlib.pyplot as plt
import numpy as np
from platoon import Platoon, PlatoonDemand
import seaborn as sns

def plot_daily_unmet_demand_include_zeros(df, platoonSize, save_path="figures/unmet_demand_histogram.png",show_plot=True,clip_percentile=0.99,show_kde=True, use_log_scale=False):
    df['Company_TotalUnmet'] = df['Company_FWBUnmet'] + df['Company_PlasmaUnmet']

    #compute size of company
    company_size=sum(platoonSize)

    # Compute total unmet units and normalize by people
    df['Company_TotalUnmet'] = (df['Company_FWBUnmet'] + df['Company_PlasmaUnmet']) / company_size


    total_unmet=df['Company_TotalUnmet']
    zero_mask = total_unmet == 0
    zero_count = zero_mask.sum()
    total_days=len(df)
    zero_percent = (zero_count/total_days)*100
    positive_unmet = total_unmet[~zero_mask]

    #clip at 99th percentile
    cap = positive_unmet.quantile(clip_percentile)
    clipped_data = positive_unmet[positive_unmet <= cap]
    outliers = positive_unmet[positive_unmet > cap]

    plt.figure(figsize=(10, 6))

    # Plot zero values as a separate histogram bin (left-aligned)
    bin_width=(clipped_data.max()-clipped_data.min())/30 #estimate width from main hist
    zero_bin_edges = [-bin_width/2, bin_width/2]
    plt.hist([0] * zero_count, bins=zero_bin_edges, color='gray', edgecolor='black', label='Zero unmet demand')

    #visual adjustments
    if show_kde:
        sns.histplot(clipped_data, bins=30, kde=True, edgecolor='black', color='skyblue')
    else:
        plt.hist(clipped_data, bins=30, edgecolor='black', color='skyblue')

    if use_log_scale:
        plt.xscale('log')
        plt.xlabel('Total Units Unmet per Person (Log Scale)')
    else:
        plt.xlabel(f'Units Unmet per Day per Person (Capped at {clip_percentile * 100:.0f}th percentile)')


    plt.title('Histogram of Daily Unmet Demand per Person (Company) \n'+ f'{zero_percent:.2f}% of days had zero unmet demand')
    plt.xlabel('Total Units Unmet per Day per Person')
    plt.ylabel('Frequency (Number of Days)')
    plt.grid(axis='y')
    plt.tight_layout()

    plt.savefig(save_path)
    print(f"Plot saved to {save_path}")
    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_daily_unmet_demand(df, platoonSize, save_path="figures/unmet_demand_histogram.png",show_plot=True,clip_percentile=0.99,show_kde=True, use_log_scale=False):
    df['Company_TotalUnmet'] = df['Company_FWBUnmet'] + df['Company_PlasmaUnmet']

    #compute size of company
    company_size=sum(platoonSize)

    # Compute total unmet units and normalize by people
    df['Company_TotalUnmet'] = (df['Company_FWBUnmet'] + df['Company_PlasmaUnmet']) / company_size

    #exclude and count zeros
    total_unmet=df['Company_TotalUnmet']
    zero_count = (total_unmet==0).sum()
    total_days=len(df)
    zero_percent = (zero_count/total_days)*100
    positive_unmet = total_unmet[total_unmet>0]


    #clip at 99th percentile
    cap = positive_unmet.quantile(clip_percentile)
    clipped_data = positive_unmet[positive_unmet <= cap]
    outliers = positive_unmet[positive_unmet > cap]

    plt.figure(figsize=(10, 6))

    #visual adjustments
    if show_kde:
        sns.histplot(clipped_data, bins=30, kde=True, edgecolor='black', color='skyblue')
    else:
        plt.hist(clipped_data, bins=30, edgecolor='black', color='skyblue')

    if use_log_scale:
        plt.xscale('log')
        plt.xlabel('Total Units Unmet per Person (Log Scale)')
    else:
        plt.xlabel(f'Units Unmet per Day per Person (Capped at {clip_percentile * 100:.0f}th percentile)')


    plt.title('Histogram of Daily Unmet Demand per Person (Company) \n'+ f'{zero_percent:.2f}% of days had zero unmet demand')
    plt.xlabel('Total Units Unmet per Day per Person')
    plt.ylabel('Frequency (Number of Days)')
    plt.grid(axis='y')
    plt.tight_layout()

    plt.savefig(save_path)
    print(f"Plot saved to {save_path}")
    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_unmet_demand_boxplot(df, save_path="figures/platoon_unmet_boxplot.png", show_plot=True):
    # Automatically detect how many platoons exist based on columns
    unmet_cols = [col for col in df.columns if '_FWBUnmet' in col or '_PlasmaUnmet' in col]

    # Group by platoon
    platoon_names = sorted(set(col.split('_')[0] for col in unmet_cols))
    unmet_by_platoon = []

    for name in platoon_names:
        fwb_col = f'{name}_FWBUnmet'
        plasma_col = f'{name}_PlasmaUnmet'
        total_unmet = df.get(fwb_col, 0) + df.get(plasma_col, 0)
        unmet_by_platoon.append(total_unmet)

    plt.figure(figsize=(10, 6))
    plt.boxplot(unmet_by_platoon, labels=platoon_names, patch_artist=True)
    plt.title('Box-and-Whisker Plot of Total Unmet Demand per Platoon')
    plt.xlabel('Platoon')
    plt.ylabel('Total Units Unmet per Day')
    plt.grid(axis='y')
    plt.tight_layout()

    plt.savefig(save_path)
    print(f"Boxplot saved to {save_path}")

    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_transport_usage(df, save_path="figures/transport_usage_timeseries.png", show_plot=True):
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['Company_TransDays'], marker='o', linestyle='-', color='darkgreen')
    plt.title('Company-Wide Transport Usage Over Time')
    plt.xlabel('Time Step (Day)')
    plt.ylabel('Number of Transports in Use')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"Transport usage timeseries saved to {save_path}")

    if show_plot:
        plt.show()
    else:
        plt.close()

def plot_transport_space_usage(df, save_path="figures/transport_space_usage_timeseries.png", show_plot=True):
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['Company_TransSpace'], marker='o', linestyle='-', color='darkblue')
    plt.title('Company-Wide Transport Space Used Over Time')
    plt.xlabel('Time Step (Day)')
    plt.ylabel('Transport Space Used (Units)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"Transport space usage timeseries saved to {save_path}")

    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_platoon_transport_histograms(df, save_path="figures/platoon_transport_usage_combined.png", show_plot=True):
    # Find all platoon transport columns
    trans_cols = [col for col in df.columns if '_TransDays' in col and col.startswith('Platoon')]
    num_platoons = len(trans_cols)

    # Set up subplot grid
    cols = 2  # You can adjust this to 3 or 4 if you have many platoons
    rows = (num_platoons + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4), sharey=False)
    axes = axes.flatten()

    for i, col in enumerate(trans_cols):
        ax = axes[i]
        ax.hist(df[col], bins=range(int(df[col].max()) + 2), edgecolor='black', color='orange')
        ax.set_title(f'{col.split("_")[0]}')
        ax.set_xlabel('Transports Used per Day')
        ax.set_ylabel('Days')

    # Hide any extra axes
    for j in range(i+1, len(axes)):
        fig.delaxes(axes[j])

    fig.suptitle('Platoon Transport Usage Histograms', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    plt.savefig(save_path)
    print(f"Combined histogram saved to {save_path}")

    if show_plot:
        plt.show()
    else:
        plt.close()

def plot_platoon_transport_space_histograms(df, save_path="figures/platoon_transport_space_usage_combined.png", show_plot=True):
    # Find all platoon transport columns
    trans_cols = [col for col in df.columns if '_TransSpace' in col and col.startswith('Platoon')]
    num_platoons = len(trans_cols)

    # Set up subplot grid
    cols = 2  # You can adjust this to 3 or 4 if you have many platoons
    rows = (num_platoons + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4), sharey=False)
    axes = axes.flatten()

    for i, col in enumerate(trans_cols):
        ax = axes[i]
        ax.hist(df[col], bins='auto', edgecolor='black', color='orange')
        ax.set_title(f'{col.split("_")[0]}')
        ax.set_xlabel('Transport Space Used per Day')
        ax.set_ylabel('Days')

    # Hide any extra axes
    for j in range(i+1, len(axes)):
        fig.delaxes(axes[j])

    fig.suptitle('Platoon Transport Space Usage Histograms', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    plt.savefig(save_path)
    print(f"Combined histogram saved to {save_path}")

    if show_plot:
        plt.show()
    else:
        plt.close()

def plot_expired(
    df,
    platoon_sizes=None,
    save_path="figures/expired_timeseries_cumulative.png",
    show_plot=True
):
    # Daily expired units
    daily_expired = df['Company_FWBExpired'] + df['Company_PlasmaExpired']

    # Normalize if platoon sizes provided
    if platoon_sizes is not None:
        total_people = sum(platoon_sizes)
        daily_expired = daily_expired / total_people
        ylabel = 'Expired Units per Person'
        title = 'Cumulative Expired Blood Units per Person Over Time'
    else:
        ylabel = 'Expired Units'
        title = 'Cumulative Expired Blood Units Over Time'

    # Cumulative total
    cumulative_expired = daily_expired.cumsum()

    plt.figure(figsize=(12, 6))

    # Plot daily expired units as bars in the background
    plt.bar(df.index, daily_expired, color='lightcoral', alpha=0.3, label='Daily Expired')

    # Plot cumulative line
    plt.plot(df.index, cumulative_expired, marker='o', linestyle='-', color='crimson', label='Cumulative Expired')

    plt.title(title)
    plt.xlabel('Time Step (Day)')
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(save_path)
    print(f"Cumulative expired plot saved to {save_path}")

    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_midway_blood_demand(platoons: list[Platoon], save_path="figures/midway_blood_demand.png", show_plot=True):
    demand = []
    for platoon in platoons:
        for i in range(100):
            platoon.updateCombatLevel()
            cl=platoon.combatLevel
            if cl<0 or cl>=4:
                print(f"[ERROR] Invalid combat level {cl} for platoon. List: {platoon.combatLevelList}")
            demand.append(PlatoonDemand(platoon)[0])
    
    demand = np.array(demand)
    zeros  = np.count_nonzero(demand == 0)
    perZeros = zeros/len(demand)*100
    nonZeroDemand  = demand[demand != 0]

    

    plt.figure(figsize=(10, 6))
    plt.hist(nonZeroDemand, bins=30, edgecolor='black', color='skyblue')
    plt.title('Histogram of Daily Demand (Company) \n ' + f'{perZeros:.2f}% of days had no demand')
    plt.suptitle('')
    plt.xlabel('Total Units per Day')
    plt.ylabel('Frequency (Number of Days)')
    plt.grid(axis='y')
    plt.tight_layout()

    plt.savefig(save_path)
    print(f"Plot saved to {save_path}")
    if show_plot:
        plt.show()
    else:
        plt.close()

