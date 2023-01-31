# qBandas

qBandas (QuickBase + Pandas) is a Python package designed to effeciently transfer tabular data between QuickBase applications and the popular Python data handling library Pandas. If you are new to Pandas, you can read more about it [here](https://pandas.pydata.org/).

The advantages of this approach over a QuickBase pipeline are:
* Unrestricted and _much_ faster data pre and post processing in Python.
* Access to databases through Python libraries like [pyodbc](https://github.com/mkleehammer/pyodbc) and [SASPy](https://sassoftware.github.io/saspy/).
* Greater control over features like error logging, automated reporting, and scheduling.
* Significantly less performance impact on your QuickBase application.
* Upload tabular data from local sources. 

The disadvantages of this approach compared to a pipeline are:
* Typically longer time to deploy.
* Requires knowledge of Python and Pandas.

## Setup

To use this library, you will need to clone this repository to your project. This package is not currently avaiable from the Python Package Index. From your terminal run the following command. Note, you will need git installed to do this. You can find the lastest version [here](https://git-scm.com/).

```bash
git clone https://github.com/jhopwood-jjk/qBandas.git
```

Alternatively, you can download this repo as a zip and place it in your project folder.

To use qBandas in your project, use the following import. Note the casing. 

```python
import qBandas.qbandas as qb
```

## Getting Started

To show you the ropes, I will do a walkthrough of uploading a DataFrame to QuickBase. If you are new to Python or Pandas, it might be a good idea to follow along with this example before you try to deploy this yourself. 

### 1) Get Your Data

Read your tabular data into Python. The method you use for this is up to you. I will simply hardcode mine. 

```python
import pandas as pd

data = {
  "name": ['John', 'Michael', 'Jill'],
  "age": [50, 40, 45]
}

df = pd.DataFrame(data) # my data is in df
```

### 2) Gathering QuickBase Information

Under the hood, qBandas calls the QuickBase API. To make the API happy, we need to give it a few bits of information. This part of the process is done entirely in Quickbase. We do this step second because if you cannot gather these items (most likely a valid user token) then you cannot use this method. This might save you the headache doing everything only to find out that you don't have permission to upload. 

You will need your:

* QuickBase realm hostname 
    - Something like `"example.quickbase.com"`
* Destination table ID 
    - This is the hash that comes after `/db/` in any QuickBase url. Each table has a unique identifier, and they can be found by visiting the table on the web.
* Valid QuickBase user token
    - Learn how to get one [here](https://developer.quickbase.com/auth).
* Agent name (Optional, for documentation purposes)
    - I am uploading names and ages, so I will call mine `"name-age-upload"`. I know, very creative.  

You can read more about how to gather each of these items [here](https://developer.quickbase.com). When you have these items, save them into variables for later use. 

I recommend storing the user token somewhat securely. There are many ways to do this and you are free to choose the one you like the best. One simple way to secure it is with an evironment varible. If you are interested, you can find out how to do it [from this stackoverflow post](https://stackoverflow.com/questions/4906977/how-can-i-access-environment-variables-in-python).

Here is what I got for this example.

```python
import os # user token is in an environment variable
hostname = "example.quickbase.com"
dbid = "1234abcdef"
token = f"QB-USER-TOKEN {os.environ['QB_USER_TOKEN']}"
agent = "name-age-upload"
```

### Creating a Schema

The schema defines how qBandas will comunicate the data to QuickBase. For example, if you have a column of integers you could specify that column as `numeric`, `text`, or `duration`. Each of those __column types__ leads to a slightly different handling of the data. Be sure to choose the one you want for your data. See the docs of `qb.transform()` for a comprehensive list of column types and their arguments. 

The first step in creating a schema is making sure that your data is _parsable_. If your Dataframe contains crazy fragmented or unstructured data, it will most likely need to be cleaned before you continue. Check that your columns contain only data that can be parsed by the specified column types. 

There are several ways to define a schema--and even ways to run qBandas without specifying a schema directly--but the method I recommend most people use is creating a `schema.json` file. The syntax for this file is simple. Inside of curly braces, each column name is a key for a string value which takes the format `"<FID> <column type> <args>"`. 

`<FID>` specifies which column on QuickBase corresponds to which column in your Dataframe. Make sure the column types on QuickBase match the ones you specify. You can gather your FIDs by looking at the QuickBase table's schema. 

If your dataset is large, you may find the method `qb.fastSchema()` helpful for this step.

Here is what I got.

<div style="margin:0;"><b>schema.json</b></div>

```json
{
    "name": "6 text",
    "age": "7 numeric"    
}
```

I can read this schema into Python.

```python
schema = qb.read_schema('schema.json')
```

### Sending the Data

Now that we have a dataset and a matching schema we can transform the data into a format that the QuickBase API can understand. 

```python
payloads = qb.full_transform(df, schema)
```