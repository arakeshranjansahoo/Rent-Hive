"""
RentHive Utility Functions
Version: 5.0
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import os


def generate_bill_pdf(bill):
    """
    Generate PDF receipt for bill
    
    Args:
        bill: Bill object
        
    Returns:
        str: PDF filename
    """
    # Create filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"bill_{bill.bill_number}_{timestamp}.pdf"
    filepath = os.path.join('bills', filename)
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2D5F3F'),  # Light green
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2D5F3F'),
        spaceAfter=12
    )
    
    # Title
    title = Paragraph("RENT INVOICE", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Bill header information
    header_data = [
        ['Bill Number:', bill.bill_number, 'Date:', datetime.now().strftime('%d-%m-%Y')],
        ['Bill Month:', bill.bill_month, 'Due Date:', bill.due_date.strftime('%d-%m-%Y')],
    ]
    
    header_table = Table(header_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5DC')),  # Sandy dune
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#F5F5DC')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 20))
    
    # Tenant details
    tenant = bill.tenant
    room = bill.room
    property_obj = room.property
    
    elements.append(Paragraph("Tenant Details", heading_style))
    
    tenant_data = [
        ['Name:', tenant.user.full_name],
        ['Room:', f"{room.room_number} ({property_obj.name})"],
        ['Phone:', tenant.user.phone],
        ['Email:', tenant.user.email],
    ]
    
    tenant_table = Table(tenant_data, colWidths=[2*inch, 4.5*inch])
    tenant_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5DC')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    
    elements.append(tenant_table)
    elements.append(Spacer(1, 20))
    
    # Bill details
    elements.append(Paragraph("Bill Details", heading_style))
    
    bill_data = [
        ['Description', 'Amount (₹)'],
        ['Monthly Rent', f"₹{bill.rent_amount:.2f}"],
        [f'Electricity ({bill.electricity_units} units)', f"₹{bill.electricity_amount:.2f}"],
        ['Water Charges', f"₹{bill.water_amount:.2f}"],
        ['Maintenance', f"₹{bill.maintenance_amount:.2f}"],
    ]
    
    if bill.other_charges > 0:
        desc = bill.other_charges_description or 'Other Charges'
        bill_data.append([desc, f"₹{bill.other_charges:.2f}"])
    
    bill_data.extend([
        ['', ''],
        ['Total Amount', f"₹{bill.total_amount:.2f}"],
        ['Amount Paid', f"₹{bill.amount_paid:.2f}"],
        ['Balance Due', f"₹{bill.balance:.2f}"]
    ])
    
    bill_table = Table(bill_data, colWidths=[4.5*inch, 2*inch])
    bill_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D5F3F')),  # Light green header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -4), 1, colors.grey),
        ('LINEABOVE', (0, -3), (-1, -3), 2, colors.black),
        ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#F0F0F0')),
        ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -3), (-1, -1), 11),
    ]))
    
    elements.append(bill_table)
    elements.append(Spacer(1, 20))
    
    # Payment status
    status_color = {
        'paid': colors.green,
        'partial': colors.orange,
        'pending': colors.red,
        'overdue': colors.darkred
    }.get(bill.status, colors.grey)
    
    status_style = ParagraphStyle(
        'StatusStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=status_color,
        alignment=TA_CENTER
    )
    
    status_text = f"<b>Payment Status: {bill.status.upper()}</b>"
    elements.append(Paragraph(status_text, status_style))
    
    if bill.payment_date:
        payment_info = f"Payment Date: {bill.payment_date.strftime('%d-%m-%Y')} | Method: {bill.payment_method}"
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(payment_info, styles['Normal']))
    
    elements.append(Spacer(1, 30))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    footer_text = f"Generated by RentHive on {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}<br/>Thank you for your business!"
    elements.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(elements)
    
    return filename


def format_currency(amount):
    """Format amount as currency"""
    return f"₹{amount:,.2f}"


def calculate_late_fee(bill, late_fee_rate=0.02):
    """
    Calculate late fee based on days overdue
    
    Args:
        bill: Bill object
        late_fee_rate: Daily late fee rate (default 2%)
        
    Returns:
        float: Late fee amount
    """
    if bill.status == 'paid' or not bill.due_date:
        return 0.0
    
    today = datetime.now().date()
    if today <= bill.due_date:
        return 0.0
    
    days_overdue = (today - bill.due_date).days
    late_fee = bill.balance * late_fee_rate * (days_overdue / 30)
    
    return round(late_fee, 2)


def validate_file_extension(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_unique_id(prefix=''):
    """Generate unique ID with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    return f"{prefix}{timestamp}"
