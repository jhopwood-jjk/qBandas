# qBandas

qBandas (QuickBase + Pandas) is a Python package designed to effeciently transfer tabular data between QuickBase applications and the popular Python data handling library Pandas. If you are new to Pandas, you can read more about it [here](https://pandas.pydata.org/).

The advantages of this approach over a QuickBase pipeline are:
* Access to databases through Python libraries like [pyodbc](https://github.com/mkleehammer/pyodbc) and [SASPy](https://sassoftware.github.io/saspy/).
* Greater control over features like error logging, data processing, automated reporting, and scheduling.
* Significantly less performance impact on your QuickBase application.
* Access tabular data from local sources. 
* Coming in v1.1.0: ~~Use SQL to pull data from your QuickBase app.~~ Easily pull data from a QuickBase app.

The disadvantages of this approach compared to a pipeline are:
* Requires some knowledge of Python and Pandas.

## Setup

To use this library, simply get it from pypi. First, update your pip, then install qBandas 


```bash
python -m pip install -U pip qbandas
```

You can now use it through import.

```python
import qbandas
```

## Getting Started

To show you the ropes, I will demo a walkthrough of uploading a DataFrame to QuickBase. 

### 1) Get Your Data

Read your tabular data into Python. The method you use for this is up to you. This step is one of the greatest strenghts of this method compared to a pipeline as you can get your data from anywher. 

```python
import pandas as pd

data = {
  "name": ['John', 'Michael', 'Jill'],
  "age": [50, 40, 45],
  "phone": ["(555) 123-456", "(123) 999-4321", "(675) 555-1234x777"]
}

df = pd.DataFrame(data) # my data is in df
```

### 2) Gathering QuickBase Information

You will need to provide credentials in the form of a `headers.json` file. This file is used to authenticate requests to the QuickBase API. You can create the file by running the following. 

```python
qbandas.headers.create(interactive = True, repair = True)
```

### 3) Getting a Schema

__What is this an why do I have to do it?__ \
Schemas are just META data bout a table. qBandas uses locally stored schemas to automatically handle data formatting for you. The QuickBase API has strict rules about how the data should be delivered, so we need to "ask" the API ahead of time for a schema *before* we can send any data. 

All you will need is the table's `DBID`; this is the hash that comes after `/db/` in any QuickBase url.  

```python
qbandas.schema.pull("dbid")
```

You should see that a `./schemas/` directory was created with one file in it. I recommend that you rerun the schema pull anytime your QuickBase table adds, removes, or modifies its fields __not__ its records. 

### 4) Sending the Data

You are all set! You can send data to your app now.

```python 
qbandas.upload.records(df, "dbid")
```