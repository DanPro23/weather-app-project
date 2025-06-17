import pandas as pd

data1 = {
    'Name': ['Dylan', 'Omelia', 'Ricardo'],
    'Age': [23, 16, 45]
}

df = pd.DataFrame(data1)

print(f"{df['Name']}\n")
print(f"{df.head(1)}\n")