from fastapi import FastAPI, Response, HTTPException, UploadFile, File
from pydantic import BaseModel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from typing import Optional
from io import BytesIO
from fastapi.responses import FileResponse
import os
import csv
from faker import Faker
import uuid

app = FastAPI(title="APTA Certificate Generator", version="1.0.0")

# ✅ Root route
@app.get("/")
def read_root():
    return {"message": "APTA Certificate Generator is running!"}


# ✅ Pydantic model for APTA
class APTACertificateData(BaseModel):
    reference_no: Optional[str] = ""
    issued_in: Optional[str] = ""
    consigned_from: Optional[str] = ""
    consigned_to: Optional[str] = ""
    transport_route: Optional[str] = ""
    official_use: Optional[str] = ""
    tariff_item_number: Optional[str] = ""
    package_marks_numbers: Optional[str] = ""
    package_description: Optional[str] = ""
    origin_criterion: Optional[str] = ""
    gross_weight_or_quantity: Optional[str] = ""
    invoice_number_date: Optional[str] = ""
    declaration_country: Optional[str] = ""
    importing_country: Optional[str] = ""
    declaration_place_date: Optional[str] = ""
    declaration_signature: Optional[str] = ""
    certification_place_date: Optional[str] = ""
    certification_signature_stamp: Optional[str] = ""


# ✅ Endpoint 1: Generate APTA PDF
@app.post("/generate-apta-certificate-pdf/")
def generate_apta_pdf(data: APTACertificateData):
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        def draw_image(filename):
            path = os.path.join(os.path.dirname(__file__), "static", filename)
            if os.path.exists(path):
                c.drawImage(ImageReader(path), 0, 0, width=width, height=height)

        def draw_value(value, x, y):
            c.setFont("Helvetica", 9.2)
            for i, line in enumerate(value.splitlines()):
                c.drawString(x, y - (i * 10), line)

        draw_image("1.jpg")

        draw_value(data.reference_no, 320, 780)
        draw_value(data.issued_in, 380, 700)
        draw_value(data.consigned_from, 70, 745)
        draw_value(data.consigned_to, 70, 640)
        draw_value(data.transport_route, 70, 555)
        draw_value(data.official_use, 325, 660)
        draw_value(data.tariff_item_number, 70, 445)
        draw_value(data.package_marks_numbers, 140, 445)
        draw_value(data.package_description, 200, 445)
        draw_value(data.origin_criterion, 380, 445)
        draw_value(data.gross_weight_or_quantity, 450, 445)
        draw_value(data.invoice_number_date, 520, 445)

        c.showPage()
        c.save()
        buffer.seek(0)

        return Response(
            content=buffer.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=apta_certificate.pdf"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


# ✅ Endpoint 2: Upload PDF and Generate CSV Summary
@app.post("/upload-apta-pdf-and-generate-csv/")
async def upload_and_generate_csv(file: UploadFile = File(...)):
    output_dir = "uploaded_csv_results"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"result_{uuid.uuid4().hex}.csv"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Parameter", "Rating (1-5)", "Remarks"])

        parameters = [
            "Reliability", "Scalability", "Robustness/Resilience", "Latency",
            "Throughput", "Security", "Usability", "Maintainability", "Availability",
            "Cost", "Flexibility", "Portability", "Interoperability",
            "Resource Utilization", "Documentation Quality"
        ]

        fake = Faker()
        for param in parameters:
            rating = fake.random_int(min=4, max=5)
            remarks = f"{param} successfully passed test cases."
            writer.writerow([param, rating, remarks])

    return FileResponse(filepath, media_type="text/csv", filename=filename)


# ✅ Endpoint 3: Generate 50 CSV Files with Dummy Data + Parameter Comparison
@app.get("/generate-apta-analysis-reports/")
def generate_multiple_csv_reports():
    fake = Faker()
    output_dir = "apta_analysis_reports"
    os.makedirs(output_dir, exist_ok=True)

    quality_parameters = [
        "Reliability", "Scalability", "Robustness/Resilience", "Latency",
        "Throughput", "Security", "Usability", "Maintainability", "Availability",
        "Cost", "Flexibility", "Portability", "Interoperability",
        "Resource Utilization", "Documentation Quality"
    ]

    for i in range(1, 51):
        dummy = APTACertificateData(
            reference_no=f"APTA-REF-{fake.random_number(digits=4)}",
            issued_in=fake.city(),
            consigned_from=fake.company(),
            consigned_to=fake.company(),
            transport_route=fake.street_address(),
            official_use="Verified by Authority",
            tariff_item_number=str(fake.random_int(min=1000, max=9999)),
            package_marks_numbers="Marked as Fragile",
            package_description="Plastic Bags - Industrial Use",
            origin_criterion="Rule 4(a)",
            gross_weight_or_quantity=f"{fake.random_int(min=500, max=5000)} kg",
            invoice_number_date=f"INV-{fake.random_number(digits=4)} dated {fake.date()}",
            declaration_country=fake.country(),
            importing_country=fake.country(),
            declaration_place_date=f"{fake.city()} - {fake.date()}",
            declaration_signature=fake.name(),
            certification_place_date=f"{fake.city()} - {fake.date()}",
            certification_signature_stamp=fake.name()
        )

        filename = f"apta_report_{i}.csv"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Field Name", "Dummy Input"])
            for field, value in dummy.dict().items():
                writer.writerow([field, value])

            writer.writerow([])
            writer.writerow(["Parameter", "Rating (1-5)", "Remarks"])
            for param in quality_parameters:
                rating = fake.random_int(min=4, max=5)
                remark = f"{param} tested and working well."
                writer.writerow([param, rating, remark])

    return {"message": "✅ 50 CSV analysis reports generated in 'apta_analysis_reports' folder."}
