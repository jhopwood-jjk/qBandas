import datetime as dt
import unittest

from qbandas._pack import (_pack_date, _pack_datetime, _pack_default,
                           _pack_duration, _pack_phonenum)


class Test_Pack(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_date_dt(self):
        date1 = dt.datetime(2022, 4, 5)
        retval = _pack_date(date1)
        self.assertEqual(retval, {'value': '2022-04-05'})
    
    def test_date_str(self):
        date1 = 'January 4, 1998'
        retval = _pack_date(date1, format = '%B %d, %Y')
        self.assertEqual(retval, {'value': '1998-01-04'})
    
    def test_date_none(self):
        date1 = None
        retval = _pack_date(date1, format = '%B %d, %Y')
        self.assertEqual(retval, None)
    
    def test_datetime_dt(self):
        date1 = dt.datetime(2022, 4, 5, 7, 30, 25, 256)
        retval = _pack_datetime(date1)
        self.assertEqual(retval, {'value': '2022-04-05T07:30:25Z'})
        
    def test_datetime_str(self):
        date1 = 'March 7 89 at 7:00 AM'
        retval = _pack_datetime(date1, format = '%B %d %y at %I:%M %p')
        self.assertEqual(retval, {'value': '1989-03-07T07:00:00Z'})
        
    def test_datetime_none(self):
        date1 = None
        retval = _pack_datetime(date1, format = 'unused')
        self.assertEqual(retval, None)
        
    def test_default(self):
        value = 'This is a value'
        retval = _pack_default(value)
        self.assertEqual(retval, {'value': 'This is a value'})
        
    def test_default_none(self):
        value = None
        retval = _pack_default(value)
        self.assertEqual(retval, None)
        
    def test_duration_milli(self):
        value = 3000
        retval = _pack_duration(value, unit = 'milliseconds') 
        self.assertEqual(retval, {'value': 3000})
        
    def test_duration_second(self):
        value = 3
        retval = _pack_duration(value) 
        self.assertEqual(retval, {'value': 3000})
        
    def test_duration_none(self):
        value = None
        retval = _pack_duration(value)
        self.assertEqual(retval, None)
        
    def test_phone_str(self):
        value1 = '(555) 333.6712X900'
        retval1 = _pack_phonenum(value1)
        self.assertEqual(retval1, {'value': '(555) 333-6712 x900'})
        
        value2 = '7770001234'
        retval2 = _pack_phonenum(value2)
        self.assertEqual(retval2, {'value': '(777) 000-1234'})
        
    def test_phonenum_int(self):
        value = 8001234567
        retval = _pack_phonenum(value)
        self.assertEqual(retval, {'value': '(800) 123-4567'})
        
    def test_phonenum_float(self):
        value = 8001234567.00001
        retval = _pack_phonenum(value)
        self.assertEqual(retval, {'value': '(800) 123-4567'})
        
    def test_phonenum_none(self):
        value = None
        retval = _pack_phonenum(value)
        self.assertEqual(retval, None)

    def tearDown(self) -> None:
        pass