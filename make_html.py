text = "<!DOCTYPE html>"

input_fol = "../input/"
figfol = "../figures/"

css_name = f"{input_fol}style"
js_name = f"{input_fol}script"

text += '\n<html lang="en">'
text += "\n"

text += "\n<head>"
# link to the css file
text += f'\n  <link rel="stylesheet" href="{css_name}.css">'
text += "\n</head>"
text += "\n"
text += "\n<body>"

text += "\n<h1>Alumni Project Dashboard</h1>"

text += "\n<h2>Summary</h2>"
text += "\n<p>This dashboard contains information about the data \
    collected and analysed as part of the alumni project.\
        I have grouped plots and summaries by theme which you can access using the dropdowns (hopefully)!</p>"

text += '\n<button type="button" class="collapsible">Open Collapsible</button>'
text += '\n<div class="content">'
# include images
text += f'\n  <img src="{figfol}citations_hist.png" alt="Citation Histogram">'
text += "\n</div>"

# link to the javascript file
text += f'\n<script src="{js_name}.js"></script>'

text += "\n</body>"
text += "\n"
text += "\n</html>"

# save the text to a file
with open("output/dashboard_new.html", "w") as f:
    f.write(text)
