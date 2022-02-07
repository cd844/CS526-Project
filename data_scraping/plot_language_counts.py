import json
import pprint
import pandas as pd

import plotly.express as px

pp = pprint.PrettyPrinter(indent = 4)
def main():
    with open('bq_results_10000.json', 'r') as f:
        repos = json.load(f)
        df = pd.DataFrame(repos)
        
        # use this macro to convert json string to dict()
        df['languages'] = df['languages'].apply(lambda x : json.loads(x)[0])

        # put langs into a dict
        language_list = dict() 
        i=0
        for lang in df['languages']:
            if lang != None:
                print(i)
                i+=1
                for l in lang.keys():
                    if l not in language_list.keys():
                        language_list[l] = 0
                    language_list[l] += lang[l]

        # dict to dataframe
        lang_df = pd.DataFrame()
        lang_df['language'] = [l for l in language_list.keys()]
        lang_df['bytes'] = [language_list[l] for l in language_list.keys()]
        print(lang_df)

        # remove rows that make up less than .1% of the total, aggregate into 'other'
        total_bytes = lang_df['bytes'].sum()
        thresh = total_bytes * 1e-3
        #low = lang_df[lang_df['bytes'] < thresh]
        low = lang_df['bytes'] < thresh
        other_count = lang_df[low]['bytes'].sum()
        lang_df = lang_df[(lang_df['bytes'] > thresh)]
        lang_df = lang_df.reset_index(drop=True)
        lang_df = pd.concat([lang_df, pd.DataFrame({'language':'other', 'bytes':other_count}, index=[0])], ignore_index=True)

        print(lang_df)
        
        pie_fig = px.pie(lang_df, values = 'bytes', names='language', title='bytes in language')
        pie_fig.show()
        bar_fig = px.bar(lang_df, x='language', y='bytes')
        bar_fig.show()

if __name__ == "__main__":
    main()