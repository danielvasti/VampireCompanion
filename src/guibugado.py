# src/gui.py

# Imports
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
from character import Character

def load_game_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar {file_path}: {e}")
        return None

class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configurações de tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- DADOS DO JOGO E DO PERSONAGEM ---
        self.MANDATORY_SPECIALTY_SKILLS = ["Acadêmicos", "Ofícios", "Performance", "Ciências"]
        self.clans_data = load_game_data('data/clans.json')
        self.attributes_data = load_game_data('data/attributes.json')
        self.skills_data = load_game_data('data/skills.json')
        self.clan_list = list(self.clans_data.keys()) if self.clans_data else []
        self.character = Character("")
        self.character.initialize_stats(self.attributes_data, self.skills_data)
        
        # Variáveis de controle para a criação
        self.attribute_selection_stage = 4
        self.selected_primary_attr = tk.StringVar(value=None)
        self.selected_secondary_attrs = {}
        self.selected_tertiary_attrs = {}
        self.attribute_widgets = {}
        self.skill_selection_stage = 3
        self.selected_skills_by_value = {3: {}, 2: {}, 1: {}}
        self.skill_widgets = {}

        # Variáveis para os medidores
        self.health_tracker_states = []
        self.willpower_tracker_states = []
        self.health_tracker_buttons = []
        self.willpower_tracker_buttons = []

        # Configurações da Janela
        self.title("Vampire: The Masquerade Companion")
        self.geometry("950x850")

        try:
            self.iconbitmap("assets/icon.ico")
        except tk.TclError:
            print("Ícone 'assets/icon.ico' não encontrado.")

        # Fontes
        self.title_font = ("Garamond", 24, "bold")
        self.category_font = ("Garamond", 18, "bold", "italic")
        self.normal_font = ("Segoe UI", 13)
        self.tracker_font = ("Courier New", 16, "bold")

        # --- ESTRUTURA PRINCIPAL ---
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Criador de Personagem", label_font=self.title_font)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- SEÇÕES DA PÁGINA ---
        self._create_basic_info_section()
        ctk.CTkFrame(self.scrollable_frame, height=2, fg_color="gray30").pack(fill='x', padx=20, pady=20)
        self._create_status_trackers_section()
        ctk.CTkFrame(self.scrollable_frame, height=2, fg_color="gray30").pack(fill='x', padx=20, pady=20)
        self._create_attributes_section()
        ctk.CTkFrame(self.scrollable_frame, height=2, fg_color="gray30").pack(fill='x', padx=20, pady=20)
        self._create_skills_section()
        ctk.CTkFrame(self.scrollable_frame, height=2, fg_color="gray30").pack(fill='x', padx=20, pady=20)
        self._create_final_sheet_section()
        
        # Inicializa os medidores com um valor padrão
        self._update_tracker_size("health", 5) # Vigor 2 (padrão) + 3 = 5
        self._update_tracker_size("willpower", 2) # Compostura 1 + Determinação 1 = 2

    def _create_basic_info_section(self):
        header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#1A1A1A", corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=(0, 20))
        ctk.CTkLabel(header_frame, text="VAMPIRE: THE MASQUERADE", font=("Garamond", 28, "bold"), text_color="#9A0000").pack(pady=(10, 0))
        ctk.CTkFrame(header_frame, height=2, fg_color="#9A0000").pack(fill="x", padx=50, pady=5)
        info_grid = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_grid.pack(pady=(0, 15), fill="x", padx=20)
        info_grid.grid_columnconfigure((0, 1, 2), weight=1)
        left_col = ctk.CTkFrame(info_grid, fg_color="transparent"); mid_col = ctk.CTkFrame(info_grid, fg_color="transparent"); right_col = ctk.CTkFrame(info_grid, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=10); mid_col.grid(row=0, column=1, sticky="nsew", padx=10); right_col.grid(row=0, column=2, sticky="nsew", padx=10)
        left_fields = [("Nome do Personagem", "name_entry", 200), ("Crônica", "chronicle_entry", 200), ("Senhor", "sire_entry", 200)]
        mid_fields = [("Conceito", "concept_entry", 200), ("Ambição", "ambition_entry", 200), ("Desejo", "desire_entry", 200)]
        right_fields = [("Predador", "predator_entry", 200), ("Clã", "clan_menu", 200, self.clan_list), ("Jogador", "player_entry", 200)]
        def populate_column(column_frame, fields_list):
            for i, (label, var_name, width, *options) in enumerate(fields_list):
                field_frame = ctk.CTkFrame(column_frame, fg_color="transparent"); field_frame.pack(fill="x", pady=5)
                ctk.CTkLabel(field_frame, text=label + ":", font=self.normal_font).pack(anchor="w")
                if var_name.endswith("_entry"):
                    entry = ctk.CTkEntry(field_frame, width=width, font=self.normal_font, border_color="#9A0000"); entry.pack(fill="x")
                    setattr(self, var_name, entry)
                elif var_name.endswith("_menu"):
                    var = tk.StringVar()
                    menu = ctk.CTkOptionMenu(field_frame, variable=var, values=options[0] if options else [], width=width, dropdown_fg_color="#1A1A1A", button_color="#9A0000", font=self.normal_font); menu.pack(fill="x")
                    setattr(self, var_name.replace("_menu", "_var"), var)
                    if options and options[0]: var.set(options[0][0])
        populate_column(left_col, left_fields); populate_column(mid_col, mid_fields); populate_column(right_col, right_fields)
    
    def _create_status_trackers_section(self):
        trackers_main_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        trackers_main_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(trackers_main_frame, text="Medidores de Status", font=self.category_font).pack()
        health_frame = ctk.CTkFrame(trackers_main_frame); health_frame.pack(pady=10)
        ctk.CTkLabel(health_frame, text="Vitalidade", font=self.normal_font).pack(pady=5)
        self.health_tracker_container = ctk.CTkFrame(health_frame, fg_color="transparent"); self.health_tracker_container.pack(pady=5)
        willpower_frame = ctk.CTkFrame(trackers_main_frame); willpower_frame.pack(pady=10)
        ctk.CTkLabel(willpower_frame, text="Força de Vontade", font=self.normal_font).pack(pady=5)
        self.willpower_tracker_container = ctk.CTkFrame(willpower_frame, fg_color="transparent"); self.willpower_tracker_container.pack(pady=5)

    def _create_attributes_section(self):
        attr_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        attr_frame.pack(fill="x", expand=True, padx=20, pady=10)
        self._populate_attribute_frame(attr_frame)

    def _create_skills_section(self):
        skills_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        skills_frame.pack(fill="x", expand=True, padx=20, pady=10)
        self._populate_skill_frame(skills_frame)
        
    def _create_final_sheet_section(self):
        final_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        final_frame.pack(fill="both", expand=True, padx=20, pady=10)
        create_button = ctk.CTkButton(final_frame, text="Gerar Ficha e Escolher Especialidades", command=self.generate_sheet, font=self.normal_font)
        create_button.pack(pady=(10, 15))
        self.output_text = ctk.CTkTextbox(final_frame, font=("Courier New", 12), height=400, activate_scrollbars=True)
        self.output_text.pack(fill="both", expand=True); self.output_text.configure(state="disabled")

    def _create_tracker_row(self, container, tracker_type, size):
        states_list = getattr(self, f"{tracker_type}_tracker_states")
        buttons_list = getattr(self, f"{tracker_type}_tracker_buttons")
        for i in range(size):
            button = ctk.CTkButton(container, text="", width=35, height=35, font=self.tracker_font, fg_color="#343638", border_width=2, border_color="gray50", hover_color="gray25", command=lambda t=tracker_type, idx=i: self._on_tracker_click(t, idx))
            button.grid(row=0, column=i, padx=3)
            buttons_list.append(button); states_list.append(0)

    def _on_tracker_click(self, tracker_type, index):
        states_list = getattr(self, f"{tracker_type}_tracker_states"); buttons_list = getattr(self, f"{tracker_type}_tracker_buttons")
        states_list[index] = (states_list[index] + 1) % 3
        new_state = states_list[index]; button_to_update = buttons_list[index]
        if new_state == 0: button_to_update.configure(text="", text_color="white")
        elif new_state == 1: button_to_update.configure(text="/", text_color="white")
        elif new_state == 2: button_to_update.configure(text="X", text_color="#FF4040")

    def _update_tracker_size(self, tracker_type, new_size):
        container = getattr(self, f"{tracker_type}_tracker_container"); buttons_list = getattr(self, f"{tracker_type}_tracker_buttons"); states_list = getattr(self, f"{tracker_type}_tracker_states")
        for widget in container.winfo_children(): widget.destroy()
        buttons_list.clear(); states_list.clear()
        self._create_tracker_row(container, tracker_type, new_size)
    
    def _populate_attribute_frame(self, parent_frame):
        header_frame = ctk.CTkFrame(parent_frame, fg_color="transparent"); header_frame.pack(fill="x", pady=5)
        self.attribute_instruction_label = ctk.CTkLabel(header_frame, text="Passo 1: Escolha seu Atributo Primário (4 pontos)", font=self.category_font); self.attribute_instruction_label.pack(side="left", padx=10)
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent"); button_frame.pack(side="right")
        reset_button = ctk.CTkButton(button_frame, text="Resetar", command=self.reset_attributes, width=80); reset_button.pack(side="right", padx=5)
        self.confirm_attr_button = ctk.CTkButton(button_frame, text="Confirmar Passo", command=self.confirm_attribute_step, width=120); self.confirm_attr_button.pack(side="right")
        content_frame = ctk.CTkFrame(parent_frame, fg_color="transparent"); content_frame.pack(fill="both", expand=True, pady=10)
        phys_frame = ctk.CTkFrame(content_frame); phys_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        soc_frame = ctk.CTkFrame(content_frame); soc_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)
        ment_frame = ctk.CTkFrame(content_frame); ment_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=5)
        content_frame.grid_columnconfigure((0,1,2), weight=1)
        frames_by_cat = {"Físico": phys_frame, "Social": soc_frame, "Mental": ment_frame}
        for category, stats in self.attributes_data.items():
            parent = frames_by_cat[category]; ctk.CTkLabel(parent, text=category, font=self.normal_font).pack(pady=(10,5))
            for stat in stats: self._create_attribute_row(parent, stat)
            
    def _populate_skill_frame(self, parent_frame):
        header_frame = ctk.CTkFrame(parent_frame, fg_color="transparent"); header_frame.pack(fill="x", pady=5)
        self.skill_instruction_label = ctk.CTkLabel(header_frame, text="Passo 1: Escolha 3 Perícias (3 pontos)", font=self.category_font); self.skill_instruction_label.pack(side="left", padx=10)
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent"); button_frame.pack(side="right")
        reset_button = ctk.CTkButton(button_frame, text="Resetar", command=self.reset_skills, width=80); reset_button.pack(side="right", padx=5)
        self.confirm_skill_button = ctk.CTkButton(button_frame, text="Confirmar Passo", command=self.confirm_skill_step, width=120); self.confirm_skill_button.pack(side="right")
        content_frame = ctk.CTkFrame(parent_frame, fg_color="transparent"); content_frame.pack(fill="both", expand=True, pady=10)
        tal_frame = ctk.CTkFrame(content_frame); tal_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        per_frame = ctk.CTkFrame(content_frame); per_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)
        con_frame = ctk.CTkFrame(content_frame); con_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=5)
        content_frame.grid_columnconfigure((0,1,2), weight=1)
        frames_by_cat = {"Talentos": tal_frame, "Perícias": per_frame, "Conhecimentos": con_frame}
        for category, skills in self.skills_data.items():
            parent = frames_by_cat[category]; ctk.CTkLabel(parent, text=category, font=self.normal_font).pack(pady=(10,5))
            for skill in skills: var = tk.BooleanVar(); self._create_skill_row(parent, skill, var, command=self._update_skill_locks); self.selected_skills_by_value[3][skill] = var
    
    def _create_attribute_row(self, parent, stat_name):
        row_frame = ctk.CTkFrame(parent, fg_color="transparent"); row_frame.pack(fill="x", padx=15, pady=4)
        selector = ctk.CTkRadioButton(row_frame, text=stat_name, variable=self.selected_primary_attr, value=stat_name, font=self.normal_font, fg_color=("#9A0000", "#700000"), border_color="#500000", hover_color="#B50000"); selector.pack(side="left")
        value_label = ctk.CTkLabel(row_frame, text="1", font=self.normal_font, width=30); value_label.pack(side="right", padx=10)
        self.attribute_widgets[stat_name] = {'frame': row_frame, 'selector': selector, 'value_label': value_label}
        
    def _create_skill_row(self, parent, skill_name, var, command):
        row_frame = ctk.CTkFrame(parent, fg_color="transparent"); row_frame.pack(fill="x", padx=15, pady=4)
        selector = ctk.CTkCheckBox(row_frame, text=skill_name, variable=var, font=self.normal_font, command=command); selector.pack(side="left")
        value_label = ctk.CTkLabel(row_frame, text="0", font=self.normal_font, width=30); value_label.pack(side="right", padx=10)
        self.skill_widgets[skill_name] = {'selector': selector, 'value_label': value_label, 'var': var}
        
    def _update_attribute_locks(self):
        if self.attribute_selection_stage == 3: limit, selectable_attrs = 3, self.selected_secondary_attrs
        elif self.attribute_selection_stage == 2: limit, selectable_attrs = 4, self.selected_tertiary_attrs
        else: return
        chosen_count = sum(1 for var in selectable_attrs.values() if var.get());
        for stat, var in selectable_attrs.items():
            if not var.get(): self.attribute_widgets[stat]['selector'].configure(state="normal" if chosen_count < limit else "disabled")
            
    # --- FUNÇÃO PRINCIPAL MODIFICADA ---
    def confirm_attribute_step(self):
        if self.attribute_selection_stage == 4:
            primary = self.selected_primary_attr.get()
            if not primary or primary == 'None': messagebox.showerror("Seleção Incompleta", "Você deve selecionar um Atributo Primário."); return
            self.character.attributes[primary] = 4; self.attribute_widgets[primary]['value_label'].configure(text="4"); self.attribute_widgets[primary]['selector'].configure(state="disabled")
            self.attribute_selection_stage = 3
            self.attribute_instruction_label.configure(text="Passo 2: Escolha 3 Atributos Secundários (3 pontos)")
            for stat, widgets in self.attribute_widgets.items():
                if stat != primary:
                    var = tk.BooleanVar(); widgets['selector'].destroy()
                    new_selector = ctk.CTkCheckBox(widgets['frame'], text=stat, variable=var, command=self._update_attribute_locks, font=self.normal_font)
                    new_selector.pack(side="left")
                    widgets['selector'] = new_selector; self.selected_secondary_attrs[stat] = var
            return

        if self.attribute_selection_stage == 3:
            chosen_secondaries = [stat for stat, var in self.selected_secondary_attrs.items() if var.get()]
            if len(chosen_secondaries) != 3: messagebox.showerror("Seleção Inválida", "Você deve escolher exatamente 3 Atributos Secundários."); return
            for stat in chosen_secondaries: self.character.attributes[stat] = 3; self.attribute_widgets[stat]['value_label'].configure(text="3"); self.attribute_widgets[stat]['selector'].configure(state="disabled")
            self.attribute_selection_stage = 2
            self.attribute_instruction_label.configure(text="Passo 3: Escolha 4 Atributos Terciários (2 pontos)")
            remaining_stats = self.selected_secondary_attrs.keys() - set(chosen_secondaries)
            for stat in remaining_stats:
                widgets = self.attribute_widgets[stat]; var = tk.BooleanVar(); widgets['selector'].destroy()
                new_selector = ctk.CTkCheckBox(widgets['frame'], text=stat, variable=var, command=self._update_attribute_locks, font=self.normal_font)
                new_selector.pack(side="left")
                widgets['selector'] = new_selector; self.selected_tertiary_attrs[stat] = var
            self._update_attribute_locks()
            return
            
        if self.attribute_selection_stage == 2:
            chosen_tertiaries = [stat for stat, var in self.selected_tertiary_attrs.items() if var.get()]
            if len(chosen_tertiaries) != 4: messagebox.showerror("Seleção Inválida", "Você deve escolher exatamente 4 Atributos Terciários."); return
            for stat in chosen_tertiaries: self.character.attributes[stat] = 2; self.attribute_widgets[stat]['value_label'].configure(text="2"); self.attribute_widgets[stat]['selector'].configure(state="disabled")
            self.attribute_selection_stage = 0
            self.attribute_instruction_label.configure(text="Atributos Distribuídos!"); self.confirm_attr_button.configure(state="disabled")
            for stat in self.selected_tertiary_attrs.keys() - set(chosen_tertiaries): self.attribute_widgets[stat]['selector'].configure(state="disabled")
            
            # --- PARTE NOVA: CÁLCULO E ATUALIZAÇÃO DOS MEDIDORES ---
            # Após a distribuição final, pegamos os valores e atualizamos os medidores
            stamina = self.character.attributes.get("Vigor", 1)
            composure = self.character.attributes.get("Compostura", 1)
            resolve = self.character.attributes.get("Determinação", 1)
            
            self._update_tracker_size("health", stamina + 3)
            self._update_tracker_size("willpower", composure + resolve)
            # --------------------------------------------------------
            return

    # --- FUNÇÃO DE RESET MODIFICADA ---
    def reset_attributes(self):
        self.character.initialize_stats(self.attributes_data, self.skills_data)
        self.attribute_selection_stage = 4
        self.selected_primary_attr.set(None)
        self.selected_secondary_attrs.clear()
        self.selected_tertiary_attrs.clear()
        self.attribute_instruction_label.configure(text="Passo 1: Escolha seu Atributo Primário (4 pontos)")
        self.confirm_attr_button.configure(state="normal")
        for stat, widgets in self.attribute_widgets.items():
            widgets['value_label'].configure(text="1")
            widgets['selector'].destroy()
            new_selector = ctk.CTkRadioButton(widgets['frame'], text=stat, variable=self.selected_primary_attr, value=stat, font=self.normal_font, fg_color=("#9A0000", "#700000"), border_color="#500000", hover_color="#B50000")
            new_selector.pack(side="left")
            widgets['selector'] = new_selector
        
        # Reseta os medidores para o tamanho padrão também
        self._update_tracker_size("health", 5)
        self._update_tracker_size("willpower", 2)

    # ... (O resto do código permanece o mesmo)
    def _update_skill_locks(self):
        limits = {3: 3, 2: 5, 1: 7}; stage = self.skill_selection_stage
        if stage not in limits: return
        limit, selectable_skills = limits[stage], self.selected_skills_by_value[stage]
        chosen_count = sum(1 for var in selectable_skills.values() if var.get())
        for skill, var in selectable_skills.items():
            if not var.get(): self.skill_widgets[skill]['selector'].configure(state="normal" if chosen_count < limit else "disabled")
            
    def confirm_skill_step(self):
        stage = self.skill_selection_stage; limits = {3: 3, 2: 5, 1: 7}
        if stage not in limits: return
        chosen = [skill for skill, var in self.selected_skills_by_value[stage].items() if var.get()]
        if len(chosen) != limits[stage]: messagebox.showerror("Seleção Inválida", f"Você deve escolher exatamente {limits[stage]} Perícias."); return
        for skill in chosen: self.character.skills[skill] = stage; self.skill_widgets[skill]['value_label'].configure(text=str(stage)); self.skill_widgets[skill]['selector'].configure(state="disabled")
        next_stage = stage - 1; self.skill_selection_stage = next_stage
        if next_stage > 0:
            self.skill_instruction_label.configure(text=f"Passo {4-next_stage}: Escolha {limits[next_stage]} Perícias ({next_stage} pontos)")
            remaining_skills = self.selected_skills_by_value[stage].keys() - set(chosen)
            for skill in remaining_skills: self.selected_skills_by_value[next_stage][skill] = self.skill_widgets[skill]['var']
            self.selected_skills_by_value[stage].clear(); self._update_skill_locks()
        else:
            self.skill_instruction_label.configure(text="Perícias Distribuídas!"); self.confirm_skill_button.configure(state="disabled")
            remaining_skills = self.selected_skills_by_value[stage].keys() - set(chosen)
            for skill in remaining_skills: self.skill_widgets[skill]['selector'].configure(state="disabled")
            self.selected_skills_by_value[stage].clear()
            
    def reset_skills(self):
        self.character.initialize_stats(self.attributes_data, self.skills_data)
        self.skill_selection_stage = 3; self.selected_skills_by_value = {3: {}, 2: {}, 1: {}}
        self.skill_instruction_label.configure(text="Passo 1: Escolha 3 Perícias (3 pontos)"); self.confirm_skill_button.configure(state="normal")
        for skill, widgets in self.skill_widgets.items():
            widgets['value_label'].configure(text="0"); widgets['selector'].configure(state="normal")
            widgets['var'].set(False); self.selected_skills_by_value[3][skill] = widgets['var']
        self._update_skill_locks()
        
    def generate_sheet(self):
        if self.attribute_selection_stage != 0 or self.skill_selection_stage != 0: messagebox.showwarning("Criação Incompleta", "Finalize Atributos e Perícias."); return
        self.character.name = self.name_entry.get()
        if not self.character.name: messagebox.showerror("Erro", "Personagem precisa de um nome."); return
        self.character.specialties.clear()
        self.character.set_clan(self.clan_menu_var.get(), self.clans_data)
        self._update_output_text(); self._open_specialty_window()
        
    def _open_specialty_window(self):
        eligible_skills = sorted([s for s, v in self.character.skills.items() if v > 0])
        if not eligible_skills: return
        mandatory_skills_with_dots = [s for s in eligible_skills if s in self.MANDATORY_SPECIALTY_SKILLS]
        free_choice_skills = [s for s in eligible_skills if s not in self.MANDATORY_SPECIALTY_SKILLS]
        popup = ctk.CTkToplevel(self) 
        popup.title("Escolher Especialidades"); popup.geometry("500x400"); popup.resizable(False, False); popup.transient(self); popup.grab_set()
        main_frame = ctk.CTkFrame(popup, fg_color="transparent", corner_radius=0); main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        entry_widgets = {}
        if mandatory_skills_with_dots:
            mandatory_frame = ctk.CTkFrame(main_frame); mandatory_frame.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(mandatory_frame, text="Especialidades Obrigatórias", font=(self.normal_font[0], 15, "bold")).pack(pady=10)
            for skill in mandatory_skills_with_dots:
                f = ctk.CTkFrame(mandatory_frame, fg_color="transparent"); f.pack(fill="x", padx=10, pady=5)
                ctk.CTkLabel(f, text=f"{skill}:", font=self.normal_font).pack(side="left")
                entry = ctk.CTkEntry(f, font=self.normal_font, width=250); entry.pack(side="right", fill="x", expand=True)
                entry_widgets[skill] = entry
        free_frame = ctk.CTkFrame(main_frame); free_frame.pack(fill="x")
        ctk.CTkLabel(free_frame, text="Especialidade Gratuita (1)", font=(self.normal_font[0], 15, "bold")).pack(pady=10)
        selected_free_skill = tk.StringVar(self); free_specialty_entry = ctk.CTkEntry(free_frame, font=self.normal_font, placeholder_text="Ex: Facas, Poesia...", width=250)
        if free_choice_skills:
            f = ctk.CTkFrame(free_frame, fg_color="transparent"); f.pack(fill="x", padx=10, pady=5)
            skill_menu = ctk.CTkOptionMenu(f, variable=selected_free_skill, values=free_choice_skills, font=self.normal_font); skill_menu.pack(side="left", padx=(0,10))
            free_specialty_entry.pack(side="right", fill="x", expand=True)
        else: ctk.CTkLabel(free_frame, text="Nenhuma outra perícia disponível.").pack()
        confirm_button = ctk.CTkButton(main_frame, text="Confirmar e Finalizar", command=lambda: self._confirm_specialty(entry_widgets, selected_free_skill, free_specialty_entry, popup))
        confirm_button.pack(pady=20)
        
    def _confirm_specialty(self, mandatory_entries, free_skill_var, free_entry_widget, popup):
        for skill, entry_widget in mandatory_entries.items():
            specialty_text = entry_widget.get().strip()
            if not specialty_text: messagebox.showerror("Erro", f"A perícia '{skill}' precisa de uma especialidade.", parent=popup); return
            self.character.add_specialty(skill, specialty_text)
        free_specialty_text = free_entry_widget.get().strip()
        if free_specialty_text:
            free_skill = free_skill_var.get()
            if free_skill: self.character.add_specialty(free_skill, free_specialty_text)
        popup.destroy(); self._update_output_text()
        
    def _update_output_text(self):
        char = self.character; result = f"--- FICHA DE PERSONAGEM: {char.name.upper()} ---\n"; result += f"CLÃ: {char.clan}\n\n"
        result += "--- ATRIBUTOS ---\n"
        for cat, stats in self.attributes_data.items(): result += f"{cat.upper()}: " + ", ".join([f"{s} {char.attributes[s]}" for s in stats]) + "\n"
        result += "\n--- PERÍCIAS ---\n"
        for cat, stats in self.skills_data.items():
            skill_lines = []
            for s in stats:
                if char.skills.get(s, 0) > 0:
                    specialty_str = f" ({', '.join(char.specialties[s])})" if s in char.specialties else ""
                    skill_lines.append(f"{s} {char.skills[s]}{specialty_str}")
            if skill_lines: result += f"{cat.upper()}: " + ", ".join(skill_lines) + "\n"
        self.output_text.configure(state="normal"); self.output_text.delete("1.0", tk.END); self.output_text.insert("1.0", result); self.output_text.configure(state="disabled")

if __name__ == "__main__":
    app = App()
    app.mainloop()