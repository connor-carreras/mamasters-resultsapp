import json
import time



# Process the columns for the updated record for the UPDATE statement
#
def process_cols(columns, tabname):
    i = 0
    stmt = ""
    tabname = tabname
    for c in columns:
        if i == 0:
            stmt = "UPDATE " + tabname + " SET " + c + " = '" + columns[c] + "'"
            i = 5
        else:
            stmt = stmt + ", " + c + " = '" + columns[c] + "'"
    return stmt

#
# Get the columns and column values and build out the UPDATE statement
#
def select_cols (df, idx):
    first = True
    stmt = ""
    cols = list(df.columns.values)
    for col in cols:
        if first:
            stmt = " WHERE " + col + " = '" + str(df.iloc[idx][col]) + "'"
            first = False
        else:
            if str(df.iloc[idx][col]) == 'None':
                stmt = stmt + " AND " + col + " IS NULL "
            else:
                stmt = stmt + " AND " + col + " = '" + str(df.iloc[idx][col]) + "'"
    return stmt

#
# Get the columns and column values and build out the INSERT statement
#
def insert_cols(cols, tabname):
    first = True
    stmt = ""
    vals = ""
    tabname = tabname
    for col in cols:
        if first:
            stmt = "INSERT INTO " + tabname + " ( " + col 
            vals = " VALUES ('" + str(cols[col]) + "'"
            first = False
        else:
            stmt = stmt + ", " + col 
            vals = vals + ", '" + str(cols[col]) + "'"
    return stmt + ") " + vals + ");"

#
# Get the columns / values for the DELETE statement
#
def delete_cols(idx, df, tabname):
    first = True
    stmt = ""
    cols = list(df.columns.values)
    for col in cols:
        if first:
            stmt = "DELETE FROM " + tabname + " WHERE " + col + " = '" + str(df.iloc[idx][col]) + "'"
            first = False
        else:
            if str(df.iloc[idx][col]) == 'None':
                stmt = stmt + " AND " + col + " IS NULL "
            else:
                stmt = stmt + " AND " + col + " = '" + str(df.iloc[idx][col]) + "'"
    return stmt