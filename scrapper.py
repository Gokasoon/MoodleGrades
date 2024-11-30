from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import html
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext

class URLInputApp:
    def __init__(self, master):
        self.master = master
        master.title("Moodle Notes Scraper")
        master.geometry("600x600")
        master.configure(bg='#0D1117')

        # Predefined configurations
        self.configurations = {
            'TP5A-APP-A': {
                'login_url': 'https://cours.iut-orsay.fr/login/index.php',
                'notes_urls': [
                    "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3482", 
                    "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3463", 
                    "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3810", 
                    "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3812", 
                    "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3795", 
                    "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3639",
                    "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3416", 
                    "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3588", 
                    "https://cours.iut-orsay.fr/grade/report/user/index.php?id=3599"
                ],
                'id_file': 'id.txt'
            },
            'Custom': {
                'login_url': '',
                'notes_urls': [],
                'id_file': 'id.txt'
            }
        }

        # Configuration Dropdown
        tk.Label(master, text="Configuration:", fg='white', bg='#0D1117').pack(pady=(10,0))
        self.config_var = tk.StringVar()
        self.config_dropdown = ttk.Combobox(master, textvariable=self.config_var, 
                                            values=list(self.configurations.keys()), 
                                            state="readonly", width=47)
        self.config_dropdown.set('TP5A-APP-A')  # Default selection
        self.config_dropdown.pack(pady=5)
        self.config_dropdown.bind('<<ComboboxSelected>>', self.on_config_select)

        # Login URL Input
        tk.Label(master, text="Login URL:", fg='white', bg='#0D1117').pack(pady=(10,0))
        self.login_url_entry = tk.Entry(master, width=50)
        self.login_url_entry.pack(pady=5)

        # Notes URLs Input
        tk.Label(master, text="Notes URLs (one per line):", fg='white', bg='#0D1117').pack(pady=(10,0))
        self.notes_urls_text = scrolledtext.ScrolledText(master, height=10, width=50)
        self.notes_urls_text.pack(pady=5)

        # ID File Input
        tk.Label(master, text="ID File Path:", fg='white', bg='#0D1117').pack(pady=(10,0))
        self.id_file_entry = tk.Entry(master, width=50)
        self.id_file_entry.pack(pady=5)

        # Scrape Button
        self.scrape_button = tk.Button(master, text="Scrape Notes", command=self.scrape_notes, 
                                       bg='#FF00FF', fg='white')
        self.scrape_button.pack(pady=20)

        # Initial population
        self.on_config_select()

    def on_config_select(self, event=None):
        # Get selected configuration
        selected_config = self.config_var.get()
        config = self.configurations[selected_config]

        # Populate fields
        self.login_url_entry.delete(0, tk.END)
        self.login_url_entry.insert(0, config['login_url'])

        self.notes_urls_text.delete('1.0', tk.END)
        if selected_config == 'TP5A-APP-A':
            self.notes_urls_text.insert(tk.END, "\n".join(config['notes_urls']))
        
        self.id_file_entry.delete(0, tk.END)
        self.id_file_entry.insert(0, config['id_file'])

    def scrape_notes(self):
        # Retrieve inputs
        login_url = self.login_url_entry.get()
        notes_urls = self.notes_urls_text.get("1.0", tk.END).strip().split("\n")
        id_file = self.id_file_entry.get()

        # Validate inputs
        if not login_url or not notes_urls or not id_file:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            # Read credentials
            with open(id_file, "r") as file:
                lines = file.readlines()
                user_id = lines[1].strip()
                password = lines[3].strip()

            # Run scraping
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

                            evaluation_name_skips = ["Note finale sur 20", "Note calculéeTotal du cours"]
                            if evaluation_name in evaluation_name_skips:
                                continue

                            if "Tendance" in evaluation_name:
                                continue

                            if grade == "-":
                                continue

                            if "Analyse de l'évaluation" in grade:
                                grade = grade.replace("Analyse de l'évaluation", "").strip()

                            if "Élément manuel" in evaluation_name:
                                evaluation_name = evaluation_name.replace("Élément manuel", "")

                            if "DevoirActivité" in evaluation_name:
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

            # Generate HTML
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Notes</title>
                <script src="https://cdn.tailwindcss.com"></script>
                <script>
                    tailwind.config = {{
                        theme: {{
                            extend: {{
                                colors: {{
                                    'dark-bg': '#0D1117',
                                    'accent-pink': '#FF00FF'
                                }}
                            }}
                        }}
                    }}
                </script>
            </head>
            <body class="bg-dark-bg text-white font-sans p-6">
                <div class="container mx-auto max-w-4xl">
                    <h1 class="text-3xl font-bold mb-6 text-accent-pink">Notes {user_id}</h1>
                    
                    <div class="overflow-x-auto">
                        <table class="w-full border-collapse">
                            <thead>
                                <tr class="bg-gray-800">
                                    <th class="p-3 text-left">Évaluation</th>
                                    <th class="p-3 text-left">Note</th>
                                </tr>
                            </thead>
                            <tbody>
            """

            for course_name, notes in courses_notes.items():
                html_content += f"""
                                <tr class="bg-gray-900">
                                    <td colspan="2" class="p-3 font-bold text-accent-pink">{course_name}</td>
                                </tr>
                """
                for note in notes:
                    html_content += f"""
                                <tr class="border-b border-gray-700 hover:bg-gray-800 transition-colors">
                                    <td class="p-3 pl-6">{note['evaluation']}</td>
                                    <td class="p-3 font-bold">{note['grade']} / {note['max']}</td>
                                </tr>
                    """

            html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
            </body>
            </html>
            """

            output_file = "notes.html"
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(html_content)

            messagebox.showinfo("Success", f"Notes scraped and saved to {output_file}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

def main():
    root = tk.Tk()
    app = URLInputApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()