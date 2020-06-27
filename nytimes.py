import pandas as pd
import requests
import json
from datetime import datetime, timedelta


class NyTimes():
    def __init__(self):
        NyTimes.data = self.download_data()
        yesterday = datetime.today() - timedelta(days=1)
        yesterday = f'{yesterday.year}-{yesterday.month}-{yesterday.day}'
        NyTimes.yesterday = NyTimes.data.sort_values(by='cases_pc', ascending=False)\
            .drop_duplicates(subset=['county', 'state'])\
            .loc[yesterday]

    def download_data(self):
        nytimes = pd.read_csv(
            'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
        population_data = self.population_data()
        nytimes = nytimes.dropna(subset=['fips'])
        nytimes.loc[:, 'fips'] = nytimes.fips.astype(int)
        nytimes.loc[:, 'fips'] = nytimes.fips.astype(str)
        nytimes = nytimes.merge(population_data[['pop', 'fips']], on='fips')
        nytimes.loc[:, 'date'] = pd.to_datetime(nytimes.date)
        nytimes.set_index('date', inplace=True)
        nytimes['pop'] = nytimes['pop'].astype(int)
        nytimes['cases_pc'] = nytimes.cases/nytimes['pop']
        return nytimes

    def population_data(self):
        def reformat_columns(x): return x.strip().replace(
            ' ', '_').replace('-', '_').lower()
        census_data = self.census_2019_pop()
        census_data = pd.DataFrame(census_data)
        census_data.columns = census_data.iloc[0]
        census_data.drop(0, inplace=True)
        census_data['fips'] = census_data.state + census_data.county
        census_data.columns = [reformat_columns(
            x) for x in census_data.columns]

        return census_data

    def census_2019_pop(self):

        QUERY = 'https://api.census.gov/data/2019/pep/population?get=POP&for=county&key=ef2b118b032f366e377ba482a7e9cdbc8cbfd617'
        resp = requests.get(QUERY).json()

        return resp

    def weekly_aggregate(self):
        dataframe = pd.DataFrame()
        fips = self.data.fips.unique()
        for fip in fips:
            fip_data = self.data[self.data['fips'] == fip]
            constants = fip_data[[
                'county', 'state', 'fips', 'pop', 'cases_pc']]
            grouped = fip_data.groupby(pd.Grouper(freq='W')).sum()
            grouped.drop(['pop', 'cases_pc'], axis=1, inplace=True)
            grouped = grouped.join(constants)
            dataframe = pd.concat([dataframe, grouped])
            dataframe.dropna(inplace=True)
        return dataframe

    def find_fip(self, county, state):
        filtered = NyTimes.data[(NyTimes.data['county'] == county) & (
            NyTimes.data['state'] == state)]
        fips = filtered.fips.unique()
        if len(fips) > 1:
            print('Multiple fips found')
            return fips
        elif len(fips) == 0:
            print('No matching fips were found')
        else:
            return fips
