# qBandas

qBandas (QuickBase + Pandas) is a Python package designed to effeciently transfer tabular data between QuickBase applications and the popular Python data handling library Pandas. If you are new to Pandas, you can read more about it [here](https://pandas.pydata.org/).

The advantages of this approach over a QuickBase pipeline are:
* Access to databases through Python libraries like [pyodbc](https://github.com/mkleehammer/pyodbc) and [SASPy](https://sassoftware.github.io/saspy/).
* Greater control over features like error logging, data processing, automated reporting, and scheduling.
* Significantly less performance impact on your QuickBase application.
* Access tabular data from local sources. 
* Coming in v1.1.0: Use SQL to pull data from your QuickBase app.

The disadvantages of this approach compared to a pipeline are:
* Requires knowledge of Python and Pandas.

## Setup

To use this library, simply get it from pypi. First, update your pip, then install qBandas 


```bash
python3 -m pip install --upgrade pip
python3 -m pip install qbandas
```

You can now use it through import.

```python
import qbandas as qb
```

## Getting Started

To show you the ropes, I will do a walkthrough of uploading a DataFrame to QuickBase. If you are new to Python or Pandas, it might be a good idea to follow along with this example before you try to deploy this yourself. Unfortunately, there are no example QuickBase apps to send data to, but everything else is doable.

### 1) Get Your Data

Read your tabular data into Python. The method you use for this is up to you. This step is one of the greatest strenghts of this method compared to a pipeline. I will simply hardcode mine. 

```python
import pandas as pd

data = {
  "name": ['John', 'Michael', 'Jill'],
  "age": [50, 40, 45],
  "phone": ["(555) 123-456", "(123) 999-4321", "(675) 555-1234x777"]
}

df = pd.DataFrame(data) # my data is in df
```

### 2) Gathering QuickBase Information - `headers.json`

You will need to provide credentials in the form of a `headers.json` file in the working directory of your project. You can automaitically generate a template for the file by running the following

```bash
python -m qbandas --head
```

Fill in the header information. Some explanations are provided below.

```json
{
    "QB-Realm-Hostname": "{QB-Realm-Hostname}",
    "User-Agent": "{User-Agent}",
    "Authorization": "{Authorization}"
}
```

* `"QB-Realm-Hostname"` 
    - Something like `"example.quickbase.com"`
* `"User-Agent"`
    - A name to identify yourself in the app logs. Can be anything.
* `"Authorization"` 
    - This is typically a QuickBase user token. Learn how to get one [here](https://developer.quickbase.com/auth).

### 3) Creating a Schema

Once you have the `headers.json` file you can make a schema for your destination table. You will need the table's `DBID`; this is the hash that comes after `/db/` in any QuickBase url. Each table has a unique identifier, and they can be found by visiting the table on the web. Run the Python command below replacing `"dbid"` with your table's `DBID`.

```python
qb.pull_schema("dbid")
```

### 4) Sending the Data

You are all set! You can send data to your app now.

```python 
qb.upload_records(df, "dbid")
```