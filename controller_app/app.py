import tkinter as tk
from tkinter import messagebox
import socket
from client import Client, IPFinder
import time
from command_consts import *

WIDTH = 600
HEIGHT = 300

GREEN = "#00ff1a"
RED = "#ff1100"

LOCALHOST_SERVER_ADDRESS = "127.0.0.1:1989"
BROADCAST_PORT = 1990

class ControllerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.title(DEFAULT_TITLE)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.init_keys()
        self.init_frames()
        self.ip_frame.pack()

        self.current_move_command = None
        self.servo_angles = [0 for _ in range(7)]

        self.table_frame = tk.Frame(self.control_frame)

        self.toggled_commands = {} # {id: command_str}
        self.untriggred_data_label = None
        self.last_untriggred_id = None
        
        self.client = None
        self.ip_finder = IPFinder()
        self.last_found_ip = None
    
    def init_keys(self):
        self.bind("<Left>", lambda event: self.send_move_command(MOVE_LEFT_COMMAND))
        self.bind("<Right>", lambda event: self.send_move_command(MOVE_RIGHT_COMMAND))
        self.bind("<Up>", lambda event: self.send_move_command(MOVE_FORWARD_COMMAND))
        self.bind("<Down>", lambda event: self.send_move_command(MOVE_BACKWARD_COMMAND))
        self.bind("<Return>", lambda event: self.send_move_command(TURN_RIGHT_COMMAND))
        self.bind("<Shift_R>", lambda event: self.send_move_command(TURN_LEFT_COMMAND))
        self.bind("<space>", lambda event: self.send_move_command(STOP_MOVING_COMMAND))
        self.bind("<KeyRelease>", lambda event: self.send_move_command(STOP_MOVING_COMMAND))
        self.focus_set()

    def change_frame(self, frame: tk.Frame, new_title: str = None):
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.pack_forget()
        frame.pack()
        if not new_title is None:
            self.title(new_title)

    def magic_connect(self):
        found_ip = self.ip_finder.get_ip()
        if found_ip:
            self.connect(found_ip)
        else:
            messagebox.showerror("Error", "Robot not found")

    def init_frames(self):
        self.init_ip_frame()
        self.init_control_frame()

    def init_ip_frame(self):
        self.ip_frame = tk.Frame(self)

        self.ip_label = tk.Label(self.ip_frame, text="Enter IP")
        self.ip_label.pack()
        self.ip_entry = tk.Entry(self.ip_frame)
        self.ip_entry.pack()
        self.connect_button = tk.Button(self.ip_frame, text="Connect", command=self.connect)
        self.connect_button.pack(pady=5)
        self.localhost_button = tk.Button(
            self.ip_frame, 
            text="Connect to localhost", 
            command=lambda: self.connect(LOCALHOST_SERVER_ADDRESS)
        )
        self.localhost_button.pack(pady=5)
        self.magic_connect_button = tk.Button(
            self.ip_frame,
            text="Magic connect",
            command=self.magic_connect
        )
        self.magic_connect_button.pack(pady=5)


    def init_control_frame(self):
        self.control_frame = tk.Frame(self)
        self.is_servos_mirrored = tk.BooleanVar()
        self.is_current_triggred = tk.BooleanVar()
        self.is_moving_mode = tk.BooleanVar()

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

        self.arrows_moving_label = tk.Label(self.control_frame, text="Enable arrows moving")
        self.arrows_moving_label.grid(row=0, column=2, padx=20)

        self.arrows_moving_checkbutton = tk.Checkbutton(self.control_frame, 
                                                        variable=self.is_moving_mode)
        self.arrows_moving_checkbutton.grid(row=1, column=2)

        self.servo_index_slider = tk.Scale(
            self.control_frame, 
            to=6, 
            orient="horizontal",
            command=self.change_servo_index
        )
        self.servo_index_slider.grid(row=2, column=2)

        self.servos_control_slider = tk.Scale(
            self.control_frame, 
            to=180, 
            orient="horizontal", 
            command=self.send_servos_control_command
        )
        self.servos_control_slider.grid(row=3, column=2)
        self.mirror_servos_label = tk.Label(self.control_frame, text="Mirror servos")
        self.mirror_servos_label.grid(row=4, column=2)
        self.mirror_servos_checkbutton = tk.Checkbutton(
            self.control_frame, 
            variable=self.is_servos_mirrored,
            command=self.change_is_mirrored
        )
        self.mirror_servos_checkbutton.grid(row=5, column=2)


    def update_data(self):
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
            if not command_id in self.toggled_commands.keys():
                continue
            command = self.toggled_commands[command_id]
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
        
        self.after(100, self.update_data)

    def send_command(self, command: str = None, is_triggred: bool = None):
        if not self.client:
            return
        if not command:
            command = self.command_entry.get()
            is_triggred = self.is_current_triggred.get()
        command_id = self.client.send_command(command, is_triggred)
        if is_triggred:
            self.toggled_commands[command_id] = command
        else:
            self.last_untriggred_id = command_id

    def send_move_command(self, command: str):
        if not self.is_moving_mode.get():
            return
        if self.current_move_command and self.current_move_command == command:
            return
        self.send_command(command, False)
        if command == STOP_MOVING_COMMAND:
            self.current_move_command = None
        else:
            self.current_move_command = command
    
    def send_servos_control_command(self, angle: int):
        servo_index = self.servo_index_slider.get()
        if not self.is_servos_mirrored.get():
            command = SERVO_CONTROL_COMMAND.replace("<index>", str(servo_index)).replace("<angle>", str(angle))
            self.client.send_command(command, False)
            self.servo_angles[servo_index] = angle
        else:
            command = SERVOS_CONTROL_COMMAND.replace("<indexes>", str([servo_index, servo_index + 3])).replace("<angle>", str(angle))
            self.client.send_command(command, False)
            self.servo_angles[servo_index] = angle
            self.servo_angles[servo_index + 3] = angle

    def change_servo_index(self, index: str):
        angle = self.servo_angles[int(index)]
        self.servos_control_slider.set(angle)

    def change_is_mirrored(self):
        if self.is_servos_mirrored.get():
            self.servo_index_slider.config(to=2)
        else:
            self.servo_index_slider.config(to=6)

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
        self.change_frame(self.control_frame, "Control Panel")
        self.table_frame.grid(pady=20)
        self.update_data()

    def disconnect(self):
        if self.client:
            self.client.running = False
            self.client.join()
            self.client = None
        self.change_frame(self.ip_frame, DEFAULT_TITLE)
        self.is_connected_label.config(text="Disconnected", bg=RED)

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