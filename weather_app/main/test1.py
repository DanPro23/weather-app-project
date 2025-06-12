import pandas as pd

data1 = {
    'Name': ['Dylan', 'Omelia', 'Ricardo'],
    'Age': [23, 16, 45]
}

df = pd.DataFrame(data1)

print(df['Name'])