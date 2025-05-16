import sys
import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class NBAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NBA 資料爬蟲與分析工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 設置樣式
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("TLabel", font=("Arial", 12))
        self.style.configure("Header.TLabel", font=("Arial", 16, "bold"))
        
        # 創建主框架
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 創建標題
        header = ttk.Label(self.main_frame, text="NBA 資料爬蟲與分析工具", style="Header.TLabel")
        header.pack(pady=20)
        
        # 創建功能按鈕框架
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.BOTH, expand=True, padx=50)
        
        # 爬蟲功能區域
        scraper_label = ttk.Label(button_frame, text="資料爬蟲", style="Header.TLabel")
        scraper_label.grid(row=0, column=0, sticky="w", pady=(10, 5))
        
        ttk.Button(button_frame, text="爬取 NBA 基本資料", 
                   command=self.run_basic_scraper).grid(row=1, column=0, sticky="ew", pady=5)
        
        ttk.Button(button_frame, text="爬取 NBA 進階 API 資料", 
                   command=self.run_advanced_scraper).grid(row=2, column=0, sticky="ew", pady=5)
        
        ttk.Button(button_frame, text="爬取特定球員資料", 
                   command=self.run_player_scraper).grid(row=3, column=0, sticky="ew", pady=5)
        
        # 分析功能區域
        analysis_label = ttk.Label(button_frame, text="資料分析", style="Header.TLabel")
        analysis_label.grid(row=4, column=0, sticky="w", pady=(20, 5))
        
        ttk.Button(button_frame, text="分析 NBA 整體資料", 
                   command=self.run_data_analyzer).grid(row=5, column=0, sticky="ew", pady=5)
        
        ttk.Button(button_frame, text="分析特定球員資料", 
                   command=self.run_player_analyzer).grid(row=6, column=0, sticky="ew", pady=5)
        
        # 比較功能區域
        comparison_label = ttk.Label(button_frame, text="球員比較", style="Header.TLabel")
        comparison_label.grid(row=7, column=0, sticky="w", pady=(20, 5))
        
        ttk.Button(button_frame, text="使用名稱比較球員", 
                   command=self.run_name_comparison).grid(row=8, column=0, sticky="ew", pady=5)
        
        ttk.Button(button_frame, text="使用 ID 比較球員", 
                   command=self.run_id_comparison).grid(row=9, column=0, sticky="ew", pady=5)
        
        # 設置按鈕寬度
        for i in range(1, 10):
            button_frame.grid_columnconfigure(0, weight=1)
        
        # 創建輸出文本區域
        output_frame = ttk.LabelFrame(self.main_frame, text="執行狀態")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.output_text = tk.Text(output_frame, height=10, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加滾動條
        scrollbar = ttk.Scrollbar(self.output_text, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)
        
        # 創建狀態欄
        self.status_var = tk.StringVar()
        self.status_var.set("就緒")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 檢查目錄
        self.check_directories()
    
    def check_directories(self):
        """檢查並創建所需的目錄"""
        directories = [
            'nba_data', 'nba_data_json', 'nba_analysis', 
            'nba_player_data', 'nba_player_analysis', 'nba_player_comparison'
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.log_output(f"已創建目錄: {directory}")
    
    def log_output(self, message):
        """將訊息記錄到文本區域"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.update()
    
    def run_command(self, command, status_message="執行命令"):
        """執行命令並處理輸出"""
        self.status_var.set(status_message + "...")
        self.log_output(f"正在執行: {' '.join(command)}")
        
        try:
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                text=True, 
                bufsize=1
            )
            
            # 實時顯示輸出
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.log_output(line.strip())
            
            process.stdout.close()
            process.wait()
            
            if process.returncode == 0:
                self.log_output("命令執行成功！")
                self.status_var.set("完成")
            else:
                self.log_output(f"命令執行失敗，返回碼: {process.returncode}")
                self.status_var.set("執行失敗")
        except Exception as e:
            self.log_output(f"發生錯誤: {e}")
            self.status_var.set("錯誤")
    
    def run_basic_scraper(self):
        """執行基本爬蟲"""
        self.run_command(["python", "nba_scraper.py"], "爬取 NBA 基本資料")
    
    def run_advanced_scraper(self):
        """執行進階爬蟲"""
        self.run_command(["python", "nba_advanced_scraper.py"], "爬取 NBA 進階 API 資料")
    
    def run_player_scraper(self):
        """爬取特定球員資料"""
        player_name = simpledialog.askstring("輸入", "請輸入球員名稱:", parent=self.root)
        if player_name:
            self.run_command(["python", "player_specific_scraper.py", player_name], f"爬取球員 {player_name} 資料")
    
    def run_data_analyzer(self):
        """分析 NBA 整體資料"""
        self.run_command(["python", "nba_data_analyzer.py"], "分析 NBA 整體資料")
    
    def run_player_analyzer(self):
        """分析特定球員資料"""
        player_id = simpledialog.askstring("輸入", "請輸入球員 ID:", parent=self.root)
        if player_id:
            self.run_command(["python", "player_specific_analyzer.py", player_id], f"分析球員 ID {player_id} 資料")
    
    def run_name_comparison(self):
        """使用名稱比較球員"""
        player1 = simpledialog.askstring("輸入", "請輸入第一位球員名稱:", parent=self.root)
        if not player1:
            return
        
        player2 = simpledialog.askstring("輸入", "請輸入第二位球員名稱:", parent=self.root)
        if not player2:
            return
        
        self.run_command(
            ["python", "player_name_comparison.py", player1, player2], 
            f"比較球員 {player1} 和 {player2}"
        )
    
    def run_id_comparison(self):
        """使用 ID 比較球員"""
        player1 = simpledialog.askstring("輸入", "請輸入第一位球員 ID:", parent=self.root)
        if not player1:
            return
        
        player2 = simpledialog.askstring("輸入", "請輸入第二位球員 ID:", parent=self.root)
        if not player2:
            return
        
        self.run_command(
            ["python", "player_comparison.py", player1, player2], 
            f"比較球員 ID {player1} 和 {player2}"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = NBAApp(root)
    root.mainloop() 