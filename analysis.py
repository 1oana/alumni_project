import pandas as pd

students = pd.read_excel('students.xlsx', sheet_name='Students')

print(students.columns)

for prefix in ['UG', 'PG']:

    universities = list(students[f'{prefix}University'])

    universities = list(set(universities))

    universities = sorted([str(i) for i in universities])

    universities = '\n'.join(universities)

    with open(f"{prefix}universities.txt", "w") as f:
        f.write(universities)


