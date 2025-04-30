import tabula

pdf_path = "input/Appendix_A.pdf"

# Read tables from PDF; pages="all" processes every page
# This will return a list of DataFrames, one for each table found
dfs = tabula.read_pdf(pdf_path, pages="all", stream=True)

# If you expect only one table, dfs[0] will hold it
# Otherwise, iterate over dfs for multiple tables
for i, df in enumerate(dfs):
    print(i)

print(dfs[0])
