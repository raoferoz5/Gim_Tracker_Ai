from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from datetime import datetime
import matplotlib.pyplot as plt
from report_generator import ReportGenerator
from database import Database
from calculations import Calculations
from ai_engine import AIEngine
from ml_predictor import MLPredictor
import numpy as np
from sklearn.linear_model import LinearRegression


class HomeScreen(Screen):
    pass


class AddWorkoutScreen(Screen):
    pass


class ViewProgressScreen(Screen):
    pass


class DashboardScreen(Screen):
    pass


class GymApp(MDApp):

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.accent_palette = "DeepPurple"

        self.db = Database()
        
        self.create_day_menu()

        #
    
    def go_home(self):   # 👈 ADD THIS
        self.root.ids.screen_manager.current = "home"

    def toggle_theme(self):
        if self.theme_cls.theme_style == "Dark":
            self.theme_cls.theme_style = "Light"
        else:
            self.theme_cls.theme_style = "Dark"
    # -------------------------
    # Dropdown Menu FIXED
    # -------------------------
    def create_day_menu(self):

        self.days = ["Chest", "Back", "Shoulders", "Biceps", "Triceps", "Legs"]

        self.menu = MDDropdownMenu(
            caller=None,
            items=[
                {
                    "text": day,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=day: self.set_day(x)
                }
                for day in self.days
            ],
            width_mult=4,
        )
    def export_pdf(self):

        exercise = self.root.get_screen("progress").ids.exercise_search.text
        data = self.db.get_exercise_data(exercise)

        if not data:
            Snackbar(text="No data to export").open()
            return

        ReportGenerator.generate_pdf(
            "progress_report.pdf",
            data
        )

        Snackbar(text="PDF Report Generated").open()
    def open_day_menu(self, button):
        """Attach menu to button before opening"""
        self.menu.caller = button
        self.menu.open()

    def set_day(self, day):
        # 1. Get the screen
        screen = self.root.ids.screen_manager.get_screen("add")
        
        # 2. Update the button text directly
        # This replaces "Select Day" with "Chest", "Back", etc.
        screen.ids.day_dropdown.text = day
        
        # 3. Close the menu
        self.menu.dismiss()

    # -------------------------
    # Save Workout
    # -------------------------
    
    def save_workout(self):
        screen = self.root.ids.screen_manager.get_screen("add")

        # This pulls the text ("Chest", "Back", etc.) from the button
        day = screen.ids.day_dropdown.text
        exercise = screen.ids.exercise.text
        weight = screen.ids.weight.text
        sets = screen.ids.sets.text
        reps = screen.ids.reps.text
        rest = screen.ids.rest.text

        # Basic Validation
        if day == "Select Day" or not all([exercise, weight, sets, reps]):
            Snackbar(text="Please select a day and fill all fields").open()
            return

        # ... (Your Volume and Database code remains the same) ...
        volume = Calculations.calculate_volume(float(weight), int(sets), int(reps))
        self.db.insert_workout((day, exercise, datetime.now().strftime("%Y-%m-%d"), 
                                float(weight), int(sets), int(reps), int(rest or 0), volume))

        # --- THE CLEANUP ---
        # This resets everything so the next entry is fresh
        screen.ids.day_dropdown.text = "Select Day"
        screen.ids.exercise.text = ""
        screen.ids.weight.text = ""
        screen.ids.sets.text = ""
        screen.ids.reps.text = ""
        screen.ids.rest.text = ""

        Snackbar(text="Workout Saved Successfully!").open()
    # -------------------------
    # Progress Graph + Stats
    # -------------------------

    def load_progress(self):

        screen = self.root.ids.screen_manager.get_screen("progress")
        exercise = screen.ids.exercise_search.text

        if not exercise:
            screen.ids.result.text = "Enter Exercise Name"
            return

        data = self.db.get_exercise_data(exercise)

        if not data:
            screen.ids.result.text = "No data found"
            return

        # Stats Calculation
        avg = Calculations.average_weight(data)
        total_vol = Calculations.total_volume(data)

        screen.ids.result.text = (
            f"Entries: {len(data)}\n"
            f"Average Weight: {round(avg,2)} kg\n"
            f"Total Volume: {round(total_vol,2)}"
        )

        # ------------------------
        # Graph Data
        # ------------------------
        # Graph Data
        dates = [datetime.strptime(d[0], "%Y-%m-%d") for d in data]
        weights = [d[1] for d in data]

        plt.figure(figsize=(10,5))

        plt.plot(dates, weights,
                marker="o",
                label="Weight Progress")

        plt.xlabel("Date")
        plt.ylabel("Weight (kg)")
        plt.title(f"{exercise} Date Wise Progress")

        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()

        # Real Performance Trend
        plt.plot(dates, weights,
                label="Weight Trend",
                linewidth=2)

        plt.plot(
            range(len(weights)),
            weights,
            linestyle="--",
            label="Performance Trend"
        )

        # ------------------------
        # ML Prediction Model
        # ------------------------

        if len(weights) >= 3:   # ML needs minimum data

            X = np.array(range(len(weights))).reshape(-1,1)
            y = np.array(weights)

            model = LinearRegression()
            model.fit(X, y)

            # Predict next value
            future_index = np.array([[len(weights)]])
            predicted_weight = model.predict(future_index)

            # Plot ML Prediction Point
            plt.scatter(
                len(weights),
                predicted_weight,
                label="🤖 ML Prediction",
                s=120
            )

            # Show prediction in UI
            screen.ids.result.text += \
                f"\n🤖 ML Predicted Next Weight: {round(float(predicted_weight[0]),2)} kg"

        else:
            screen.ids.result.text += "\n📉 Add more data for ML prediction"

        # Graph Labels
        plt.xlabel("Date")
        plt.ylabel("Weight (kg)")
        plt.title(f"{exercise} Progress Tracking")

        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()

        # AI Suggestion Logic
        self.show_ai_suggestion()
                # -------------------------
            # Dashboard
            # -------------------------
    def load_dashboard(self):

        total = self.db.get_total_workouts()

        exercise = "Chest"

        data = self.db.get_exercise_data(exercise)

        suggestion = AIEngine.suggest_next_weight(data)

        dashboard =self.root.ids.screen_manager.get_screen("dashboard")

        dashboard.ids.total_label.text = \
            f"Total Workouts Logged: {total}"

        dashboard.ids.ai_label.text = \
            f"AI Suggested Next Weight: {suggestion} kg"
    def load_history_list(self, exercise):

        list_widget = self.root.get_screen("progress").ids.history_list
        list_widget.clear_widgets()

        data = self.db.get_exercise_data(exercise)

        from kivymd.uix.list import OneLineListItem

        for row in data:
            # row = (date, weight, volume)
            list_widget.add_widget(
                OneLineListItem(
                    text=f"📅 {row[0]} | 💪 {exercise} | ⚖ {row[1]} kg | 📦 Vol {row[2]}"
                )
            )
    def monthly_comparison(self, exercise):

        feb = self.db.get_month_average(exercise, "02")
        mar = self.db.get_month_average(exercise, "03")

        if not feb or feb == 0 or not mar:
            Snackbar(text="Not enough data for comparison").open()
            return

        improvement = ((mar - feb) / feb) * 100

        Snackbar(
            text=f"Monthly Improvement: {round(improvement,2)}%"
        ).open()

    def show_ai_suggestion(self):

        screen = self.root.ids.screen_manager.get_screen("progress")
        exercise = screen.ids.exercise_search.text

        if not exercise:
            return

        data = self.db.get_exercise_data(exercise)

        if len(data) < 3:
            screen.ids.result.text += "\n📉 Not enough data for ML prediction"
            return

        prediction = MLPredictor.predict_next_weight(data)

        screen.ids.result.text += \
            f"\n🤖 ML Predicted Next Weight: {prediction} kg"  

if __name__ == "__main__":
    GymApp().run()