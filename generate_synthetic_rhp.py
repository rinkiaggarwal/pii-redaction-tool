from docx import Document

doc = Document()
doc.add_heading('Red Herring Prospectus - KSH International Limited', 0)

doc.add_heading('1. General Information', level=1)
doc.add_paragraph(
    "KSH International Limited (the \"Company\") is a public limited company. "
    "Our registered office is located at 404, Raheja Centre, Nariman Point, Mumbai 400021. "
    "For queries, contact our Compliance Officer, Sarthak Malvadkar at sarthak.m@ksh.com or +91 98765 43210."
)

doc.add_heading('2. Board of Directors', level=1)
doc.add_paragraph(
    "1. Mr. Rajesh Sharma, Managing Director. DOB: 15/08/1975. PAN: ABCDE1234F. Aadhaar: 1234 5678 9012. "
    "Address: 12, Sea View Apartments, Bandra West, Mumbai. "
    "2. Ms. Priya Desai, Independent Director. Email: priya.desai@gmail.com. Phone: +91-9988776655."
)

doc.add_heading('3. Lead Managers and Bankers', level=1)
doc.add_paragraph(
    "The Lead Manager for the issue is ICICI Securities. The contact person at ICICI Securities is Amit Patel "
    "(amit.patel@icicisecurities.com). The Escrow Collection Bank is HDFC Bank. "
    "The company's CIN is L12345MH2000PLC123456. Payments can be made via credit card ending in 4111111111111111. "
    "For online applications, the IP address 192.168.1.1 is recorded for audit purposes."
)

doc.save('sample_rhp.docx')
