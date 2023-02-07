# qBandas

qBandas (QuickBase + Pandas) is a Python package designed to effeciently transfer tabular data between QuickBase applications and the popular Python data handling library Pandas. If you are new to Pandas, you can read more about it [here](https://pandas.pydata.org/).

The advantages of this approach over a QuickBase pipeline are:
* Access to databases through Python libraries like [pyodbc](https://github.com/mkleehammer/pyodbc) and [SASPy](https://sassoftware.github.io/saspy/).
* Greater control over features like error logging, data processing, automated reporting, and scheduling.
* Significantly less performance impact on your QuickBase application.
* Access tabular data from local sources. 

The disadvantages of this approach compared to a pipeline are:
* Typically longer time to deploy.
* Requires knowledge of Python and Pandas.

## Setup

To use this library, simply get it from pypi. First, update your pip.

```bash
python3 -m pip install --upgrade pip
```
Then install qBandas. 

```bash
python3 -m pip install qbandas
```

You can now use it through import.

```python
import qbandas as qb
```

Alternatively, you can clone this repository to your project. From your terminal run the following command. Note, you will need git installed to do this. You can find the lastest version [here](https://git-scm.com/).

```bash
git clone https://github.com/jhopwood-jjk/qBandas.git
```

If you don't like the other aproahes, you can download this repo as a zip and place it in your project folder. This is probably the worst method, but it works. 

For the last two methods, to use qBandas in your project, use the following import. Note the casing. 

```python
import qBandas.qbandas as qb
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

### 2) Gathering QuickBase Information

Under the hood, qBandas calls the QuickBase API. To make the API happy, we need to give it a few bits of information. We do this step early-on because if you cannot gather these items,then you cannot use this method. This might save you the headache doing everything only to find out that you don't have permission to upload. 

You will need your:

* QuickBase realm hostname 
    - Something like `"example.quickbase.com"`
* Destination table DBID
    - This is the hash that comes after `/db/` in any QuickBase url. Each table has a unique identifier, and they can be found by visiting the table on the web.
* QuickBase user token
    - Learn how to get one [here](https://developer.quickbase.com/auth).

You can read more about how to gather each of these items [here](https://developer.quickbase.com). When you have these items, we will save them into an info dictonary.

>   __Additional Consideration__ \
    You might want to store the user token somewhat securely. There are many ways to do this, and you are free to choose the one you like the best. One simple way to "secure" it is with an evironment varible. If you are interested, you can find out how to do it [from this stackoverflow post](https://stackoverflow.com/questions/4906977/how-can-i-access-environment-variables-in-python).

Here is what I got for this example.

```python
import os # user token is in an environment variable
info = {
    "QB-Realm-Hostname": "example.quickbase.com",
    "DBID": "abcdef123",
    "Authorization": f"QB-USER-TOKEN {os.environ['QB_USER_TOKEN']}"
}
```

### 3) Creating a Schema

The schema defines how qBandas will comunicate the data to QuickBase. For example, if you have a column of integers you could specify that column as `numeric`, `text`, or `duration`. Each of those __column types__ leads to a slightly different handling of the data. Be sure to choose the one you want for your data. The schema also defines the column mapping from your DataFrame to QuickBase. It does this by specifying the QuickBase field ID for each column. To create your mapping, you can find your field IDs in your table's [field list](https://helpv2.quickbase.com/hc/en-us/articles/4570416261524-About-the-field-list-). 

To find a complete list of supported column types and their behaviors, run the following command. Note, you will have to do the pip install method for this to work. 

```bash
python3 -m qbandas --col-types
```

The first step in creating a schema is making sure that your data is _parsable_. If your Dataframe contains crazy fragmented or unstructured data, it will most likely need to be cleaned before you continue. 

You will be creating your schema in a `.json` file; the default name for this file is `schema.json`. You have two _fast_ options for creating a schema. 

1. Have a sample of your data in a `.csv`, `.tsv`, or other delimited format. Run the command below. 
    ```bash
    python3 -m qbandas --create-schema -d path/to/data/file 
    ```
    This will create a template `schema.json` file in your current directory. Then, all you need to do is adjust the field IDs and s few column types. 
2. Have your data in a DataFrame and pass it into `qb.write_schema()` along with a writable file object. The file will get the template schema for your dataframe. 

If for some reason you cannot do the above methods and your dataset is large, good luck. 

Here is what I got. Notice the aditional argument for the phone column. 

<div style="margin:0;"><b>schema.json</b></div>

```json
{
    "name": "6 text",
    "age": "7 numeric",
    "phone": "8 phone-number '(###) ###-####x####'
}
```

Finally, I can read this schema into Python.

```python
schema = qb.read_schema('schema.json')
```

### 4) Sending the Data

Now that we have a dataset and a matching schema, we can transform the data into a format that the QuickBase API can understand, and send it. This last step is the most likely to throw errors. The formatting of the data in this call is spesific as we've seen above, so be sure to read any error messages carefully; they will tell you what is wrong.

To send the DataFrame, call `qb.upload()`.

```python 
qb.upload(df, schema, info)
```