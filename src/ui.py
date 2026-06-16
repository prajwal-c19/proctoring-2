import tkinter as tk
from tkinter import ttk
import queue
from datetime import datetime

class ProctoringUI:
    def __init__(self, root, data_queue):
        self.root = root
        self.data_queue = data_queue
        self.root.title("Proctoring Monitor")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Main frame
        main_frame = ttk.Frame(root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="Proctoring Monitor", 
                         font=("Arial", 18, "bold"))
        title.pack(pady=10)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Detection Status", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Audio monitoring
        audio_frame = ttk.Frame(status_frame)
        audio_frame.pack(fill=tk.X, pady=5)
        ttk.Label(audio_frame, text="Audio Detection:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.audio_label = ttk.Label(audio_frame, text="Normal", foreground="green", 
                                     font=("Arial", 10))
        self.audio_label.pack(side=tk.LEFT, padx=10)
        
        # Head pose X-axis
        x_frame = ttk.Frame(status_frame)
        x_frame.pack(fill=tk.X, pady=5)
        ttk.Label(x_frame, text="Head Pose (X-axis):", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.x_axis_label = ttk.Label(x_frame, text="Normal", foreground="green", 
                                      font=("Arial", 10))
        self.x_axis_label.pack(side=tk.LEFT, padx=10)
        
        # Head pose Y-axis
        y_frame = ttk.Frame(status_frame)
        y_frame.pack(fill=tk.X, pady=5)
        ttk.Label(y_frame, text="Head Pose (Y-axis):", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.y_axis_label = ttk.Label(y_frame, text="Normal", foreground="green", 
                                      font=("Arial", 10))
        self.y_axis_label.pack(side=tk.LEFT, padx=10)
        
        # Lip movement
        lip_frame = ttk.Frame(status_frame)
        lip_frame.pack(fill=tk.X, pady=5)
        ttk.Label(lip_frame, text="Lip Movement:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.lip_label = ttk.Label(lip_frame, text="Normal", foreground="green", 
                                   font=("Arial", 10))
        self.lip_label.pack(side=tk.LEFT, padx=10)
        
        # Overall cheat percentage
        cheat_frame = ttk.LabelFrame(main_frame, text="Overall Analysis", padding=10)
        cheat_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Cheat percentage bar
        percent_frame = ttk.Frame(cheat_frame)
        percent_frame.pack(fill=tk.X, pady=5)
        ttk.Label(percent_frame, text="Cheat Probability:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.cheat_percentage = ttk.Label(percent_frame, text="0%", foreground="green", 
                                          font=("Arial", 10, "bold"))
        self.cheat_percentage.pack(side=tk.LEFT, padx=10)
        
        # Progress bar for cheat percentage
        self.progress = ttk.Progressbar(cheat_frame, length=400, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # Global cheat status
        global_frame = ttk.Frame(cheat_frame)
        global_frame.pack(fill=tk.X, pady=5)
        ttk.Label(global_frame, text="Overall Status:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.global_cheat_label = ttk.Label(global_frame, text="OK", foreground="green", 
                                            font=("Arial", 10, "bold"))
        self.global_cheat_label.pack(side=tk.LEFT, padx=10)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, height=5, width=70, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Start polling for data
        self.poll_queue()
    
    def poll_queue(self):
        try:
            while True:
                data = self.data_queue.get_nowait()
                self.update_ui(data)
        except queue.Empty:
            pass
        
        # Schedule next poll
        self.root.after(100, self.poll_queue)
    
    def update_ui(self, data):
        # Update audio status
        audio_status = "⚠️ SUSPICIOUS" if data.get('audio_cheat') else "✓ Normal"
        audio_color = "red" if data.get('audio_cheat') else "green"
        self.audio_label.config(text=audio_status, foreground=audio_color)
        
        # Update head pose X-axis
        x_status = "⚠️ SUSPICIOUS" if data.get('x_axis_cheat') else "✓ Normal"
        x_color = "red" if data.get('x_axis_cheat') else "green"
        self.x_axis_label.config(text=x_status, foreground=x_color)
        
        # Update head pose Y-axis
        y_status = "⚠️ SUSPICIOUS" if data.get('y_axis_cheat') else "✓ Normal"
        y_color = "red" if data.get('y_axis_cheat') else "green"
        self.y_axis_label.config(text=y_status, foreground=y_color)
        
        # Update lip movement
        lip_status = "⚠️ SUSPICIOUS" if data.get('lip_movement_cheat') else "✓ Normal"
        lip_color = "red" if data.get('lip_movement_cheat') else "green"
        self.lip_label.config(text=lip_status, foreground=lip_color)
        
        # Update cheat percentage
        cheat_pct = data.get('percentage_cheat', 0) * 100
        self.cheat_percentage.config(text=f"{cheat_pct:.1f}%")
        self.progress['value'] = cheat_pct
        
        # Update global cheat status
        global_status = "🚨 CHEATING" if data.get('global_cheat') else "✓ OK"
        global_color = "red" if data.get('global_cheat') else "green"
        self.global_cheat_label.config(text=global_status, foreground=global_color)
        
        # Add to log
        self.add_log_entry(data)
    
    def add_log_entry(self, data):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Build log message
        msg_parts = [timestamp]
        
        if data.get('audio_cheat'):
            msg_parts.append("🔊 Audio anomaly")
        if data.get('x_axis_cheat'):
            msg_parts.append("📐 Head pose X anomaly")
        if data.get('y_axis_cheat'):
            msg_parts.append("📐 Head pose Y anomaly")
        if data.get('lip_movement_cheat'):
            msg_parts.append("👄 Lip movement anomaly")
        if data.get('global_cheat'):
            msg_parts.append("⚠️ ALERT: Cheating detected!")
        
        if len(msg_parts) > 1:
            log_msg = " | ".join(msg_parts) + "\n"
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, log_msg)
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    q = queue.Queue()
    app = ProctoringUI(root, q)
    root.mainloop()