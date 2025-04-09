import pandas as pd
import tempfile
import uuid
import os
from typing import List, Dict
from .headers import REPORT_HEADERS


class ReportGenerator:
    def __init__(self, report_id: int, body: List[Dict]):
        self.report_id = report_id
        self.body = body
        self.header = self.get_header(report_id)

    def get_header(self, report_id):
        header = REPORT_HEADERS.get(report_id)
        if not header:
            raise ValueError(f"Tipo de relatório inválido: {report_id}")
        return header

    def generate_xlsx(self) -> str:
        df = pd.DataFrame(self.body)
        df = df.reindex(columns=self.header)

        filename = f"report_{uuid.uuid4().hex}.xlsx"
        temp_path = os.path.join(tempfile.gettempdir(), filename)

        df.to_excel(temp_path, index=False)

        return temp_path

    def generate_pdf(self) -> str:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet

        filename = f"report_{uuid.uuid4().hex}.pdf"
        temp_path = os.path.join(tempfile.gettempdir(), filename)

        data = [self.header]
        for item in self.body:
            row = [item.get(col, '') for col in self.header]
            data.append(row)

        doc = SimpleDocTemplate(temp_path, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        title = Paragraph("Relatório", styles["Title"])
        elements.append(title)
        elements.append(Spacer(1, 12))

        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        doc.build(elements)

        return temp_path
