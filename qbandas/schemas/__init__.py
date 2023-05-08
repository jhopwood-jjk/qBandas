'''
Methods that deal with handling local copies of QuickBase tables' 
schemas.

Everytime you want to upload records to a table on QuickBase, you must
have a valid schema for the table. 
'''

from .schemas import (_read_schema, _write_schema, add_schema_args,
                      fetch_schema, list_schemas, set_schema_args)
