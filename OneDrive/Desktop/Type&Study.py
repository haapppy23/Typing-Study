import tkinter as tk
from tkinter import messagebox
import json
import os
import warnings
import subprocess 
import random
import math

warnings.filterwarnings("ignore", category=UserWarning)
import pygame

class MemorizeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("자격증 필기 합격 프리패스 - 무한 빡공 암기장")
        self.root.geometry("850x700")

        # 🎵 Pygame 사운드 초기화
        pygame.mixer.init()
        try:
            self.sound_typing = pygame.mixer.Sound("click.wav.mp3") 
        except Exception as e:
            self.sound_typing = None
            print(f"소리 파일을 불러오지 못했습니다: {e}")

        # 사용자 제공 JSON 파일 로드
        self.filename = 'quiz_data.json'
        self.all_data = self.load_data()
        self.current_data = []
        
        self.current_index = 0
        self.rep_count = 0
        self.target_reps = 1  
        self.chunk_size = 30 # 한 세트당 문제 개수 (원하는 대로 수정 가능)

        if not self.all_data:
            return

        self.main_frame = tk.Frame(self.root)
        self.study_frame = tk.Frame(self.root)
        self.test_frame = tk.Frame(self.root)
        
        self.show_main_menu()

    def load_data(self):
        if not os.path.exists(self.filename):
            messagebox.showerror("에러", f"{self.filename} 파일이 같은 폴더에 없습니다!\n문제를 먼저 준비해주세요.")
            self.root.destroy()
            return []
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("에러", f"파일 로드 오류:\n{e}")
            self.root.destroy()
            return []

    # ==========================================
    # ✨ 메모장 실행 기능
    # ==========================================
    def open_notepad(self):
        try:
            subprocess.Popen(["notepad.exe"])
        except Exception as e:
            messagebox.showerror("에러", f"메모장을 열 수 없습니다: {e}")

    # ==========================================
    # 🎵 사운드 이펙트 모듈
    # ==========================================
    def play_typing_sound(self, event=None):
        if event and event.keysym in ['Return', 'Shift_L', 'Shift_R', 'Caps_Lock', 'Tab']:
            return
        if self.sound_typing:
            self.sound_typing.play() 

    def play_success_sound(self):
        pass 

    def play_error_sound(self):
        pass 

    # ==========================================
    # 1. 메인 메뉴 (✨ 범용 자동 분할 세팅 ✨)
    # ==========================================
    def show_main_menu(self):
        self.study_frame.pack_forget()
        self.test_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)

        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tk.Label(self.main_frame, text="🔥 자격증 만능 빡공 암기장 🔥", font=("Arial", 20, "bold")).pack(pady=20)
        tk.Label(self.main_frame, text="학습할 세트를 선택하세요 (자동 분할)", font=("Arial", 12)).pack(pady=5)

        # JSON 데이터를 chunk_size 만큼 자동으로 쪼갬
        chunks = [self.all_data[i:i + self.chunk_size] for i in range(0, len(self.all_data), self.chunk_size)]

        frame_container = tk.Frame(self.main_frame)
        frame_container.pack(pady=10)
        
        left_frame = tk.Frame(frame_container)
        left_frame.pack(side="left", anchor="n", padx=15)
        
        right_frame = tk.Frame(frame_container)
        right_frame.pack(side="left", anchor="n", padx=15)

        half_point = math.ceil(len(chunks) / 2)

        for idx, chunk in enumerate(chunks):
            start_num = idx * self.chunk_size + 1
            end_num = start_num + len(chunk) - 1
            title = f"Set {idx + 1} ({start_num}~{end_num}번)"
            
            parent = left_frame if idx < half_point else right_frame
            
            row_frame = tk.Frame(parent)
            row_frame.pack(pady=8, fill="x")
            
            tk.Label(row_frame, text=title, font=("Arial", 11, "bold"), width=20, anchor="w").pack(side="left", padx=5)
            tk.Button(row_frame, text="✍️ 자유 빡공", bg="#e6f2ff", command=lambda c=chunk: self.start_study(c)).pack(side="left", padx=3)
            tk.Button(row_frame, text="🔥 실전", bg="#ffe6e6", command=lambda c=chunk: self.start_test(c)).pack(side="left", padx=3)

        tk.Button(self.main_frame, text="📝 오답노트 (메모장 켜기)", font=("Arial", 12, "bold"), bg="#fff0b3", command=self.open_notepad).pack(pady=20)

    # ==========================================
    # 2. 자유 빡공 모드 (문제 칸 채점 안 함!)
    # ==========================================
    def start_study(self, chunk_data):
        self.current_data = chunk_data
        self.current_index = 0
        self.rep_count = 0
        
        self.main_frame.pack_forget()
        self.study_frame.pack(fill="both", expand=True)
        self.setup_study_ui()
        self.display_study_question()

    def setup_study_ui(self):
        for widget in self.study_frame.winfo_children():
            widget.destroy()

        self.lbl_s_progress = tk.Label(self.study_frame, text="", font=("Arial", 10), fg="gray")
        self.lbl_s_progress.pack(pady=5)

        tk.Label(self.study_frame, text="[원본 지문]", font=("Arial", 12, "bold"), fg="purple").pack(pady=5)
        self.lbl_s_question = tk.Label(self.study_frame, text="", font=("Arial", 16, "bold"), fg="#333333", wraplength=700)
        self.lbl_s_question.pack(pady=10)

        # ✨ 강제 타이핑이 아닌 맘대로 쓰는 자유 타이핑 공간!
        tk.Label(self.study_frame, text="[자유 메모/타이핑 (채점 안 함)]", font=("Arial", 10, "bold"), fg="gray").pack(pady=(15, 5))
        self.entry_q = tk.Entry(self.study_frame, font=("Arial", 14), width=60)
        self.entry_q.pack(pady=5)
        self.entry_q.bind("<KeyPress>", self.play_typing_sound)

        tk.Label(self.study_frame, text="[정답 입력 (엔터)]", font=("Arial", 12, "bold"), fg="blue").pack(pady=(15, 5))
        self.lbl_s_answer = tk.Label(self.study_frame, text="", font=("Arial", 16, "bold"), fg="blue")
        self.lbl_s_answer.pack(pady=5)

        self.entry_a = tk.Entry(self.study_frame, font=("Arial", 16), width=30, justify="center")
        self.entry_a.pack(pady=5)
        self.entry_a.bind("<Return>", self.check_study_typing)
        self.entry_a.bind("<KeyPress>", self.play_typing_sound)

        self.lbl_s_feedback = tk.Label(self.study_frame, text="지문을 보며 자유롭게 치시고, 정답만 똑같이 맞춰보세요!", font=("Arial", 12))
        self.lbl_s_feedback.pack(pady=15)

        nav_frame = tk.Frame(self.study_frame)
        nav_frame.pack(pady=10)
        
        tk.Button(nav_frame, text="◀ 이전 문제", command=self.prev_study_question, width=15, font=("Arial", 10, "bold")).pack(side="left", padx=10)
        tk.Button(nav_frame, text="건너뛰기 ▶", command=self.skip_study_question, width=15, font=("Arial", 10, "bold")).pack(side="left", padx=10)

        bottom_frame = tk.Frame(self.study_frame)
        bottom_frame.pack(pady=15)
        
        tk.Button(bottom_frame, text="메인 메뉴로", command=self.show_main_menu).pack(side="left", padx=10)
        tk.Button(bottom_frame, text="📝 메모장 켜기", bg="#fff0b3", command=self.open_notepad).pack(side="left", padx=10)

    def display_study_question(self):
        if self.current_index >= len(self.current_data):
            self.play_success_sound()
            messagebox.showinfo("완료", "이 세트의 빡공 모드를 마쳤습니다!")
            self.show_main_menu()
            return

        item = self.current_data[self.current_index]
        self.current_q = item['question']
        self.current_a = item['answer']
        self.rep_count = 0

        self.lbl_s_progress.config(text=f"진행도: {self.current_index + 1} / {len(self.current_data)}")
        self.lbl_s_question.config(text=self.current_q)
        self.lbl_s_answer.config(text=f"힌트: {self.current_a}")
        
        self.entry_q.delete(0, tk.END)
        self.entry_a.delete(0, tk.END)
        self.lbl_s_feedback.config(text="지문을 보며 자유롭게 치시고, 정답만 똑같이 맞춰보세요!", fg="black")
        
        self.entry_q.focus()

    def check_study_typing(self, event=None):
        typed_a = self.entry_a.get().strip()

        if typed_a == self.current_a:
            self.play_success_sound()
            self.entry_q.delete(0, tk.END)
            self.entry_a.delete(0, tk.END)
            
            self.lbl_s_feedback.config(text="👍 정답입니다! 패스!", fg="green")
            self.root.after(400, self.next_study_question)
        else:
            self.play_error_sound()
            self.lbl_s_feedback.config(text="❌ 정답에 오타가 있습니다! 다시 확인해 주세요.", fg="red")

    def next_study_question(self):
        self.current_index += 1
        self.display_study_question()

    def prev_study_question(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_study_question()
        else:
            messagebox.showinfo("알림", "첫 번째 문제입니다!")

    def skip_study_question(self):
        self.next_study_question()

    # ==========================================
    # 3. 실전 테스트 모드 (✨ 무작위 셔플 적용! ✨)
    # ==========================================
    def start_test(self, chunk_data):
        self.current_data = list(chunk_data) 
        random.shuffle(self.current_data)
        
        self.current_index = 0
        self.is_correction_mode = False
        
        self.main_frame.pack_forget()
        self.test_frame.pack(fill="both", expand=True)
        self.setup_test_ui()
        self.display_test_question()

    def setup_test_ui(self):
        for widget in self.test_frame.winfo_children():
            widget.destroy()

        self.lbl_t_progress = tk.Label(self.test_frame, text="", font=("Arial", 10), fg="gray")
        self.lbl_t_progress.pack(pady=10)

        tk.Label(self.test_frame, text="🚨 실전 테스트 (무작위 출제) 🚨", font=("Arial", 16, "bold"), fg="red").pack(pady=10)

        self.lbl_t_question = tk.Label(self.test_frame, text="", font=("Arial", 16, "bold"), wraplength=700, fg="#333333")
        self.lbl_t_question.pack(pady=30)

        self.lbl_t_correction = tk.Label(self.test_frame, text="", font=("Arial", 14, "bold"), fg="blue")
        self.lbl_t_correction.pack(pady=10)

        self.entry_t = tk.Entry(self.test_frame, font=("Arial", 18), width=30, justify="center")
        self.entry_t.pack(pady=10)
        self.entry_t.bind("<Return>", self.check_test_typing)
        self.entry_t.bind("<KeyPress>", self.play_typing_sound)

        self.lbl_t_feedback = tk.Label(self.test_frame, text="정답을 입력하고 엔터를 누르세요.", font=("Arial", 12))
        self.lbl_t_feedback.pack(pady=10)

        nav_frame_t = tk.Frame(self.test_frame)
        nav_frame_t.pack(pady=10)
        
        tk.Button(nav_frame_t, text="◀ 이전 문제", command=self.prev_test_question, width=15, font=("Arial", 10, "bold")).pack(side="left", padx=10)
        tk.Button(nav_frame_t, text="건너뛰기 ▶", command=self.skip_test_question, width=15, font=("Arial", 10, "bold")).pack(side="left", padx=10)

        bottom_frame_t = tk.Frame(self.test_frame)
        bottom_frame_t.pack(pady=20)

        tk.Button(bottom_frame_t, text="메인 메뉴로 포기", command=self.show_main_menu).pack(side="left", padx=10)
        tk.Button(bottom_frame_t, text="📝 메모장 켜기", bg="#fff0b3", command=self.open_notepad).pack(side="left", padx=10)

    def display_test_question(self):
        if self.current_index >= len(self.current_data):
            self.play_success_sound()
            messagebox.showinfo("테스트 완료", "고생하셨습니다! 실전 테스트를 모두 마쳤습니다.")
            self.show_main_menu()
            return

        item = self.current_data[self.current_index]
        self.current_q = item['question']
        self.current_a = item['answer']
        self.is_correction_mode = False

        self.lbl_t_progress.config(text=f"진행도: {self.current_index + 1} / {len(self.current_data)}")
        self.lbl_t_question.config(text=self.current_q)
        self.lbl_t_correction.config(text="")
        self.lbl_t_feedback.config(text="정답을 입력하고 엔터를 누르세요.", fg="black")
        
        self.entry_t.delete(0, tk.END)
        self.entry_t.focus()

    def check_test_typing(self, event=None):
        typed_a = self.entry_t.get().strip()

        if self.is_correction_mode:
            if typed_a == self.current_a:
                self.play_success_sound()
                self.lbl_t_feedback.config(text="확인 완료! 다음 문제로 넘어갑니다.", fg="green")
                self.root.after(400, self.next_test_question)
            else:
                self.play_error_sound()
                self.lbl_t_feedback.config(text="정답을 정확히 똑같이 따라 쳐주세요!", fg="red")
            return

        if typed_a == self.current_a:
            self.play_success_sound()
            self.lbl_t_feedback.config(text="⭕ 정답입니다! 패스!", fg="green")
            self.root.after(400, self.next_test_question)
        else:
            self.play_error_sound()
            self.is_correction_mode = True
            self.lbl_t_feedback.config(text="❌ 틀렸습니다! 아래 정답을 똑같이 한 번 타이핑하고 넘어가세요.", fg="red")
            self.lbl_t_correction.config(text=f"정답: {self.current_a}")
            self.entry_t.delete(0, tk.END)

    def next_test_question(self):
        self.current_index += 1
        self.display_test_question()

    def prev_test_question(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_test_question()
        else:
            messagebox.showinfo("알림", "첫 번째 문제입니다!")

    def skip_test_question(self):
        self.next_test_question()

if __name__ == "__main__":
    root = tk.Tk()
    app = MemorizeApp(root)
    root.mainloop()