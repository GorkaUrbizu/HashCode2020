import sys
import types
import numpy as np
from tqdm import tqdm

def read_instance(stream=sys.stdin):
    line = stream.readline()
    n_books, n_lib, n_days = line.rstrip().split()
    n_books, n_lib, n_days = int(n_books), int(n_lib), int(n_days)

    line = stream.readline()
    book_scores = np.array([int(sc) for sc in line.rstrip().split()], dtype=np.int32)

    book_frecuencies = np.zeros(n_books, dtype=np.float32)

    lib_book_counts = []
    lib_signups = []
    lib_shipss = []

    lib_books = []

    for _ in range(n_lib):
        line = stream.readline()
        lib_book_count, lib_signup, lib_ships = line.rstrip().split()
        lib_book_count, lib_signup, lib_ships = int(lib_book_count), int(lib_signup), int(lib_ships)

        lib_book_counts.append(lib_book_count)
        lib_signups.append(lib_signup)
        lib_shipss.append(lib_ships)

        line = stream.readline()
        lib_book = [int(book) for book in line.rstrip().split()]
        lib_book.sort(key=lambda x: book_scores[x], reverse=True)
        lib_book = np.array(lib_book, dtype=np.int32)
        lib_books.append(lib_book)

        book_frecuencies[lib_book] += 1

    lib_book_counts = np.array(lib_book_counts, dtype=np.int32)
    lib_signups = np.array(lib_signups, dtype=np.int32)
    lib_shipss = np.array(lib_shipss, dtype=np.int32)


    inst = types.SimpleNamespace()

    inst.n_books = n_books
    inst.n_lib = n_lib
    inst.n_days = n_days
    inst.book_scores = book_scores
    inst.lib_book_counts = lib_book_counts
    inst.lib_signups = lib_signups
    inst.lib_ships = lib_shipss

    inst.lib_books = lib_books
    inst.book_frecuencies = book_frecuencies

    return inst

def signup_criterion1(instance, lib):
    return np.sum(instance.book_scores[instance.lib_books[lib]])

def signup_criterion2(instance, lib):
    return np.sum(instance.book_scores[instance.lib_books[lib]] / instance.book_frecuencies[instance.lib_books[lib]]) - instance.lib_signups[lib]

def signup_criterion3(instance, lib):
    return np.average(instance.book_scores[instance.lib_books[lib]] - instance.book_frecuencies[instance.lib_books[lib]]) * inst.lib_ships[lib] + instance.lib_signups[lib]

def signup_criterion4(instance, lib):
    return np.sum(np.sort(instance.book_scores[instance.lib_books[lib]] / instance.book_frecuencies[instance.lib_books[lib]])[:-inst.n_days*inst.lib_ships[lib]]) * inst.lib_ships[lib] + instance.lib_signups[lib] 

def signup_critC(instance, lib):
    return instance.lib_book_counts[lib] - instance.lib_signups[lib]*8 + np.average(instance.book_scores[instance.lib_books[lib]] ) 

def get_signups(instance, criterion=signup_critC):

    libraries = list(range(instance.n_lib))
    libraries.sort(key=lambda x: criterion(instance,x), reverse=True)
    return libraries

def get_scans(instance, signup_order):

    scanned_set = set()
    available_lib = []
    last_signup = -1

    lib_book_index = np.zeros(instance.n_lib, dtype=np.int32)
    lib_books_chosen = [[] for _ in range(instance.n_lib)]

    for day in tqdm(range(instance.n_days)):

        # Scan the books
        for lib in available_lib:
            if lib_book_index[lib] == instance.lib_book_counts[lib]:
                continue
            for _ in range(instance.lib_ships[lib]):
                for book_i in range(lib_book_index[lib],instance.lib_book_counts[lib]): 
                    lib_book_index[lib] = book_i+1       
                    book = instance.lib_books[lib][book_i]
                    if book not in scanned_set:
                        lib_books_chosen[lib].append(book)
                        scanned_set.add(book)
                        break
                    
        #print(len(available_lib))
        #print(len(scanned_set))

        if len(available_lib) == instance.n_lib:
            continue

        next_signup_lib = signup_order[len(available_lib)]
        signup_duration = instance.lib_signups[next_signup_lib]

        if day == last_signup + signup_duration:
            available_lib.append(next_signup_lib)
            last_signup = day


    return available_lib, lib_books_chosen

def write_solution(sign_ups, sol, stream=sys.stdout):

    s_ups = sum((1 for sign_up in sign_ups if len(sol[sign_up]) != 0 ))

    stream.write(f"{s_ups}\n")

    for sign_up in sign_ups:
        scan_books = sol[sign_up]
        if len(scan_books) == 0:
            continue
        stream.write(f"{sign_up} {len(scan_books)}\n")
        stream.write(" ".join([str(scan_book) for scan_book in scan_books]))
        stream.write("\n")
    

def eval_sol(inst, lib_books_chosen):
    return sum((np.sum(inst.book_scores[books]) for books in lib_books_chosen))

if __name__ == "__main__":
    """
    inst = read_instance(open("a_example.txt"))
    sign_up = get_signups(inst)
    sign_up_order, books_chosen = get_scans(inst,sign_up)
    eval1 = eval_sol(inst, books_chosen)
    write_solution(sign_up_order, books_chosen, open("a_sol.txt","w+"))
    print(eval1)

    inst = read_instance(open("b_read_on.txt"))
    sign_up = get_signups(inst)
    sign_up_order, books_chosen = get_scans(inst,sign_up)
    eval2 = eval_sol(inst, books_chosen)
    write_solution(sign_up_order, books_chosen, open("b_sol.txt","w+"))
    print(eval2)

    inst = read_instance(open("c_incunabula.txt"))
    sign_up = get_signups(inst)
    sign_up_order, books_chosen = get_scans(inst,sign_up)
    eval3 = eval_sol(inst, books_chosen)
    write_solution(sign_up_order, books_chosen, open("c_sol.txt","w+"))
    print(eval3)
    

    inst = read_instance(open("d_tough_choices.txt"))
    sign_up = get_signups(inst)
    sign_up_order, books_chosen = get_scans(inst,sign_up)
    eval4 = eval_sol(inst, books_chosen)
    write_solution(sign_up_order, books_chosen, open("d_sol.txt","w+"))
    print(eval4)
    
    
    inst = read_instance(open("e_so_many_books.txt"))
    sign_up = get_signups(inst)
    sign_up_order, books_chosen = get_scans(inst,sign_up)
    eval5 = eval_sol(inst, books_chosen)
    write_solution(sign_up_order, books_chosen, open("e_sol.txt","w+"))
    print(eval5)
    """

    inst = read_instance(open("f_libraries_of_the_world.txt"))
    sign_up = get_signups(inst)
    sign_up_order, books_chosen = get_scans(inst,sign_up)
    eval6 = eval_sol(inst, books_chosen)
    write_solution(sign_up_order, books_chosen, open("f_sol.txt","w+"))
    print(eval6)

    print(sum([eval1, eval2, eval3, eval4, eval5, eval6]))
