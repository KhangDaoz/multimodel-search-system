"""Show actual CLI output in a Python window for reproducible screenshot capture.
Run from submission: python presentation/demo_window.py
"""
import os,subprocess,sys,tkinter as tk
from pathlib import Path
root_dir=Path(__file__).resolve().parents[1]
output=subprocess.run([os.environ.get('DEMO_PYTHON',sys.executable),str(root_dir/'main.py'),'--cli'],cwd=root_dir,capture_output=True,text=True,check=True).stdout
window=tk.Tk();window.title('Assignment 06 — Python Multimodal Search Demo');window.geometry('1120x820+30+30')
tk.Label(window,text='Assignment 06 | Actual Python execution',font=('Sans',16,'bold'),bg='#15253b',fg='white',anchor='w',padx=18,pady=12).pack(fill='x')
text=tk.Text(window,bg='#101c2c',fg='#d8e8fa',font=('Monospace',11),wrap='none',padx=18,pady=12)
text.pack(fill='both',expand=True);text.insert('1.0',output);text.configure(state='disabled');window.mainloop()
