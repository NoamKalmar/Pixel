import tkinter as tk
from tkinter import messagebox
import socket
from client import Client, IPFinder
import time
from collections import defaultdict

WIDTH = 600
HEIGHT = 300

GREEN = "#00ff1a"
RED = "#ff1100"

DEFAULT_TITLE = "Waiting for connection"
MOVE_LEFT_COMMAND = "motors_manager.move_x(-255)"
MOVE_RIGHT_COMMAND = "motors_manager.move_x(255)"
MOVE_FORWARD_COMMAND = "motors_manager.move_y(255)"
MOVE_BACKWARD_COMMAND = "motors_manager.move_y(-255)"
TURN_LEFT_COMMAND = "motors_manager.turn(-175)"
TURN_RIGHT_COMMAND = "motors_manager.turn(175)"
STOP_MOVING_COMMAND = "motors_manager.stop_moving()"

LOCALHOST_SERVER_ADDRESS = "127.0.0.1:1989"
BROADCAST_PORT = 1990

class ControllerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.title(DEFAULT_TITLE)

        self.is_current_triggred = tk.BooleanVar()
        self.is_arrows_moving_mode = False
        self.current_move_command = None

        self.ip_frame = tk.Frame(self)
        self.ip_frame.pack()
        self.add_ip_frame()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.control_frame = tk.Frame(self)
        # self.control_frame.pack()
        self.add_control_frame()

        self.table_frame = tk.Frame(self)

        self.commands = defaultdict(str) # {id: command_str}
        self.untriggred_data_label = None
        self.last_untriggred_id = None
        
        self.client = None
        self.ip_finder = IPFinder()
        self.last_found_ip = None
        self.search_robot()
    
    def add_ip_frame(self):
        self.ip_label = tk.Label(self.ip_frame, text="Enter IP")
        self.ip_label.pack()
        self.ip_entry = tk.Entry(self.ip_frame)
        self.ip_entry.pack()
        self.connect_button = tk.Button(self.ip_frame, text="Connect!", command=self.connect)
        self.connect_button.pack(pady=5)
        self.localhost_button = tk.Button(
            self.ip_frame, 
            text="Connect to localhost", 
            command=lambda: self.connect(LOCALHOST_SERVER_ADDRESS)
        )
        self.localhost_button.pack(pady=5)
        self.found_ip_button = tk.Button(
            self.ip_frame,
            text="Found: "
        )
        self.found_ip_button.pack(pady=5)
        self.focus_set()
    
    def search_robot(self):
        found_ip = self.ip_finder.get_ip()
        if found_ip is None:
            self.found_ip_button.config(
                text=f"Found: ",
                command=False
            )
        else:
            self.found_ip_button.config(
                text=f"Found: {found_ip}", 
                command=lambda found_ip=found_ip: self.connect(found_ip)
            )

        if not self.client:
            self.after(100, self.search_robot)

    def add_control_frame(self):
        self.disconnect_button = tk.Button(self, text="Disconnect", command=self.disconnect)
        self.disconnect_button.place(x=10, y=10, anchor="nw")
        self.is_connected_label = tk.Label(self, text="Disconnected", bg=RED)
        self.is_connected_label.place(x=5, y=45, anchor="nw")
        self.command_label = tk.Label(self.control_frame, text="Enter command")
        self.command_label.grid(row=0, column=0)

        self.command_entry = tk.Entry(self.control_frame)
        self.command_entry.grid()

        self.toggle_label = tk.Label(self.control_frame, text="Toggle")
        self.toggle_label.grid(row=0, column=1)
        
        self.toggle_checkbutton = tk.Checkbutton(self.control_frame, variable=self.is_current_triggred)
        self.toggle_checkbutton.grid(row=1, column=1)

        self.eval_button = tk.Button(self.control_frame, text="Evaluate!", command=self.send_command)
        self.eval_button.grid(pady=10)

        self.remove_all_button = tk.Button(
            self.control_frame, 
            text="Remove all commands", 
            command=self.remove_all
        )
        self.remove_all_button.grid(pady=10)

        self.left_button = tk.Button(
            self.control_frame, 
            text="Left", 
            command=lambda: self.send_command(MOVE_LEFT_COMMAND, False)
        )
        self.left_button.grid(row=1, column=2)

        self.right_button = tk.Button(
            self.control_frame, 
            text="Right",
            command=lambda: self.send_command(MOVE_RIGHT_COMMAND, False)
        )
        self.right_button.grid(row=1, column=4)

        self.forward_button = tk.Button(
            self.control_frame, 
            text="Forward",
            command=lambda: self.send_command(MOVE_FORWARD_COMMAND, False)
        )
        self.forward_button.grid(row=0, column=3)

        self.backward_button = tk.Button(
            self.control_frame, 
            text="Backward",
            command=lambda: self.send_command(MOVE_BACKWARD_COMMAND, False)
        )
        self.backward_button.grid(row=2, column=3)

        self.stop_button = tk.Button(
            self.control_frame, 
            text="Stop",
            command=lambda: self.send_command(STOP_MOVING_COMMAND, False)
        )
        self.stop_button.grid(row=1, column=3, pady=10)
        
        self.arrows_moving_label = tk.Label(self.control_frame, text="Enable arrows moving")
        self.arrows_moving_label.grid(row=0, column=5)

        self.arrows_moving_checkbutton = tk.Checkbutton(self.control_frame, 
                                                        command=self.moving_mode_change)
        self.arrows_moving_checkbutton.grid(row=1, column=5)

    def moving_mode_change(self):
        if not self.is_arrows_moving_mode:
            self.bind("<Left>", lambda event: self.send_move_command(MOVE_LEFT_COMMAND))
            self.bind("<Right>", lambda event: self.send_move_command(MOVE_RIGHT_COMMAND))
            self.bind("<Up>", lambda event: self.send_move_command(MOVE_FORWARD_COMMAND))
            self.bind("<Down>", lambda event: self.send_move_command(MOVE_BACKWARD_COMMAND))
            self.bind("<Return>", lambda event: self.send_move_command(TURN_RIGHT_COMMAND))
            self.bind("<Shift_R>", lambda event: self.send_move_command(TURN_LEFT_COMMAND))
            self.bind("<space>", lambda event: self.send_move_command(STOP_MOVING_COMMAND))
            self.bind("<KeyRelease>", lambda event: self.send_move_command(STOP_MOVING_COMMAND))
            self.is_arrows_moving_mode = True
        else:
            self.unbind("<Left>")
            self.unbind("<Right>")
            self.unbind("<Up>")
            self.unbind("<Down>")
            self.unbind("<KeyRelease>")
            self.unbind("<Return>")
            self.is_arrows_moving_mode = False


    def update_data_table(self):
        if not self.client or not self.client.is_connected:
            self.is_connected_label.config(text="Disconnected", bg=RED)
        else:
            self.is_connected_label.config(text="Connected", bg=GREEN)
        if not self.client:
            return
        for widget in self.table_frame.winfo_children():
            if self.untriggred_data_label and widget == self.untriggred_data_label:
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
                command=lambda command_id=int(command_id): self.remove_command(command_id)
            )
            remove_button.grid(row=row + 1, column=0)

            command_label = tk.Label(self.table_frame, text=command)
            command_label.grid(row=row + 1, column=1)

            value_label = tk.Label(self.table_frame, text=value)
            value_label.grid(row=row + 1, column=2, padx=20)
        
        self.after(100, self.update_data_table)

    def send_command(self, command: str = None, is_triggred: bool = None):
        if not self.client:
            return
        if not command:
            command = self.command_entry.get()
            is_triggred = self.is_current_triggred.get()
        command_id = self.client.send_command(command, is_triggred)
        if is_triggred:
            self.commands[command_id] = command
        else:
            self.last_untriggred_id = command_id

    def send_move_command(self, command: str):
        if self.current_move_command and self.current_move_command == command:
            return
        self.send_command(command, False)
        if command == STOP_MOVING_COMMAND:
            self.current_move_command = None
        else:
            self.current_move_command = command


    def remove_command(self, command_id: int):
        self.client.remove_command(command_id)
    
    def remove_all(self):
        self.client.remove_all_commands()

    def connect(self, address_str: str = None):
        try:
            if not address_str:
                address_str = self.ip_entry.get()
            address, port = address_str.split(":")
            port = int(port)
            self.client = Client(address, port)
            self.client.start()
            if self.client.connection_error:
                raise
        except:
            self.client = None
            messagebox.showerror("Error", "Error while trying to connect to the robot")
            return
        self.ip_frame.pack_forget()
        self.title("Connected")
        self.control_frame.pack()
        self.table_frame.pack(pady=20)
        self.update_data_table()

    def disconnect(self):
        if self.client:
            self.client.running = False
            self.client.join()
            self.client = None
        self.control_frame.pack_forget()
        self.table_frame.pack_forget()
        self.is_connected_label.config(text="Disconnected", bg=RED)
        self.title(DEFAULT_TITLE)
        self.ip_frame.pack()
        self.search_robot()

    def on_closing(self):
        if self.client:
            self.client.running = False
            self.client.join()
        self.ip_finder.close()
        self.destroy()


def main():
    app = ControllerApp()
    app.mainloop()

if __name__ == "__main__":
    main()