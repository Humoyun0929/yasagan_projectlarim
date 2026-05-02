import tkinter as tk

SIZE = 8
CELL = 70

EMPTY = 0
BLACK = 1
WHITE = 2
BLACK_KING = 3
WHITE_KING = 4


class Checkers:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=SIZE*CELL, height=SIZE*CELL)
        self.canvas.pack()

        self.board = [[EMPTY]*SIZE for _ in range(SIZE)]

        self.turn = WHITE   # ⭐ OQLAR BOSHLAYDI

        self.selected = None
        self.moves = []

        self.init_board()
        self.draw()

        self.canvas.bind("<Button-1>", self.click)

    def init_board(self):
        for r in range(3):
            for c in range(SIZE):
                if (r+c)%2==1:
                    self.board[r][c]=WHITE

        for r in range(5,8):
            for c in range(SIZE):
                if (r+c)%2==1:
                    self.board[r][c]=BLACK

    def draw(self):
        self.canvas.delete("all")

        for r in range(SIZE):
            for c in range(SIZE):
                x1,y1=c*CELL,r*CELL
                x2,y2=x1+CELL,y1+CELL

                color = "#EEE" if (r+c)%2==0 else "#555"
                self.canvas.create_rectangle(x1,y1,x2,y2,fill=color)

                if (r,c) in self.moves:
                    self.canvas.create_rectangle(x1,y1,x2,y2,fill="green")

                p=self.board[r][c]
                if p!=EMPTY:
                    fill="black" if p in (BLACK,BLACK_KING) else "white"
                    self.canvas.create_oval(x1+10,y1+10,x2-10,y2-10,fill=fill)

                    if p in (BLACK_KING,WHITE_KING):
                        self.canvas.create_text((x1+x2)//2,(y1+y2)//2,text="K",fill="gold")

    # ================= CLICK =================
    def click(self,event):
        r = event.y//CELL
        c = event.x//CELL

        if self.selected:
            if (r,c) in self.moves:
                cont = self.make_move(self.selected,(r,c))

                if cont:
                    self.selected=(r,c)
                    self.moves=self.get_moves(r,c,only_capture=True)
                else:
                    self.selected=None
                    self.moves=[]
                    self.turn = WHITE if self.turn==BLACK else BLACK
            else:
                self.selected=None
                self.moves=[]
        else:
            if self.is_own(r,c):
                self.selected=(r,c)
                self.moves=self.get_moves(r,c)

        self.draw()
        self.check_win()

    def is_own(self,r,c):
        p=self.board[r][c]
        return (self.turn==BLACK and p in (BLACK,BLACK_KING)) or \
               (self.turn==WHITE and p in (WHITE,WHITE_KING))

    def same(self,a,b):
        return (a in (BLACK,BLACK_KING) and b in (BLACK,BLACK_KING)) or \
               (a in (WHITE,WHITE_KING) and b in (WHITE,WHITE_KING))

    # ================= CAPTURE =================
    def get_all_captures(self):
        all_caps={}
        max_len=0

        for r in range(SIZE):
            for c in range(SIZE):
                if self.is_own(r,c):
                    caps=self.find_captures(r,c,self.board)
                    if caps:
                        m=max(len(p) for p in caps)
                        if m>max_len:
                            max_len=m
                            all_caps={(r,c):caps}
                        elif m==max_len:
                            all_caps[(r,c)]=caps

        return all_caps,max_len

    def find_captures(self,r,c,board):
        piece=board[r][c]
        results=[]
        dirs=[(-1,-1),(-1,1),(1,-1),(1,1)]

        # ===== KING =====
        if piece in (BLACK_KING,WHITE_KING):
            for dr,dc in dirs:
                rr,cc=r+dr,c+dc
                enemy=None

                while 0<=rr<SIZE and 0<=cc<SIZE:
                    if board[rr][cc]!=EMPTY:
                        if enemy is None and not self.same(piece,board[rr][cc]):
                            enemy=(rr,cc)
                        else:
                            break
                    else:
                        if enemy:
                            new=[row[:] for row in board]
                            er,ec=enemy

                            new[r][c]=EMPTY
                            new[er][ec]=EMPTY
                            new[rr][cc]=piece

                            further=self.find_captures(rr,cc,new)
                            if further:
                                for f in further:
                                    results.append([(rr,cc)]+f)
                            else:
                                results.append([(rr,cc)])

                    rr+=dr
                    cc+=dc

            return results

        # ===== NORMAL =====
        for dr,dc in dirs:
            r1,c1=r+dr,c+dc
            r2,c2=r+2*dr,c+2*dc

            if 0<=r2<SIZE and 0<=c2<SIZE:
                if board[r1][c1]!=EMPTY and not self.same(piece,board[r1][c1]) and board[r2][c2]==EMPTY:
                    new=[row[:] for row in board]

                    new[r][c]=EMPTY
                    new[r1][c1]=EMPTY
                    new[r2][c2]=piece

                    further=self.find_captures(r2,c2,new)
                    if further:
                        for f in further:
                            results.append([(r2,c2)]+f)
                    else:
                        results.append([(r2,c2)])

        return results

    # ================= MOVES =================
    def get_moves(self,r,c,only_capture=False):
        caps,max_len=self.get_all_captures()

        if max_len>0:
            if (r,c) in caps:
                return [p[0] for p in caps[(r,c)]]
            return []

        if only_capture:
            return []

        moves=[]
        p=self.board[r][c]
        dirs=[(-1,-1),(-1,1),(1,-1),(1,1)]

        for dr,dc in dirs:
            rr,cc=r+dr,c+dc
            if 0<=rr<SIZE and 0<=cc<SIZE and self.board[rr][cc]==EMPTY:
                if p==BLACK and dr==-1: moves.append((rr,cc))
                elif p==WHITE and dr==1: moves.append((rr,cc))
                elif p in (BLACK_KING,WHITE_KING): moves.append((rr,cc))

        return moves

    # ================= MOVE EXEC =================
    def make_move(self,start,end):
        r1,c1=start
        r2,c2=end
        p=self.board[r1][c1]

        dr=(r2-r1)//max(1,abs(r2-r1))
        dc=(c2-c1)//max(1,abs(c2-c1))

        captured=False
        r,c=r1+dr,c1+dc

        while (r,c)!=(r2,c2):
            if self.board[r][c]!=EMPTY:
                self.board[r][c]=EMPTY
                captured=True
                break
            r+=dr
            c+=dc

        self.board[r2][c2]=p
        self.board[r1][c1]=EMPTY

        # promote
        if p==BLACK and r2==0:
            self.board[r2][c2]=BLACK_KING
        if p==WHITE and r2==SIZE-1:
            self.board[r2][c2]=WHITE_KING

        if captured:
            more=self.find_captures(r2,c2,self.board)
            if more:
                return True

        return False

    # ================= WIN =================
    def check_win(self):
        b=any(p in (BLACK,BLACK_KING) for row in self.board for p in row)
        w=any(p in (WHITE,WHITE_KING) for row in self.board for p in row)

        if not b:
            self.end("Oq yutdi!")
        elif not w:
            self.end("Qora yutdi!")

    def end(self,text):
        self.canvas.create_text(280,280,text=text,fill="yellow",font=("Arial",24))
        self.canvas.unbind("<Button-1>")


root=tk.Tk()
root.title("Shashka FINAL PRO")
Checkers(root)
root.mainloop()