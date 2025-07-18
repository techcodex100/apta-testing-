import csv
import os
import requests
import time
import datetime
import psutil
from main import APTACertificateData

# ✅ Output folders (different names)
pdf_output_dir = "pdfs_from_csv_input"
os.makedirs(pdf_output_dir, exist_ok=True)

csv_output_dir = "csv_reports_from_csv_input"
os.makedirs(csv_output_dir, exist_ok=True)

# 🌐 Render API endpoint
RENDER_URL = "https://apta-product.onrender.com/generate-apta-certificate-pdf/"

# 📋 Parameters for software quality evaluation
test_parameters = [
    "Reliability", "Scalability", "Robustness/Resilience", "Latency", "Throughput",
    "Security", "Usability/User-Friendliness", "Maintainability", "Availability", "Cost",
    "Flexibility/Adaptability", "Portability", "Interoperability",
    "Resource Utilization", "Documentation Quality"
]

# 🧠 Simple evaluation generator (random)
from random import randint
def get_evaluation(param):
    score = randint(3, 5)
    remarks = {
        5: "Excellent performance under all tested conditions.",
        4: "Good performance with minor improvements suggested.",
        3: "Acceptable performance; needs better optimization."
    }
    return score, remarks[score]

# 📖 Read dummy input CSV (50 entries)
with open("dummy_input_data.csv", newline='', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for idx, row in enumerate(reader, start=1):
        start_time = time.time()

        # ✅ Clean row and safely convert all values to strings
        clean_row = {str(k).strip(): str(v).strip() for k, v in row.items()}
        dummy_data = APTACertificateData(**clean_row)

        # 🌐 Send to Render API
        response = requests.post(RENDER_URL, json=dummy_data.dict())

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        pdf_filename = os.path.join(pdf_output_dir, f"apta_certificate_{idx}_{timestamp}.pdf")

        if response.status_code == 200:
            with open(pdf_filename, "wb") as f:
                f.write(response.content)
        else:
            print(f"❌ Failed to generate PDF {idx}: {response.status_code}")
            continue

        # 📊 Save test evaluation CSV
        csv_filename = os.path.join(csv_output_dir, f"apta_report_{idx}.csv")
        with open(csv_filename, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow(["🔹 Dummy Input Field", "Value"])
            for field, value in dummy_data.dict().items():
                writer.writerow([field, value])

            writer.writerow([])

            writer.writerow(["✅ Test Parameter", "Rating (1–5)", "Remarks"])
            for param in test_parameters:
                score, remark = get_evaluation(param)
                writer.writerow([param, score, remark])

        # 🧠 Print system stats
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        elapsed = round(time.time() - start_time, 2)

        print(f"✅ [{idx}/50] PDF: {pdf_filename}")
        print(f"   CPU Usage: {cpu}% | Memory Usage: {mem}% | Time Taken: {elapsed}s")
        print("--------------------------------------------------")

print("🎉 All PDFs and CSVs successfully generated using input CSV and Render API.")