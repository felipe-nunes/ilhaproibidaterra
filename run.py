import tkinter as tk
from tkinter import simpledialog  # Importação adicional
import random

def logging_decorator(func):
    """
    Decorator para registrar o início e o fim da execução de uma função.

    :param func: Função a ser decorada.
    :type func: function
    :return: Função decorada com capacidades de log.
    :rtype: function
    """
    def wrapper(*args, **kwargs):
        print(f"Executing {func.__name__}...")
        result = func(*args, **kwargs)
        print(f"Done executing {func.__name__}.")
        return result
    return wrapper

# Decorator para atribuição de nomes aos terrenos
def assign_names_decorator(func):
    """
    Decorator para inicializar e embaralhar os nomes dos terrenos.

    :param func: Função a ser decorada.
    :type func: function
    :return: Função decorada com inicialização de nomes dos terrenos.
    :rtype: function
    """
    def wrapper(self, *args, **kwargs):
        self.terrain_names = [
            "Jardim Sussurrante", "Jardim Uivante", "Caverna das Sombras", 
            "Caverna das Chamas", "Palácio de Coral", "Palácio das Marés", 
            "Templo da Lua", "Templo do Sol", "Rocha Fantasma", 
            "Floresta Carmesim", "Clareira do Crepúsculo", "Torre de Vigia",
            "Pântano de Pavor", "Portal de Prata", "Portal de Bronze", 
            "Portal de Ferro", "Portal de Ouro", "Portal de Cobre",
            "Observatório", "Heliponto", "Caverna do Vórtice", "Templo do Vento",
            "Templo do Fogo", "Caverna da Onda"
        ]

        random.shuffle(self.terrain_names)
        return func(self, *args, **kwargs)
    return wrapper

# Decorator para status do terreno
def tile_status_decorator(func):
    """
    Decorator para definir o status dos terrenos.

    :param func: Função a ser decorada.
    :type func: function
    :return: Função decorada com a lógica de status dos terrenos.
    :rtype: function
    """
    def wrapper(self, row, col, terrain_index, *args, **kwargs):
        tile_number = row * self.grid_size + col + 1
        status = "Normal"
        if self.sunk_tile_number and tile_number == self.sunk_tile_number:
            status = "Afundado"
        elif self.sinking_tiles and tile_number in self.sinking_tiles:
            status = "Afundando"
        return func(self, row, col, terrain_index, status, *args, **kwargs)
    return wrapper

# Decorator para tesouros nas diagonais
def treasure_decorator(func):
    """
    Decorator para criar e embaralhar os nomes dos tesouros.

    :param func: Função a ser decorada.
    :type func: function
    :return: Função decorada com inicialização de nomes dos tesouros.
    :rtype: function
    """
    def wrapper(self, *args, **kwargs):
        self.treasure_names = ["Cálice da Maré", "Cristal de Fogo", "Estátua de Pedra", "Orbe Terrestre"]
        random.shuffle(self.treasure_names)
        return func(self, *args, **kwargs)
    return wrapper

class ForbiddenIslandBoard:
    """
    Representa o tabuleiro do jogo 'Ilha Proibida'.

    :param root: Instância do tkinter.
    :type root: Tk
    :param grid_size: Tamanho do grid do tabuleiro.
    :type grid_size: int
    :param tile_size: Tamanho visual de cada tile.
    :type tile_size: int
    """
    def __init__(self, root, grid_size=6, tile_size=110):
        """
        Inicializador da classe ForbiddenIslandBoard.

        :param root: Instância do Tk.
        :param grid_size: Tamanho do grid, padrão é 6.
        :param tile_size: Tamanho de cada tile, padrão é 110.
        """
        self.root = root
        self.grid_size = grid_size
        self.tile_size = tile_size
        self.canvas_width = grid_size * tile_size + 15 # Adiciona 1 ou mais pixels
        self.canvas_height = grid_size * tile_size + 50
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()
        self.black_tiles_numbers = {1, 2, 5, 6, 7, 12, 25, 30, 31, 32, 35, 36}
        self.initialize_terrain_names()
        self.assign_player_roles()
        self.initialize_treasures()
        self.terrain_positions = {}
        # Inicialmente, não há terrenos com status especial
        self.sunk_tile_number = None
        self.sinking_tiles = set()
        self.terrain_treasure_mapping = {
            "Jardim Sussurrante": "Cálice da Maré",
            "Jardim Uivante": "Cálice da Maré",
            "Caverna das Sombras": "Estátua de Pedra",
            "Caverna das Chamas": "Estátua de Pedra",
            "Palácio de Coral": "Cristal de Fogo",
            "Palácio das Marés": "Cristal de Fogo",
            "Templo da Lua": "Orbe Terrestre",
            "Templo do Sol": "Orbe Terrestre"
            }
        self.treasure_colors = {
            "Cálice da Maré": "#800080",  # Exemplo de cor em hexadecimal
            "Cristal de Fogo": "#FF8C00",
            "Estátua de Pedra": "#8B4513",
            "Orbe Terrestre": "#006400"
            }
        self.num_players = self.ask_number_of_players()  # Pergunta o número de jogadores
        self.assign_roles_randomly()  # Atribui os papéis aleatoriamente
        self.player_positions = {}  # Dicionário para manter as posições dos jogadores
        self.set_initial_positions()

        self.player_turn_order = random.sample(self.player_roles, len(self.player_roles))
        self.current_turn_index = 0

        self.setup_key_bindings()

        print(f"Ordem dos turnos dos jogadores: {self.player_turn_order}")
        print(f"É a vez do jogador: {self.player_turn_order[self.current_turn_index]}")

        # Inicializa o label para mostrar as coordenadas
        self.coordinates_label = tk.Label(root, text="")
        self.coordinates_label.pack()
        # Vincula o evento de movimento do mouse ao canvas
        self.canvas.bind("<Motion>", self.on_mouse_move)

        self.player_rectangles = {}
    
    def on_mouse_move(self, event):
        # Atualiza o label com a posição atual do mouse
        self.coordinates_label.config(text=f"X: {event.x}, Y: {event.y}")

    def setup_key_bindings(self):
        print("Setting up key bindings")
        self.root.bind("<Left>", lambda e: self.move_player("oeste"))
        self.root.bind("<Right>", lambda e: self.move_player("leste"))
        self.root.bind("<Up>", lambda e: self.move_player("norte"))
        self.root.bind("<Down>", lambda e: self.move_player("sul"))

    def is_move_valid(self, current_position, direction):
        x, y = self.get_tile_position(current_position)
        grid_x, grid_y = int(x / self.tile_size), int(y / self.tile_size)
        print(f"Posição atual: ({grid_x}, {grid_y}), Direção: {direction}")

        new_grid_x, new_grid_y = grid_x, grid_y

        if direction == "norte" and grid_y > 0:
            new_grid_y -= 1
        elif direction == "sul" and grid_y < self.grid_size - 1:
            new_grid_y += 1
        elif direction == "leste" and grid_x < self.grid_size - 1:
            new_grid_x += 1
        elif direction == "oeste" and grid_x > 0:
            new_grid_x -= 1

        for terrain, pos in self.terrain_positions.items():
            pos_x, pos_y = pos
            pos_grid_x, pos_grid_y = int(pos_x / self.tile_size), int(pos_y / self.tile_size)
            if pos_grid_x == new_grid_x and pos_grid_y == new_grid_y:
                print(f"Nova posição encontrada no terreno: {terrain}")
                tile_number = new_grid_y * self.grid_size + new_grid_x + 1
                if self.sunk_tile_number == tile_number or tile_number in self.sinking_tiles:
                    print(f"Tile {tile_number} não é válido para movimento")
                    return False
                return True
        print(f"Nenhuma correspondência de terreno encontrada para a nova posição")
        return False
    
    def move_player(self, direction):
        role = self.player_turn_order[self.current_turn_index]
        current_terrain = self.player_positions[role]

        new_terrain = self.calculate_new_position(current_terrain, direction)
        if new_terrain and new_terrain != current_terrain:
            print(f"Jogador {role} moveu-se de {current_terrain} para {new_terrain}.")
            self.update_player_position(role, new_terrain)
            self.end_player_turn()  # Move para o próximo turno somente se a movimentação for bem-sucedida
        else:
            print(f"Jogador {role} não pode se mover para {direction} a partir de {current_terrain}.")        

    def calculate_new_position(self, current_terrain, direction):
        x, y = self.get_tile_position(current_terrain)
        grid_x, grid_y = int(x / self.tile_size), int(y / self.tile_size)
        print(f"Calculando nova posição a partir de ({grid_x}, {grid_y}) na direção {direction}")

        if direction == "norte":
            grid_y -= 1
        elif direction == "sul":
            grid_y += 1
        elif direction == "leste":
            grid_x += 1
        elif direction == "oeste":
            grid_x -= 1

        for terrain, pos in self.terrain_positions.items():
            pos_x, pos_y = pos
            pos_grid_x, pos_grid_y = int(pos_x / self.tile_size), int(pos_y / self.tile_size)
            if pos_grid_x == grid_x and pos_grid_y == grid_y:
                print(f"Nova posição encontrada no terreno: {terrain}")
                return terrain
        print("Nova posição não encontrada")
        return None

    def update_player_position(self, role, new_position):
        x_old, y_old = self.get_tile_position(self.player_positions[role])
        x_new, y_new = self.get_tile_position(new_position)

        if (x_old, y_old) != (x_new, y_new):
            old_rect = self.player_rectangles.get(role)
            if old_rect:
                self.canvas.delete(old_rect)  # Apaga o retângulo antigo
                self.redraw_tile_at(x_old, y_old)  # Redesenhar o tile antigo

            new_rect = self.draw_player_square(x_new, y_new, self.tile_size, role, highlight=True, highlight_color=self.player_piece_colors[role])
            self.player_positions[role] = new_position
            self.player_rectangles[role] = new_rect
        
    def end_player_turn(self):
        # Remover highlight do jogador atual
        self.highlight_current_player(remove=True)
        # Proceder para o próximo turno
        self.next_turn()
        
    def next_turn(self):
        # Atualiza o índice para o próximo jogador na ordem
        self.current_turn_index = (self.current_turn_index + 1) % len(self.player_turn_order)
        # Aplicar highlight ao próximo jogador
        self.highlight_current_player()

    def update_player_rectangle(self, role, add_highlight):
        x, y = self.get_tile_position(self.player_positions[role])
        old_rect = self.player_rectangles.get(role)
        if old_rect:
            self.canvas.delete(old_rect)
        highlight_color = "#800080" if add_highlight else self.player_piece_colors[role]
        new_rect = self.draw_player_square(x, y, self.tile_size, role, highlight=add_highlight, highlight_color=highlight_color)
        self.player_rectangles[role] = new_rect

    def highlight_current_player(self, remove=False):
        role = self.player_turn_order[self.current_turn_index]
        current_terrain = self.player_positions[role]
        self.update_player_rectangle(role, add_highlight=True)
    
    def end_player_turn(self):
        current_role = self.player_turn_order[self.current_turn_index]
        self.update_player_rectangle(current_role, add_highlight=False)
        self.next_turn()

    def redraw_tile_at(self, x, y):
        # Calcular a posição do grid com base em x e y
        grid_x = int(x / self.tile_size)
        grid_y = int(y / self.tile_size)

        # Encontrar o nome do terreno e o índice correspondente
        terrain_name = None
        for name, pos in self.terrain_positions.items():
            if pos == (x, y):
                terrain_name = name
                break

        # Se o terreno foi encontrado, redesenhe-o
        if terrain_name:
            # Encontrar o índice do terreno na lista de terrenos
            terrain_index = self.terrain_names.index(terrain_name)
            # Chame draw_tile com o índice correto
            self.draw_tile(grid_y, grid_x, terrain_index)

            # Definir a cor do texto com base no terreno
            font_color = 'black' if terrain_name not in self.player_piece_colors else self.player_piece_colors[terrain_name]
            font_style = ('Helvetica', 6)
            self.canvas.create_text(x, y - 15, text=terrain_name, fill=font_color, font=font_style)
        else:
            print("Erro: terreno não encontrado para redesenhar.")


    def set_initial_positions(self):
        """ Define as posições iniciais dos jogadores com base em seus papéis. """
        role_starting_points = {
            "Piloto": "Heliponto",
            "Engenheiro": "Portal de Bronze",
            "Explorador": "Portal de Cobre",
            "Mergulhador": "Portal de Ferro",
            "Mensageiro": "Portal de Prata",
            "Navegador": "Portal de Ouro"
        }
        for role in self.player_roles:
            starting_point = role_starting_points[role]
            self.player_positions[role] = starting_point  # Define a posição inicial para cada papel
            print(f"{role} começa em {starting_point}")  # Adicione esta linha para debugar
    
    def draw_player_square(self, x, y, tile_size, role, highlight=False, highlight_color=None):
        player_index = self.player_roles.index(role)
        player_color = self.player_piece_colors[role]
        player_square_size = tile_size // 4
        half_player_square_size = player_square_size // 2

        square_x1 = x - half_player_square_size
        square_y1 = y - half_player_square_size
        square_x2 = x + half_player_square_size
        square_y2 = y + half_player_square_size

        part_width = player_square_size // 3
        part_height = player_square_size // 2

        col = player_index % 3
        row = player_index // 3

        part_x1 = square_x1 + (col * part_width)
        part_y1 = square_y1 + (row * part_height)
        part_x2 = part_x1 + part_width
        part_y2 = part_y1 + part_height

        # Se o highlight está ativo, usa a cor do highlight, senão usa a cor do jogador
        outline_color = highlight_color if highlight else player_color
        player_rect = self.canvas.create_rectangle(part_x1, part_y1, part_x2, part_y2, fill=player_color, outline=outline_color, width=3 if highlight else 0)

        return player_rect

    def ask_number_of_players(self):
        """ Pergunta ao usuário o número de jogadores. """
        # Aqui você pode usar uma caixa de diálogo Tkinter ou um simples input
        num_players = simpledialog.askinteger("Número de Jogadores", "Digite o número de jogadores (2, 3 ou 4):", minvalue=2, maxvalue=4)
        return num_players
    
    def assign_roles_randomly(self):
        """ Atribui papéis aos jogadores de forma aleatória. """
        roles = ["Piloto", "Engenheiro", "Explorador", "Mergulhador", "Mensageiro", "Navegador"]
        random.shuffle(roles)
        self.player_roles = roles[:self.num_players]  # Seleciona os papéis com base no número de jogadores
        print(f"Papéis atribuídos: {self.player_roles}")  # Adicione esta linha para debugar

        
    @assign_names_decorator
    def initialize_terrain_names(self):
        pass

    def assign_player_roles(self):
        # Atribuições dinâmicas baseadas nos terrenos embaralhados
        self.player_piece_colors = {
            "Piloto": "#0000FF",         # Azul
            "Engenheiro": "#FF0000",     # Vermelho
            "Explorador": "#008000",     # Verde
            "Mergulhador": "#000000",    # Preto
            "Mensageiro": "#505050",     # Cinza
            "Navegador": "#DAA520"       # Amarelo Escuro
        }

    @logging_decorator
    def draw_grid(self):
        """
        Desenha o grid do tabuleiro com os terrenos e tesouros.
        """
        terrain_index = 0
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                tile_number = row * self.grid_size + col + 1
                if tile_number not in self.black_tiles_numbers:
                    # Verificar se o terrain_index ainda está dentro do intervalo antes de desenhar
                    if terrain_index < len(self.terrain_names):
                        self.draw_tile(row, col, terrain_index)
                        terrain_index += 1
                    else:
                        print(f"Erro: Não há terrenos suficientes para o tile_number {tile_number}")
        self.place_treasures()
        self.canvas.update()
        self.draw_players()  # Chame após desenhar o grid
        print("Grid desenhado com sucesso")

    
    def draw_players(self):
        """ Desenha os jogadores no tabuleiro. """
        for role, position in self.player_positions.items():
            x, y = self.get_tile_position(position)
            self.draw_player_square(x, y, self.tile_size, role)  # Passa tile_size como argumento
    
    @treasure_decorator
    def initialize_treasures(self):
        """ Método para inicializar os tesouros. """
        pass  # O corpo deste método está vazio, pois a lógica está no decorator


    @tile_status_decorator
    def draw_tile(self, row, col, terrain_index, status=None):
        margin = 9  # Margem de 10 pixels
        x1 = col * self.tile_size + margin
        y1 = row * self.tile_size + margin
        x2 = x1 + self.tile_size
        y2 = y1 + self.tile_size

        # Verifica se o índice do terreno está dentro do alcance antes de desenhar
        if terrain_index < len(self.terrain_names):
            terrain_name = self.terrain_names[terrain_index]
        else:
            print(f"Erro: Índice de terreno {terrain_index} fora do alcance.")
            return

        # Desenhar o retângulo do tile
        self.canvas.create_rectangle(x1, y1, x2, y2, fill='white', outline='black', width=2)

        # Definir a cor do texto com base no terreno
        font_color = 'black'
        if terrain_name in self.treasure_colors:
            font_color = self.treasure_colors[terrain_name]
        elif terrain_name in self.player_piece_colors:
            font_color = self.player_piece_colors[terrain_name]

        # Desenhar o nome do terreno no centro do tile
        center_x = x1 + self.tile_size / 2
        center_y = y1 + self.tile_size / 2
        self.canvas.create_text(center_x, center_y, text=terrain_name, fill=font_color, font=('Helvetica', 6))

        # Atualiza a posição do terreno no dicionário de posições
        self.terrain_positions[terrain_name] = (center_x, center_y)

        # Adicionar status do tile se aplicável
        if status != "Normal":
            status_color = 'blue' if status == "Afundando" else 'red'
            self.canvas.create_text(center_x, center_y + 15, text=status, fill=status_color, font=('Helvetica', 8))



    def get_tile_position(self, terrain_name):
        position = self.terrain_positions.get(terrain_name, (0, 0))
        print(f"Posição para {terrain_name}: {position}")  # Debugging
        """ Retorna a posição x, y do centro de um tile com base no nome do terreno. """
        return self.terrain_positions.get(terrain_name, (0, 0))  # Retorna a posição ou (0, 0) se não encontrado

    def place_treasures(self):
       treasure_index = 0
       for i in range(self.grid_size):
            if i == 0 or i == self.grid_size - 1:
                for j in [0, self.grid_size - 1]:
                    if (i, j) not in self.black_tiles_numbers:
                        x1 = j * self.tile_size
                        y1 = i * self.tile_size
                        treasure_name = self.treasure_names[treasure_index % len(self.treasure_names)]
                        treasure_color = self.treasure_colors[treasure_name]  # Use a cor correspondente
                        treasure_index += 1
                        self.canvas.create_text(x1 + self.tile_size/2, y1 + self.tile_size/2, text=treasure_name, fill=treasure_color, font=('Helvetica', 10, 'bold'))
    # Inicialização da janela principal do tkinter
root = tk.Tk()
root.title("Ilha Proibida Grid de Terrenos")

# Criação da instância da classe ForbiddenIslandBoard e desenho do grid
board = ForbiddenIslandBoard(root)
board.draw_grid()
board.highlight_current_player() 

# Execução do loop do tkinter
root.mainloop()