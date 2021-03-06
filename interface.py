""" Interface for the Cornellsearch implementation of elasticsearch

interface example basis: https://stackoverflow.com/questions/34276663/tkinter-gui-layout-using-frames-and-grid
Bryan Oakley

"""

# Use Tkinter for python 2, tkinter for python 3
import tkinter as tk
from PIL import Image, ImageTk
import os


import matplotlib
from datetime import datetime
from matplotlib.dates import date2num
import matplotlib.dates
import matplotlib.pyplot as plt


import search

Frame = tk.Frame
Label = tk.Label
Entry = tk.Entry
Button = tk.Button
Canvas = tk.Canvas
Scrollbar = tk.Scrollbar

root = tk.Tk()
root.title('CornellSearch')



screen_width = 1450
screen_height = 1100

search_height = screen_height*0.08
res_height = screen_height*0.92
single_res_height = screen_height*0.15

bot_height = int(screen_height*0.07)
link_width = int(screen_width*0.6)

graph_width = int(screen_width-link_width)
graph_height = int(res_height*0.5)

def to_datetime(teststring):
    return datetime.strptime(teststring, '%Y-%m-%d')


def make_figure_dates(list_of_datetimes):
    list_of_datetimes = [to_datetime(date) for date in list_of_datetimes]
    values = [1 for _ in list_of_datetimes]
    values = [sum(values[:i+1]) for i, _ in enumerate(values)]
    plt.plot(list_of_datetimes, values)
    plt.savefig("current_time_plot.png")
    plt.clf()


def opendoc(doclink):
    os.system("atom "+doclink)


def make_resbox(master_frame, title, doclink, highlights, author="", titlebg='lightcyan'):
    resframe = Frame(master_frame, bg=titlebg, width=link_width, height=single_res_height)
    titleframe = Label(resframe, text=title + "\t" + author + "\t" + doclink , bg=titlebg, padx=20)
    titleframe.grid(sticky='nw')
    titleframe.grid_columnconfigure(0, minsize=link_width)
    titleframe.bind("<Button-1>", lambda e, doclink = doclink: opendoc(doclink))

    resframe.grid_columnconfigure(0, minsize=link_width)
    resframe.grid_rowconfigure(1, minsize=single_res_height)
    subresframe = Frame(resframe, bg='white')
    subresframe.grid(row=1, column=0)
    subresframe.grid_columnconfigure(0, minsize=link_width)
    subresframe.grid_rowconfigure(0, minsize=single_res_height)


    description = Label(subresframe, text=highlights, fg='gray15', bg='white', pady=20, padx=20)
    description.grid(row=0, column=0)
    description.grid(sticky='nw')
    description.grid_rowconfigure(1, minsize=single_res_height)
    rfh= resframe.winfo_reqheight()
    tfh = titleframe.winfo_reqheight()
    srfh = description.winfo_reqheight()
    return resframe, rfh+srfh




root.geometry('{}x{}'.format(screen_width, screen_height))

# create all of the main containers
search_frame = Frame(root, bg='white', width=screen_width, height=search_height)
resultframe = Frame(root, bg="white", width=screen_width, height=res_height)

search_frame.grid(row=0)
resultframe.grid(row=1)

for col in range(12):
    search_frame.grid_columnconfigure(col, minsize=screen_width/12)

for row in range(3):
    search_frame.grid_rowconfigure(row, minsize=search_height/3)



linkframe = Frame(resultframe, bg='white', width=link_width, height=res_height)
graph_frame = Frame(resultframe, bg='white', width=graph_width, height=res_height)
graph_frame.grid(sticky='n')

# layout all of the main containers
linkframe.grid(row=0, column=0)
graph_frame.grid(row=0, column=1)

# layout the widgets in the top frame
queryframe = Frame(search_frame, bg='white')
queryframe.grid(row=1, column=2, columnspan=7)


def query(somestring):
    first_results = search.elastic(somestring)
    results = [[res["_source"].get("title", ""),
                res["_source"].get("docID"),
                res.get("highlight", {'content':''})["content"],
                res["_source"].get("author", "NOT FOUND")] for res in first_results]
    dates = [res["_source"].get("date") for res in first_results]
    dates = sorted(dates)
    make_figure_dates(dates)

    if dates:
        search.word_cloud(somestring, first_results)
    basedoclink = ""
    return results, somestring + ".png", "current_time_plot.png"

def process_query(query_entry, resbox, wordcloud_frame, time_frame):
    q = query_entry.get()
    #results, wordcloud, time_graph = elastic(q)

    results, wordcloud, time_graph = query(q)
    if results:
        put_image_in_frame(wordcloud, wordcloud_frame, graph_width, graph_height)
        put_image_in_frame(time_graph, time_frame, graph_width, graph_height)

    for widget in resbox.winfo_children():
        widget.destroy()
    tot_height = 0
    doclinks = []
    for i, res in enumerate(results):
        title, doclink, abstract_or_highlight, author = res
        doclinks.append(doclink)
        abstract_or_highlight = abstract_or_highlight[0]
        abstract_or_highlight = abstract_or_highlight.replace("<em>", "")
        abstract_or_highlight = abstract_or_highlight.replace("</em>", "")
        abstract_or_highlight = abstract_or_highlight.replace("\n", "")
        if not title:
            title = "[No title found for this document]"
            resbutton, h = make_resbox(res_buttons_frame, title, doclink, abstract_or_highlight, author=author)
        else:
            resbutton, h = make_resbox(res_buttons_frame, title[6:-1], doclink, abstract_or_highlight, author=author)

        tot_height += h
        resbutton.grid(row=i, column=1, sticky='news')
    bbox = canvas.bbox(tk.ALL)

    bbox = list(bbox)
    bbox[3] = tot_height
    bbox = tuple(bbox)
    #print("search term = '", q, "' results are:\n", doclinks)
    canvas.configure(scrollregion=bbox, width=dw, height=dh)



def put_image_in_frame(imagefile, frame, width, height):
    load = Image.open(imagefile)
    resized = load.resize((width, height), Image.BICUBIC)
    render = ImageTk.PhotoImage(resized)

    # labels can be text or images
    img = Label(frame, image=render)
    img.image = render
    img.place(x=0, y=0)



# create the widgets for the top frame


################################################################################

LABEL_BG = "#ccc"  # Light gray.
ROWS, COLS = 10, 1  # Size of grid.
ROWS_DISP = 10  # Number of rows to display.
COLS_DISP = 1  # Number of columns to display.

# Create a frame for the canvas and scrollbar(s).
frame2 = tk.Frame(linkframe)
frame2.grid(row=0, sticky=tk.NW)
frame2.grid_rowconfigure(0, minsize=res_height)

# Add a canvas in that frame.
canvas = tk.Canvas(frame2, bg="white")
canvas.grid(row=0, column=0)
canvas.grid_rowconfigure(0, minsize=res_height)

# Create a vertical scrollbar linked to the canvas.
vsbar = tk.Scrollbar(frame2, orient=tk.VERTICAL, command=canvas.yview)
vsbar.grid(row=0, column=1, sticky=tk.NS)
canvas.configure(yscrollcommand=vsbar.set)

# Create a horizontal scrollbar linked to the canvas.

# Create a frame on the canvas to contain the buttons.
res_buttons_frame = tk.Frame(canvas, bg="white", bd=2)

# Add the buttons to the frame.
for i in range(1, ROWS+1):
    for j in range(1, COLS+1):
        #button = tk.Button(res_buttons_frame, padx=7, pady=7, relief=tk.RIDGE,
        #                   text="[%d, %d]" % (i, j))
        resbutton, h = make_resbox(res_buttons_frame, "", "", "", titlebg='white')
        resbutton.grid(row=i, column=j, sticky='news')

# Create canvas window to hold the buttons_frame.
canvas.create_window((0,0), window=res_buttons_frame, anchor=tk.NW)

res_buttons_frame.update_idletasks()  # Needed to make bbox info available.
bbox = canvas.bbox(tk.ALL)  # Get bounding box of canvas with Buttons.

# Define the scrollable region as entire canvas with only the desired
# number of rows and columns displayed.
w, h = bbox[2]-bbox[1], bbox[3]-bbox[1]
dw, dh = int((link_width/COLS) * COLS_DISP), int((res_height/ROWS) * ROWS_DISP)
canvas.configure(scrollregion=bbox, width=dw, height=dh)


# layout the graphs in the right frame
time_frame = Frame(graph_frame, bg='white', width=graph_width, height=graph_height)
wordcloud_frame = Frame(graph_frame, bg='white', width=graph_width, height=graph_height)

time_frame.grid(row=0)
wordcloud_frame.grid(row=1)

################################################################################



# create the linkframe widgets


linkframe.grid_columnconfigure('0', minsize=link_width)


queryframe.grid_columnconfigure(0, minsize=int(5/12 * screen_width))
queryframe.grid_columnconfigure(1, minsize=int(1/12 * screen_width))

query_entry = Entry(queryframe, bg="white")
GO_button = Button(queryframe, text="Search!", command= lambda: process_query(query_entry, res_buttons_frame, wordcloud_frame, time_frame))

query_entry.grid(row=1, column=0, sticky='nswe')
GO_button.grid(row=1, column=1, sticky='nswe')


def main():
    root.mainloop()


if __name__ == '__main__':
    main()
