import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import date
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class FinanceManager:
    DATA_FILE = 'finance_data.json'

    def __init__(self, file_path=None):
        self.file_path = file_path or self.DATA_FILE
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    self.data = json.load(f)
                for key in ['incomes', 'expenses', 'budgets', 'goals']:
                    val = self.data.get(key, None)
                    if not isinstance(val, list):
                        self.data[key] = [val] if isinstance(val, dict) else []
            except Exception:
                self.data = {"incomes": [], "expenses": [], "budgets": [], "goals": []}
                self.save_data()
        else:
            self.data = {"incomes": [], "expenses": [], "budgets": [], "goals": []}
            self.save_data()

    def save_data(self):
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save data: {e}")

    def normalize_category(self, name):
        # Capitalize first letter, rest lower
        return name.strip().capitalize()
    
    def get_category_expense(self, category):
        return sum(e["amount"] for e in self.data.get("expenses", []) if e["category"] == category)

    def add_income(self, category, amount):
        entry = {"category": category, "amount": amount, "date": date.today().isoformat()}
        self.data['incomes'].append(entry)
        self.save_data()

    def add_expense(self, category, amount):
        entry = {"category": category, "amount": amount, "date": date.today().isoformat()}
        self.data['expenses'].append(entry)
        self.save_data()

    def add_budget(self, category, amount):
        entry = {"category": category, "amount": amount}
        self.data['budgets'].append(entry)
        self.save_data()

    def add_goal(self, name, amount):
        entry = {"name": name, "amount": amount}
        self.data['goals'].append(entry)
        self.save_data()

    def get_total_income(self):
        return sum(item.get("amount", 0) for item in self.data.get("incomes", []))

    def get_total_expense(self):
        return sum(item.get("amount", 0) for item in self.data.get("expenses", []))

    def get_available_funds(self):
        return self.get_total_income() - self.get_total_expense()

    def can_add_expense(self, amount):
        return amount <= self.get_available_funds()

    def categories(self):
        cats = set()
        for inc in self.data.get("incomes", []):
            cats.add(inc.get("category", ""))
        for exp in self.data.get("expenses", []):
            cats.add(exp.get("category", ""))
        return sorted(cats)

    def delete_goal(self, index):
        try:
            del self.data['goals'][index]
            self.save_data()
        except (IndexError, KeyError):
            pass

    def achieve_goal(self, index):
        try:
            goal = self.data['goals'][index]
            del self.data['goals'][index]
            self.save_data()
            return goal
        except (IndexError, KeyError):
            return None

    def achieve_all_goals(self):
        achieved_goals = list(self.data['goals'])
        self.data['goals'].clear()
        self.save_data()
        return achieved_goals

    def delete_all_goals(self):
        self.data['goals'].clear()
        self.save_data()

class FinanceFlowApp(tk.Tk):
    """Main application class managing frames and navigation."""
    def __init__(self):
        super().__init__()
        self.title("FinanceFlow")
        self.geometry("500x400")
        self.resizable(False, False)

        self.manager = FinanceManager()

        container = ttk.Frame(self)
        container.pack(fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainMenuFrame, IncomeFrame, ExpenseFrame, BudgetFrame,
                  GoalFrame, CategorySummaryFrame, SummaryFrame, PieChartFrame):
            frame = F(parent=container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(MainMenuFrame)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        if hasattr(frame, 'refresh'):
            frame.refresh()
        frame.tkraise()

class MainMenuFrame(ttk.Frame):
    """Main menu with buttons to access all features."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="FinanceFlow Main Menu", font=("Helvetica", 16))
        label.pack(pady=20)

        ttk.Button(self, text="Add Income", 
                   command=lambda: controller.show_frame(IncomeFrame)).pack(fill='x', padx=100, pady=5)
        ttk.Button(self, text="Add Expense", 
                   command=lambda: controller.show_frame(ExpenseFrame)).pack(fill='x', padx=100, pady=5)
        ttk.Button(self, text="Set Budget", 
                   command=lambda: controller.show_frame(BudgetFrame)).pack(fill='x', padx=100, pady=5)
        ttk.Button(self, text="Set Goal", 
                   command=lambda: controller.show_frame(GoalFrame)).pack(fill='x', padx=100, pady=5)
        ttk.Button(self, text="Category Summary", 
                   command=lambda: controller.show_frame(CategorySummaryFrame)).pack(fill='x', padx=100, pady=5)
        ttk.Button(self, text="Summary View", 
                   command=lambda: controller.show_frame(SummaryFrame)).pack(fill='x', padx=100, pady=5)
        ttk.Button(self, text="Pie Chart (Expenses)", 
                   command=lambda: controller.show_frame(PieChartFrame)).pack(fill='x', padx=100, pady=5)
        ttk.Button(self, text="Quit", command=controller.destroy).pack(fill='x', padx=100, pady=20)

class IncomeFrame(ttk.Frame):
    """Frame for adding an income (category + amount)."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Add Income", font=("Helvetica", 14)).pack(pady=10)
        form = ttk.Frame(self)
        form.pack(pady=10)

        ttk.Label(form, text="Category:").grid(row=0, column=0, sticky='e')
        self.entry_cat = ttk.Entry(form)
        self.entry_cat.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(form, text="Amount:").grid(row=1, column=0, sticky='e')
        self.entry_amt = ttk.Entry(form)
        self.entry_amt.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self, text="Add", command=self.add_income).pack(pady=5)
        ttk.Button(self, text="Back to Main Menu", 
                   command=lambda: controller.show_frame(MainMenuFrame)).pack(pady=5)

    def add_income(self):
        cat = self.entry_cat.get().strip()
        amt_str = self.entry_amt.get().strip()
        if not cat:
            messagebox.showerror("Input Error", "Category cannot be empty.")
            return
        try:
            amt = float(amt_str)
            if amt <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Enter a valid positive number for amount.")
            return

        self.controller.manager.add_income(cat, amt)
        messagebox.showinfo("Success", f"Income of RM{amt:.2f} added under '{cat}'.")
        self.entry_cat.delete(0, tk.END)
        self.entry_amt.delete(0, tk.END)
        self.controller.show_frame(MainMenuFrame)

class ExpenseFrame(ttk.Frame):
    """Frame for adding an expense (category + amount). Blocks overspending."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Add Expense", font=("Helvetica", 14)).pack(pady=10)
        form = ttk.Frame(self)
        form.pack(pady=10)

        ttk.Label(form, text="Category:").grid(row=0, column=0, sticky='e')
        self.entry_cat = ttk.Entry(form)
        self.entry_cat.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(form, text="Amount:").grid(row=1, column=0, sticky='e')
        self.entry_amt = ttk.Entry(form)
        self.entry_amt.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self, text="Add", command=self.add_expense).pack(pady=5)
        ttk.Button(self, text="Back to Main Menu", 
                   command=lambda: controller.show_frame(MainMenuFrame)).pack(pady=5)

    def add_expense(self):
        cat = self.entry_cat.get().strip()
        amt_str = self.entry_amt.get().strip()
        if not cat:
            messagebox.showerror("Input Error", "Category cannot be empty.")
            return
        try:
            amt = float(amt_str)
            if amt <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Enter a valid positive number for amount.")
            return

        # Normalize category for budget check
        norm_cat = self.controller.manager.normalize_category(cat)

        if not self.controller.manager.can_add_expense(amt):
            messagebox.showerror(
                "Insufficient Funds",
                "You don’t have enough money in your account for this expense."
            )
            return

        budgets = self.controller.manager.data.get("budgets", [])
        budget_amt = next((b["amount"] for b in budgets if self.controller.manager.normalize_category(b["category"]) == norm_cat), 0)
        if budget_amt > 0:
            current_spent = self.controller.manager.get_category_expense(norm_cat)
            if current_spent + amt > budget_amt:
                messagebox.showerror(
                    "Budget Exceeded",
                    f"Adding RM{amt:.2f} to '{norm_cat}' exceeds its budget of RM{budget_amt:.2f}."
                )
                return

        self.controller.manager.add_expense(cat, amt)
        messagebox.showinfo("Success", f"Expense of RM{amt:.2f} added under '{norm_cat}'.")
        self.entry_cat.delete(0, tk.END)
        self.entry_amt.delete(0, tk.END)
        self.controller.show_frame(MainMenuFrame)

class BudgetFrame(ttk.Frame):
    """Frame for setting a budget (category + amount). Warns if exceeding funds."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Set Budget", font=("Helvetica", 14)).pack(pady=10)
        form = ttk.Frame(self)
        form.pack(pady=10)

        ttk.Label(form, text="Category:").grid(row=0, column=0, sticky='e')
        self.entry_cat = ttk.Entry(form)
        self.entry_cat.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(form, text="Amount:").grid(row=1, column=0, sticky='e')
        self.entry_amt = ttk.Entry(form)
        self.entry_amt.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self, text="Set Budget", command=self.set_budget).pack(pady=5)
        ttk.Button(self, text="Back to Main Menu", 
                   command=lambda: controller.show_frame(MainMenuFrame)).pack(pady=5)

    def set_budget(self):
        cat = self.entry_cat.get().strip()
        amt_str = self.entry_amt.get().strip()
        if not cat:
            messagebox.showerror("Input Error", "Category cannot be empty.")
            return
        try:
            amt = float(amt_str)
            if amt <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Enter a valid positive number for amount.")
            return

        self.controller.manager.add_budget(cat, amt)
        messagebox.showinfo("Success", f"Budget of RM{amt:.2f} set for '{cat}'.")
        self.entry_cat.delete(0, tk.END)
        self.entry_amt.delete(0, tk.END)
        self.controller.show_frame(MainMenuFrame)

class GoalFrame(ttk.Frame):
    """Frame for setting a savings goal (name + amount). Blocks goals exceeding funds."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Set Goal", font=("Helvetica", 14)).pack(pady=10)
        form = ttk.Frame(self)
        form.pack(pady=10)

        ttk.Label(form, text="Goal Name:").grid(row=0, column=0, sticky='e')
        self.entry_name = ttk.Entry(form)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(form, text="Amount:").grid(row=1, column=0, sticky='e')
        self.entry_amt = ttk.Entry(form)
        self.entry_amt.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self, text="Set Goal", command=self.set_goal).pack(pady=5)
        ttk.Button(self, text="Back to Main Menu", 
                   command=lambda: controller.show_frame(MainMenuFrame)).pack(pady=5)

    def set_goal(self):
        name = self.entry_name.get().strip()
        amt_str = self.entry_amt.get().strip()
        if not name:
            messagebox.showerror("Input Error", "Goal name cannot be empty.")
            return
        try:
            amt = float(amt_str)
            if amt <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Enter a valid positive number for amount.")
            return

        self.controller.manager.add_goal(name, amt)
        messagebox.showinfo("Success", f"Goal '{name}' set for amount RM{amt:.2f}.")
        self.entry_name.delete(0, tk.END)
        self.entry_amt.delete(0, tk.END)
        self.controller.show_frame(MainMenuFrame)

class CategorySummaryFrame(ttk.Frame):
    """Frame displaying a table of total income and expense per category, with a clear button and latest date."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Category Summary", font=("Helvetica", 14)).pack(pady=10)
        columns = ("category", "income", "expense", "latest_date")
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.heading("category", text="Category")
        self.tree.heading("income", text="Income")
        self.tree.heading("expense", text="Expense")
        self.tree.heading("latest_date", text="Latest Date")
        self.tree.column("category", width=120, anchor="w")
        self.tree.column("income", width=80, anchor="center")
        self.tree.column("expense", width=80, anchor="center")
        self.tree.column("latest_date", width=120, anchor="center")
        self.tree.pack(padx=10, pady=10, fill='both', expand=True)

        ttk.Button(self, text="Clear Transactions", command=self.clear_transactions).pack(pady=5)
        ttk.Button(self, text="Back to Main Menu", 
                   command=lambda: controller.show_frame(MainMenuFrame)).pack(pady=5)

    def refresh(self):
        """Refresh the category summary table, including latest transaction date."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        cats = self.controller.manager.categories()
        for cat in cats:
            inc_total = sum(item["amount"] 
                            for item in self.controller.manager.data["incomes"] if item["category"] == cat)
            exp_total = sum(item["amount"] 
                            for item in self.controller.manager.data["expenses"] if item["category"] == cat)
            # Find latest date for this category
            dates = []
            for item in self.controller.manager.data["incomes"]:
                if item["category"] == cat and "date" in item:
                    dates.append(item["date"])
            for item in self.controller.manager.data["expenses"]:
                if item["category"] == cat and "date" in item:
                    dates.append(item["date"])
            latest_date = max(dates) if dates else "-"
            self.tree.insert("", "end", values=(cat, f"RM {inc_total:.2f}", f"{exp_total:.2f}", latest_date))

    def clear_transactions(self):
        """Clear all incomes and expenses after confirmation."""
        if messagebox.askyesno("Confirm", "Clear ALL incomes and expenses?"):
            self.controller.manager.data['incomes'] = []
            self.controller.manager.data['expenses'] = []
            self.controller.manager.save_data()
            self.refresh()
            messagebox.showinfo("Cleared", "All incomes and expenses have been cleared.")
    
class SummaryFrame(ttk.Frame):
    """Frame showing overall income, expenses, balance, and budget/goal stats."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Financial Summary", font=("Helvetica", 14)).pack(pady=10)
        self.summary_text = tk.Text(self, width=50, height=10, state='disabled')
        self.summary_text.pack(padx=10, pady=10)

        # Frame for goals and their buttons
        self.goals_frame = tk.LabelFrame(self, text="Goals")
        self.goals_frame.pack(fill="x", pady=10)

        # Frame for Achieve All / Delete All buttons
        self.all_goals_btn_frame = tk.Frame(self)
        self.all_goals_btn_frame.pack(fill="x", pady=(0,10))
        # Delete Budgets button
        ttk.Button(self, text="Delete Budgets", command=self.delete_budgets).pack(pady=5)
        # Back to Main Menu button at the bottom
        ttk.Button(self, text="Back to Main Menu", 
                   command=lambda: controller.show_frame(MainMenuFrame)).pack(pady=5)
        self.update_goals_display()

    def refresh(self):
        """Update the summary text with current totals."""
        total_income = self.controller.manager.get_total_income()
        total_expense = self.controller.manager.get_total_expense()
        balance = self.controller.manager.get_available_funds()
        budgets = self.controller.manager.data.get("budgets", [])
        raw_goals = self.controller.manager.data.get("goals", [])
        valid_goals = [
            g for g in raw_goals
            if isinstance(g, dict)
                and "amount" in g
                and isinstance(g["amount"], (int, float))
        ]
        lines = [
            f"Total Income:   RM {total_income:.2f}",
            f"Total Expenses: RM {total_expense:.2f}",
            f"Current Balance: RM {balance:.2f}",
            ""
        ]
        if budgets:
            total_bud = sum(item["amount"] for item in budgets)
            lines.append(f"Budgets Set: {len(budgets)}, Total Budget: {total_bud:.2f}")
        if valid_goals:
            total_goal = sum(g["amount"] for g in valid_goals)
            lines.append(f"Goals Set: {len(valid_goals)}, Total Goal Amount: {total_goal:.2f}")

        content = "\n".join(lines)
        self.summary_text.configure(state='normal')
        self.summary_text.delete('1.0', tk.END)
        self.summary_text.insert(tk.END, content)
        self.summary_text.configure(state='disabled')
        self.update_goals_display()
    
    def update_goals_display(self):
        """Show all unachieved goals with Achieve/Delete buttons, and all-goals controls."""
        for widget in self.goals_frame.winfo_children():
            widget.destroy()
        for widget in self.all_goals_btn_frame.winfo_children():
            widget.destroy()

        goals = self.controller.manager.data.get('goals', [])
        for idx, goal in enumerate(goals):
            goal_name = goal.get('name') if isinstance(goal, dict) and 'name' in goal else str(goal)
            goal_amt = goal.get('amount') if isinstance(goal, dict) and 'amount' in goal else ""
            row_frame = tk.Frame(self.goals_frame)
            row_frame.pack(fill="x", padx=5, pady=2)
            tk.Label(row_frame, text=f"{goal_name}  RM{goal_amt:.2f}", anchor="w", width=30).pack(side="left")
            tk.Button(row_frame, text="Achieve", width=8,
                      command=lambda i=idx: self.achieve_goal(i)).pack(side="left", padx=5)
            tk.Button(row_frame, text="Delete", width=8,
                      command=lambda i=idx: self.delete_goal(i)).pack(side="left", padx=5)

        if goals:
            tk.Button(self.all_goals_btn_frame, text="Achieve All", width=12,
                      command=self.achieve_all_goals).pack(side="left", padx=5)
            tk.Button(self.all_goals_btn_frame, text="Delete All", width=12,
                      command=self.delete_all_goals).pack(side="left", padx=5)

    def delete_budgets(self):
        """Delete all budgets after confirmation."""
        if messagebox.askyesno("Confirm", "Delete ALL budgets?"):
            self.controller.manager.data['budgets'] = []
            self.controller.manager.save_data()
            messagebox.showinfo("Deleted", "All budgets have been deleted.")
            self.refresh()

    def achieve_goal(self, idx):
        goals = self.controller.manager.data.get('goals', [])
        if idx < 0 or idx >= len(goals):
            return
        goal = goals[idx]
        goal_name = goal.get('name') if isinstance(goal, dict) and 'name' in goal else str(goal)
        goal_amt = goal.get('amount') if isinstance(goal, dict) and 'amount' in goal else 0
        balance = self.controller.manager.get_available_funds()
        if goal_amt > balance:
            messagebox.showwarning("Insufficient Balance", f"Your balance is not enough to achieve the goal '{goal_name}'.")
            return
        # Remove goal and add to expenses as "Goal (Goal Name)"
        self.controller.manager.delete_goal(idx)
        expense_category = f'Goal ("{goal_name}")'
        self.controller.manager.add_expense(expense_category, goal_amt)
        self.update_goals_display()
        messagebox.showinfo("Goal Achieved", f"You have achieved the goal: {goal_name} (RM{goal_amt:.2f})")

    def delete_goal(self, idx):
        self.controller.manager.delete_goal(idx)
        self.update_goals_display()

    def achieve_all_goals(self):
        goals = list(self.controller.manager.data.get('goals', []))  # Copy to avoid modification during iteration
        balance = self.controller.manager.get_available_funds()
        achieved = []
        not_achieved = []
        for idx, goal in enumerate(goals):
            goal_name = goal.get('name') if isinstance(goal, dict) and 'name' in goal else str(goal)
            goal_amt = goal.get('amount') if isinstance(goal, dict) and 'amount' in goal else 0
            if goal_amt <= balance:
                # Remove goal and add to expenses as "Goal (Goal Name)"
                self.controller.manager.delete_goal(0)  # Always delete first since list shrinks
                self.controller.manager.add_expense(f'Goal ("{goal_name}")', goal_amt)
                balance -= goal_amt
                achieved.append(goal_name)
            else:
                not_achieved.append(goal_name)
        self.update_goals_display()
        if achieved:
            messagebox.showinfo("Goals Achieved", f"Achieved goals: {', '.join(achieved)}")
        if not_achieved:
            messagebox.showwarning("Not Enough Balance", f"Could not achieve: {', '.join(not_achieved)} (not enough balance)")

    def delete_all_goals(self):
        self.controller.manager.delete_all_goals()
        self.update_goals_display()

class PieChartFrame(ttk.Frame):
    """Frame embedding a Matplotlib pie chart of expenses by category."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Expenses by Category", font=("Helvetica", 14)).pack(pady=10)
        self.figure = Figure(figsize=(5,4), dpi=80)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        ttk.Button(self, text="Back to Main Menu", 
                   command=lambda: controller.show_frame(MainMenuFrame)).pack(pady=5)

    def refresh(self):
        """Redraw the pie chart with current expense data."""
        self.ax.clear()
        data = self.controller.manager.data.get("expenses", [])
        cat_sums = {}
        for item in data:
            cat = item["category"]
            amt = item["amount"]
            cat_sums[cat] = cat_sums.get(cat, 0) + amt
        categories = list(cat_sums.keys())
        amounts = list(cat_sums.values())
        if categories and amounts:
            self.ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
            self.ax.axis('equal')  # keep chart circular
        else:
            self.ax.text(0.5, 0.5, "No expenses to display", 
                         horizontalalignment='center', verticalalignment='center')
        self.canvas.draw()

if __name__ == "__main__":
    app = FinanceFlowApp()
    app.mainloop()