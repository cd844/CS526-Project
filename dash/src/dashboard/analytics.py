import pandas as pd
def count_language_bytes(df):
    # put langs into a dict
    language_list = dict() 
    i=0
    for lang in df['languages']:
        if lang != None:
            i+=1
            for l in lang.keys():
                if l not in language_list.keys():
                    language_list[l] = 0
                language_list[l] += lang[l]

    # dict to dataframe
    lang_df = pd.DataFrame()
    lang_df['language'] = [l for l in language_list.keys()]
    lang_df['bytes'] = [language_list[l] for l in language_list.keys()]
    #print(lang_df)

    # remove rows that make up less than .1% of the total, aggregate into 'other'
    total_bytes = lang_df['bytes'].sum()
    thresh = total_bytes * 1e-3
    #low = lang_df[lang_df['bytes'] < thresh]
    low = lang_df['bytes'] < thresh
    other_count = lang_df[low]['bytes'].sum()
    lang_df = lang_df[(lang_df['bytes'] > thresh)]
    lang_df = lang_df.reset_index(drop=True)
    lang_df = pd.concat([lang_df, pd.DataFrame({'language':'other', 'bytes':other_count}, index=[0])], ignore_index=True)
    return lang_df

# same as above but each use of language per repo is weighed the same
def count_language_use(df):
    # put langs into a dict
    total = 0
    language_list = dict() 
    i=0
    for lang in df['languages']:
        if lang != None:
            i+=1
            for l in lang.keys():
                total += 1
                if l not in language_list.keys():
                    language_list[l] = 0
                language_list[l] += 1

    # dict to dataframe
    lang_df = pd.DataFrame()
    lang_df['language'] = [l for l in language_list.keys()]
    lang_df['count'] = [language_list[l] for l in language_list.keys()]
    #print(lang_df)

    # find better way to aggregate OTHER category
    #low = lang_df[lang_df['bytes'] < thresh]
    thresh = total * 1e-3
    low = lang_df['count'] < thresh
    other_count = lang_df[low]['count'].sum()
    lang_df = lang_df[(lang_df['count'] > thresh)]
    lang_df = lang_df.reset_index(drop=True)
    lang_df = pd.concat([lang_df, pd.DataFrame({'language':'other', 'count':other_count}, index=[0])], ignore_index=True)

    return lang_df

