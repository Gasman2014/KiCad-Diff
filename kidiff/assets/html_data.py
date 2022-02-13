# Get HTML Data from HTML files (easier to manage)

import os


script_path = os.path.dirname(os.path.realpath(__file__))

# Main Page

with open(script_path + "/index_header.html", "r") as file:
    index_header = "".join(map(str, file.readlines()))

with open(script_path + "/index_gallery_item.html", "r") as file:
    index_gallery_item = "".join(map(str, file.readlines()))

with open(script_path + "/index_footer.html", "r") as file:
    index_footer = "".join(map(str, file.readlines()))


# Triptych Page(s)

with open(script_path + "/triptych.js", "r") as file:
    triptych_js = "".join(map(str, file.readlines()))

with open(script_path + "/triptych.html", "r") as file:
    triptych_html = "".join(map(str, file.readlines()))


triptych_footer = "<script>" + triptych_js + "</script></body></html>"
