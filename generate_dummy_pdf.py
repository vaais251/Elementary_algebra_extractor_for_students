from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_pdf(filename="sample_math.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Page 1
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 50, "Header: Day 1 - Math Foundation (Page 1)")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, "Here is some dummy text to illustrate text extraction.")
    c.drawString(50, height - 120, "This section contains some basic math formulas.")
    
    c.setFont("Helvetica-Oblique", 14)
    c.drawString(50, height - 160, "Quadratic Equation:")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 180, "ax^2 + bx + c = 0")
    c.drawString(50, height - 200, "x = (-b ± √(b^2 - 4ac)) / 2a")
    
    c.drawString(50, 50, "1") # Page number footer
    
    c.showPage()
    
    # Page 2
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 50, "Header: Day 1 - Math Foundation (Page 2)")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, "Continuing with more mathematical concepts.")
    c.drawString(50, height - 120, "Pythagorean theorem:")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 140, "a^2 + b^2 = c^2")
    
    c.drawString(50, height - 180, "Euler's Identity:")
    c.drawString(50, height - 200, "e^(iπ) + 1 = 0")
    
    c.drawString(50, 50, "2") # Page number footer
    
    c.save()

if __name__ == "__main__":
    create_pdf()
    print("Dummy PDF 'sample_math.pdf' generated successfully.")
