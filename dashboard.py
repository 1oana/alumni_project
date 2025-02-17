import streamlit as st
import pandas as pd

st.title('Alumni Project: Dashboard')

input_fol = 'input/'
output_fol = 'output/'
students = pd.read_csv(f'{input_fol}students.csv')
papers = pd.read_csv(f'{output_fol}papers.csv')
