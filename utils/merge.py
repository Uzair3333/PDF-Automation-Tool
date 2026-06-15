from pypdf import PdfWriter

# Initialize the writer object (acts as a blank canvas)
writer = PdfWriter()

# You must add at least one page to create a valid PDF
writer.add_blank_page(width=612, height=792)  # Standard Letter size in points

# Save and write the data to a physical file
with open("new_document.pdf", "wb") as f:
    writer.write(f)
