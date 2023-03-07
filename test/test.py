import sys, os; sys.path.append(os.path.abspath(".."));
import src.qbandas as qb;
import pandas as pd


if __name__ == '__main__':

    #qb.pull_schema("bs397hfuy")
    
    #df = pd.read_csv("data.csv")
    #qb.upload_records(df, "Example Table", drop=True)

    qb.set_args("Example Table", "names", "nums", argy="Arga")
    qb.add_args("Example Table",  more_args="replacement!")
    #qb.upload_records(df, "Example Table", debug=True, drop=True)


