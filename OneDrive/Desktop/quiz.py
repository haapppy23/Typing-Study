import tkinter as tk
from tkinter import messagebox
import json
import random
import os

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("리눅스 마스터/네트워크 퀴즈")
        self.root.geometry("600x600") # 타이핑 칸을 위해 높이 약간 증가
        
        # 데이터 로드
        self.filename = 'quiz_data.json'
        self.data = self.load_data()
        if not self.data:
            return
        
        self.all_answers = list(set([item['answer'] for item in self.data]))
        
        # 퀴즈 상태 변수
        self.current_index = 0
        self.total_questions = len(self.data)
        self.results = [0] * self.total_questions # 문제 이동을 위해 리스트로 점수 관리
        self.current_correct_answer = ""
        
        # UI 변수
        self.selected_var = tk.StringVar() 
        self.selected_var.set(None)

        # UI 구성 및 첫 문제 시작
        self.setup_ui()
        self.display_question()

    def load_data(self):
        if not os.path.exists(self.filename):
            messagebox.showerror("에러", f"'{self.filename}' 파일이 없습니다.\n같은 폴더에 파일을 넣어주세요.")
            self.root.destroy()
            return []
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("에러", f"JSON 파일을 읽는 중 오류 발생:\n{e}")
            self.root.destroy()
            return []

    def setup_ui(self):
        # 1. 진행 상황
        self.lbl_progress = tk.Label(self.root, text="", font=("Arial", 10), fg="gray")
        self.lbl_progress.pack(pady=10)

        # 2. 문제 표시
        self.lbl_question = tk.Label(self.root, text="문제 로딩 중...", font=("Arial", 14, "bold"), wraplength=550)
        self.lbl_question.pack(pady=10)

        # 3. 객관식 라디오 버튼 프레임
        self.frame_options = tk.Frame(self.root)
        self.frame_options.pack(pady=5, fill="both", expand=True)

        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(self.frame_options, text="", variable=self.selected_var, 
                                value="", font=("Arial", 12), wraplength=500, justify="left")
            rb.pack(anchor="w", padx=50, pady=5)
            self.radio_buttons.append(rb)

        # 4. 객관식 피드백
        self.lbl_feedback = tk.Label(self.root, text="", font=("Arial", 12, "bold"))
        self.lbl_feedback.pack(pady=5)

        # 5. 타이핑 연습 프레임 (초기에는 숨김)
        self.frame_typing = tk.Frame(self.root)
        self.lbl_typing_prompt = tk.Label(self.frame_typing, text="정답을 직접 타이핑해보세요:", font=("Arial", 11, "bold"))
        self.lbl_typing_prompt.pack()
        
        self.entry_typing = tk.Entry(self.frame_typing, font=("Arial", 14), width=25, justify="center")
        self.entry_typing.pack(pady=5)
        self.entry_typing.bind("<Return>", lambda event: self.check_typing()) # 엔터키로 확인 가능
        
        self.lbl_typing_feedback = tk.Label(self.frame_typing, text="", font=("Arial", 10))
        self.lbl_typing_feedback.pack()

        # 6. 하단 버튼 프레임 (이전 문제 / 액션 버튼)
        self.frame_buttons = tk.Frame(self.root)
        self.frame_buttons.pack(pady=15)

        self.btn_prev = tk.Button(self.frame_buttons, text="< 이전 문제", command=self.prev_question, 
                                  font=("Arial", 12), bg="#eeeeee", width=12)
        self.btn_prev.pack(side="left", padx=10)

        self.btn_action = tk.Button(self.frame_buttons, text="정답 확인", command=self.check_answer, 
                                    font=("Arial", 12), bg="#dddddd", width=12)
        self.btn_action.pack(side="right", padx=10)

    def display_question(self):
        if self.current_index >= self.total_questions:
            self.show_final_result()
            return

        # UI 초기화
        self.selected_var.set(None)
        self.lbl_feedback.config(text="")
        
        # 타이핑 관련 UI 숨기기 및 초기화
        self.frame_typing.pack_forget()
        self.entry_typing.delete(0, tk.END)
        self.lbl_typing_feedback.config(text="")
        
        # 버튼 상태 초기화
        self.btn_action.config(text="정답 확인", command=self.check_answer, state="normal")
        self.btn_prev.config(state="normal" if self.current_index > 0 else "disabled")
        
        for rb in self.radio_buttons:
            rb.config(state="normal") # 라디오 버튼 활성화

        # 현재 문제 로드
        item = self.data[self.current_index]
        self.current_correct_answer = item['answer']
        
        self.lbl_progress.config(text=f"문제 {self.current_index + 1} / {self.total_questions}")
        self.lbl_question.config(text=item['question'])

        wrong_pool = [ans for ans in self.all_answers if ans != self.current_correct_answer]
        if len(wrong_pool) < 3:
            distractors = wrong_pool
        else:
            distractors = random.sample(wrong_pool, 3)
            
        options = distractors + [self.current_correct_answer]
        random.shuffle(options)

        for i, rb in enumerate(self.radio_buttons):
            rb.config(text=f"{i+1}. {options[i]}", value=options[i], fg="black", selectcolor="white")

    def check_answer(self):
        user_choice = self.selected_var.get()

        if not user_choice:
            messagebox.showwarning("경고", "보기를 선택해주세요!")
            return

        # 객관식 채점 및 배열 기록
        if user_choice == self.current_correct_answer:
            self.results[self.current_index] = 1
            self.lbl_feedback.config(text="✅ 정답입니다!", fg="green")
        else:
            self.results[self.current_index] = 0
            self.lbl_feedback.config(text=f"❌ 오답! 정답은: {self.current_correct_answer}", fg="red")

        # 라디오 버튼 클릭 방지 처리
        for rb in self.radio_buttons:
            rb.config(state="disabled")

        # 타이핑 UI 표시
        self.frame_typing.pack(pady=10)
        self.entry_typing.focus() # 텍스트 박스에 바로 커서 활성화
        
        # 메인 버튼을 '입력 확인'으로 변경
        self.btn_action.config(text="타이핑 확인", command=self.check_typing)

    def check_typing(self):
        typed_text = self.entry_typing.get().strip()
        
        # 대소문자 구분 없이 확인 (리눅스 명령어 등 편의를 위해)
        if typed_text.lower() == self.current_correct_answer.lower():
            self.lbl_typing_feedback.config(text="👍 완벽합니다!", fg="blue")
            self.btn_action.config(text="다음 문제 >", command=self.next_question)
            
            # 엔터 치면 바로 넘어갈 수 있게 바인딩 변경
            self.entry_typing.bind("<Return>", lambda event: self.next_question())
        else:
            self.lbl_typing_feedback.config(text=f"오타가 있습니다. 다시 입력해주세요.\n(정답: {self.current_correct_answer})", fg="red")

    def next_question(self):
        self.current_index += 1
        self.display_question()

    def prev_question(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_question()

    def show_final_result(self):
        self.lbl_progress.pack_forget()
        self.frame_options.pack_forget()
        self.frame_typing.pack_forget()
        self.frame_buttons.pack_forget()
        self.lbl_feedback.pack_forget()

        final_score = sum(self.results)
        percentage = (final_score / self.total_questions) * 100 if self.total_questions > 0 else 0
        result_text = f"퀴즈 종료!\n\n총 점수: {final_score} / {self.total_questions}\n({percentage:.1f}%)"
        
        self.lbl_question.config(text=result_text)
        
        btn_quit = tk.Button(self.root, text="종료", command=self.root.quit, font=("Arial", 12), bg="#ffcccc", width=15)
        btn_quit.pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
