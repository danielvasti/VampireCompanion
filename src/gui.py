# src/gui.py

import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox, Toplevel
import json
from character import Character
import sv_ttk

def load_game_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar {file_path}: {e}")
        return None

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sv_ttk.set_theme("dark")

        # --- Carregar Todos os Dados ---
        self.MANDATORY_SPECIALTY_SKILLS = ["Acadêmicos", "Ofícios", "Performance", "Ciências"]
        self.clans_data = load_game_data('data/clans.json')
        self.attributes_data = load_game_data('data/attributes.json')
        self.skills_data = load_game_data('data/skills.json')
        self.clan_list = list(self.clans_data.keys()) if self.clans_data else []
        
        self.character = Character("")
        self.character.initialize_stats(self.attributes_data, self.skills_data)
        
        self.attribute_selection_stage = 4
        self.selected_primary_attr = tk.StringVar(value=None)
        self.selected_secondary_attrs = {}
        self.selected_tertiary_attrs = {}
        self.attribute_widgets = {}

        self.skill_selection_stage = 3
        self.selected_skills_by_value = {3: {}, 2: {}, 1: {}}
        self.skill_widgets = {}

        self.title("Vampire: The Masquerade Companion")
        self.geometry("850x700")
        self.title_font = tkfont.Font(family='Garamond', size=16, weight="bold")
        self.normal_font = tkfont.Font(family='Garamond', size=12)
        self.category_font = tkfont.Font(family='Garamond', size=14, weight="bold", slant="italic")

        notebook = ttk.Notebook(self)
        notebook.pack(pady=10, padx=10, fill="both", expand=True)
        main_tab, attr_tab, skills_tab = ttk.Frame(notebook), ttk.Frame(notebook), ttk.Frame(notebook)
        notebook.add(main_tab, text='Ficha Principal'); notebook.add(attr_tab, text='Atributos'); notebook.add(skills_tab, text='Perícias')

        self._create_main_tab(main_tab)
        self._create_attribute_tab(attr_tab)
        self._create_skill_tab(skills_tab)

    def _create_main_tab(self, parent_tab):
        # (Esta função permanece idêntica)
        input_frame = ttk.Frame(parent_tab); input_frame.pack(pady=10, padx=10, fill="x")
        output_frame = ttk.Frame(parent_tab); output_frame.pack(pady=10, padx=10, fill="both", expand=True)
        ttk.Label(input_frame, text="Nome:", font=self.normal_font).grid(row=0, column=0, sticky="w", padx=5)
        self.name_entry = ttk.Entry(input_frame, font=self.normal_font, width=30); self.name_entry.grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(input_frame, text="Clã:", font=self.normal_font).grid(row=0, column=2, sticky="w", padx=5)
        self.selected_clan = tk.StringVar(self)
        if self.clan_list: self.selected_clan.set(self.clan_list[0])
        clan_menu = ttk.OptionMenu(input_frame, self.selected_clan, self.clan_list[0], *self.clan_list); clan_menu.config(width=15); clan_menu.grid(row=0, column=3, sticky="w", padx=5)
        create_button = ttk.Button(input_frame, text="Gerar Ficha", command=self.generate_sheet); create_button.grid(row=0, column=4, padx=20)
        self.output_text = tk.Text(output_frame, font=("Courier New", 10), wrap="word", state="disabled"); self.output_text.pack(fill="both", expand=True)

    # --- LÓGICA DE ATRIBUTOS ---
    def _create_attribute_tab(self, parent_tab):
        header_frame = ttk.Frame(parent_tab); header_frame.pack(fill="x", pady=5, padx=10)
        self.attribute_instruction_label = ttk.Label(header_frame, text="Passo 1: Escolha seu Atributo Primário (4 pontos)", font=self.title_font); self.attribute_instruction_label.pack(side="left")
        reset_button = ttk.Button(header_frame, text="Resetar Atributos", command=self.reset_attributes); reset_button.pack(side="right", padx=5)
        self.confirm_attr_button = ttk.Button(header_frame, text="Confirmar Passo", command=self.confirm_attribute_step); self.confirm_attr_button.pack(side="right")
        content_frame = ttk.Frame(parent_tab); content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        for category, stats in self.attributes_data.items():
            cat_frame = ttk.LabelFrame(content_frame, text=category, labelwidget=ttk.Label(content_frame, text=category, font=self.category_font)); cat_frame.pack(fill="x", padx=10, pady=10, ipady=5)
            for stat in stats: self._create_attribute_row(cat_frame, stat)
    def _create_attribute_row(self, parent, stat_name):
        row_frame = ttk.Frame(parent); row_frame.pack(fill="x", padx=15, pady=2)
        selector = ttk.Radiobutton(row_frame, text=stat_name, variable=self.selected_primary_attr, value=stat_name); selector.pack(side="left")
        value_label = ttk.Label(row_frame, text="1", font=self.normal_font, width=5); value_label.pack(side="right", padx=20)
        self.attribute_widgets[stat_name] = {'frame': row_frame, 'selector': selector, 'value_label': value_label}

    def _update_attribute_locks(self):
        """NOVA FUNÇÃO: Chamada a cada clique de checkbox de atributo para travar/destravar."""
        if self.attribute_selection_stage == 3:
            limit = 3
            selectable_attrs = self.selected_secondary_attrs
        elif self.attribute_selection_stage == 2:
            limit = 4
            selectable_attrs = self.selected_tertiary_attrs
        else:
            return # Não faz nada em outras etapas

        chosen_count = sum(1 for var in selectable_attrs.values() if var.get())
        
        for stat, var in selectable_attrs.items():
            if not var.get(): # Se o checkbox não está marcado
                state = "normal" if chosen_count < limit else "disabled"
                self.attribute_widgets[stat]['selector'].config(state=state)

    def confirm_attribute_step(self):
        if self.attribute_selection_stage == 4:
            primary = self.selected_primary_attr.get()
            if not primary or primary == 'None': messagebox.showerror("Seleção Incompleta", "Você deve selecionar um Atributo Primário."); return
            self.character.attributes[primary] = 4; self.attribute_widgets[primary]['value_label'].config(text="4"); self.attribute_widgets[primary]['selector'].config(state="disabled")
            self.attribute_selection_stage = 3
            self.attribute_instruction_label.config(text="Passo 2: Escolha 3 Atributos Secundários (3 pontos)")
            for stat, widgets in self.attribute_widgets.items():
                if stat != primary:
                    var = tk.BooleanVar()
                    widgets['selector'].destroy()
                    # A MUDANÇA: Adicionamos o 'command' aqui
                    new_selector = ttk.Checkbutton(widgets['frame'], text=stat, variable=var, command=self._update_attribute_locks)
                    new_selector.pack(side="left")
                    widgets['selector'] = new_selector; self.selected_secondary_attrs[stat] = var
            return
        if self.attribute_selection_stage == 3:
            chosen_secondaries = [stat for stat, var in self.selected_secondary_attrs.items() if var.get()]
            if len(chosen_secondaries) != 3: messagebox.showerror("Seleção Inválida", "Você deve escolher exatamente 3 Atributos Secundários."); return
            for stat in chosen_secondaries: self.character.attributes[stat] = 3; self.attribute_widgets[stat]['value_label'].config(text="3"); self.attribute_widgets[stat]['selector'].config(state="disabled")
            self.attribute_selection_stage = 2
            self.attribute_instruction_label.config(text="Passo 3: Escolha 4 Atributos Terciários (2 pontos)")
            remaining_stats = self.selected_secondary_attrs.keys() - set(chosen_secondaries)
            for stat in remaining_stats:
                widgets = self.attribute_widgets[stat]; var = tk.BooleanVar(); widgets['selector'].destroy()
                # A MUDANÇA: Adicionamos o 'command' aqui também
                new_selector = ttk.Checkbutton(widgets['frame'], text=stat, variable=var, command=self._update_attribute_locks)
                new_selector.pack(side="left")
                widgets['selector'] = new_selector; self.selected_tertiary_attrs[stat] = var
            self._update_attribute_locks() # Chama uma vez para travar se já tiver 4.
            return
        if self.attribute_selection_stage == 2:
            chosen_tertiaries = [stat for stat, var in self.selected_tertiary_attrs.items() if var.get()]
            if len(chosen_tertiaries) != 4: messagebox.showerror("Seleção Inválida", f"Você deve escolher exatamente 4 Atributos Terciários."); return
            for stat in chosen_tertiaries: self.character.attributes[stat] = 2; self.attribute_widgets[stat]['value_label'].config(text="2"); self.attribute_widgets[stat]['selector'].config(state="disabled")
            self.attribute_selection_stage = 0; self.attribute_instruction_label.config(text="Atributos Distribuídos!"); self.confirm_attr_button.config(state="disabled")
            for stat in self.selected_tertiary_attrs.keys() - set(chosen_tertiaries): self.attribute_widgets[stat]['selector'].config(state="disabled")
            return
    def reset_attributes(self):
        # (Esta função permanece idêntica)
        self.character.initialize_stats(self.attributes_data, self.skills_data)
        self.attribute_selection_stage = 4; self.selected_primary_attr.set(None)
        self.selected_secondary_attrs.clear(); self.selected_tertiary_attrs.clear()
        self.attribute_instruction_label.config(text="Passo 1: Escolha seu Atributo Primário (4 pontos)"); self.confirm_attr_button.config(state="normal")
        for stat, widgets in self.attribute_widgets.items():
            widgets['value_label'].config(text="1"); widgets['selector'].destroy()
            new_selector = ttk.Radiobutton(widgets['frame'], text=stat, variable=self.selected_primary_attr, value=stat)
            new_selector.pack(side="left"); widgets['selector'] = new_selector

    # --- LÓGICA DE PERÍCIAS ---
    def _create_skill_tab(self, parent_tab):
        header_frame = ttk.Frame(parent_tab); header_frame.pack(fill="x", pady=5, padx=10)
        self.skill_instruction_label = ttk.Label(header_frame, text="Passo 1: Escolha 3 Perícias (3 pontos)", font=self.title_font); self.skill_instruction_label.pack(side="left")
        reset_button = ttk.Button(header_frame, text="Resetar Perícias", command=self.reset_skills); reset_button.pack(side="right", padx=5)
        self.confirm_skill_button = ttk.Button(header_frame, text="Confirmar Passo", command=self.confirm_skill_step); self.confirm_skill_button.pack(side="right")
        canvas = tk.Canvas(parent_tab); scrollbar = ttk.Scrollbar(parent_tab, orient="vertical", command=canvas.yview); scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))); canvas.create_window((0, 0), window=scrollable_frame, anchor="nw"); canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=10); scrollbar.pack(side="right", fill="y")
        for category, skills in self.skills_data.items():
            cat_frame = ttk.LabelFrame(scrollable_frame, text=category, labelwidget=ttk.Label(scrollable_frame, text=category, font=self.category_font)); cat_frame.pack(fill="x", padx=10, pady=10, ipady=5)
            for skill in skills:
                var = tk.BooleanVar()
                # A MUDANÇA: Adicionamos o 'command' aqui na criação inicial
                self._create_skill_row(cat_frame, skill, var, command=self._update_skill_locks)
                self.selected_skills_by_value[3][skill] = var
    def _create_skill_row(self, parent, skill_name, var, command):
        row_frame = ttk.Frame(parent); row_frame.pack(fill="x", padx=15, pady=2)
        selector = ttk.Checkbutton(row_frame, text=skill_name, variable=var, width=20, command=command); selector.pack(side="left")
        value_label = ttk.Label(row_frame, text="0", font=self.normal_font, width=5); value_label.pack(side="right", padx=20)
        self.skill_widgets[skill_name] = {'selector': selector, 'value_label': value_label, 'var': var}

    def _update_skill_locks(self):
        """NOVA FUNÇÃO: Chamada a cada clique de checkbox de perícia para travar/destravar."""
        limits = {3: 3, 2: 5, 1: 7}
        stage = self.skill_selection_stage
        if stage not in limits: return

        limit = limits[stage]
        selectable_skills = self.selected_skills_by_value[stage]
        chosen_count = sum(1 for var in selectable_skills.values() if var.get())

        for skill, var in selectable_skills.items():
            if not var.get():
                state = "normal" if chosen_count < limit else "disabled"
                self.skill_widgets[skill]['selector'].config(state=state)
    
    def confirm_skill_step(self):
        stage = self.skill_selection_stage
        limits = {3: 3, 2: 5, 1: 7}
        if stage not in limits: return
        
        chosen = [skill for skill, var in self.selected_skills_by_value[stage].items() if var.get()]
        if len(chosen) != limits[stage]: messagebox.showerror("Seleção Inválida", f"Você deve escolher exatamente {limits[stage]} Perícias para ter {stage} ponto(s)."); return

        for skill in chosen: self.character.skills[skill] = stage; self.skill_widgets[skill]['value_label'].config(text=str(stage)); self.skill_widgets[skill]['selector'].config(state="disabled")

        next_stage = stage - 1
        self.skill_selection_stage = next_stage
        
        if next_stage > 0:
            self.skill_instruction_label.config(text=f"Passo {4-next_stage}: Escolha {limits[next_stage]} Perícias ({next_stage} pontos)")
            remaining_skills = self.selected_skills_by_value[stage].keys() - set(chosen)
            for skill in remaining_skills: self.selected_skills_by_value[next_stage][skill] = self.skill_widgets[skill]['var']
            self.selected_skills_by_value[stage].clear()
            self._update_skill_locks() # Roda a trava para o novo estado
        else:
            self.skill_instruction_label.config(text="Perícias Distribuídas!")
            self.confirm_skill_button.config(state="disabled")
            remaining_skills = self.selected_skills_by_value[stage].keys() - set(chosen)
            for skill in remaining_skills: self.skill_widgets[skill]['selector'].config(state="disabled")
            self.selected_skills_by_value[stage].clear()

    def reset_skills(self):
        self.character.initialize_stats(self.attributes_data, self.skills_data)
        self.skill_selection_stage = 3
        self.selected_skills_by_value = {3: {}, 2: {}, 1: {}}
        self.skill_instruction_label.config(text="Passo 1: Escolha 3 Perícias (3 pontos)"); self.confirm_skill_button.config(state="normal")
        for skill, widgets in self.skill_widgets.items():
            widgets['value_label'].config(text="0"); widgets['selector'].config(state="normal")
            widgets['var'].set(False)
            self.selected_skills_by_value[3][skill] = widgets['var']
        self._update_skill_locks() # Roda para garantir que tudo está habilitado

    def generate_sheet(self):
        """Compila os dados do personagem e abre a janela de especialidade."""
        # Etapa 1: Validar e compilar dados básicos
        if self.attribute_selection_stage != 0 or self.skill_selection_stage != 0:
            messagebox.showwarning("Criação Incompleta", "Por favor, finalize a distribuição de Atributos e Perícias antes de gerar a ficha.")
            return

        self.character.name = self.name_entry.get()
        self.character.set_clan(self.selected_clan.get(), self.clans_data)

        if not self.character.name:
            messagebox.showerror("Erro", "Personagem precisa de um nome.")
            return

        # Etapa 2: Atualiza a ficha uma vez, depois abre o pop-up
        self._update_output_text()
        self._open_specialty_window()

    def _open_specialty_window(self):
        """NOVO: Abre uma janela pop-up para escolher a especialidade."""
        eligible_skills = [s for s, v in self.character.skills.items() if v > 0]
        if not eligible_skills:
            return # Não faz nada se não houver perícias com pontos

        # Cria a janela pop-up
        popup = Toplevel(self)
        popup.title("Escolher Especialidade")
        popup.geometry("450x200")
        popup.resizable(False, False)
        popup.transient(self) # Mantém o pop-up sobre a janela principal
        popup.grab_set() # Bloqueia interação com a janela principal

        # Verifica se há perícias que exigem especialidade
        mandatory_choices = [s for s in eligible_skills if s in self.MANDATORY_SPECIALTY_SKILLS]
        
        main_frame = ttk.Frame(popup, padding=15)
        main_frame.pack(fill="both", expand=True)

        instruction_text = "Você tem 1 especialidade gratuita."
        if mandatory_choices:
            instruction_text += f"\nVocê DEVE escolher uma para: {', '.join(mandatory_choices)}."
        
        ttk.Label(main_frame, text=instruction_text, wraplength=400).pack(pady=(0, 10))

        # Dropdown para escolher a perícia
        ttk.Label(main_frame, text="Perícia para Especializar:").pack(anchor="w")
        selected_skill = tk.StringVar(self)
        # Sugere a primeira perícia obrigatória, se houver
        if mandatory_choices:
            selected_skill.set(mandatory_choices[0])
        else:
            selected_skill.set(eligible_skills[0])
        
        skill_menu = ttk.OptionMenu(main_frame, selected_skill, eligible_skills[0], *eligible_skills)
        skill_menu.pack(fill="x", pady=5)

        # Campo para digitar a especialidade
        ttk.Label(main_frame, text="Digite a Especialidade (ex: Facas, Poesia, etc.):").pack(anchor="w")
        specialty_entry = ttk.Entry(main_frame, font=self.normal_font)
        specialty_entry.pack(fill="x", pady=5)
        specialty_entry.focus() # Foco no campo de texto

        # Botão de confirmação
        confirm_button = ttk.Button(
            main_frame, 
            text="Confirmar Especialidade",
            command=lambda: self._confirm_specialty(selected_skill.get(), specialty_entry.get(), popup)
        )
        confirm_button.pack(pady=10)

    def _confirm_specialty(self, skill, specialty_text, popup):
        """NOVO: Chamada pelo botão do pop-up para salvar a especialidade."""
        if not specialty_text.strip():
            messagebox.showerror("Erro", "O nome da especialidade não pode estar em branco.", parent=popup)
            return

        self.character.add_specialty(skill, specialty_text.strip())
        popup.destroy()
        self._update_output_text() # Atualiza a ficha principal com a nova info

    def _update_output_text(self):
        """NOVO: Refatorado para gerar/atualizar o texto da ficha a qualquer momento."""
        char = self.character
        result = f"--- FICHA DE PERSONAGEM: {char.name.upper()} ---\n"
        result += f"CLÃ: {char.clan}\n\n"
        
        result += "--- ATRIBUTOS ---\n"
        for cat, stats in self.attributes_data.items():
            line = f"{cat.upper()}: "
            line += ", ".join([f"{s} {char.attributes[s]}" for s in stats])
            result += line + "\n"
        
        result += "\n--- PERÍCIAS ---\n"
        for cat, stats in self.skills_data.items():
            skill_lines = []
            for s in stats:
                if char.skills.get(s, 0) > 0:
                    specialty_str = ""
                    if s in char.specialties:
                        # Formata como: Perícia 3 (Especialidade1, Especialidade2)
                        specialty_str = f" ({', '.join(char.specialties[s])})"
                    skill_lines.append(f"{s} {char.skills[s]}{specialty_str}")
            
            if skill_lines:
                result += f"{cat.upper()}: " + ", ".join(skill_lines) + "\n"

        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, result)
        self.output_text.config(state="disabled")

# --- COLE O RESTANTE DO CÓDIGO AQUI ---
# Cole aqui todo o código das funções de Atributos e Perícias que já tínhamos.
# As funções de _create_attribute_tab, confirm_attribute_step, reset_attributes, etc.
# permanecem as mesmas. É crucial que elas estejam presentes para o programa funcionar.
# A única função modificada é generate_sheet, e as 3 novas (_open_specialty_window,
# _confirm_specialty, _update_output_text) devem ser adicionadas.

# ... (código restante) ...

if __name__ == "__main__":
    app = App()
    app.mainloop()
