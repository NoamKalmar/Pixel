import tkinter as tk
from tkinter import messagebox
import socket
from client import Client, CommandReturnValue, IPFinder
import time
from command_consts import *

WIDTH = 600
HEIGHT = 300

GREEN = "#00ff1a"
RED = "#ff1100"
GOLD = "#ffd700"
DEFAULT_BUTTON_COLOR = "SystemButtonFace"
DEFAULT_TITLE = "Waiting for connection"
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

        self.show_frames: dict = {} # {name: frame}
        self.step_buttons: list[tk.Button] = []
        self.selected_step: int | None = None
        self.running_step_command_id: int | None = None
        self.angle_command_id: int | None = None
        
        self.client = None
        self.ip_finder = IPFinder()
        self.last_found_ip = None

    def init_keys(self) -> None:
        self.bind("<Left>", lambda event: self.send_move_command(MOVE_LEFT_COMMAND))
        self.bind("<Right>", lambda event: self.send_move_command(MOVE_RIGHT_COMMAND))
        self.bind("<Up>", lambda event: self.send_move_command(MOVE_FORWARD_COMMAND))
        self.bind("<Down>", lambda event: self.send_move_command(MOVE_BACKWARD_COMMAND))
        self.bind("<Return>", lambda event: self.send_move_command(TURN_RIGHT_COMMAND))
        self.bind("<Shift_R>", lambda event: self.send_move_command(TURN_LEFT_COMMAND))
        self.bind("<space>", lambda event: self.send_move_command(STOP_MOVING_COMMAND))
        self.bind("<KeyRelease>", lambda event: self.send_move_command(STOP_MOVING_COMMAND))
        self.focus_set()

    def change_frame(self, frame: tk.Frame, new_title: str = None) -> None:
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.pack_forget()
        frame.pack()
        if new_title is not None:
            self.title(new_title)

    def magic_connect(self) -> None:
        found_ip = self.ip_finder.get_ip()
        if found_ip:
            self.connect(found_ip)
        else:
            messagebox.showerror("Error", "Robot not found")

    def init_frames(self) -> None:
        self.init_ip_frame()
        self.init_control_frame()
        # The shows menu frame will be initalized when loaded

    def init_ip_frame(self) -> None:
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


    def init_control_frame(self) -> None:
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

        self.shows_menu_button = tk.Button(
            self.control_frame,
            text="Shows menu",
            command=lambda: self.client.get_command_value(GET_SHOW_NAMES_COMMAND, 
                                                          on_return=self.load_shows_menu)
        )
        self.shows_menu_button.grid(row=0, column=3)

        self.angle_label = tk.Label(self.control_frame, text="")
        self.angle_label.grid(row=1, column=3)

    def load_shows_menu(self, show_names: str | None) -> None:
        if show_names is None:
            return
        
        self.shows_menu_frame = tk.Frame(self)
        shows_list = show_names.split(",")
        for i, show_name in enumerate(shows_list):
            show_button = tk.Button(
                self.shows_menu_frame, 
                text=show_name,
                command=lambda name=show_name: self.client.get_command_value(
                    GET_SHOW_STEPS_COMMAND.replace("<name>", name),
                    on_return=lambda step_names, name=name: self.load_show_menu(name, 
                                                                                step_names)
                )
            )
            show_button.grid(row=i, column=0, pady=10)

        self.go_back_button = tk.Button(
            self.shows_menu_frame,
            text="Back",
            command=lambda: self.change_frame(self.control_frame)
        )
        self.go_back_button.grid(row=0, column=1, padx=30)
        
        self.change_frame(self.shows_menu_frame)
    
    def load_show_menu(self, show_name: str, step_names: str | None) -> None:
        if step_names is None:
            return
        self.selected_step = None
        self.show_frames[show_name] = tk.Frame(self)
        frame = self.show_frames[show_name]
        self.step_buttons = []
        steps = step_names.split(",")
        for i, step in enumerate(steps):
            step_button = tk.Button(
                frame,
                text=step,
                command=lambda index=i: self.select_step(index)
            )
            step_button.grid(row=i, column=0)
            self.step_buttons.append(step_button)
        
        self.play_show_button = tk.Button(
            frame,
            text="Play show",
            command=lambda name=show_name: self.send_show_playing_command(PLAY_SHOW_COMMAND.replace("<name>", name))
        )
        self.play_show_button.grid(row=0, column=1, padx=20)

        self.play_show_from_step_button = tk.Button(
            frame,
            text="Play show from step",
            command=lambda name=show_name: self.send_show_playing_command(
                PLAY_SHOW_FROM_STEP_COMMAND.replace("<name>", name).replace("<step>", str(self.selected_step))
            )
        )
        self.play_show_from_step_button.grid(row=1, column=1, padx=20)

        self.play_step_button = tk.Button(
            frame,
            text="Play step",
            command=lambda name=show_name: self.send_show_playing_command(
                PLAY_STEP_COMMAND.replace("<name>", name).replace("<step>", str(self.selected_step))
            )
        )
        self.play_step_button.grid(row=2, column=1)

        self.end_show_button = tk.Button(
            frame,
            text="End show",
            command=lambda: self.send_command(END_SHOW_COMMAND)
        )
        self.end_show_button.grid(row=3, column=1)

        self.go_back_button = tk.Button(
            frame,
            text="Back",
            command=lambda: self.change_frame(self.control_frame)
        )
        self.go_back_button.grid(row=0, column=2, padx=20)

        self.change_frame(frame)
    
    def select_step(self, step_index: int) -> None:
        if self.running_step_command_id is not None: # Show is already running
            return
        step_button = self.step_buttons[step_index]
        # If step is already select, then unselect it
        if self.selected_step == step_index:
            step_button.config(bg=DEFAULT_BUTTON_COLOR)
            self.selected_step = None
            return
        
        # When a button is selected, unselect all of the other ones
        self.selected_step = step_index
        self.default_all_steps()
        self.step_buttons[step_index].config(bg=GREEN)
    
    def default_all_steps(self) -> None:
        for button in self.step_buttons:
            button.config(bg=DEFAULT_BUTTON_COLOR)

    def get_robot_data(self) -> None:
        self.client.get_command_value(GET_NAME_COMMAND, on_return=self.got_name)
        self.angle_command_id = self.send_command(GET_ANGLE_COMMAND, True, False)
    
    def got_name(self, name: str | None) -> None:
        if name is None:
            return
        self.title(name)

    def loop(self) -> None:
        if not self.client or not self.client.is_connected:
            self.is_connected_label.config(text="Disconnected", bg=RED)
        else:
            self.is_connected_label.config(text="Connected", bg=GREEN)
        if not self.client:
            return
        if self.client.got_command_response(self.angle_command_id):
            self.angle_label.config(text=f"Angle: {self.client.commands_data[self.angle_command_id]}")
        if self.client.got_command_response(self.running_step_command_id):
            running_step = int(self.client.commands_data[self.running_step_command_id])
            if running_step == -1:
                self.default_all_steps()
                self.remove_command(self.running_step_command_id)
                self.running_step_command_id = None
            else:
                self.default_all_steps()
                self.step_buttons[int(running_step)].config(bg=GOLD)
        self.update_commands_data()
        self.after(100, self.loop)
    
    def update_commands_data(self) -> None:
        for widget in self.table_frame.winfo_children():
            if self.untriggred_data_label and widget == self.untriggred_data_label:
                continue
            widget.destroy()
        
        if self.last_untriggred_id in self.client.commands_data:
            self.untriggred_data_label = tk.Label(
                self.table_frame, 
                text=f"Value: {self.client.commands_data[self.last_untriggred_id]}"
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

    def send_command(self, command: str = None, is_triggred: bool = None, display: bool = True) -> int:
        if not self.client:
            return
        if not command:
            command = self.command_entry.get()
            is_triggred = self.is_current_triggred.get()
        command_id = self.client.send_command(command, is_triggred)
        if not display:
            return
        if is_triggred:
            self.toggled_commands[command_id] = command
        else:
            self.last_untriggred_id = command_id

        return command_id

    def send_move_command(self, command: str) -> None:
        if not self.is_moving_mode.get():
            return
        if self.current_move_command and self.current_move_command == command:
            return
        self.send_command(command, False)
        if command == STOP_MOVING_COMMAND:
            self.current_move_command = None
        else:
            self.current_move_command = command
    
    def send_servos_control_command(self, angle: int) -> None:
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
    
    def send_show_playing_command(self, command: str) -> None:
        self.selected_step = None
        self.default_all_steps()
        self.send_command(command)
        self.running_step_command_id = self.send_command(GET_RUNNING_COMMAND, True, False)

    def change_servo_index(self, index: str) -> None:
        angle = self.servo_angles[int(index)]
        self.servos_control_slider.set(angle)

    def change_is_mirrored(self) -> None:
        if self.is_servos_mirrored.get():
            self.servo_index_slider.config(to=2)
        else:
            self.servo_index_slider.config(to=6)

    def remove_command(self, command_id: int) -> None:
        self.client.remove_command(command_id)
    
    def remove_all(self) -> None:
        self.client.remove_all_commands()

    def connect(self, address_str: str = None) -> None:
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
        self.after(100, self.get_robot_data)
        self.table_frame.grid(pady=20)
        self.loop()

    def disconnect(self) -> None:
        if self.client:
            self.client.running = False
            self.client.join()
            self.client = None
        self.change_frame(self.ip_frame, DEFAULT_TITLE)
        self.is_connected_label.config(text="Disconnected", bg=RED)

    def on_closing(self) -> None:
        if self.client:
            self.client.running = False
            self.client.join()
        self.ip_finder.close()
        self.destroy()


def main() -> None:
    app = ControllerApp()
    app.mainloop()

if __name__ == "__main__":
    main()