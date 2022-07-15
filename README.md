# Auto-MineSweeper
Using logic deduction to solve the minesweeper game

Parts of the codes come from U.C.Berkeley's course project in cs188
* agents.py
* logic.py
* logic_utils.py
* util.py
* part of logicPlan.py

**updated in 14th July 2022:**
brute cnf version

using global cnf to deduct the location of mines

achieve a winning rate of 92/100 in simple version of MineSweeper

![avatar](./image/simple_in_brute_cnf.png)



**updated in 15th July 2022:**

add local cnf search and scanning

demo video here:

<iframe 
    width="800" 
    height="450" 
    src="./video/demo.mp4"
    frameborder="0" 
    allowfullscreen>
</iframe>
<iframe src="//player.bilibili.com/player.html?aid=215970874&bvid=BV1Ga411H7i3&cid=773655901&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>
