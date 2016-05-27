# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import codecs
import os
import pdb
import sys
import traceback
from datetime import date

import pdfkit

if sys.version_info > (3,):
    long = int


def export(bill, template_dir=None, pdf_dir=None):
    """Takes bill dict and inserts fields into the appropriate HTML bill template
       The template is converted to a PDF using pdfkit and stored in new_bills/
    """
    # if template_dir not provided,
    # look for the template directory of this script's location
    if not template_dir:
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template')
    # If the user-defined or default template directories don't exist, raise an error
    if not os.path.exists(template_dir):
        raise OSError('Could not find the template directory')

    # If no user-defined pdf output directory, put it in a folder where this script lives
    if not pdf_dir:
        basedir = os.path.dirname(os.path.abspath(__file__))
        pdf_dir = os.path.join(basedir, 'pdfs')
        # if the default pdf output directory doesn't exist, make it
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)

    # if the user-defined pdf_dir does not exist, raise an error
    if not os.path.exists(pdf_dir):
        raise IOError('Could not find a directory to output pdfs')

    # get the path to the template
    template_path = os.path.join(template_dir, 'templates', 'template.html')
    template = codecs.open(template_path, encoding='utf-8').read()

    # Replace relative imports of images and CSS with the full path to the files
    # Note: I'm including the '/' in the replacement so that
    # it doesn't replace other uses for '..' such as in regular text (i.e. an ellipsis)
    template = template.replace('../', os.path.join(path2url(template_dir), ''))

    # Insert billing data using find/replace
    # Sort by field length longest to shortest
    # This prevents values from fields that are substrings of other fields from going in the wrong place
    # e.g. the value of "rebate" would be inserted into the field "rebate_closing_balance"
    for key, value in sorted(bill.items(), key=lambda t: len(t[0]), reverse=True):
        template = template.replace("__"+key, format_value(value))

    # Now create the pdf
    try:
        # options = {'encoding': 'utf-8'}
        report_name = make_report_name(bill)
        output_file = os.path.join(pdf_dir, report_name)
        pdfkit.from_string(template, output_file)
    except:
        typ, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)


def format_value(value):
    """Define display value for various data types"""

    if isinstance(value, float):
        # floats are monetary values
        return "{:.2f}".format(value)
    elif isinstance(value, long) or isinstance(value, int):
        return str(value)
    elif isinstance(value, date):
        return value.strftime("%Y-%m-%d")

    return value


def make_report_name(bill):
    return "_".join([
        'Customer',
        str(bill['customer_id']),
        date.today().strftime("%Y%m%d"),
    ]) + '.pdf'


def path2url(path):
    if sys.version_info > (3,):
        import pathlib
        return pathlib.Path(path).as_uri()
    else:
        import urlparse, urllib
        return urlparse.urljoin(
            'file:', urllib.pathname2url(path))


if __name__ == "__main__":
    bill = dict(
        report_date=date(2016, 5, 5),
        customer_id=100,
        customer_name="John Doré",
        start_date=date(2016, 4, 1),
        end_date=date(2016, 4, 30),
        offpeak_usage=90.0,
        onpeak_usage=10.0,
        offpeak_cost=45.0,
        onpeak_cost=10.0,
        final_cost=55.0,
        curr_rate=60.0,
        rate_highlow="LOWER",
        rate_difference=5.00,
        rebate=5.00,
        rebate_closing_balance=10.00,
    )

    export(bill)
