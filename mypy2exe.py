from distutils.core import setup
import py2exe
#setup(console=["pyautotrade.pyw"])

#python mysetup.py py2exe
"""
setup(
    windows=[{'script': 'dataOperation.py'}],
    options={
        'py2exe': 
        {
            #'includes': ['lxml.etree', 'lxml._elementpath', 'gzip'],
            'includes': ['gzip'],
        }
    }
)
"""
#,fileOperation.py,sendMail.py

setup(console=['dataOperation.py'])