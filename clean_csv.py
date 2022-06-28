import pandas as pd
import args
import os

args.add_argument('csv_name', help='Name of the csv file to clean.')
args.add_argument('--data_path', default='.',
                  help='Directory in which the csv file is located. Default: "."')
args.parser.parse_args()

data_path = args.data_path
csv_path = os.path.join(data_path, args.csv_name)


def file_exists(x):
    return os.path.exists(os.path.join(data_path, x['filename']))


def delete_nonexistent(dataframe):
    new_dataframe = dataframe[dataframe.apply(lambda x: file_exists(x), axis=1)]
    new_df_len = len(dataframe.index)
    diff = df_len - new_df_len
    print(f'{diff} of the media files seem to be non-existent. If you proceed, these examples will be deleted. {new_df_len} examples will be left. Proceed? [y/n]')
    decision = input()
    if decision == 'y':
        return new_dataframe
    elif decision == 'n':
        return dataframe
    print(f'Input {decision} not recognised. Type y or n. If y, the examples will be removed. If n, they will be kept.')
    return delete_nonexistent(dataframe)


def drop_duplicates_and_overwrite(dataframe)
    df_len = len(dataframe.index)
    dataframe.drop_duplicates(subset='filename', inplace=True)
    nondup_len = len(dataframe.index)
    duplicates_count = df_len - nondup_len
    print(f'Dropped {duplicates_count} duplicated examples. Left {nondup_len} examples. Proceed to overwrite the csv file? [y/n]')
    decision = input()
    if decision == 'y':
        dataframe.to_csv(csv_path, sep='\t', index=False)
        return
    elif decision == 'n':
        return
    print(f'Input {decision} not recognised. Type y or n. If y, the csv file will be overwritten. If n, nothing will happen.')
    return drop_duplicates_and_overwrite(dataframe)

df = pd.read_csv(csv_path)

df_len = len(df.index)
print(f'The csv file contains {df_len} examples.')
df = delete_nonexistent(df)
drop_duplicates_and_overwrite(df)

