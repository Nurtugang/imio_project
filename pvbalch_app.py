import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
from pvbalch_computing_module import (Compound, 
                                      calculate_total_elements,
                                      calculate_element_percentages, 
                                      calculate_materials_in_slug, 
                                      calculate_materials_in_stein)

class CompoundInputFrame(tk.Frame):
    """Frame для ввода данных о компоненте."""
    def __init__(self, parent, data=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs, borderwidth=2, relief="groove")
        self.entries = {}
        self.data = data if data is not None else {}
        self.create_widgets()

    def create_widgets(self):
        labels = ['Weight', 'Au', 'Ag', 'SiO2', 'CaO', 'S', 'Fe', 'Cu', 'Al2O3', 'As']
        for i, label in enumerate(labels):
            tk.Label(self, text=label).grid(row=i, column=0)
            entry = tk.Entry(self)
            entry.grid(row=i, column=1)
            self.entries[label] = entry
            if label in self.data:
                entry.insert(0, str(self.data[label]))  

    def get_values(self):
        """Собирает данные из Entry виджетов."""
        return {label: float(self.entries[label].get()) for label in self.entries if self.entries[label].get() != ''}

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Compound Data Input")
        self.geometry("800x600")

        self.compound_frames = []
        self.init_ui()

    def init_ui(self):
        self.frame = ttk.Frame(self)
        self.frame.pack(expand=True, fill="both")

        # self.add_compound_button = tk.Button(self.frame, text="Add Compound", command=self.add_compound_frame)
        # self.add_compound_button.grid(row=0, column=0, padx=10, pady=10)

        self.calculate_button = tk.Button(self.frame, text="Calculate", command=self.calculate)
        self.calculate_button.grid(row=0, column=2, padx=10, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(self)
        self.results_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.load_json_button = tk.Button(self.frame, text="Load from JSON", command=self.load_from_json)
        self.load_json_button.grid(row=0, column=1, padx=10, pady=10)

    def add_compound_frame(self, data=None):
        row = len(self.compound_frames) // 4
        column = len(self.compound_frames) % 4
        compound_frame = CompoundInputFrame(self.frame, data=data)
        compound_frame.grid(row=row+1, column=column, padx=10, pady=10, sticky="nsew")
        self.compound_frames.append(compound_frame)

    def load_from_json(self):
        filepath = filedialog.askopenfilename(
            title="Open JSON file",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if not filepath:
            return
        
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    for comp_data in data:
                        self.add_compound_frame(data=comp_data)
                else:
                    messagebox.showerror("Error", "JSON format is not correct")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON: {e}")

    def calculate(self):
        if not self.compound_frames:
            messagebox.showinfo("Предупреждение", "Нет добавленных компонентов для расчета.")
            return
        
        compounds = [] 
        for frame in self.compound_frames:
            data = frame.get_values()
            compound = Compound(**data)
            compounds.append(compound)

        total_weight = sum(compound.Weight for compound in compounds)
        total_elements = calculate_total_elements(compounds)  
        element_percentages = calculate_element_percentages(total_elements, total_weight)  
        stein_results = calculate_materials_in_stein(total_elements, total_weight, element_percentages)  
        slug_results = calculate_materials_in_slug(total_elements, stein_results)

        self.results_text.delete('1.0', tk.END)

        self.results_text.insert(tk.END, "Calculation Results:\n")
        self.results_text.insert(tk.END, f"Copper in Stein: {stein_results['Cu_in_stein_percentage']:.2f}%\n")
        self.results_text.insert(tk.END, f"Iron in Stein: {stein_results['Fe_in_stein_percentage']:.2f}%\n")
        self.results_text.insert(tk.END, f"Sulfur in Stein: {stein_results['S_in_stein_percentage']:.2f}%\n")
        self.results_text.insert(tk.END, f"Gold Concentration in Stein: {slug_results['gold_concentration_stein']} ppm\n")
        self.results_text.insert(tk.END, f"Silver Concentration in Stein: {slug_results['silver_concentration_stein']} ppm\n")
        self.results_text.insert(tk.END, "_____________________________________________\n")
        stein_weight_percentage = stein_results['stein_weight'] / total_weight * 100
        self.results_text.insert(tk.END, f"Stein weight: {stein_results['stein_weight']} ({stein_weight_percentage:.2f}%)\n\n")
        
        self.results_text.insert(tk.END, f"SiO2 in Slag: {slug_results['SiO2_in_slag_percentage']:.2f}%\n")
        self.results_text.insert(tk.END, f"CaO in Slag: {slug_results['CaO_in_slag_percentage']:.2f}%\n")
        self.results_text.insert(tk.END, f"Al2O3 in Slag: {slug_results['Al2O3_in_slag_percentage']:.2f}%\n")
        self.results_text.insert(tk.END, f"FeO in Slag: {slug_results['FeO_in_slag_percentage']:.2f}%\n")
        self.results_text.insert(tk.END, "_____________________________________________\n")
        slag_weight_percentage = slug_results['slag_weight'] / total_weight * 100
        self.results_text.insert(tk.END, f"Total Slag Weight: {slug_results['slag_weight']} ({slag_weight_percentage:.2f}%)\n\n")
        
        melt_weight = stein_results['stein_weight'] + slug_results['slag_weight']
        sublimates_weight = total_weight - stein_results['stein_weight'] - slug_results['slag_weight']
        self.results_text.insert(tk.END, f"Melt weight: {melt_weight} ({melt_weight / total_weight * 100:.2f}%)\n")
        sublimates_weight_percentage = sublimates_weight / total_weight * 100
        self.results_text.insert(tk.END, f"Sublimates weight: {sublimates_weight} ({sublimates_weight_percentage:.2f}%)\n")
        self.results_text.insert(tk.END, f"Total weight check: {stein_results['stein_weight'] + slug_results['slag_weight'] + sublimates_weight} ({stein_weight_percentage + slag_weight_percentage + sublimates_weight_percentage:.2f}%)\n")




if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
