import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import uuid
from datetime import datetime

import storage


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('Ouvidoria CETEP/LNAB')
        self.geometry('900x640')
        self.minsize(820, 580)

        # Container
        self.container = ttk.Frame(self)
        self.container.pack(fill='both', expand=True)
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(1, weight=1)

        # Nav
        self.nav = ttk.Frame(self.container)
        self.nav.grid(row=0, column=0, sticky='ew')
        self.nav.columnconfigure(0, weight=1)

        self.brand = ttk.Label(self.nav, text='CETEP/LNAB', font=('Segoe UI', 12, 'bold'))
        self.brand.grid(row=0, column=0, sticky='w', padx=10, pady=8)

        self.nav_buttons = ttk.Frame(self.nav)
        self.nav_buttons.grid(row=0, column=1, sticky='e', padx=10)

        # Content frame (stacked pages)
        self.pages = {}
        self.page_container = ttk.Frame(self.container)
        self.page_container.grid(row=1, column=0, sticky='nsew')
        self.page_container.columnconfigure(0, weight=1)
        self.page_container.rowconfigure(0, weight=1)

        for PageClass in (HomePage, LoginPage, RegisterPage, ViewPage):
            page = PageClass(self.page_container, self)
            self.pages[PageClass.__name__] = page
            page.grid(row=0, column=0, sticky='nsew')

        self.show_page('HomePage')
        self.render_nav()

    # Session helpers
    @property
    def user(self) -> Optional[dict]:
        return storage.get_session()

    def login(self, user: dict) -> None:
        storage.set_session({'id': user['id'], 'name': user['name'], 'email': user['email']})
        self.render_nav()
        self.refresh_home()

    def logout(self) -> None:
        storage.set_session(None)
        self.render_nav()
        self.show_page('HomePage')
        self.refresh_home()

    def render_nav(self) -> None:
        for w in self.nav_buttons.winfo_children():
            w.destroy()
        if self.user:
            ttk.Button(self.nav_buttons, text='Início', command=lambda: self.show_page('HomePage')).pack(side='left', padx=4)
            ttk.Label(self.nav_buttons, text=f"Olá, {self.user['name'].split(' ')[0]}").pack(side='left', padx=8)
            ttk.Button(self.nav_buttons, text='Sair', command=self.logout).pack(side='left', padx=4)
        else:
            ttk.Button(self.nav_buttons, text='Início', command=lambda: self.show_page('HomePage')).pack(side='left', padx=4)
            ttk.Button(self.nav_buttons, text='Entrar', command=lambda: self.show_page('LoginPage')).pack(side='left', padx=4)
            ttk.Button(self.nav_buttons, text='Registrar', command=lambda: self.show_page('RegisterPage')).pack(side='left', padx=4)

    def show_page(self, name: str) -> None:
        page = self.pages[name]
        page.tkraise()
        if name == 'HomePage':
            self.refresh_home()

    def refresh_home(self) -> None:
        home: HomePage = self.pages['HomePage']  # type: ignore
        home.refresh()


class HomePage(ttk.Frame):
    def __init__(self, parent, app: App) -> None:
        super().__init__(parent)
        self.app = app
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        ttk.Label(self, text='Ouvidoria', font=('Segoe UI', 18, 'bold')).grid(row=0, column=0, pady=(20, 4))
        ttk.Label(self, text='Denúncias, elogios, reclamações e sugestões — em um só lugar.', foreground='#666').grid(row=1, column=0, pady=(0, 16))

        # Formulario
        form = ttk.LabelFrame(self, text='Novo envio')
        form.grid(row=2, column=0, sticky='ew', padx=16)
        for i in range(4):
            form.columnconfigure(i, weight=1)

        self.tipo_var = tk.StringVar(value='denúncia')
        ttk.Label(form, text='Tipo').grid(row=0, column=0, sticky='w', padx=8, pady=8)
        tipo_row = ttk.Frame(form)
        tipo_row.grid(row=0, column=1, columnspan=3, sticky='w')
        for label in ['denúncia', 'elogio', 'reclamação', 'sugestão']:
            ttk.Radiobutton(tipo_row, text=label.capitalize(), variable=self.tipo_var, value=label).pack(side='left', padx=6)

        self.aluno_var = tk.StringVar()
        self.turma_var = tk.StringVar()
        self.titulo_var = tk.StringVar()
        self.msg_text = tk.Text(form, height=6, wrap='word')

        ttk.Label(form, text='Nome do aluno').grid(row=1, column=0, sticky='w', padx=8, pady=4)
        ttk.Entry(form, textvariable=self.aluno_var).grid(row=1, column=1, sticky='ew', padx=8, pady=4)
        ttk.Label(form, text='Turma').grid(row=1, column=2, sticky='w', padx=8, pady=4)
        ttk.Entry(form, textvariable=self.turma_var).grid(row=1, column=3, sticky='ew', padx=8, pady=4)

        ttk.Label(form, text='Título').grid(row=2, column=0, sticky='w', padx=8, pady=4)
        ttk.Entry(form, textvariable=self.titulo_var).grid(row=2, column=1, columnspan=3, sticky='ew', padx=8, pady=4)

        ttk.Label(form, text='Mensagem').grid(row=3, column=0, sticky='nw', padx=8, pady=4)
        self.msg_text.grid(row=3, column=1, columnspan=3, sticky='ew', padx=8, pady=4)

        self.submit_btn = ttk.Button(form, text='Enviar', command=self.on_submit)
        self.submit_btn.grid(row=4, column=3, sticky='e', padx=8, pady=12)

        # List
        self.list_frame = ttk.LabelFrame(self, text='Meus envios')
        self.list_frame.grid(row=3, column=0, sticky='nsew', padx=16, pady=12)
        self.list_frame.columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(self.list_frame, columns=('tipo', 'titulo', 'data'), show='headings', height=10)
        self.tree.heading('tipo', text='Tipo')
        self.tree.heading('titulo', text='Título')
        self.tree.heading('data', text='Data')
        self.tree.column('tipo', width=120)
        self.tree.column('titulo', width=480)
        self.tree.column('data', width=180)
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.list_frame.rowconfigure(0, weight=1)

        btns = ttk.Frame(self.list_frame)
        btns.grid(row=1, column=0, sticky='e', pady=8)
        ttk.Button(btns, text='Abrir', command=self.open_selected).pack(side='left', padx=4)
        ttk.Button(btns, text='Apagar', command=self.delete_selected).pack(side='left', padx=4)

        self.hint = ttk.Label(form, text='Faça login para enviar', foreground='#888')
        self.hint.grid(row=0, column=3, sticky='e', padx=8)

    def refresh(self) -> None:
        # Toggle form according to session
        logged = self.app.user is not None
        state = 'normal' if logged else 'disabled'
        for child in self.children_recursive(self):
            if isinstance(child, (ttk.Entry, ttk.Radiobutton, ttk.Button)) and child is not self.submit_btn:
                try:
                    child.configure(state=state)
                except tk.TclError:
                    pass
        try:
            self.msg_text.configure(state=state)
        except tk.TclError:
            pass
        self.submit_btn.configure(state='normal' if logged else 'disabled')
        if logged:
            self.hint.configure(text=f"Olá, {self.app.user['name']}")
        else:
            self.hint.configure(text='Faça login para enviar')

        # Populate list
        for i in self.tree.get_children():
            self.tree.delete(i)
        if logged:
            reports = storage.list_reports_by_user(self.app.user['id'])
            for r in reports:
                d = datetime.fromisoformat(r['createdAt']).strftime('%d/%m/%Y %H:%M')
                self.tree.insert('', 'end', iid=str(r['id']), values=(r['tipo'].upper(), r['titulo'], d))

    def children_recursive(self, widget):
        for child in widget.winfo_children():
            yield child
            yield from self.children_recursive(child)

    def on_submit(self) -> None:
        if not self.app.user:
            messagebox.showinfo('Ouvidoria', 'Faça login para enviar.')
            self.app.show_page('LoginPage')
            return
        titulo = self.titulo_var.get().strip()
        mensagem = self.msg_text.get('1.0', 'end').strip()
        if not titulo or not mensagem:
            messagebox.showwarning('Campos obrigatórios', 'Preencha título e mensagem.')
            return
        report = {
            'id': str(uuid.uuid4()),
            'userId': self.app.user['id'],
            'tipo': self.tipo_var.get(),
            'titulo': titulo,
            'mensagem': mensagem,
            'turma': self.turma_var.get().strip(),
            'alunoNome': self.aluno_var.get().strip(),
            'createdAt': datetime.now().isoformat(),
        }
        storage.save_report(report)
        self.titulo_var.set('')
        self.msg_text.delete('1.0', 'end')
        self.refresh()
        messagebox.showinfo('Ouvidoria', 'Enviado com sucesso!')

    def open_selected(self) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        report_id = sel[0]
        view: ViewPage = self.app.pages['ViewPage']  # type: ignore
        view.load_report(report_id)
        self.app.show_page('ViewPage')

    def delete_selected(self) -> None:
        if not self.app.user:
            return
        sel = self.tree.selection()
        if not sel:
            return
        report_id = sel[0]
        if messagebox.askyesno('Confirmar', 'Deseja apagar este manifesto?'):
            ok = storage.delete_report(self.app.user['id'], report_id)
            if ok:
                self.refresh()
                messagebox.showinfo('Ouvidoria', 'Apagado com sucesso')
            else:
                messagebox.showerror('Ouvidoria', 'Não foi possível apagar')


class LoginPage(ttk.Frame):
    def __init__(self, parent, app: App) -> None:
        super().__init__(parent)
        self.app = app
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text='Entrar', font=('Segoe UI', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(24, 12))
        ttk.Label(self, text='Email').grid(row=1, column=0, sticky='e', padx=6, pady=6)
        ttk.Label(self, text='Senha').grid(row=2, column=0, sticky='e', padx=6, pady=6)
        self.email_var = tk.StringVar()
        self.pass_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.email_var).grid(row=1, column=1, sticky='ew', padx=6, pady=6)
        ttk.Entry(self, textvariable=self.pass_var, show='*').grid(row=2, column=1, sticky='ew', padx=6, pady=6)
        ttk.Button(self, text='Entrar', command=self.on_login).grid(row=3, column=1, sticky='e', padx=6, pady=10)

    def on_login(self) -> None:
        email = self.email_var.get().strip()
        password = self.pass_var.get()
        user = storage.find_user_by_email(email)
        if not user or user.get('passwordHash') != password:
            messagebox.showerror('Erro', 'Credenciais inválidas')
            return
        self.app.login(user)
        self.app.show_page('HomePage')


class RegisterPage(ttk.Frame):
    def __init__(self, parent, app: App) -> None:
        super().__init__(parent)
        self.app = app
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text='Criar conta', font=('Segoe UI', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(24, 12))
        ttk.Label(self, text='Nome').grid(row=1, column=0, sticky='e', padx=6, pady=6)
        ttk.Label(self, text='Email').grid(row=2, column=0, sticky='e', padx=6, pady=6)
        ttk.Label(self, text='Senha').grid(row=3, column=0, sticky='e', padx=6, pady=6)
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.pass_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.name_var).grid(row=1, column=1, sticky='ew', padx=6, pady=6)
        ttk.Entry(self, textvariable=self.email_var).grid(row=2, column=1, sticky='ew', padx=6, pady=6)
        ttk.Entry(self, textvariable=self.pass_var, show='*').grid(row=3, column=1, sticky='ew', padx=6, pady=6)
        ttk.Button(self, text='Registrar', command=self.on_register).grid(row=4, column=1, sticky='e', padx=6, pady=10)

    def on_register(self) -> None:
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        password = self.pass_var.get()
        if not name or not email or not password:
            messagebox.showwarning('Campos obrigatórios', 'Preencha todos os campos.')
            return
        if storage.find_user_by_email(email):
            messagebox.showerror('Erro', 'Email já cadastrado')
            return
        user = {
            'id': str(uuid.uuid4()),
            'name': name,
            'email': email,
            'passwordHash': password,
        }
        storage.save_user(user)
        messagebox.showinfo('Conta criada', 'Conta criada! Agora faça login.')
        self.app.show_page('LoginPage')


class ViewPage(ttk.Frame):
    def __init__(self, parent, app: App) -> None:
        super().__init__(parent)
        self.app = app
        self.columnconfigure(0, weight=1)
        ttk.Button(self, text='← Voltar', command=lambda: app.show_page('HomePage')).grid(row=0, column=0, sticky='w', padx=12, pady=12)
        self.tipo = ttk.Label(self, text='TIPO', font=('Segoe UI', 10, 'bold'))
        self.tipo.grid(row=1, column=0, sticky='w', padx=12)
        self.subject = ttk.Label(self, text='Assunto', font=('Segoe UI', 16, 'bold'))
        self.subject.grid(row=2, column=0, sticky='w', padx=12, pady=(4, 0))
        self.meta = ttk.Label(self, text='Para: você — Data', foreground='#777')
        self.meta.grid(row=3, column=0, sticky='w', padx=12, pady=(0, 8))
        self.extra = ttk.Label(self, text='Aluno: — | Turma: —', foreground='#777')
        self.extra.grid(row=4, column=0, sticky='w', padx=12, pady=(0, 8))
        self.body = tk.Text(self, height=16, wrap='word')
        self.body.grid(row=5, column=0, sticky='nsew', padx=12, pady=(0, 8))
        self.body.configure(state='disabled')
        self.rowconfigure(5, weight=1)
        ttk.Button(self, text='Apagar manifesto', command=self.delete_current).grid(row=6, column=0, sticky='e', padx=12, pady=12)
        self.current_id: Optional[str] = None

    def load_report(self, report_id: str) -> None:
        self.current_id = report_id
        if not self.app.user:
            return
        r = storage.get_report(self.app.user['id'], report_id)
        if not r:
            messagebox.showerror('Erro', 'Envio não encontrado ou sem permissão.')
            self.app.show_page('HomePage')
            return
        self.tipo.configure(text=r['tipo'].upper())
        self.subject.configure(text=r['titulo'])
        d = datetime.fromisoformat(r['createdAt']).strftime('%d/%m/%Y %H:%M')
        self.meta.configure(text=f'Para: você — {d}')
        self.extra.configure(text=f"Aluno: {r.get('alunoNome') or '—'} | Turma: {r.get('turma') or '—'}")
        self.body.configure(state='normal')
        self.body.delete('1.0', 'end')
        self.body.insert('1.0', r['mensagem'])
        self.body.configure(state='disabled')

    def delete_current(self) -> None:
        if not self.current_id or not self.app.user:
            return
        if messagebox.askyesno('Confirmar', 'Deseja apagar este manifesto?'):
            ok = storage.delete_report(self.app.user['id'], self.current_id)
            if ok:
                self.app.show_page('HomePage')
                self.app.refresh_home()
                messagebox.showinfo('Ouvidoria', 'Apagado com sucesso')
            else:
                messagebox.showerror('Ouvidoria', 'Não foi possível apagar')


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()


