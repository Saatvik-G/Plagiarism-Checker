import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import math
from collections import Counter
from docx import Document
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)

class PlagiarismChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("📑 Plagiarism Checker")
        self.root.geometry("700x600")
        self.root.configure(bg="#1e1e2f")
        self.root.minsize(700, 600)
        self.file1_content = ""
        self.file2_content = ""
        self.stop_words = set(stopwords.words('english'))
        self.setup_gui()

    def tokenize_text(self, text):
        text = text.lower()
        words = re.findall(r'\b[a-z][a-z0-9\'-]*\b', text)
        return [word for word in words if word not in self.stop_words]

    def calculate_word_frequencies(self, words):
        return Counter(words)

    def compute_cosine_similarity(self, freq1, freq2):
        if not freq1 or not freq2:
            return 0.0
        intersection = set(freq1.keys()) & set(freq2.keys())
        if not intersection:
            return 0.0
        numerator = sum(freq1[word] * freq2[word] for word in intersection)
        sum1 = sum(v ** 2 for v in freq1.values())
        sum2 = sum(v ** 2 for v in freq2.values())
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        return round((numerator / denominator) * 100, 2) if denominator else 0.0

    def read_file_content(self, file_path):
        if file_path.endswith('.txt'):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif file_path.endswith('.docx'):
            doc = Document(file_path)
            return "\n".join(para.text for para in doc.paragraphs)
        return ""

    def load_first_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("Word files", "*.docx")])
        if file_path:
            try:
                self.file1_content = self.read_file_content(file_path)
                self.file1_label.config(text=f"✅ {file_path.split('/')[-1]}", fg="#a3e635")
                self.update_status("First file loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"⚠ Failed to read file: {str(e)}")
                self.update_status("Failed to load first file")

    def load_second_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("Word files", "*.docx")])
        if file_path:
            try:
                self.file2_content = self.read_file_content(file_path)
                self.file2_label.config(text=f"✅ {file_path.split('/')[-1]}", fg="#a3e635")
                self.update_status("Second file loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"⚠ Failed to read file: {str(e)}")
                self.update_status("Failed to load second file")

    def compare_files(self):
        if not self.file1_content or not self.file2_content:
            messagebox.showerror("Error", "⚠ Please upload both files!")
            self.update_status("Missing files")
            return
        try:
            self.update_status("Comparing files...")
            words1 = self.tokenize_text(self.file1_content)
            words2 = self.tokenize_text(self.file2_content)
            if not words1 or not words2:
                messagebox.showerror("Error", "⚠ One or both files are empty!")
                self.update_status("Empty file detected")
                return
            freq1 = self.calculate_word_frequencies(words1)
            freq2 = self.calculate_word_frequencies(words2)
            similarity = self.compute_cosine_similarity(freq1, freq2)
            color = "#ff3333" if similarity > 70 else "#ffcc00" if similarity > 30 else "#a3e635"
            self.result_label.config(text=f"Similarity: {similarity}%", fg=color)
            self.display_detailed_report(freq1, freq2, similarity)
            self.update_status("Comparison complete")
        except Exception as e:
            messagebox.showerror("Error", f"⚠ An error occurred: {str(e)}")
            self.update_status("Comparison failed")

    def display_detailed_report(self, freq1, freq2, similarity):
        common_words = set(freq1.keys()) & set(freq2.keys())
        report = f"Similarity Score: {similarity}%\n\nCommon Words (with frequencies):\n"
        for word in sorted(common_words):
            report += f"{word}: File 1 ({freq1[word]}), File 2 ({freq2[word]})\n"
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report)

    def save_report(self):
        if not self.result_label.cget("text"):
            messagebox.showerror("Error", "⚠ No report to save!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.report_text.get(1.0, tk.END))
                self.update_status("Report saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"⚠ Failed to save report: {str(e)}")
                self.update_status("Failed to save report")

    def clear_files(self):
        self.file1_content = ""
        self.file2_content = ""
        self.file1_label.config(text="No File Uploaded", fg="#aaaaaa")
        self.file2_label.config(text="No File Uploaded", fg="#aaaaaa")
        self.result_label.config(text="Similarity: --%", fg="#ffffff")
        self.report_text.delete(1.0, tk.END)
        self.update_status("Files cleared")

    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")

    def setup_gui(self):
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12, "bold"))
        style.configure("TLabel", background="#2c2c3c", foreground="#ffffff", font=("Arial", 11))

        title_label = tk.Label(self.root, text="📑 Plagiarism Checker", font=("Arial", 24, "bold"), bg="#1e1e2f", fg="#ffffff")
        title_label.pack(pady=15)

        upload_frame = tk.Frame(self.root, bg="#2c2c3c", bd=5, relief="flat")
        upload_frame.pack(pady=15, padx=20, fill="x")

        file1_button = ttk.Button(upload_frame, text="📂 Upload First File", command=self.load_first_file)
        file1_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.create_tooltip(file1_button, "Select the first text or Word file to compare")

        self.file1_label = tk.Label(upload_frame, text="No File Uploaded", fg="#aaaaaa", bg="#2c2c3c", font=("Arial", 11))
        self.file1_label.grid(row=0, column=1, padx=10, sticky="w")

        file2_button = ttk.Button(upload_frame, text="📂 Upload Second File", command=self.load_second_file)
        file2_button.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.create_tooltip(file2_button, "Select the second text or Word file to compare")

        self.file2_label = tk.Label(upload_frame, text="No File Uploaded", fg="#aaaaaa", bg="#2c2c3c", font=("Arial", 11))
        self.file2_label.grid(row=1, column=1, padx=10, sticky="w")

        self.result_label = tk.Label(self.root, text="Similarity: --%", font=("Arial", 16, "bold"), bg="#1e1e2f", fg="#ffffff")
        self.result_label.pack(pady=10)

        report_frame = tk.Frame(self.root, bg="#1e1e2f")
        report_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.report_text = tk.Text(report_frame, height=8, font=("Arial", 11), bg="#2c2c3c", fg="#ffffff", relief="flat")
        self.report_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(report_frame, orient="vertical", command=self.report_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.report_text.config(yscrollcommand=scrollbar.set)

        button_frame = tk.Frame(self.root, bg="#1e1e2f")
        button_frame.pack(pady=10)

        compare_button = ttk.Button(button_frame, text="🔎 Compare Files", command=self.compare_files)
        compare_button.pack(side="left", padx=5)
        self.create_tooltip(compare_button, "Compare the uploaded files for similarity")

        save_button = ttk.Button(button_frame, text="💾 Save Report", command=self.save_report)
        save_button.pack(side="left", padx=5)
        self.create_tooltip(save_button, "Save the comparison report to a file")

        clear_button = ttk.Button(button_frame, text="🔄 Clear Files", command=self.clear_files)
        clear_button.pack(side="left", padx=5)
        self.create_tooltip(clear_button, "Clear uploaded files and reset the tool")

        self.status_label = tk.Label(self.root, text="Status: Ready", font=("Arial", 10), bg="#1e1e2f", fg="#aaaaaa")
        self.status_label.pack(pady=10)

        footer_label = tk.Label(self.root, text="Developed with Python & Tkinter", font=("Arial", 9), bg="#1e1e2f", fg="#aaaaaa")
        footer_label.pack(side="bottom", pady=10)

    def create_tooltip(self, widget, text):
        tooltip = tk.Toplevel(self.root)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry("+1000+1000")
        label = tk.Label(tooltip, text=text, bg="#333333", fg="#ffffff", font=("Arial", 9), relief="solid", borderwidth=1)
        label.pack()

        def show(event):
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 30
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def hide(event):
            tooltip.withdraw()

        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)
        tooltip.withdraw()

if __name__ == "__main__":
    root = tk.Tk()
    app = PlagiarismChecker(root)
    root.mainloop()