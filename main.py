from logicPlan import *
from random import randint




class TwoDimensionArray:
    def __init__(self,x,y,initialnum=0):
        self.x=x
        self.y=y
        self.array=[]
        for i in range(0,(x+2)*(y+2)):
            self.array.append(initialnum)
    def __getitem__(self,index):
        x, y = index
        if x<=self.x+1 and x>=0 and y<=self.y+1 and y>=0:
            return self.array[(self.y+2)*x+y]
        else:
            return None
    def __setitem__(self,index,item):
        x, y = index
        if x<=self.x+1 and x>=0 and y<=self.y+1 and y>=0:
            self.array[(self.y+2)*x+y] = item
    
    def pick_Num(self,target_item):
        while True:
            pickCorr = (randint(1,self.x), randint(1,self.y))
            if self.__getitem__(pickCorr) == target_item:
                return pickCorr
            





class MineSweeper:
    def __init__(self,x,y,mine_num):
        assert(x>0 and y>0 and x*y > mine_num)
        
        ## pubilc info
        self.x=x
        self.y=y
        self.mine_num=mine_num

        ## private info inside
        self.arr=TwoDimensionArray(self.x,self.y) #-1:mine 0~8:num -2:wall
        
        ## ui and logic
        self.state=TwoDimensionArray(self.x,self.y,-1) #what player can see: -1:close 0~8:open -2:flag -3:wall
        self.frontier = set([]) 
        self.KB = []

        ## user approx.
        self.remaining_mines = self.mine_num

    def wall(self, corr):
        return self.arr[corr] == -2

    def start_game(self):
        
        # initialize array
        for i in range(self.x+2):
            self.arr[(i,0)] = -2
            self.arr[(i,self.y+1)] = -2
        
        for j in range(self.y+2):
            self.arr[(0,j)] = -2
            self.arr[(self.x+1,j)] = -2
        
        # randomly choose a corr to start
        start_corr = (randint(1,self.x), randint(1,self.y))
        # generate booms
        for i in range(self.mine_num):
            while True:
                mine_corr = (randint(1,self.x), randint(1,self.y))
                #if mine_corr != start_corr and self.arr[mine_corr] == 0:
                if mine_corr != start_corr and self.arr[mine_corr] == 0 and (mine_corr[0] - start_corr[0], mine_corr[1] - start_corr[1])  not in adjacent_pairs:
                    self.arr[mine_corr] = -1
                    break
        
        # generate numbers
        for i in range(1, self.x+1):
            for j in range(1, self.y+1):
                if self.arr[(i,j)] == 0:
                    boom_num = 0
                    for di, dj in adjacent_pairs:
                        corr = (i+di, j+dj)
                        if self.arr[corr] == -1:
                            boom_num += 1
                    self.arr[(i,j)] = boom_num

        # for ui:
        # update state 
        self.state[start_corr] = self.arr[start_corr]

        # initialize state wall
        for i in range(self.x+2):
            self.state[(i,0)] = -3
            self.state[(i,self.y+1)] = -3
        
        for j in range(self.y+2):
            self.state[(0,j)] = -3
            self.state[(self.x+1,j)] = -3
        
        # for logic:
        # update KB
        self.KB.append(wallAxioms(self.x, self.y))
        
        # update start_corr frontier and KB
        self.updateFrontier(start_corr)
        self.updateKB(start_corr)
    
    # update frontier from excavated corr
    def updateFrontier(self, excavated_corr):
        for di, dj in adjacent_pairs:
            corr = (excavated_corr[0]+di, excavated_corr[1]+dj)
            if (not self.wall(corr)) and self.state[corr] == -1:
                self.frontier |= set([corr])
    
    # update KB from excavated corr
    def updateKB(self, excavated_corr):
        self.KB.append(adjacentAxioms(excavated_corr[0], excavated_corr[1], self.state[excavated_corr]))

    ## entail possible mines and non-mine area
    def entailRound(self):
        frontierCopy = self.frontier.copy()
        entailSuccess = 0
        for key in frontierCopy:
            x, y = key
            if entails(conjoin(self.KB), PropSymbolExpr(mine_str, x, y)):
                ## assert 
                if not self.arr[key] == -1:
                    return -1

                self.KB.append(PropSymbolExpr(mine_str, x, y))
                self.state[key] = -2 #flag
                self.frontier -= set([key])
                
                self.remaining_mines -= 1

                entailSuccess = 1

            elif entails(conjoin(self.KB), ~PropSymbolExpr(mine_str, x, y)):
                ## assert
                if not (self.arr[key] != -1 and self.arr[key] != -2):
                    return -1

                self.KB.append(~PropSymbolExpr(mine_str, x, y))
                self.state[key] = self.arr[key]
                self.frontier -= set([key])
                self.updateFrontier(key)
                self.updateKB(key)

                entailSuccess = 1

        return entailSuccess
    
    ## guess an area to open
    def guess(self):
        corr = self.guess_frontier()
        ## assert
        if not (self.arr[corr] != -1 and self.arr[corr] != -2):
            return -1

        x, y = corr
        self.KB.append(~PropSymbolExpr(mine_str, x, y))
        self.state[corr] = self.arr[corr]
        self.frontier -= set([corr])
        self.updateFrontier(corr)
        self.updateKB(corr)

        return 0
    
    def guess_frontier(self):
        frontierCopy = self.frontier.copy()
        minPlace = None
        minNum = 999999
        for key in frontierCopy:
            x, y = key
            currNum = 0
            for dx, dy in adjacent_pairs:
                corr = (x+dx, y+dy)
                if self.state[corr] >= 0:
                    currNum += self.state[corr]
                    for d2x, d2y in adjacent_pairs:
                        if self.state[(corr[0]+d2x, corr[1]+d2y)] == -2:
                            currNum -= 1
            if currNum < minNum:
                minNum = currNum
                minPlace = key 
        
        return minPlace
        
    
    def guess_global(self):

        return self.state.pick_Num(-1)


    def display_info(self):
        for i in range(self.x+2):
            for j in range(self.y+2):
                print("{:>2}".format(self.arr[(i,j)]), end='')
            print("")
    
    def display_ui(self):
        for i in range(self.x+2):
            for j in range(self.y+2):
                print("{:>2}".format(self.state[(i,j)]), end='')
            print("")
        print("")

if __name__=='__main__':

    simple = (9, 9, 10)
    medium = (16, 16, 40)
    hard = (16, 30, 99)

    x, y, mine_num = medium
    
    roundNum = 100
    success = 0
    for i in range(roundNum):
        game=MineSweeper(x,y,mine_num)
        game.start_game()

        #print("start game:")
        #game.display_ui()

        while game.remaining_mines != 0:
            entailsuccess = game.entailRound()
            if entailsuccess == 0:
                #print("can't entail any, guess:")
                if game.guess() == -1:
                    break
            elif entailsuccess == -1:
                #print("after a round of entailment:")
                break
            #game.display_ui()
        
        if game.remaining_mines == 0:
            success += 1
            print("\rSuccess in round "+str(i+1)+" , now: "+str(success)+"/"+str(i+1), end='')
        else:
            print("\rFailure in round "+str(i+1)+" , now: "+str(success)+"/"+str(i+1), end='')
    
    print("\medium: success rate = "+str(success/roundNum))
        
        




        