import automator
import tkinter_tools as tkTools
from pynput.keyboard import Key


class Root(tkTools.MainWindow):
    def __init__(self):
        super().__init__(title="Screen capture tools",
                         window_size=(360, 360),
                         min_size=(360, 360),
                         max_size=(720, 760),
                         position=(0, 0)
                         )
        self.frame = None
        self.stop_key = Key.esc
        self.grid_setup()
        self.widgets()
        self.HomeFrame = HomeFrame(self)
        self.HomeFrame.grid()
        self.mainloop()

    def grid_setup(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def widgets(self):
        self.frame = tkTools.Frame(self)
        self.frame.grid_configure(row=0, column=0, sticky="NSEW")
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)


# home frame
class HomeFrame(tkTools.Frame):
    def __init__(self, root):
        super().__init__(root.frame)
        self.root = root
        self.log_list = automator.get_automation_logs()
        self.repeat_options = True
        self.repeat_options_frame = RepeatOptionsFrame(self, self.root)
        self.grid_configure(row=0, column=0, sticky="NSEW")
        self.grid_setup()
        self.widgets()

    def grid_setup(self):
        self.grid_rowconfigure(0, weight=1, minsize=100)
        self.grid_rowconfigure(1, minsize=36)
        self.grid_rowconfigure(2)
        self.grid_rowconfigure(3, weight=1, minsize=40)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1, minsize=40)
        self.grid_columnconfigure(0, weight=1, minsize=40)
        self.grid_columnconfigure(1, weight=1, minsize=100)
        self.grid_columnconfigure(2, weight=1, minsize=100)
        self.grid_columnconfigure(3, weight=1, minsize=40)
        self.grid_remove()

    def widgets(self):
        def set_log_dropdown_value():
            self.log_list = automator.get_automation_logs()
            log_dropdown.configure(values=self.log_list)
            if not self.log_list:
                log_dropdown.delete(first=0, last="end")
                log_dropdown.configure(foreground="gray")
                log_dropdown.insert(0, "No logs found")
                no_logs_label.grid_configure(row=2, column=1, columnspan=2, sticky="NW")
            else:
                no_logs_label.grid_remove()
                log_dropdown.configure(foreground="black")
                log_dropdown.current(0)

        def run_automator_decor(func):
            def wrapper():
                if not self.log_list:
                    log_output_textbox.output("There are no logs to automate.")
                    log_output_textbox.see("end")
                    return
                automate_button.configure(state="disabled")
                record_button.configure(state="disabled")
                log = log_dropdown.get()
                log_dropdown.configure(state="disabled")
                log_output_textbox.output('Starting "' + log + '"...'),
                log_output_textbox.see("end"),
                self.root.iconify()
                func(log)
                self.root.deiconify()
                log_output_textbox.output('Finished running "' + log + '"\n')
                log_output_textbox.see("end"),
                log_dropdown.configure(state="normal")
                record_button.configure(state="normal")
                automate_button.configure(state="normal")
            return wrapper

        @run_automator_decor
        def run_automator(log):
            automator.run_automator(log + ".log", repeat_num=self.repeat_options_frame.repeat_times),

        def run_recorder_decor(func):
            def wrapper():
                name = "log"
                record_button.configure(state="disabled")
                automate_button.configure(state="disabled")
                log_output_textbox.output("Recording started.")
                log_output_textbox.see("end"),
                self.root.iconify()
                func(name)
                self.root.deiconify()
                log_output_textbox.output("Recording saved.")
                log_output_textbox.see("end"),
                Editor(self.root, self, name)
                log_dropdown.configure(state="normal")
                set_log_dropdown_value()
                automate_button.configure(state="normal")
                record_button.configure(state="normal")
            return wrapper

        @run_recorder_decor
        def run_recorder(name):
            automator.start_recording(name),

        def open_log_deletion_window():
            if not self.log_list:
                log_output_textbox.output("There are no logs to delete.")
                log_output_textbox.see("end")
                return
            log_deletion_window = tkTools.SubWindow(self, title="Log deletion", window_size=(360, 180), min_size=(360, 180))
            log_deletion_window.grid_rowconfigure(0, weight=1)
            log_deletion_window.grid_rowconfigure(1, minsize=72)
            log_deletion_window.grid_rowconfigure(2, weight=4)
            log_deletion_window.grid_columnconfigure(0, weight=1)
            log_deletion_window.grid_columnconfigure(1, minsize=20)
            log_deletion_window.grid_columnconfigure(2, weight=1)
            log_deletion_text = "Are you sure you want to delete:"
            log_deletion_label = tkTools.Label(log_deletion_window, display_text=log_deletion_text)
            log_deletion_label.grid_configure(row=0, column=0, columnspan=3, sticky="S")
            log_label = tkTools.Label(log_deletion_window, display_text=log_dropdown.get(), font="Consolas", backdrop="ridge")
            log_label.configure(padding=4)
            log_label.grid_configure(row=1, column=0, columnspan=3)
            log_deletion_confirm_button = tkTools.Button(log_deletion_window, display_text="Delete",
                                                         function_when_clicked=lambda: [
                                                             delete_log(log_dropdown.get()),
                                                             log_deletion_window.destroy(),
                                                             log_deletion_window.update()
                                                         ])
            log_deletion_confirm_button.grid_configure(row=2, column=0, sticky="NE")
            log_deletion_cancel_button = tkTools.Button(log_deletion_window, display_text="Cancel",
                                                        function_when_clicked=lambda: [
                                                            log_deletion_window.destroy(),
                                                            log_deletion_window.update()
                                                        ])
            log_deletion_cancel_button.grid_configure(row=2, column=2, sticky="NW")

        def delete_log(log):
            automator.delete_log(log)
            log_output_textbox.output("Deleted: " + log)
            set_log_dropdown_value()

        # first initialize the log-fetching widgets so that they can be referenced with other buttons
        welcome_msg = ("Hi!\n"
                       "This tool can be used to automate mouse clicks and key presses.\n"
                       "To do so, start by clicking the button on the top right. Once clicked, the program will "
                       "begin to record your mouse clicks and key presses. Use the ESC key to stop the recording.\n"
                       "To run a recording, click the button on the top left. The ESC key will stop the playback.\n\n")
        log_dropdown = tkTools.Combobox(self, values=self.log_list, font=("Consolas", 10))
        no_logs_label = tkTools.Label(self, display_text="No logs found", text_color="red", text_alignment="left")
        set_log_dropdown_value()
        log_dropdown.grid_configure(row=1, column=1, columnspan=2, sticky="NEW")
        log_deletion_button = tkTools.Button(self, display_text="delete", function_when_clicked=open_log_deletion_window)
        log_deletion_button.grid_configure(row=3, column=2, sticky="E")
        log_output_textbox = tkTools.Text(self, wrap_on="word", state="disabled", text=welcome_msg)
        log_output_textbox.grid_configure(row=4, column=1, columnspan=2, sticky="NSEW")
        log_dropdown.bind("<FocusIn>", lambda e: set_log_dropdown_value())

        # more widgets
        automate_button = tkTools.Button(self, display_text="Play", function_when_clicked=run_automator)
        automate_button.grid_configure(row=0, column=1)
        record_button = tkTools.Button(self, display_text="Rec.", function_when_clicked=run_recorder)
        record_button.grid_configure(row=0, column=2, sticky="E")
        settings_button = tkTools.Button(self, display_text="Settings")
        settings_button.grid_configure(row=5, column=2, sticky="SE")
        if self.repeat_options:
            self.repeat_options_frame.grid_configure(row=2, column=1, columnspan=2, sticky="NSEW")


# Frame with options for repeating automations
class RepeatOptionsFrame(tkTools.Frame):
    def __init__(self, parent, root):
        super().__init__(parent)
        self.root = root
        self.parent = parent
        self.repeat_times = 1
        self.grid_setup()
        self.widgets()

    def grid_setup(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_remove()

    def widgets(self):
        def isdigit_callback(value):
            if str.isdigit(value) or value == "":
                return True
            return False

        def set_repeat_times():
            if nTimes_entry.get() == "":
                nTimes_entry.insert(0, "1")
            self.repeat_times = int(nTimes_entry.get())

        isdigit_cmd = self.register(isdigit_callback)

        nTimes_frame = tkTools.Frame(self)
        nTimes_frame.grid_configure(row=0, column=0, sticky="NSEW")
        nTimes_label1 = tkTools.Label(nTimes_frame, display_text="Repeat ")
        nTimes_label2 = tkTools.Label(nTimes_frame, display_text=" times")
        nTimes_entry = tkTools.Entry(nTimes_frame, width=4, validate_on="key", function_for_testing_validation=(isdigit_cmd, "%P"))
        nTimes_entry.insert(0, "1")
        nTimes_entry.bind("<FocusOut>", lambda e: set_repeat_times())
        nTimes_label1.pack_configure(side="left")
        nTimes_entry.pack_configure(side="left")
        nTimes_label2.pack_configure(side="left")


class Editor(tkTools.SubWindow):
    def __init__(self, root, parent, log):
        super().__init__(parent,
                         title="Editor",
                         window_size=(360, 120),
                         position=(root.winfo_x(), root.winfo_y())
                         )
        self.root = root
        self.parent = parent
        self.log_name = log
        self.grid_setup()
        self.widgets()

    def grid_setup(self):
        self.grid_rowconfigure(0)
        self.grid_rowconfigure(1)
        self.grid_columnconfigure(0)
        self.grid_columnconfigure(1)

    def widgets(self):
        name_label = tkTools.Label(self, display_text="Filename: ")
        name_label.grid_configure(row=0, column=0, sticky="NW")
        name_entry = tkTools.Entry(self)
        name_entry.insert(0, self.log_name)
        name_entry.grid_configure(row=0, column=1, sticky="NW")
        save_button = tkTools.Button(self, display_text="Save",
                                     function_when_clicked=lambda: [
                                         automator.rename_log(self.log_name, name_entry.get()),
                                         self.destroy(),
                                         self.update()
                                     ])
        save_button.grid_configure(row=1, column=1)


Root()
