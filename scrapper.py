from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import html

id_file = "id.txt"

with open(id_file, "r") as file:
    lines = file.readlines()
    user_id = lines[1].strip()
    password = lines[3].strip()

login_url = "https://cours.iut-orsay.fr/login/index.php"  # Login page
notes_urls = ["https://cours.iut-orsay.fr/grade/report/user/index.php?id=3482", "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3463", "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3810", 
             "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3812", "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3795", "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3639",
             "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3416", "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3588", "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3599"]  # Notes pages

driver = webdriver.Chrome()

courses_notes = {}

try:
    driver.get(login_url)
    time.sleep(2)

    id_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    id_field.send_keys(user_id)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    time.sleep(2)

    for url in notes_urls:
        driver.get(url)
        time.sleep(3)

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")

        course_header = soup.find("h1", class_="h2 mb-0")
        if course_header:
            course_name = course_header.get_text(strip=True)
            if course_name not in courses_notes:
                courses_notes[course_name] = []

        rows = soup.select("tbody tr")

        for row in rows:
            evaluation_cell = row.find("th", class_="column-itemname")
            if evaluation_cell:
                evaluation_name = evaluation_cell.get_text(strip=True)

                grade_cell = row.find("td", class_="column-grade")
                grade = grade_cell.get_text(strip=True) if grade_cell else "-"

                range_cell = row.find("td", class_="column-range")
                range_value = range_cell.get_text(strip=True) if range_cell else "-"

                if "Analyse de l’évaluation" in grade:
                    grade = grade.replace("Analyse de l’évaluation", "").strip()

                evaluation_name_skips = ["Note finale sur 20"]
                if evaluation_name in evaluation_name_skips:
                    continue

                if "Tendance" in evaluation_name:
                    continue

                if grade == "-":
                    continue

                if evaluation_name == "Note calculéeTotal du cours" :
                    continue

                if evaluation_name == "Élément manuelInterrogation en TP" :
                    evaluation_name = "Interrogation en TP"

                if "DevoirActivité" in evaluation_name :
                    evaluation_name = evaluation_name.replace("DevoirActivité", "Activité")

                max_value = range_value.split("–")[1].strip()

                courses_notes[course_name].append({
                    "evaluation": evaluation_name,
                    "grade": grade,
                    "max": max_value,
                })



finally:
    time.sleep(2)
    driver.quit()

for course, notes in courses_notes.items():
    print(f"Course: {course}")
    for note in notes:
        print(f"    {note['evaluation']}: {note['grade']} / {note['max']}")


html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notes</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #0D1117;
        }}
        table {{
            width: 100%;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1 class="my-4" style="color: #FF00FF; font-weight: bold;">Notes {user_id}</h1>
        <div class="table-responsive">
            <table class="table table-dark table-striped table-bordered">
                <thead class="table-dark">
                    <tr>
                        <th>Évaluation</th>
                        <th>Note</th>
                    </tr>
                </thead>
                <tbody>
"""

for course_name, notes in courses_notes.items():
    html_content += f"""
        <tr>
            <td colspan="3" class="table-primary-dark" style="color: #FF00FF; font-weight: bold;">{course_name}</td>
        </tr>
    """
    for note in notes:
        html_content += f"""
            <tr>
                <td style="padding-left: 20px;">{note['evaluation']}</td>
                <td style="font-weight: bold;">{note['grade']} / {note['max']}</td>
            </tr>
        """

html_content += """
                </tbody>
            </table>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js" integrity="sha384-IQsoLXl5PILFhosVNubq5LC7Qb9DXgDA9i+tQ8Zj3iwWAwPtgFTxbJ8NT4GN1R8p" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.min.js" integrity="sha384-cVKIPhGWiC2Al4u+LWgxfKTRIcfu0JTxR+EQDz/bgldoEyl4H0zUF0QKbrJ0EcQF" crossorigin="anonymous"></script>
</body>
</html>
"""


output_file = "notes.html"
with open(output_file, "w", encoding="utf-8") as file:
    file.write(html_content)

print(f"HTML page generated: {output_file}")

