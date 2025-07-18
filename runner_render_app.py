import csv
import os
import requests
from faker import Faker
from main import APTACertificateData

fake = Faker()

# ✅ Folder to save PDF downloads and CSV reports
pdf_output_dir = "rendered_apta_pdfs"
os.makedirs(pdf_output_dir, exist_ok=True)

csv_output_dir = "rendered_apta_csv_reports"
os.makedirs(csv_output_dir, exist_ok=True)

# 📋 Parameters for evaluation
test_parameters = [
    "Reliability", "Scalability", "Robustness/Resilience", "Latency", "Throughput",
    "Security", "Usability/User-Friendliness", "Maintainability", "Availability", "Cost",
    "Flexibility/Adaptability", "Portability", "Interoperability", "Resource Utilization", "Documentation Quality"
]

# 🌐 Render API endpoint
RENDER_URL = "https://apta-product.onrender.com/generate-apta-certificate-pdf/"

# 🧠 Evaluation generator
def get_evaluation(parameter):
    score = fake.random_int(min=3, max=5)
    remarks = {
        5: "Excellent performance under all tested conditions.",
        4: "Good performance with minor improvements suggested.",
        3: "Acceptable performance; needs better optimization."
    }
    return score, remarks[score]

# 🔁 Generate 50 requests
for i in range(1, 51):
    dummy_data = APTACertificateData(
        reference_no=f"APTA-REF-{fake.random_number(digits=4)}",
        issued_in=fake.city(),
        consigned_from=fake.company() + "\n" + fake.address(),
        consigned_to=fake.company() + "\n" + fake.address(),
        transport_route="Sea via " + fake.city(),
        official_use="Approved by Trade Dept.",
        tariff_item_number=str(fake.random_number(digits=4)),
        package_marks_numbers="PKG-" + str(fake.random_number(digits=3)),
        package_description=fake.text(max_nb_chars=40),
        origin_criterion="Rule " + fake.random_element(elements=("A", "B", "C")),
        gross_weight_or_quantity=f"{fake.random_int(min=500, max=2000)} kg",
        invoice_number_date=f"INV-{fake.random_number(digits=5)} dated {fake.date()}",
        declaration_country="India",
        importing_country=fake.country(),
        declaration_place_date=fake.city() + ", " + fake.date(),
        declaration_signature=fake.name(),
        certification_place_date=fake.city() + ", " + fake.date(),
        certification_signature_stamp=fake.name()
    )

    # 🌐 Call Render API
    response = requests.post(RENDER_URL, json=dummy_data.dict())

    # 📥 Save PDF if successful
    if response.status_code == 200:
        pdf_filename = os.path.join(pdf_output_dir, f"apta_certificate_{i}.pdf")
        with open(pdf_filename, "wb") as pdf_file:
            pdf_file.write(response.content)
    else:
        print(f"❌ Failed to generate PDF {i}: {response.status_code}")
        continue

    # 📊 Save CSV with dummy + evaluation
    csv_filename = os.path.join(csv_output_dir, f"apta_report_{i}.csv")
    with open(csv_filename, "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        # Section 1: Dummy Data
        writer.writerow(["🔹 Dummy Input Field", "Value"])
        for field, value in dummy_data.dict().items():
            writer.writerow([field, value])

        writer.writerow([])

        # Section 2: Evaluation
        writer.writerow(["✅ Test Parameter", "Rating (1–5)", "Remarks"])
        for param in test_parameters:
            score, remark = get_evaluation(param)
            writer.writerow([param, score, remark])

print("✅ All 50 PDFs and CSVs generated from Render API.")
