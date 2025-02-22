import tkinter as tk
from tkinter import messagebox
import socket
from client import Client
import time
from collections import defaultdict

DEFAULT_TITLE = "Waiting for connection"
MOVE_LEFT_COMMAND = "motors_manager.move_side(-255)"
MOVE_RIGHT_COMMAND = "motors_manager.move_side(255)"
MOVE_FORWARDS_COMMAND = "motors_manager.move_straight(255)"
MOVE_BACKWARDS_COMMAND = "motors_manager.move_straight(-255)"

class ControllerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("600x100")
        self.title(DEFAULT_TITLE)

        self.is_current_triggred = tk.BooleanVar()

        self.ip_frame = tk.Frame(self)
        self.ip_frame.pack()
        self.add_ip_frame()

        self.control_frame = tk.Frame(self)
        # self.control_frame.pack()
        self.add_control_frame()

        self.table_frame = tk.Frame(self)

        self.commands = defaultdict(str) # {id: command_str}
        self.last_untriggred_id = None
        self.client = None
    
    def add_ip_frame(self):
        self.ip_label = tk.Label(self.ip_frame, text="Enter IP")
        self.ip_label.pack()
        self.ip_entry = tk.Entry(self.ip_frame)
        self.ip_entry.pack()
        self.connect_button = tk.Button(self.ip_frame, text="Connect!", command=self.connect)
        self.connect_button.pack(pady=10)

    def add_control_frame(self):
        self.command_label = tk.Label(self.control_frame, text="Enter command")
        self.command_label.grid(row=0, column=0)

        self.command_entry = tk.Entry(self.control_frame)
        self.command_entry.grid()

        self.toggle_label = tk.Label(self.control_frame, text="Toggle")
        self.toggle_label.grid(row=0, column=1)
        
        self.toggle_checkbutton = tk.Checkbutton(self.control_frame, variable=self.is_current_triggred)
        self.toggle_checkbutton.grid(row=1, column=1)

        self.eval_button = tk.Button(self.control_frame, text="Evaluate!", command=self.add_command)
        self.eval_button.grid(pady=10)

        self.left_button = tk.Button(
            self.control_frame, 
            text="Left", 
            command=lambda: self.add_command(MOVE_LEFT_COMMAND, False)
        )
        self.left_button.grid(row=1, column=2)

        self.right_button = tk.Button(
            self.control_frame, 
            text="Right",
            command=lambda: self.add_command(MOVE_RIGHT_COMMAND, False)
        )
        self.right_button.grid(row=1, column=4)

        self.forwards_button = tk.Button(
            self.control_frame, 
            text="Forward",
            command=lambda: self.add_command(MOVE_FORWARDS_COMMAND, False)
        )
        self.forwards_button.grid(row=0, column=3)

        self.backward_button = tk.Button(
            self.control_frame, 
            text="Backward",
            command=lambda: self.add_command(MOVE_BACKWARDS_COMMAND, False)
        )
        self.backward_button.grid(row=2, column=3)


    def update_data_table(self):
        for widget in self.table_frame.winfo_children():
            if widget == self.untriggred_data_label:
                continue
            widget.destroy()
        
        if str(self.last_untriggred_id) in self.client.commands_data:
            self.untriggred_data_label = tk.Label(
                self.table_frame, 
                text=f"Value: {self.client.commands_data[str(self.last_untriggred_id)]}"
            )
            self.untriggred_data_label.grid(row=0, column=0)

        for row, (key, value) in enumerate(self.client.commands_data.items()):
            command_id = int(key)
            if command_id == self.last_untriggred_id:
                continue
            command = self.commands[command_id]
            remove_button = tk.Button(
                self.table_frame, 
                text="X", 
                command=lambda: self.client.remove_command(command_id)
            )
            remove_button.grid(row=row + 1, column=0)

            command_label = tk.Label(self.table_frame, text=command)
            command_label.grid(row=row + 1, column=1)

            value_label = tk.Label(self.table_frame, text=value)
            value_label.grid(row=row + 1, column=2)
        
        self.after(100, self.update_data_table)

    def add_command(self, command: str = None, is_triggred: bool = None):
        if not command:
            command = self.command_entry.get()
            is_triggred = self.is_current_triggred.get()

        command_id = self.client.send_command(command, is_triggred)
        if is_triggred:
            self.commands[command_id] = command
        else:
            self.last_untriggred_id = command_id

    def remove_command(self, command_id: int):
        self.client.remvoe_command(command_id)

    def connect(self):
        try:
            address = self.ip_entry.get().split(":")
            address[1] = int(address[1])
            self.client = Client(address[0], address[1])
            self.client.start()
            time.sleep(3)
            if self.client.connection_error:
                raise
        except:
            self.client = None
            messagebox.showerror("Error", "Error while trying to connect to the robot")
            return
        self.ip_frame.pack_forget()
        self.geometry("600x600")
        self.title("Connected")
        self.control_frame.pack()
        self.table_frame.pack(pady=20)
        self.update_data_table()

    def on_closing(self):
        if self.client:
            self.client.running = False
            self.client.join()
        self.destroy()


def main():
    app = ControllerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()