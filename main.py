import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image, ImageDraw
from DelaunayTriangulation import BW_Delaunay_Triangulation
from PointGeneration import generate_points, generate_all_points_with_addition, generate_points_for_solo
from QuadTree import QuadTree
from QuadTreeStruct import QuadTreeStruct
from itertools import chain


def convert_png_to_matrix(filename):
    # wczytaj plik PNG
    image = Image.open(filename)

    # pobierz rozmiar obrazka
    width, height = image.size
    # stwórz pustą macierz o odpowiednim rozmiarze
    matrix = [[0 for j in range(width)] for i in range(height)]

    for y in range(0, height, 1):
        for x in range(0, width, 1):
            pixel = image.getpixel((x, y))
            black = 0
            if pixel == (0, 0, 0):
                black = 1

            if black == 1:
                matrix[y][x] = 1

    # wyświetl macierz
    return matrix


class GUI:
    def __init__(self, master):
        self.img = None
        self.mesh = None
        self.master = master
        master.title("Geometria Obliczeniowa - Projekt, Albert Dańko, Jakub Ficek")
        master.configure(bg='gray')

        self.file_path = ""
        self.selected_grid = tk.StringVar(value="strukturalna")
        self.grid_generated = False

        # Tworzenie etykiety z informacją o wybranym pliku
        self.filename_label_text = tk.StringVar()
        self.filename_label_text.set("Wybierz plik:")
        self.filename_label = tk.Label(master, textvariable=self.filename_label_text, font=('Calibri', 10), bg='gray')
        self.filename_label.grid(row=0, column=0, pady=10, sticky='n')

        # Tworzenie przycisku do wyboru pliku
        self.select_file_button = tk.Button(master, text="Wybierz plik", font=('Calibri', 10), command=self.select_file,
                                            bg="#e8c846")
        self.select_file_button.grid(row=1, column=0, pady=5, sticky='n')

        # Tworzenie przycisku do wczytywania pliku
        self.load_file_button = tk.Button(master, text="Wczytaj", font=('Calibri', 10), command=self.load_file,
                                          bg="#e8c846")
        self.load_file_button.grid(row=2, column=0, pady=5, sticky='n')

        # Tworzenie ramki z radiobuttonami wyboru rodzaju siatki
        self.grid_label_text = tk.StringVar()
        self.grid_label_text.set("Wybierz rodzaj siatki:")
        self.grid_label = tk.Label(master, textvariable=self.grid_label_text, font=('Calibri', 10), bg='gray')
        self.grid_label.grid(row=3, column=0, pady=5, sticky='n')

        self.grid_frame = tk.Frame(master)
        self.grid_type_structural = tk.Radiobutton(self.grid_frame, text="Strukturalna              ",
                                                   variable=self.selected_grid,
                                                   value="strukturalna", font=('Calibri', 10), bg='#e8c846')
        self.grid_type_structural.pack(anchor='n')
        self.grid_type_structuralQT = tk.Radiobutton(self.grid_frame, text="Strukturalna  QT       ",
                                                       variable=self.selected_grid, value="strukturalnaQT",
                                                       font=('Calibri', 10), bg='#e8c846')
        self.grid_type_structuralQT.pack(anchor='n')
        self.grid_type_nonstructural = tk.Radiobutton(self.grid_frame, text="Niestrukturalna        ",
                                                       variable=self.selected_grid, value="niestrukturalna",
                                                       font=('Calibri', 10), bg='#e8c846')
        self.grid_type_nonstructural.pack(anchor='n')
        self.grid_type_nonstructural_solo = tk.Radiobutton(self.grid_frame, text="NiestrukturalnaSolo",
                                                       variable=self.selected_grid, value="niestrukturalnaSolo",
                                                       font=('Calibri', 10), bg='#e8c846')
        self.grid_type_nonstructural_solo.pack(anchor='n')
        self.grid_frame.grid(row=4, column=0, pady=5, padx=10, sticky='n')

        self.selected_grid.trace("w", self.grid_type_changed)

        # Tworzenie przycisku generowania/ukrywania siatki oraz przycisku exportuj siatkę
        self.generate_grid_button = tk.Button(master, text="Generuj siatkę", font=('Calibri', 10),
                                              command=self.generate_grid, bg="#e8c846")
        self.generate_grid_button.grid(row=5, column=0, pady=5, sticky='n')

        self.export_grid_button = tk.Button(master, text="Exportuj siatkę", font=('Calibri', 10),
                                            command=self.export_grid, bg="#e8c846")
        self.export_grid_button.grid(row=8, column=0, pady=5, sticky='n')

        # Tworzenie obszaru dla wyświetlania obrazu
        self.image_canvas = tk.Canvas(master, width=300, height=300, bg="#e8c846", highlightbackground="#e8c846")
        self.image_canvas.grid(row=0, column=1, rowspan=7, padx=20, pady=20, sticky='ne')

        if self.selected_grid.get() == "strukturalna":
            # Tworzenie pola tekstowego z opisem "Podaj rozmiar elementu"
            self.grid_size_label = tk.Label(self.master, text="Podaj rozmiar elementu:", font=('Calibri', 10),
                                            bg='gray')
            self.grid_size_entry = tk.Entry(self.master, font=('Calibri', 10))
            self.grid_size_label.grid(row=6, column=0, pady=0, padx=10, sticky='n')
            self.grid_size_entry.grid(row=7, column=0, pady=0, padx=10, sticky='n')

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("PNG", "*.png")])
        self.filename_label_text.set("Wybrany plik: " + self.file_path)

    def grid_type_changed(self, *args):
        if self.selected_grid.get() == "strukturalna":
            self.grid_size_label.grid_remove()
            self.grid_size_entry.grid_remove()

            self.grid_size_label = tk.Label(self.master, text="Podaj rozmiar elementu:", font=('Calibri', 10),
                                            bg='gray')
            self.grid_size_label.grid(row=6, column=0, pady=0, padx=10, sticky='n')

            self.grid_size_entry = tk.Entry(self.master, font=('Calibri', 10))
            self.grid_size_entry.grid(row=7, column=0, pady=0, padx=10, sticky='n')
        elif self.selected_grid.get() == "strukturalnaQT":
            self.grid_size_label.grid_remove()
            self.grid_size_entry.grid_remove()

            self.grid_size_label = tk.Label(self.master, text="Podaj minimalny rozmiar elementu:", font=('Calibri', 10),
                                            bg='gray')
            self.grid_size_label.grid(row=6, column=0, pady=0, padx=10, sticky='n')

            self.grid_size_entry = tk.Entry(self.master, font=('Calibri', 10))
            self.grid_size_entry.grid(row=7, column=0, pady=0, padx=10, sticky='n')
        elif self.selected_grid.get() == "niestrukturalna":
            self.grid_size_label.grid_remove()
            self.grid_size_entry.grid_remove()

            self.grid_size_label = tk.Label(self.master, text="Podaj co ile maja być rozmieszczone punkty pomocnicze:",
                                            font=('Calibri', 10),
                                            bg='gray')
            self.grid_size_label.grid(row=6, column=0, pady=0, padx=10, sticky='n')

            self.grid_size_entry = tk.Entry(self.master, font=('Calibri', 10))
            self.grid_size_entry.grid(row=7, column=0, pady=0, padx=10, sticky='n')
        else:
            self.grid_size_label.grid_remove()
            self.grid_size_entry.grid_remove()

            self.grid_size_label = tk.Label(self.master, text="Podaj jak rozrzedzic punkty w srodku:",
                                            font=('Calibri', 10),
                                            bg='gray')
            self.grid_size_label.grid(row=6, column=0, pady=0, padx=10, sticky='n')

            self.grid_size_entry = tk.Entry(self.master, font=('Calibri', 10))
            self.grid_size_entry.grid(row=7, column=0, pady=0, padx=10, sticky='n')

    def load_file(self):
        if self.file_path != "":
            img = Image.open(self.file_path)

            self.img = ImageTk.PhotoImage(img)
            self.image_canvas.config(width=img.width, height=img.height)  # zmiana rozmiaru Canvas
            self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
            self.image_canvas.image = self.img

            # Ustawienie rozmiaru okna na rozmiar obrazka
            if not self.grid_generated:
                self.master.geometry("{}x{}".format(img.width, img.height))

            min_width = img.width + self.image_canvas.winfo_x() + 100
            min_height = img.height + self.image_canvas.winfo_y() * 2 + 100
            self.master.minsize(min_width, min_height)

    def generate_grid(self):
        if self.grid_generated:
            self.grid_generated = False
            self.generate_grid_button.config(text="Generuj siatkę")
            self.load_file()
        else:
            self.grid_generated = True
            self.generate_grid_button.config(text="Schowaj siatkę")

            matrix = convert_png_to_matrix(self.file_path)

            if self.selected_grid.get() == "strukturalna":
                if self.grid_size_entry.get() == "":
                    num = 1
                else:
                    num = self.grid_size_entry.getint(self.grid_size_entry.get())
                self.mesh = QuadTreeStruct(matrix, self.file_path, num)
                self.mesh.build_tree()
                # wczytaj plik PNG
                img = self.mesh.print_tree()
                self.img = ImageTk.PhotoImage(img)
                self.image_canvas.config(width=img.width, height=img.height)  # zmiana rozmiaru Canvas
                self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
                self.image_canvas.image = self.img
            elif self.selected_grid.get() == "strukturalnaQT":
                if self.grid_size_entry.get() == "":
                    num = 1
                else:
                    num = self.grid_size_entry.getint(self.grid_size_entry.get())
                self.mesh = QuadTree(matrix, self.file_path, num)
                self.mesh.build_tree()
                # wczytaj plik PNG
                img = self.mesh.print_tree()
                self.img = ImageTk.PhotoImage(img)
                self.image_canvas.config(width=img.width, height=img.height)  # zmiana rozmiaru Canvas
                self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
                self.image_canvas.image = self.img
            elif self.selected_grid.get() == "niestrukturalna":
                if self.grid_size_entry.get() == "":
                    num = 60
                else:
                    num = self.grid_size_entry.getint(self.grid_size_entry.get())
                points = generate_all_points_with_addition(matrix, num)
                img = Image.open(self.file_path)
                draw = ImageDraw.Draw(img)
                point_size = 1
                for point in points:
                    # for p in point:
                        x, y = point
                        draw.ellipse((x - point_size, y - point_size, x + point_size, y + point_size), fill="red")

                triangles = BW_Delaunay_Triangulation(points)
                for triangle in triangles:
                    p1 = triangle[0][0], triangle[0][1]
                    p2 = triangle[1][0], triangle[1][1]
                    p3 = triangle[2][0], triangle[2][1]
                    draw.line((p1, p2), fill=160, width=2)
                    draw.line((p2, p3), fill=160, width=2)
                    draw.line((p3, p1), fill=160, width=2)
                print("NON STRUCTURAL - IL PUNKTOW:", len(points), "IL TROJKATOW: ", len(triangles))
                self.mesh = (points, triangles)

                self.img = ImageTk.PhotoImage(img)
                self.image_canvas.config(width=img.width, height=img.height)  # zmiana rozmiaru Canvas
                self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
                self.image_canvas.image = self.img
            elif self.selected_grid.get() == "niestrukturalnaSolo":
                if self.grid_size_entry.get() == "":
                    num = 250
                else:
                    num = self.grid_size_entry.getint(self.grid_size_entry.get())
                points = generate_points_for_solo(matrix, num)
                img = Image.open(self.file_path)
                draw = ImageDraw.Draw(img)
                point_size = 1
                all_triangles = []
                for points_list in points:
                    for p in points_list:
                        x, y = p
                        draw.ellipse((x - point_size, y - point_size, x + point_size, y + point_size), fill="red")

                    triangles = BW_Delaunay_Triangulation(points_list)
                    all_triangles.append(triangles)
                    for triangle in triangles:
                        p1 = triangle[0][0], triangle[0][1]
                        p2 = triangle[1][0], triangle[1][1]
                        p3 = triangle[2][0], triangle[2][1]
                        draw.line((p1, p2), fill=160, width=2)
                        draw.line((p2, p3), fill=160, width=2)
                        draw.line((p3, p1), fill=160, width=2)
                    print("NON STRUCTURAL OBJECTS - IL PUNKTOW:", len(points_list), "IL TROJKATOW: ", len(triangles))

                self.mesh = (points, all_triangles)

                self.img = ImageTk.PhotoImage(img)
                self.image_canvas.config(width=img.width, height=img.height)  # zmiana rozmiaru Canvas
                self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
                self.image_canvas.image = self.img

    def export_grid(self):
        # funkcja eksportująca siatkę
        if self.selected_grid.get() == "strukturalna":
            self.mesh.save_to_txt()
        elif self.selected_grid.get() == "strukturalnaQT":
            self.mesh.save_to_txt()
        elif self.selected_grid.get() == "niestrukturalna":
            points, triangles = self.mesh
            with open("UnstructuralMesh.txt", 'w') as file:
                file.write("Nodes: (ID, X, Y)\n")
                for i, (x, y) in enumerate(points):
                    file.write(f"{i} {x} {y}\n")

                file.write("\nTriangles: (ID, node1ID, node2ID, node3ID)\n")
                for i, (node1, node2, node3) in enumerate(triangles):
                    indexN1 = points.index(node1)
                    indexN2 = points.index(node2)
                    indexN3 = points.index(node3)
                    file.write(f"{i} {indexN1} {indexN2} {indexN3}\n")
        elif self.selected_grid.get() == "niestrukturalnaSolo":
            points, triangles = self.mesh
            with open("UnstructuralOnlyObjectsMesh.txt", 'w') as file:
                for i, (points_list, triangles_list) in enumerate(zip(points, triangles)):
                    file.write(f"Object: {i+1}\n")
                    file.write("Nodes: (ID, X, Y)\n")
                    for ind, (x, y) in enumerate(points_list):
                        file.write(f"{ind} {x} {y}\n")

                    file.write("\nTriangles: (ID, node1ID, node2ID, node3ID)\n")
                    for ind, (node1, node2, node3) in enumerate(triangles_list):
                        indexN1 = points_list.index(node1)
                        indexN2 = points_list.index(node2)
                        indexN3 = points_list.index(node3)
                        file.write(f"{ind} {indexN1} {indexN2} {indexN3}\n")


def main():
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
