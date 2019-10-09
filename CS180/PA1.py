#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy
import cv2
import copy
import sys

X_VAL = 1
Y_VAL = 0
F_VAL = 2
PAR_VAL = 3
G_VAL = 4
MATRIX_HEIGHT = 10
MATRIX_WIDTH = 10
direction = None


# In[2]:


'''
Priority Queue class taken from GeeksForGeeks
I modified the delete function and added the find_parent and lowest_similar
functions
https://www.geeksforgeeks.org/priority-queue-in-python/
'''
class PriorityQueue(object): 
    def __init__(self): 
        self.queue = [] 
  
    def __str__(self): 
        return ' '.join([str(i) for i in self.queue]) 
  
    # for checking if the queue is empty 
    def isEmpty(self): 
        return self.queue == []
  
    # for inserting an element in the queue 
    def insert(self, data): 
        self.queue.append(data) 
        
    def find_parent(self,data):
        for i in self.queue:
            if data == [i[Y_VAL], i[X_VAL], i[F_VAL]]:
                return i
            
    def lowest_similar(self, data):
        lowest = None
        #print("ls_data:", data)
        for i in self.queue:
            if data[X_VAL] == i[X_VAL] and data[Y_VAL] == i[Y_VAL]:
                if lowest == None or lowest > i[F_VAL]:
                    lowest = i[F_VAL]
                    
        #print("Queue:", self.queue)
        #print("Lowest:", lowest)
        return lowest
    
    def delete(self): 
        try: 
            min_i= 0
            for i in range(len(self.queue)): 
                if self.queue[i][F_VAL] < self.queue[min_i][F_VAL]: 
                    min_i = i 
            item = self.queue[min_i] 
            del self.queue[min_i] 
            return item 
        except IndexError: 
            print() 
            exit() 


# In[3]:




# In[4]:


def find_start(matrix):
    for i in range(0, len(matrix), 50):
        for j in range(0, len(matrix[i]), 50):
            if(matrix[i][j][0] > 0):
                start = format_coordinates(j, i)
    return start


# In[5]:


def find_end(matrix):
    for i in range(0, len(matrix), 50):
        for j in range(0, len(matrix[i]), 50):
            if(matrix[i][j][2] > 0):
                end = format_coordinates(j, i)
    return end 


# In[39]:


def search(matrix, start, end, algo="UCS", heuristic="MH"):
    open_list = PriorityQueue()
    closed_list = PriorityQueue()
    start.append(1) #F(start)
    start.append([start[Y_VAL], start[X_VAL], 0])
    if algo == "A*" or algo == "GBFS":
        start.append(0) #g(start)
    open_list.insert(start)
    steps = 0
    print("Algorithm:", algo)
   
    while not open_list.isEmpty():
        #print("Open List: ", open_list)
        q = open_list.delete()
        steps += 1
        if q[X_VAL] == end[X_VAL] and q[Y_VAL] == end[Y_VAL]:
            closed_list.insert(q)
            break
        successors = generate_successors(q[X_VAL], q[Y_VAL])
        q_data = get_color_data(matrix, q[X_VAL], q[Y_VAL])
        #print(q_data)
        for successor in successors:
            g = 0
            successor_data = get_color_data(matrix, successor[X_VAL], successor[Y_VAL])
            if algo == "UCS":
                f = get_intensity(q_data, successor_data)
                f += q[F_VAL]
                #print(f)
            elif algo == "GBFS":
                f = calculate_heuristic(successor, end, heuristic)
                g = get_intensity(q_data, successor_data) + q[G_VAL]
            elif algo == "A*":
                g = get_intensity(q_data, successor_data) + q[G_VAL]
                f = g + calculate_heuristic(successor, end, heuristic)
                
                #f += q[F_VAL]
            successor.append(f)
            
            #successor.append([q[Y_VAL], q[X_VAL], q[F_VAL], q[PAR_VAL]])
            successor.append([q[Y_VAL], q[X_VAL], q[F_VAL]])
            
            if algo == "A*" or algo == "GBFS":
                successor.append(g)
            
            will_add = True
            ol_low = open_list.lowest_similar(successor) 
            if not ol_low == None and ol_low <= f:
                will_add = False
            if will_add:
                cl_low = closed_list.lowest_similar(successor) 
                if not cl_low == None and cl_low <= f:
                    will_add = False
            
            if successor_data[0] == 0 and successor_data[1] == 0 and successor_data[2] == 0 :
                will_add = False
            if will_add:
                open_list.insert(successor)
        closed_list.insert(q)
        
    img = copy.copy(matrix)
    curr = q
    attempt_list = copy.deepcopy(closed_list)
    try:
        show_attempts = sys.argv[5]
    except IndexError:
        show_attempts = False
    while not attempt_list.isEmpty() and show_attempts:
        curr = attempt_list.delete()
        if len(curr) >= 4:
            x1 = curr[PAR_VAL][X_VAL] 
            y1 = curr[PAR_VAL][Y_VAL]
        else:
            x1 = start[X_VAL] 
            y1 = start[Y_VAL]
        x2 = curr[X_VAL] 
        y2 = curr[Y_VAL]
        draw_line(img, line_convert(x1), line_convert(y1), 
                  line_convert(x2), line_convert(y2), color=(139,139,139))
    curr = q
    while curr != start:
        if len(curr) >= 4:
            x1 = curr[PAR_VAL][X_VAL] 
            y1 = curr[PAR_VAL][Y_VAL]
        else:
            x1 = start[X_VAL] 
            y1 = start[Y_VAL]
        x2 = curr[X_VAL] 
        y2 = curr[Y_VAL]
        draw_line(img, line_convert(x1), line_convert(y1), 
                  line_convert(x2), line_convert(y2))
        curr = closed_list.find_parent(curr[PAR_VAL])
        

        
    print("Nodes Expanded: ", steps)
    if len(q) == 5:
        print("Line Distance:", q[G_VAL])
    else:
        print("Line distance:", q[F_VAL])
    cv2.startWindowThread()
    cv2.imshow("image", img)
    cv2.imwrite(sys.argv[3], img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    img = matrix
            
        
        
    
    
    


# In[7]:


def line_convert(n):
    return (n * 50) + 25


# In[8]:


def check_and_add(queue, successor):
    for i in queue:
        if successor[X_VAL] == i[X_VAL] and successor[Y_VAL] == i[Y_VAL]:
            if successor[F_VAL] < i[F_VAL]:
                arr = []
                arr[X_VAL] = successor[X_VAL]
                arr[Y_VAL] = successor[Y_VAL]
                arr[F_VAL] = successor[F_VAL]
                queue.insert(arr)
    return queue


# In[9]:


def format_coordinates(x, y):
     return [y //50, x//50]


# In[10]:


def convert_coordinates(x, y):
    return [y * 50, x * 50]


# In[11]:


'''
returns color matrix where channels are BGR
'''
def get_color_data(matrix, x, y):
    return matrix[y * 50][x * 50]


# In[12]:


def generate_successors(x, y):
    successors = []
    if y < MATRIX_HEIGHT - 1:
        successors.append([y + 1, x])
    if y > 0:
        successors.append([y - 1, x])
    if x < MATRIX_WIDTH -1:
        successors.append([y, x + 1])
    if x > 0:
        successors.append([y, x - 1])
    return successors 
        


# In[13]:


def get_intensity(i, j):
    x = int(i[1])
    y = int(j[1])
    intensity = abs(x - y)
    return intensity


# In[14]:


def draw_line(image, x1, y1, x2, y2, color=(255,255,255)):
    img = cv2.line(image, (x1, y1), (x2, y2), color, 1)
    return img


# In[15]:


def calculate_heuristic(curr, end, heuristic):
    global direction
    if heuristic == "MH":
        return abs(curr[X_VAL] - end[X_VAL] + abs(curr[Y_VAL] - end[Y_VAL]))
    elif heuristic == "FDD":
        if direction == None:
            if abs(curr[X_VAL] - end[X_VAL] ) > abs(curr[Y_VAL] - end[Y_VAL]):
                direction = "X"
            else:
                direction = "Y"
        if direction == "X":
            return abs(curr[X_VAL] - end[X_VAL] )
        else:
            return abs(curr[Y_VAL] - end[Y_VAL] )
    elif heuristic == "DD":
        return max(abs(curr[X_VAL] - end[X_VAL]), abs(curr[Y_VAL] - end[Y_VAL]))
    


# In[34]:


matrix = cv2.imread(sys.argv[1], 1)
start = find_start(matrix)
end = find_end(matrix)
#Algo options = UCS, GBFS, A*
algo_arg = int(sys.argv[2])
algo = ""
if algo_arg == 0:
    algo = "UCS"
elif algo_arg == 1:
    algo = "GBFS"
else:
    algo = "A*"


try:
    heuristic = sys.argv[4]
except IndexError:
    heuristic = "FDD"

#Heuristic Options = MH, DD, FDD
print("Heuristic: ", end="")
if heuristic == "FDD":
    print("Fixed Dimensional Distance")
elif heuristic == "MH":
    print("Manhattan Distance")
elif heuristic == "DD":
    print("Diagonal Distance")
else:
    print("Unknown Distance")

search(matrix, start, end, algo, heuristic=heuristic)


# # Run Area

# In[35]:




# In[ ]:





# In[ ]:





# In[ ]:




