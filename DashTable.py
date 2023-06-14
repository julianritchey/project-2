from dash import dcc, html, dash_table


dash_table.DataTable(
    id='for-table',
    columns=df.columns.to_list(),
    # the contents of the table
    data=df.to_dict('records'),
    editable=False,              # allow editing of data inside all cells
    # allow filtering of data by user ('native') or not ('none')
    filter_action="native",
    # enables data to be sorted per-column by user or not ('none')
    sort_action="native",
    sort_mode="multi",         # sort across 'multi' or 'single' columns
    # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
    # row_selectable="single",     # allow users to select 'multi' or 'single' rows
    # choose if user can delete a row (True) or not (False)
    row_deletable=True,
    # selected_columns=[],        # ids of columns that user selects
    selected_rows=[],           # indices of rows that user selects
    # all data is passed to the table up-front or not ('none')
    page_action="native",
    page_current=0,             # page number that user is on
    page_size=30,                # number of rows visible per page
    style_cell={                # ensure adequate header width when text is shorter than cell's text
        'minWidth': 125, 'maxWidth': 300, 'width': 125, 'whiteSpace': 'normal', 'textAlign': 'left'
    },
    style_data={  # overflow cells' content into multiple lines
        'whiteSpace': 'normal',
        'height': 'auto'
    },
    style_header={
        'whiteSpace': 'normal',
        'height': 'auto'
    }
)
