# qBandas

qBandas (QuickBase + Pandas) is a Python package designed to effeciently transfer tabular data between QuickBase applications and the popular Python data handling library Pandas. If you are new to Pandas, you can read more about it [here](https://pandas.pydata.org/).

The advantages of this approach over a QuickBase pipeline are:
* Access to databases through Python libraries like [pyodbc](https://github.com/mkleehammer/pyodbc) and [SASPy](https://sassoftware.github.io/saspy/).
* Greater control over features like error logging, data processing, automated reporting, and scheduling.
* Significantly less performance impact on your QuickBase application.
* Access tabular data from local sources. 
* Easily pull data from a QuickBase app into Python.

The disadvantages of this approach compared to a pipeline are:
* Requires some knowledge of Python and Pandas.

[Read the docs](https://jhopwood-jjk.github.io/qbandas/index.html)

## Setup

To use this library, simply get it from pypi. First, update your pip, then install qBandas 


```bash
python -m pip install -U pip qbandas
```

You can now use it through import.

```python
import qbandas
```