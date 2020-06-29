import pandas as pd
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rc
import requests
import warnings
warnings.filterwarnings('ignore')

class Covid():
    def __init__(self):
        states = requests.get('https://covidtracking.com/api/states/daily').json()
        states = pd.DataFrame(states)
        states.loc[:,'date'] = pd.to_datetime(states.date, format='%Y%m%d')
        states.set_index('date', inplace = True)
        self.states_data = states
        self.weekly_aggregate()
        self.state_columns()


    def weekly_aggregate(self):
        dataframe = pd.DataFrame()
        for name in self.states_data.state.unique():
            filtered_df = self.states_data[self.states_data.state == name]
            grouped = filtered_df.groupby(pd.Grouper(freq='W')).sum()
            grouped['state'] = name
            dataframe = pd.concat([dataframe, grouped])
        self.weekly=dataframe
        self.top_states = self.weekly.sort_values(by='positiveIncrease', ascending=False)\
                            .drop_duplicates(subset=['state'])\
                            .head(10)\
                            .state\
                            .values
            
    def state_columns(self):
            
        self.pivot = self.weekly.pivot(columns = 'state', values='positiveIncrease').fillna(0)
        

        
    def plot_proportions(self, columns=None, title='COVID19 Case\nIncrease'):
    
        if columns is not None:
                pass
        else:
            columns = self.top_states
            
        colors = ['#026813','#A00560', '#ccc508', 
                  '#E87408', '#0000FF', '#06ECF4',
                  '#BD0505', '#EA03D7', '#07DE2A', '#7F5301']
        self.map_ = {}
        for idx in range(len(columns)):
            self.map_[columns[idx]] = colors[idx]
        
        def color(column):
            if column in self.map_:
                return self.map_[column]
            else:
                return '#111111'

        rc('font',**{'family':'serif','serif':['Andale Mono'], 'size': 18})

        x = self.pivot.index
        y = [self.pivot[column] for column in self.pivot.columns]
        colors = [color(column) for column in self.pivot.columns]
        
        fig, ax = plt.subplots(figsize=(9,16))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B %Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=30))
        ax.stackplot(x,y, colors=colors,edgecolor='white', linewidth=0)

        custom_lines = []
        names = []
        for column in self.pivot.columns:
            if column in columns:
                custom_lines.append(Line2D([0],[0], color=color(column), lw=4))
                names.append(column)

        custom_lines.append(Line2D([0], [0], color='black', lw=4))
        names.append('Other')
        ax.legend(custom_lines, names, loc='upper left',
                  bbox_to_anchor=(0,.93), ncol=1, 
                  edgecolor='black', prop={'size': 15})


        plt.gcf().autofmt_xdate()
        plt.margins(0,0)

        ax.tick_params(axis='x', labelrotation=0)
        yticks = ax.yaxis.get_major_ticks()
        yticks[0].set_visible(False)
        handles,labels = ax.get_legend_handles_labels()
        fig.suptitle(title, y=.85, x=.3, fontsize=50, color='white', horizontalalignment='left')

        ax.axis(False)
        return fig
    
    def outbreaks(self):
        diff = self.pivot.diff().dropna()
        last_three_weeks_diff = diff.iloc[-3:]
        average_change = pd.DataFrame(last_three_weeks_diff.mean(), columns = ['mean_change'])
        self.outbreak_columns = list(average_change.sort_values(by='mean_change', ascending=False).head(10)\
                                                                     .index)
        
        self.plot_proportions(columns=self.outbreak_columns, title='COVID19\nOutbreaks')