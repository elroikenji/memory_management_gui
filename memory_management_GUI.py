from datetime import datetime, timedelta
from tkinter import messagebox
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import os

class MainWindow(Tk):
    def __init__ (self):
        super().__init__()
        self.title("Memory Management")
        self.configure(background="white")
        self.geometry("700x600")
        self.resizable(0,0)
        directory = os.getcwd ()
        directory1 = directory + "\logo.png"
        image1 = Image.open(directory1)
        resized_image = image1.resize((600, 200))
        logo = ImageTk.PhotoImage(resized_image)
        label_logo = Label(self, image=logo)
        label_logo.image = logo  
        label_logo.grid(padx=50,pady=50)
        #center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        #displays the button in the main window and the user can select the type of memory management to use
        self.button_class1 = Button(self, text="Single Contiguous", command = self.open_single_cont_window)
        self.button_class1.grid(pady=10)

        self.button_class2 = Button(self, text="Static Partitioned")
        self.button_class2.grid(pady=10)

        self.button_class3 = Button(self, text="Dynamic Partitioned First Fit")
        self.button_class3.grid(pady=10)

        self.button_class4 = Button(self, text="Dynamic Partitioned Best Fit")
        self.button_class4.grid(pady=10)

        self.button_class5 = Button(self, text="Dynamic Partitioned Worst Fit")
        self.button_class5.grid(pady=10)

        self.button_class6 = Button(self, text="Dynamic with Compaction")
        self.button_class6.grid(pady=10)

    def open_single_cont_window(self):
        self.withdraw()
        single_cont = SingleContiguousWindow(self)
        single_cont.grab_set()

class SingleContiguousWindow(Toplevel): 
    def __init__(self, master):
        super().__init__(master)
        self.jobnum_list = []
        self.size_list = []
        self.arrival_list = []
        self.runtime_list = []
        self.job_block = []
        self.list_previous_job = []
        self.list_wait_job = [1]
        
        self.memory_block = ["OS (32)"]
        
        self.title("Single Contiguous Window")
        self.geometry("600x500")
        self.resizable(0,0)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        # Create "Memory Size" label and entry widget
        self.memory_label = ttk.Label(self, text="Memory Size:")
        self.memory_label.grid(pady=(45,0))
        self.memory_entry = ttk.Entry(self, width=15)
        self.memory_entry.grid()
        # Create "OS Size" label and entry widget
        self.os_label = ttk.Label(self, text="OS Size:")
        self.os_label.grid(pady=5)
        self.os_entry = ttk.Entry(self, width=15)
        self.os_entry.grid()
        # Create the table
        table_frame = ttk.Frame(self)
        table_frame.grid(padx=80, pady=50)
        # Define the headers
        headers = ["Job No.", "Size", "Arrival Time", "Run Time"]
        # Create header labels
        for col, header in enumerate(headers):
            label = ttk.Label(table_frame, text=header, width=15, anchor=CENTER)
            label.grid(row=0, column=col, padx=5, pady=5)
        # Create entry widgets for data input
        self.entry_widgets = []
        for row in range(5):
            row_entries = []
            for col in range(4):
                entry = ttk.Entry(table_frame, width=15)
                entry.grid(row=row + 1, column=col, padx=5, pady=5)
                row_entries.append(entry)
                entry.bind("<Down>", lambda event, r=row, c=col: self.navigate_entries(event, r + 1, c))
                entry.bind("<Up>", lambda event, r=row, c=col: self.navigate_entries(event, r - 1, c))
                entry.bind("<Right>", lambda event, r=row, c=col: self.navigate_entries(event, r, c + 1))
                entry.bind("<Left>", lambda event, r=row, c=col: self.navigate_entries(event, r, c - 1))
            self.entry_widgets.append(row_entries)
        # Button to check input
        self.button_memory_map = ttk.Button(self, text="Create Memory Map", command=self.process_input)
        self.button_memory_map.grid(pady=10)

    def navigate_entries(self, event, row, col):
        if 0 <= row < len(self.entry_widgets) and 0 <= col < len(self.entry_widgets[row]):
            self.entry_widgets[row][col].focus_set()

    def on_close(self):
        self.master.deiconify()
        self.destroy()

    def process_input(self): #gets the values on the table (WITH ERROR HANDLING)
        try:
            memory_size = self.memory_entry.get()
            os_size = self.os_entry.get()
            if not memory_size.isdigit() or not os_size.isdigit():
                raise ValueError("Memory Size and OS Size must be integers.")
            self.memory_size = int(memory_size)
            self.os_size = int(os_size)
           
            for row_entries in self.entry_widgets:
                jobnum =row_entries[0].get()
                size = row_entries[1].get()
                arrival = row_entries[2].get()
                runtime = row_entries[3].get()
                if not jobnum.isdigit() or not size.isdigit() or not runtime.isdigit():
                    raise ValueError("Job No., Size, and Run Time must be integers.")
                self.jobnum_list.append(int(jobnum))
                self.size_list.append(int(size))
                self.runtime_list.append(int(runtime))
                #adjusting the time format if the user didn't follow (%H:%M)
                arrival = datetime.strptime(arrival, "%H:%M")
                arrivalstr = arrival.strftime('%H:%M')
                self.arrival_list.append(arrivalstr)
             # If all conditions are satisfied, create the memory map
            self.withdraw()
            self.sequence_time_events()
            self.create_memory_map()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def sequence_time_events(self): 
        self.seq_time_events = []
        self.starting_time = [datetime.strptime(self.arrival_list[0], "%H:%M")]
        # for the remaining jobs
        for i in range(1, len(self.arrival_list)):
            arrival_time = datetime.strptime(self.arrival_list[i], "%H:%M")
            completion_time = self.starting_time[i-1] + timedelta(minutes=self.runtime_list[i-1])
            starting_time = max(arrival_time, completion_time)
            self.starting_time.append(starting_time)

        self.list_starting_time = [] #string list of starting time 
        for time in self.starting_time:
            starting_time_str = time.strftime("%H:%M")
            self.list_starting_time.append(starting_time_str)

        self.list_run_time_done = [] #string list of run time done/complete 
        for i in range(5):
            starting_time_str =  self.list_starting_time[i]
            starting_time_obj = datetime.strptime(starting_time_str, "%H:%M")
            run_time_done = starting_time_obj + timedelta(minutes=self.runtime_list[i])
            run_time_done_str = run_time_done.strftime("%H:%M")
            self.list_run_time_done.append(run_time_done_str)
        #create list for cpu wait
        self.list_cpu_wait = []
        for start,arrive in zip(self.list_starting_time, self.arrival_list):
            start_obj = datetime.strptime(start, "%H:%M")
            arrive_obj = datetime.strptime(arrive, "%H:%M")
            cpu_wait = start_obj - arrive_obj
            cpu_wait_min = cpu_wait.total_seconds() // 60
            self.list_cpu_wait.append(cpu_wait_min)
        #Sequence of time events list
        self.seq_time_events = list(set(self.arrival_list + self.list_starting_time + self.list_run_time_done))
        self.seq_time_events = sorted(self.seq_time_events)

    def duplicate_event(self, event):
        # this method determine if a certain event is duplicated: meaning it has multi-event existing
        # FOR ARRIVAL TIME AND STARTING TIME DUPLICATION
        self.duplicate_arrive_and_start = []
        self.newlist_arrive_and_start = []
        #combined list for arrival time and starting time
        self.arrive_plus_start = self.arrival_list + self.list_starting_time
        for i in self.arrive_plus_start:
            if i not in self.newlist_arrive_and_start:
                self.newlist_arrive_and_start.append(i)
            else:
                self.duplicate_arrive_and_start.append(i)
        self.duplicate_arrive_and_start = sorted(self.duplicate_arrive_and_start)
        # FOR STARTING TIME AND RUN TIME DONE DUPLICATION
        self.duplicate_start_and_runtime = []
        self.newlist_start_and_runtime = []
        #combined list for starting time and run time done
        self.start_plus_runtime =  self.list_starting_time + self.list_run_time_done
        for i in self.start_plus_runtime:
            if i not in self.newlist_start_and_runtime:
                self.newlist_start_and_runtime.append(i)
            else:
                self.duplicate_start_and_runtime.append(i)
        self.duplicate_start_and_runtime = sorted(self.duplicate_start_and_runtime)
        # FOR ARRIVAL TIME AND RUN TIME DONE DUPLICATION
        self.duplicate_arrive_and_runtime = []
        self.newlist_arrive_and_runtime = []
        #combined list for arrival time and run time done 
        self.arrive_plus_runtime = self.arrival_list + self.list_run_time_done
        for i in self.arrive_plus_runtime:
            if i not in self.newlist_arrive_and_runtime:
                self.newlist_arrive_and_runtime.append(i)
            else:
                self.duplicate_arrive_and_runtime.append(i)
        self.duplicate_arrive_and_runtime = sorted(self.duplicate_arrive_and_runtime)
        if event in self.duplicate_arrive_and_start:
            self.is_duplicate = True
        elif event in self.duplicate_start_and_runtime:
            self.is_duplicate = True
        elif event in self.duplicate_arrive_and_runtime:
            self.is_duplicate = True
        else:
            self.is_duplicate = False

    def job_alloc(self, counter):
        # activates whenever the memory block is ready for the next job allocation
        self.job_block.append(counter)
        self.memory_block.pop()
        # distribute the job size to the current job
        self.current_job_size = self.size_list[self.job_block[0] - 1]

    def job_dealloc(self):
        # activates whenever the memory block is ready for the termination of job 
        self.previous_job = self.job_block.pop() 
        
        self.list_previous_job.append(self.previous_job)

    def wait_job(self):
        # job arrives but there's another job allocated in the memory block
        self.job_wait = self.list_wait_job[-1] + 1
        self.list_wait_job.append(self.job_wait)

    def create_memory_map(self):
        #create new window for memory map
        self.memory_map = Toplevel(self)
        self.memory_map.title("Memory Map Window")
        self.memory_map.geometry("500x400")
        self.memory_map.resizable(0,0)
        self.memory_map.protocol("WM_DELETE_WINDOW", self.on_close_memory_map)
        #center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        mem_map_frame = ttk.Frame(self.memory_map)
        mem_map_frame.grid(row=0, column=0,padx=60, pady=40)

        self.memory_available = self.memory_size - self.os_size
        self.counter = 1
        colors = ["#6cf542", "#42eff5", "#f54290"]
        
        for event in self.seq_time_events:
            button_clicked = BooleanVar()
            button_clicked.set(False)
            self.duplicate_event(event)
            if event in self.arrival_list and event in self.list_starting_time and event in self.list_run_time_done:
            # JOB TERMINATED FIRST THEN JOB NUM START/ JOB NUM ARRIVES
                action = "terminated then start/arrive"
            elif event in self.duplicate_arrive_and_start:
                action = "arrive/start"
            elif event in self.duplicate_start_and_runtime:
                action = "start/terminated" 
            
            if self.is_duplicate == False:
                if event in self.list_run_time_done:
                    action = "terminated"
                else:
                    action = "arrive/wait"
            self.generate_table(colors, mem_map_frame, self.counter, event, action)
            #last event should not have next button since it is the last event
            if event != self.seq_time_events[-1]:
                self.next_button(mem_map_frame, button_clicked)
                self.next_button_clicked(mem_map_frame)
                # try:
                #     self.next_button_clicked(mem_map_frame)
                # except Exception as e:
                #     # Handle the exception
                #     print(f"Error: {e}")

    def generate_table(self, colors, mem_map_frame, counter, event, action):
        if action == "arrive/start" and event == self.arrival_list[0]:
            label = ttk.Label(mem_map_frame, text="Before " + str(event), font=("Arial", 16))
            label.grid(row=0, column=0, padx=80, pady=10)
            self.memory_block.append("Memory Available (" + str(self.memory_available) + ")")
            for index, item in enumerate(self.memory_block):
                label = ttk.Label(mem_map_frame, text=item, font=("Arial", 16), anchor=CENTER, width=25, background=colors[index])
                label.grid(row=index+1, column=0)
            self.job_alloc(counter)
            label_nx = ttk.Label(mem_map_frame, text="At " + str(event) + " J" + str(self.job_block[0]) + " Arrive/Start", font=("Arial", 16))
            label_nx.grid(row=5, column=0, padx=80, pady=20)
            self.memory_block.append("J" + str(self.job_block[0]) + " (" + str(self.current_job_size)+")")
            self.wasted = self.memory_size - self.os_size - self.current_job_size
            self.loc = self.os_size + self.current_job_size
            self.memory_block.append("Wasted(" + str(self.wasted)+")")
            for index, item in enumerate(self.memory_block,start=6):
                x = self.memory_block.index(item)
                label = ttk.Label(mem_map_frame, text=item, font=("Arial", 16), anchor=CENTER, width=25, background=colors[x])
                label.grid(row=index, column=0)
            self.counter += 1
        
        if action == "arrive/start" and event != self.arrival_list[0]:
            self.job_alloc(counter)
            label = ttk.Label(mem_map_frame, text="At " + str(event) + " J" + str(self.job_block[0]) + " Arrive/Start", font=("Arial", 16))
            label.grid(row=0, column=0, padx=80, pady=10)
            self.memory_block.append("J" + str(self.job_block[0]) + " (" + str(self.current_job_size)+")")
            self.wasted = self.memory_size - self.os_size - self.current_job_size
            self.loc = self.os_size + self.current_job_size
            self.memory_block.append("Wasted(" + str(self.wasted)+")")
            for index, item in enumerate(self.memory_block):
                label = ttk.Label(mem_map_frame, text=item, font=("Arial", 16), anchor=CENTER, width=25, background=colors[index])
                label.grid(row=index+1, column=0)
            self.counter += 1

        if action == "start/terminated":
            self.job_dealloc()
            self.memory_block.pop()
            self.memory_block.pop()
            label = ttk.Label(mem_map_frame, text="At " + str(event) + " J" + str(self.list_previous_job[-1]) + " Terminated", font=("Arial", 16))
            label.grid(row=0, column=0, padx=40, pady=10)
            self.memory_block.append("Memory Available (" + str(self.memory_available) + ")")
            for index, item in enumerate(self.memory_block):
                label = ttk.Label(mem_map_frame, text=item, font=("Arial", 16), anchor=CENTER, width=25, background=colors[index])
                label.grid(row=index+1, column=0)
            self.job_alloc(counter)
            label_nx = ttk.Label(mem_map_frame, text="At " + str(event) + " J" + str(self.list_previous_job[-1]) + " Terminated; J" + str(self.job_block[-1]) + " Start", font=("Arial", 16))
            label_nx.grid(row=5, column=0, padx=40, pady=20)
            self.memory_block.append("J" + str(self.job_block[0]) + " (" + str(self.current_job_size) + ")")
            self.wasted = self.memory_size - self.os_size - self.current_job_size
            self.loc = self.os_size + self.current_job_size
            self.memory_block.append("Wasted(" + str(self.wasted)+")")
            for index, item in enumerate(self.memory_block,start=6):
                x = self.memory_block.index(item)
                label = ttk.Label(mem_map_frame, text=item, font=("Arial", 16), anchor=CENTER, width=25, background=colors[x])
                label.grid(row=index, column=0)
            self.counter += 1

        if action == "terminated then start/arrive": 
            self.job_dealloc()
            self.memory_block.pop()
            self.memory_block.pop()
            label = ttk.Label(mem_map_frame, text="At " + str(event) + " J" + str(self.list_previous_job[-1]) + " Terminated", font=("Arial", 16))
            label.grid(row=0, column=0, padx=40, pady=10)
            self.memory_block.append("Memory Available (" + str(self.memory_available) + ")")
            for index, item in enumerate(self.memory_block):
                label = ttk.Label(mem_map_frame, text=item, font=("Arial", 16), anchor=CENTER, width=25, background=colors[index])
                label.grid(row=index+1, column=0)
            self.job_alloc(counter)
            self.wait_job()
            label_nx = ttk.Label(mem_map_frame, text="At " + str(event) + " J" + str(self.job_block[0]) + " Start; J" + str(self.list_wait_job[-1]) + " Arrive/Wait", font=("Arial", 16))
            label_nx.grid(row=5, column=0, padx=40, pady=20)
            self.memory_block.append("J" + str(self.job_block[0]) + " (" + str(self.current_job_size) + ")")
            self.wasted = self.memory_size - self.os_size - self.current_job_size
            self.loc = self.os_size + self.current_job_size
            self.memory_block.append("Wasted(" + str(self.wasted)+")")
            for index, item in enumerate(self.memory_block,start=6):
                x = self.memory_block.index(item)
                label = ttk.Label(mem_map_frame, text=item, font=("Arial", 16), anchor=CENTER, width=25, background=colors[x])
                label.grid(row=index, column=0)
            self.counter += 1

        if action == "arrive/wait":
            self.wait_job()
            label = ttk.Label(mem_map_frame, text="At " + str(event) + " J" + str(self.list_wait_job[-1]) + " Arrive/Wait", font=("Arial", 16))
            label.grid(row=0, column=0, padx=80, pady=40)
            self.wasted = self.memory_size - self.os_size - self.current_job_size
            self.loc = self.os_size + self.current_job_size
            for index, item in enumerate(self.memory_block):
                label = ttk.Label(mem_map_frame, text=item, font=("Arial", 16), anchor=CENTER, width=25, background=colors[index])
                label.grid(row=index+1, column=0)

        if action == "terminated":
            self.job_dealloc()
            self.memory_block.pop()
            self.memory_block.pop()
            label = ttk.Label(mem_map_frame, text="At " + str(event) + " J" + str(self.list_previous_job[-1]) + " Terminated", font=("Arial", 16))
            label.grid(row=0, column=0, padx=80, pady=40)
            self.memory_block.append("Memory Available (" + str(self.memory_available) + ")")
            for index, item in enumerate(self.memory_block):
                label = ttk.Label(mem_map_frame, text=item, font=("Arial", 16), anchor=CENTER, width=25, background=colors[index])
                label.grid(row=index+1, column=0)
            self.nextbutton = ttk.Button(mem_map_frame, text="Show Summary Table", command=self.summary_table)
            self.nextbutton.grid(row=9, column=0, pady=40)
            
    def next_button(self, mem_map_frame, button_clicked):
        self.nextbutton = ttk.Button(mem_map_frame, text="Next Memory Map", command=lambda: button_clicked.set(True))
        self.nextbutton.grid(row=9, column=0, pady=40)
        self.nextbutton.wait_variable(button_clicked)
        
    def next_button_clicked(self,mem_map_frame):
        for widgets in mem_map_frame.winfo_children():
            widgets.destroy()

    def summary_table(self):
        self.summary = Toplevel(self)
        self.summary.title("Summary Table Window")
        self.summary.geometry("790x200")
        self.summary.resizable(0,0)
        self.summary.protocol("WM_DELETE_WINDOW", self.on_close_summary)
        headers = ["Job No.", "Size", "Arrival Time", "Run Time (min.)", "Starting Time", "CPU Wait (min.)"]
        data = list(zip(self.jobnum_list,self.size_list,self.arrival_list,self.runtime_list,self.list_starting_time,self.list_cpu_wait))
        self.treeview = ttk.Treeview(self.summary, columns=headers, show="headings")
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), anchor="center")  # Adjust font size for column headers
        style.configure("Treeview", font=("Arial", 10), cellanchor="center")  # Adjust font size for data cells
        for header in headers:
            self.treeview.heading(header, text=header)
            self.treeview.column(header, width=131)
        for row in data:
            self.treeview.insert("", END, values=row)
        self.treeview.grid()

    def on_close_memory_map(self):
        messagebox.showwarning(title="Confirmation",message="Back to the Main Window")
        self.master.deiconify()
        self.destroy()

    def on_close_summary(self):
        messagebox.showinfo(title="Confirmation",message="Back to the Main Window")
        self.master.deiconify()
        self.destroy()


if __name__ == "__main__":
    gui = MainWindow()
    gui.mainloop()
