import pygame, sys, os
from pygame.locals import *

from collections import deque

def to_box(level, index):
    if level[index] == '-' or level[index] == '@':
        level[index] = '$'
    else:
        level[index] = '*'

def to_man(level, i):
    if level[i] == '-' or level[i] == '$':
        level[i]='@'
    else:
        level[i]='+'

def to_floor(level, i):
    if level[i] == '@' or level[i] == '$':
        level[i]='-'
    else:
        level[i]='.'

def to_offset(d, width):
    d4 = [-1, -width, 1, width]
    m4 = ['l','u','r','d']
    return d4[m4.index(d.lower())]

def b_manto(level,width,b,m,t):
    maze = list(level)
    maze[b] = '#'
    if m == t:
        return 1
    queue = deque([])
    queue.append(m)
    d4 = [-1, -width, 1, width]
    m4 = ['l','u','r','d']
    while len(queue) > 0:
        pos = queue.popleft()
        for i in range(4):
            newpos = pos + d4[i]
            if maze[newpos] in ['-','.']:
                if newpos == t:
                    return 1
                maze[newpos] = i
                queue.append(newpos)
    return 0

def b_manto_2(level,width,b,m,t):
    maze = list(level)
    maze[b] = '#'
    maze[m] = '@'
    if m == t:
        return []
    queue = deque([])
    queue.append(m)
    d4 = [-1, -width, 1, width]
    m4 = ['l','u','r','d']
    while len(queue) > 0:
        pos = queue.popleft()
        for i in range(4):
            newpos = pos + d4[i]
            if maze[newpos] in ['-','.']:
                maze[newpos] = i
                queue.append(newpos)
                if newpos == t:
                    path = []
                    while maze[t] != '@':
                        path.append( m4[maze[t]])
                        t = t - d4[maze[t]]
                    return path
                
    return []



    
class Sokoban:
    def __init__(self):
        self.levels = []
        self.load_levels_from_file('levels.txt')
        self.current_level = 0
        self.load_level(self.current_level)
        
        self.hint = list(self.level)
        self.solution = []
        self.push = 0
        self.todo = []
        self.auto = 0
        self.sbox = 0
        self.queue = []
    
    def load_levels_from_file(self, filename):
        """Загружает уровни из текстового файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line and not line.startswith('#'):
                    # Читаем размеры
                    w, h = map(int, line.split())
                    # Читаем строку уровня
                    level_str = lines[i+1].strip()
                    # Читаем позицию игрока
                    man_pos = int(lines[i+2].strip())
                    
                    # Проверяем соответствие размера
                    expected_size = w * h
                    if len(level_str) != expected_size:
                        print(f"Предупреждение: Уровень {len(self.levels)+1} имеет размер {len(level_str)}, ожидалось {expected_size}")
                        # Корректируем строку до нужного размера
                        if len(level_str) < expected_size:
                            level_str = level_str + '-' * (expected_size - len(level_str))
                        else:
                            level_str = level_str[:expected_size]
                    
                    self.levels.append({
                        'level': level_str,
                        'w': w,
                        'h': h,
                        'man': man_pos
                    })
                    i += 3
                else:
                    i += 1
        except FileNotFoundError:
            # Если файл не найден, создаем уровень по умолчанию
            print("Файл levels.txt не найден. Использую уровень по умолчанию.")
            self.levels.append({
                'level': '----#####--------------#---#--------------#$--#------------###--$##-----------#--$-$-#---------###-#-##-#---#######---#-##-#####--..##-$--$----------..######-###-#@##--..#----#-----#########----#######--------',
                'w': 19,
                'h': 11,
                'man': 163
            })
        except Exception as e:
            print(f"Ошибка при загрузке уровней: {e}")
            # Создаем уровень по умолчанию
            self.levels.append({
                'level': '----#####--------------#---#--------------#$--#------------###--$##-----------#--$-$-#---------###-#-##-#---#######---#-##-#####--..##-$--$----------..######-###-#@##--..#----#-----#########----#######--------',
                'w': 19,
                'h': 11,
                'man': 163
            })
    
    def load_level(self, index):
        """Загружает уровень по индексу"""
        if 0 <= index < len(self.levels):
            level_data = self.levels[index]
            self.level = list(level_data['level'])
            self.w = level_data['w']
            self.h = level_data['h']
            self.man = level_data['man']
            
            # Дополнительная проверка после загрузки
            expected_size = self.w * self.h
            if len(self.level) != expected_size:
                print(f"Ошибка: Уровень {index+1} имеет размер {len(self.level)}, ожидалось {expected_size}")
                # Корректируем размер
                if len(self.level) < expected_size:
                    self.level.extend(['-'] * (expected_size - len(self.level)))
                else:
                    self.level = self.level[:expected_size]
            
            return True
        return False
    
    def next_level(self):
        """Переход на следующий уровень"""
        if self.current_level + 1 < len(self.levels):
            self.current_level += 1
            self.load_level(self.current_level)
            self.hint = list(self.level)
            self.solution = []
            self.push = 0
            self.todo = []
            self.auto = 0
            self.sbox = 0
            self.queue = []
            return True
        return False
    
    def restart_level(self):
        """Перезапуск текущего уровня"""
        self.load_level(self.current_level)
        self.hint = list(self.level)
        self.solution = []
        self.push = 0
        self.todo = []
        self.auto = 0
        self.sbox = 0
        self.queue = []
    
    def check_win(self):
        """Проверяет, все ли коробки на местах"""
        return self.level.count('.') == 0 and self.level.count('+') == 0
    
    def draw(self, screen, skin):
        w = skin.get_width() / 4
        for i in range(0,self.w):
            for j in range(0,self.h):
                index = j*self.w + i
                if index >= len(self.level):
                    continue  # Пропускаем, если индекс вне диапазона
                if self.level[index] == '#':
                    screen.blit(skin, (i*w, j*w), (0,2*w,w,w))
                elif self.level[index] == '-':
                    screen.blit(skin, (i*w, j*w), (0,0,w,w))
                elif self.level[index] == '@':
                    screen.blit(skin, (i*w, j*w), (w,0,w,w))
                elif self.level[index] == '$':
                    screen.blit(skin, (i*w, j*w), (2*w,0,w,w))
                elif self.level[index] == '.':
                    screen.blit(skin, (i*w, j*w), (0,w,w,w))
                elif self.level[index] == '+':
                    screen.blit(skin, (i*w, j*w), (w,w,w,w))
                elif self.level[index] == '*':
                    screen.blit(skin, (i*w, j*w), (2*w,w,w,w))
    
    def move(self, d):
        self._move(d)
        self.todo = []
    
    def _move(self, d):
        self.sbox = 0
        h = to_offset(d, self.w)
        h2 = 2 * h
        if self.level[self.man + h] == '-' or self.level[self.man + h] == '.':
        # move
            to_man(self.level, self.man+h)
            to_floor(self.level, self.man)
            self.man += h
            self.solution.append(d)
        elif self.level[self.man + h] == '*' or self.level[self.man + h] == '$':
            if self.level[self.man + h2] == '-' or self.level[self.man + h2] == '.':
            # push
                to_box(self.level, self.man + h2)
                to_man(self.level, self.man + h)
                to_floor(self.level, self.man)
                self.man += h
                self.solution.append(d.upper())
                self.push += 1
    
    def undo(self):
        if len(self.solution) > 0:
            last_move = self.solution[-1]
            self.todo.append(last_move)
            self.solution.pop()
            
            h = to_offset(last_move.lower(), self.w) * -1
            
            if last_move.islower():
                # undo a move
                to_man(self.level, self.man + h)
                to_floor(self.level, self.man)
                self.man += h
            else:
                # undo a push
                to_floor(self.level, self.man - h)
                to_box(self.level, self.man)
                to_man(self.level, self.man + h)
                self.man += h
                self.push -= 1
    
    def redo(self):
        if len(self.todo) > 0:
            last_undone = self.todo[-1]
            self.todo.pop()
            self._move(last_undone.lower())

def main():

    # start pygame
    pygame.init()
    screen = pygame.display.set_mode((400,300))


    # load skin
    skinfilename = os.path.join('borgar.png')
    try:
        skin = pygame.image.load(skinfilename)
    except:
        print ('cannot load skin')
        raise SystemExit
    skin = skin.convert()

    screen.fill(skin.get_at((0,0)))
    pygame.display.set_caption('sokoban.py')

    # create Sokoban object
    skb = Sokoban()
    skb.draw(screen,skin)

    #
    clock = pygame.time.Clock()
    pygame.key.set_repeat(200,50)

    # main game loop
    while True:
        clock.tick(60)
        
        # Проверка победы - автоматический переход на следующий уровень
        if skb.check_win():
            if not skb.next_level():
                # Если уровни закончились, просто перезапускаем последний уровень
                skb.restart_level()
            skb.draw(screen, skin)
            pygame.display.set_caption(f'Уровень {skb.current_level + 1}/{len(skb.levels)} - {skb.solution.__len__()}/{skb.push} - sokoban.py')

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_LEFT:
                    skb.move('l')
                    skb.draw(screen,skin)
                elif event.key == K_UP:
                    skb.move('u')
                    skb.draw(screen,skin)
                elif event.key == K_RIGHT:
                    skb.move('r')
                    skb.draw(screen,skin)
                elif event.key == K_DOWN:
                    skb.move('d')
                    skb.draw(screen,skin)
                elif event.key == K_BACKSPACE:
                    skb.undo()
                    skb.draw(screen,skin)
                elif event.key == K_SPACE:
                    skb.redo()
                    skb.draw(screen,skin)
                elif event.key == K_r:
                    # Перезапуск уровня
                    skb.restart_level()
                    skb.draw(screen, skin)

        pygame.display.update()
        # Обновляем заголовок с номером уровня
        pygame.display.set_caption(f'Уровень {skb.current_level + 1}/{len(skb.levels)} - {skb.solution.__len__()}/{skb.push} - sokoban.py')


if __name__ == '__main__':
    main()