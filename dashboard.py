import streamlit as st
import pandas as pd

st.title('Alumni Project: Dashboard')

input_fol = 'input/'
output_fol = 'output/'
csv_fol = f'{output_fol}csv/'
students = pd.read_excel(f'{input_fol}students.xlsx', sheet_name='Students')
papers = pd.read_csv(f'{csv_fol}papers.csv')
