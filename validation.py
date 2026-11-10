def check_invoice_number(record):
    return record['invoice_number'] == record['expected_invoice_number']

def check_amount(record):
    return abs(record['amount'] - record['expected_amount']) < 0.01

def check_date(record):
    return record['date'] == record['expected_date']

def validate_record(record):
    errors = []
    if not check_invoice_number(record):
        errors.append("Invoice number mismatch")
    if not check_amount(record):
        errors.append("Amount mismatch")
    if not check_date(record):
        errors.append("Date mismatch")
    return errors