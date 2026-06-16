import audio
import head_pose
import detection
import threading as th
import queue
import time
from ui import ProctoringUI
import tkinter as tk

# Queue for thread-safe communication between backend and UI
data_queue = queue.Queue()


def poll_backend_status():
    """Poll backend modules and put their status in the queue"""
    poll_count = 0
    while True:
        try:
            data = {
                'audio_cheat': audio.AUDIO_CHEAT,
                'x_axis_cheat': head_pose.X_AXIS_CHEAT,
                'y_axis_cheat': head_pose.Y_AXIS_CHEAT,
                'lip_movement_cheat': head_pose.LIP_MOVEMENT_CHEAT,
                'percentage_cheat': detection.PERCENTAGE_CHEAT,
                'global_cheat': detection.GLOBAL_CHEAT,
            }
            data_queue.put(data)
            
            # Debug: always show terminal status for all indicators
            poll_count += 1
            if poll_count % 2 == 0:
                print(
                    f"STATUS | Audio={audio.AUDIO_CHEAT} | HeadX={head_pose.X_AXIS_CHEAT} | HeadY={head_pose.Y_AXIS_CHEAT} | "
                    f"Lip={head_pose.LIP_MOVEMENT_CHEAT} | Cheat%={detection.PERCENTAGE_CHEAT:.2%} | Global={detection.GLOBAL_CHEAT}"
                )
            
            time.sleep(0.5)  # Poll every 500ms
        except Exception as e:
            print(f"Error polling backend: {e}")
            time.sleep(1)


if __name__ == "__main__":
    # Start backend threads (non-daemon for clean shutdown)
    head_pose_thread = th.Thread(target=head_pose.pose, daemon=False)
    audio_thread = th.Thread(target=audio.sound, daemon=False)
    detection_thread = th.Thread(target=detection.run_detection, daemon=False)
    
    # Start status polling thread
    polling_thread = th.Thread(target=poll_backend_status, daemon=True)

    head_pose_thread.start()
    audio_thread.start()
    detection_thread.start()
    polling_thread.start()

    # Start UI in main thread
    root = tk.Tk()
    app = ProctoringUI(root, data_queue)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.destroy()
