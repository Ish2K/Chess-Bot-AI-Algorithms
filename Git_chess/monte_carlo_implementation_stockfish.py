'''
 *    author:  Ishaan Gupta
 *    created: 9.11.2020 12:04:06       
'''

import chess
import chess.pgn
import chess.engine
import random
import time
import heapq
from math import log,sqrt,e,inf

depth = 0
engine = chess.engine.SimpleEngine.popen_uci(r'C:\Users\ishaa\Desktop\chess_engine\stockfish-11-win\Windows\stockfish_20011801_x64.exe')

class node():
    def __init__(self):
        self.state = chess.Board()
        self.children = set()
        self.parent = None
        self.N = 0
        self.n = 0
        self.v = 0
        self.ucb = 0
    def __lt__(self,other):
        return self.ucb<other.ucb
def ucb1(curr_node):
    ans = curr_node.v+2*(sqrt(log(curr_node.N+e+(10**-6))/(curr_node.n+(random.randint(3,7)))))
    return ans

def rollout(curr_node):
    global depth
    global engine
    if(curr_node.state.is_game_over()):
        board = curr_node.state
        if(board.result()=='1-0'):
            #print("h1")
            return (1,curr_node)
        elif(board.result()=='0-1'):
            #print("h2")
            return (-1,curr_node)
        else:
            return (0.5,curr_node)
    depth+=1
    all_moves = [curr_node.state.san(i) for i in list(curr_node.state.legal_moves)]
    
    result = engine.play(curr_node.state, chess.engine.Limit(time=0.001))
    move = curr_node.state.san(result.move)
    
    tmp_state = chess.Board(curr_node.state.fen())
    tmp_state.push_san(move)

    to_use = None
    
    for i in all_moves:
        tmp_state1 = chess.Board(curr_node.state.fen())
        tmp_state1.push_san(i)
        child = node()
        child.state = tmp_state1
        child.parent = curr_node
        curr_node.children.add(child)
        if(child.state==tmp_state):
            to_use = child
            break
    return rollout(to_use)

def expand(curr_node,white):
    global depth
    if(len(curr_node.children)==0):
        return curr_node
    depth+=1
    max_ucb = -inf
    if(white):
        heap = list(curr_node.children)
        sel_child = heapq._heappop_max(heap)
        return(expand(sel_child,0))

    else:
        heap = list(curr_node.children)
        sel_child = heapq.heappop(heap)
        return expand(sel_child,1)

def rollback(curr_node,reward):
    global depth
    sel_child = None
    while(curr_node.parent!=None):
        curr_node.N+=1
        curr_node.n+=1
        curr_node.v+=reward
        curr_node.ucb = ucb1(curr_node)
        if(depth==1):
            sel_child = curr_node
        curr_node = curr_node.parent
        depth-=1
        
    return (sel_child,curr_node)

def mcts_pred(curr_node,over,white,iterations=10):
    global depth
    if(over):
        return -1
    all_moves = [curr_node.state.san(i) for i in list(curr_node.state.legal_moves)]
    map_state_move = dict()
    
    for i in all_moves:
        tmp_state = chess.Board(curr_node.state.fen())
        tmp_state.push_san(i)
        child = node()
        child.state = tmp_state
        child.parent = curr_node
        curr_node.children.add(child)
        map_state_move[child] = i
    heap = list(curr_node.children)
    
    while(iterations>0):
        if(white):
            
            sel_child = heapq._heappop_max(heap)
            sel_child.parent = curr_node
            depth = 1
            st = time.time()
            
            st = time.time()
            reward,state = rollout(sel_child)
            print(time.time()-st)
            sel_child,curr_node = rollback(state,reward)
            heapq.heappush(heap,sel_child)
            iterations-=1
        else:
            sel_child = heapq.heappop(heap)
            depth = 1
            reward,state = rollout(sel_child)
            print(depth)
            sel_child,curr_node = rollback(state,reward)
            
            heapq.heappush(heap,sel_child)
            iterations-=1
    if(white):
        
        sel_child = heapq._heappop_max(heap)
        selected_move = map_state_move[sel_child]
        return selected_move
    else:
        sel_child = heapq.heappop(heap)
        selected_move = map_state_move[sel_child]
        return selected_move
def start():
    board = chess.Board()
    white = 1
    moves = 0
    pgn = []
    game = chess.pgn.Game()
    evaluations = []
    sm = 0
    cnt = 0
    while((not board.is_game_over())):
        all_moves = [board.san(i) for i in list(board.legal_moves)]
        root = node()
        root.state = board
        result = mcts_pred(root,board.is_game_over(),white)
        board.push_san(result)
        print(result)
        pgn.append(result)
        white ^= 1
        moves+=1

    print(board)
    print(" ".join(pgn))
    print()
    #print(evaluations)
    print(board.result())
    game.headers["Result"] = board.result()

if __name__=='__main__':
    start()
