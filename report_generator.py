from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet


class ReportGenerator:

    @staticmethod
    def generate_pdf(filename, data):

        doc = SimpleDocTemplate(filename)
        styles = getSampleStyleSheet()

        elements = []

        elements.append(Paragraph("Gym Progress Report", styles["Heading1"]))

        table_data = [["Date", "Weight", "Volume"]]

        for row in data:
            table_data.append(list(row))

        table = Table(table_data)
        elements.append(table)

        doc.build(elements)