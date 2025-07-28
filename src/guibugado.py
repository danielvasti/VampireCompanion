# src/gui.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
from character import Character

def load_game_data(file_path):
    """Carrega dados de um arquivo JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Erro de Arquivo", f"Não foi possível carregar o arquivo: {file_path}\n\n{e}")
        return None

class DotSelector(ctk.CTkFrame):
    """
    Widget customizado para criar uma fileira de "bolinhas" (rádios) para seleção de pontos.
    """
    def __init__(self, master, total_dots=5, variable=None, command=None):
        super().__init__(master, fg_color="transparent")
        self.variable = variable if variable else tk.IntVar(value=0)
        self.command = command
        self.total_dots = total_dots
        self.dots = []

        for i in range(1, total_dots + 1):
            dot = ctk.CTkRadioButton(
                self,
                text="",
                variable=self.variable,
                value=i,
                width=18,
                height=18,
                border_width_unchecked=2,
                border_width_checked=2,
                fg_color=("#9A0000", "#700000"),
                border_color=("#500000", "#500000"),
                hover_color=("#B50000", "#B50000"),
                command=self.on_select
            )
            dot.pack(side="left", padx=2)
            self.dots.append(dot)

    def on_select(self):
        if self.command:
            self.command(self.variable.get())

    def get(self):
        return self.variable.get()

    def set(self, value):
        self.variable.set(value)

    def configure_state(self, state="normal"):
        """Habilita ou desabilita todos os botões."""
        for dot in self.dots:
            dot.configure(state=state)

class CharacterSheet(ctk.CTkToplevel):
    def __init__(self, master, character, clans_data, attributes_data, skills_data):
        super().__init__(master)
        self.title("Ficha de Personagem - Vampiro: A Máscara")
        self.geometry("1100x850")
        self.resizable(True, True)

        self.character = character
        self.clans_data = clans_data
        self.attributes_data = attributes_data
        self.skills_data = skills_data
        self.MANDATORY_SPECIALTY_SKILLS = ["Acadêmicos", "Ofícios", "Performance", "Ciências"]

        self.info_vars = {
            "Nome": tk.StringVar(value=self.character.name),
            "Jogador": tk.StringVar(), "Crônica": tk.StringVar(),
            "Natureza": tk.StringVar(), "Comportamento": tk.StringVar(),
            "Clã": tk.StringVar(value=self.character.clan or list(clans_data.keys())[0]),
            "Geração": tk.StringVar(), "Senhor": tk.StringVar()
        }
        self.attribute_vars = {attr: tk.IntVar(value=self.character.attributes.get(attr, 1)) for cat in attributes_data.values() for attr in cat}
        self.skill_vars = {skill: tk.IntVar(value=self.character.skills.get(skill, 0)) for cat in skills_data.values() for skill in cat}
        
        self.setup_ui()
        self.bind_character_to_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.create_header_frame(row=0)
        self.create_main_content(row=1)
        self.create_footer_frame(row=2)
        self.create_action_buttons(row=3)

    def bind_character_to_ui(self):
        for key, var in self.info_vars.items():
            def on_var_change(name, index, mode, k=key, v=var):
                attr_name = 'name' if k == 'Nome' else k.lower()
                setattr(self.character, attr_name, v.get())
            var.trace_add("write", on_var_change)

    def create_header_frame(self, row):
        header_frame = ctk.CTkFrame(self, corner_radius=10)
        header_frame.grid(row=row, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        header_frame.grid_columnconfigure((1, 3, 5), weight=1)
        fields = [
            ("Nome", 0, 0), ("Jogador", 0, 2), ("Crônica", 0, 4),
            ("Natureza", 1, 0), ("Comportamento", 1, 2), ("Clã", 1, 4),
            ("Geração", 2, 0), ("Senhor", 2, 2)
        ]
        for label, r, c in fields:
            ctk.CTkLabel(header_frame, text=f"{label}:").grid(row=r, column=c, padx=(10, 0), pady=5, sticky="w")
            if label == "Clã":
                widget = ctk.CTkOptionMenu(header_frame, variable=self.info_vars[label], values=list(self.clans_data.keys()))
            else:
                widget = ctk.CTkEntry(header_frame, textvariable=self.info_vars[label])
            colspan = 3 if label == "Senhor" else 1
            widget.grid(row=r, column=c+1, padx=(0, 10), pady=5, sticky="ew", columnspan=colspan)

    def create_main_content(self, row):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=row, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nsew")
        main_frame.grid_columnconfigure((0, 1, 2), weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        self.create_attributes_column(main_frame).grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        self.create_abilities_column(main_frame).grid(row=0, column=1, padx=5, sticky="nsew")
        self.create_advantages_column(main_frame).grid(row=0, column=2, padx=(5, 0), sticky="nsew")
        
    def _create_column_frame(self, parent, title):
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=10, padx=10, sticky="ew")
        return frame

    def create_attributes_column(self, parent):
        frame = self._create_column_frame(parent, "Atributos")
        # --- CORREÇÃO AQUI: Usando as chaves no SINGULAR ---
        self._create_trait_category(frame, "Físicos", self.attributes_data['Físico'], self.attribute_vars, row=1)
        self._create_trait_category(frame, "Sociais", self.attributes_data['Social'], self.attribute_vars, row=3)
        self._create_trait_category(frame, "Mentais", self.attributes_data['Mental'], self.attribute_vars, row=5)
        return frame

    def create_abilities_column(self, parent):
        frame = self._create_column_frame(parent, "Habilidades")
        # As chaves de Habilidades geralmente estão no plural nos seus dados
        self._create_trait_category(frame, "Talentos", self.skills_data['Talentos'], self.skill_vars, row=1)
        self._create_trait_category(frame, "Perícias", self.skills_data['Perícias'], self.skill_vars, row=3)
        self._create_trait_category(frame, "Conhecimentos", self.skills_data['Conhecimentos'], self.skill_vars, row=5)
        return frame
        
    def create_advantages_column(self, parent):
        frame = self._create_column_frame(parent, "Vantagens")
        self._create_trait_category(frame, "Disciplinas", [""] * 3, {}, row=1, dots=0)
        self._create_trait_category(frame, "Antecedentes", [""] * 5, {}, row=2, dots=0)
        self._create_trait_category(frame, "Virtudes", ["Consciência", "Autocontrole", "Coragem"], {}, row=3, dots=5)
        return frame

    def _create_trait_category(self, parent_frame, title, items, var_dict, row, dots=5):
        category_group_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        category_group_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        category_group_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(category_group_frame, text=title, font=ctk.CTkFont(size=13, weight="bold"), anchor="w").grid(row=0, column=0, sticky="ew", padx=20, pady=(0, 2))
        items_frame = ctk.CTkFrame(category_group_frame, fg_color="transparent")
        items_frame.grid(row=1, column=0, sticky="ew", padx=10)
        items_frame.grid_columnconfigure(1, weight=1)
        for i, item_name in enumerate(items):
            display_name = item_name if item_name else "_____________"
            label = ctk.CTkLabel(items_frame, text=display_name, anchor="w")
            label.grid(row=i, column=0, sticky="w", padx=10)
            if item_name and var_dict and dots > 0:
                var = var_dict.get(item_name)
                if var:
                    selector = DotSelector(items_frame, total_dots=dots, variable=var)
                    selector.grid(row=i, column=1, sticky="e", padx=(0, 10))
                    selector.configure_state("disabled")

    def create_footer_frame(self, row):
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=row, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew")
        footer_frame.grid_columnconfigure((0, 1), weight=1)
        left_frame = ctk.CTkFrame(footer_frame, corner_radius=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(left_frame, text="Qualidades e Defeitos", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=5, padx=10, sticky="ew")
        ctk.CTkTextbox(left_frame, height=80).grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))
        right_frame = ctk.CTkFrame(footer_frame, corner_radius=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(right_frame, text="Vitalidade", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=5, padx=10, sticky="ew")
        ctk.CTkTextbox(right_frame, height=80).grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))

    def create_action_buttons(self, row):
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=row, column=0, columnspan=3, padx=10, pady=10, sticky="e")
        ctk.CTkButton(action_frame, text="Distribuir Pontos", command=self.open_distribution_window).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Escolher Especialidades", command=self.open_specialty_window).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Salvar Personagem", command=self.save_character).pack(side="right", padx=5)

    def open_distribution_window(self):
        messagebox.showinfo("Em Construção", "A janela para distribuição de pontos será implementada aqui.")

    def open_specialty_window(self):
        messagebox.showinfo("Em Construção", "A janela para escolha de especialidades será implementada aqui.")

    def save_character(self):
        self.update_character_from_ui()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Salvar Ficha de Personagem",
            initialfile=f"{self.character.name or 'personagem'}.json"
        )
        if not file_path: return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.character.to_dict(), f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Sucesso", f"Personagem salvo em {file_path}", parent=self)
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo.\n\n{e}", parent=self)

    def update_character_from_ui(self):
        for attr, var in self.attribute_vars.items():
            self.character.attributes[attr] = var.get()
        for skill, var in self.skill_vars.items():
            self.character.skills[skill] = var.get()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Vampire Companion")
        self.geometry("350x200")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.clans_data = load_game_data('data/clans.json')
        self.attributes_data = load_game_data('data/attributes.json')
        self.skills_data = load_game_data('data/skills.json')

        if not all([self.clans_data, self.attributes_data, self.skills_data]):
            self.after(100, self.destroy)
            return

        self.character = Character("")
        self.character.initialize_stats(self.attributes_data, self.skills_data)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        ctk.CTkButton(self.main_frame, text="Criar Novo Personagem", command=self.open_sheet).pack(pady=10, fill="x")
        ctk.CTkButton(self.main_frame, text="Carregar Personagem", command=self.load_character).pack(pady=10, fill="x")
        self.sheet_window = None

    def open_sheet(self, char_data=None):
        if self.sheet_window is None or not self.sheet_window.winfo_exists():
            if char_data:
                self.character.from_dict(char_data)
            else:
                self.character = Character("")
                self.character.initialize_stats(self.attributes_data, self.skills_data)
            self.sheet_window = CharacterSheet(self, self.character, self.clans_data, self.attributes_data, self.skills_data)
            self.sheet_window.focus()
        else:
            self.sheet_window.focus()

    def load_character(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if not file_path: return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.open_sheet(char_data=data)
        except Exception as e:
            messagebox.showerror("Erro ao Carregar", f"Não foi possível carregar o personagem.\n\n{e}")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Vampire Companion")
        self.geometry("350x200")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.clans_data = load_game_data('data/clans.json')
        self.attributes_data = load_game_data('data/attributes.json')
        self.skills_data = load_game_data('data/skills.json')

        if not all([self.clans_data, self.attributes_data, self.skills_data]):
            self.after(100, self.destroy)
            return

        self.character = Character("")
        self.character.initialize_stats(self.attributes_data, self.skills_data)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkButton(self.main_frame, text="Criar Novo Personagem", command=self.open_sheet).pack(pady=10, fill="x")
        ctk.CTkButton(self.main_frame, text="Carregar Personagem", command=self.load_character).pack(pady=10, fill="x")
        
        self.sheet_window = None

    def open_sheet(self, char_data=None):
        if self.sheet_window is None or not self.sheet_window.winfo_exists():
            if char_data:
                # Assumindo que seu objeto character tem um método from_dict()
                self.character.from_dict(char_data)
            else:
                self.character = Character("")
                self.character.initialize_stats(self.attributes_data, self.skills_data)
            
            self.sheet_window = CharacterSheet(self, self.character, self.clans_data, self.attributes_data, self.skills_data)
            self.sheet_window.focus()
        else:
            self.sheet_window.focus()

    def load_character(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.open_sheet(char_data=data)
        except Exception as e:
            messagebox.showerror("Erro ao Carregar", f"Não foi possível carregar o personagem.\n\n{e}")
if __name__ == "__main__":
    app = App()
    app.mainloop()