import os
import mysql.connector
import random
import numpy as np
from scipy.optimize import linear_sum_assignment
from dotenv import load_dotenv
load_dotenv()  # Charge les variables d'environnement depuis le fichier .env



def run_dispatching():
    # -----------------------
    # CONNECT TO MYSQL
    # -----------------------
    conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB")
)
    cursor = conn.cursor(dictionary=True)

    # -----------------------
    # GET AVERAGE TIMES
    # -----------------------
    cursor.execute("""
    SELECT machine_id, product, employee_id,
           AVG(task_duration_min) AS avg_time
    FROM factory_logs
    WHERE anomaly_flag = 0
    GROUP BY machine_id, product, employee_id;
    """)
    results = cursor.fetchall()

    fitness_dict = {}
    for row in results:
        key = (row["machine_id"], row["product"])
        emp = row["employee_id"]
        avg_time = float(row["avg_time"])
        if key not in fitness_dict:
            fitness_dict[key] = {}
        fitness_dict[key][emp] = avg_time

    # -----------------------
    # BUILD BALANCED TASK POOL
    # -----------------------
    cursor.execute("""
    SELECT DISTINCT machine_id, product
    FROM factory_logs
    WHERE anomaly_flag = 0;
    """)
    unique_tasks = cursor.fetchall()
    unique_task_pairs = [(t["machine_id"], t["product"]) for t in unique_tasks]

    all_employees = set()
    for key in fitness_dict:
        for emp in fitness_dict[key]:
            all_employees.add(emp)
    all_employees = sorted(all_employees)

    NUM_EMPLOYEES = len(all_employees)
    NUM_UNIQUE_PAIRS = len(unique_task_pairs)
    REPEATS = max(1, NUM_EMPLOYEES // NUM_UNIQUE_PAIRS)

    tasks = unique_task_pairs * REPEATS
    # Trim or pad to exactly NUM_EMPLOYEES tasks so we have 1 task per employee
    if len(tasks) < NUM_EMPLOYEES:
        extra = NUM_EMPLOYEES - len(tasks)
        tasks += random.choices(unique_task_pairs, k=extra)
    tasks = tasks[:NUM_EMPLOYEES]
    random.shuffle(tasks)
    NUM_TASKS = len(tasks)  # == NUM_EMPLOYEES

    # -----------------------
    # GA PARAMETERS
    # -----------------------
    POP_SIZE = 50
    GENERATIONS = 100
    MUTATION_RATE = 0.1
    NUM_RUNS = 5

    # -----------------------
    # HELPER FUNCTIONS
    # -----------------------

    def get_eligible(task_index):
        """Return list of employees eligible for a given task."""
        m, p = tasks[task_index]
        return list(fitness_dict[(m, p)].keys())

    def create_individual():
        """
        Create a valid individual where each employee is assigned AT MOST ONE task.
        We shuffle employees and assign them 1-to-1 to tasks.
        If an employee is not eligible for their assigned task, we find the
        nearest unassigned eligible employee.
        """
        employee_pool = all_employees.copy()
        random.shuffle(employee_pool)
        individual = [None] * NUM_TASKS

        # First pass: try direct 1-to-1 assignment
        unassigned_tasks = []
        used_employees = set()

        for i in range(NUM_TASKS):
            emp = employee_pool[i]
            eligible = get_eligible(i)
            if emp in eligible:
                individual[i] = emp
                used_employees.add(emp)
            else:
                unassigned_tasks.append(i)

        # Second pass: for unassigned tasks, find unused eligible employees
        unused_employees = [e for e in all_employees if e not in used_employees]
        random.shuffle(unused_employees)

        for i in unassigned_tasks:
            eligible = set(get_eligible(i))
            assigned = False
            for emp in unused_employees:
                if emp in eligible:
                    individual[i] = emp
                    used_employees.add(emp)
                    unused_employees.remove(emp)
                    assigned = True
                    break
            if not assigned:
                # Fallback: allow reuse only if no unused eligible employee exists
                individual[i] = random.choice(get_eligible(i))

        return individual

    def evaluate(individual):
        """Evaluate fitness — penalize any employee assigned more than once."""
        total_time = 0
        employee_times = {}
        employee_task_count = {}

        for i, emp in enumerate(individual):
            machine, product = tasks[i]
            avg_time = fitness_dict[(machine, product)].get(emp, 999999)
            employee_times[emp] = employee_times.get(emp, 0) + avg_time
            employee_task_count[emp] = employee_task_count.get(emp, 0) + 1
            total_time += avg_time

        # Heavy penalty for duplicate assignments
        duplicates = sum(v - 1 for v in employee_task_count.values() if v > 1)
        penalty = duplicates * 100000

        time_std = np.std(list(employee_times.values()))
        task_std = np.std(list(employee_task_count.values()))

        return (total_time + penalty, time_std, task_std)

    def fitness(individual):
        total_time, time_std, task_std = evaluate(individual)
        return total_time + (time_std * 50) + (task_std * 500)

    def selection(pop):
        return sorted(pop, key=fitness)[:POP_SIZE // 2]

    def crossover(p1, p2):
        """
        Order-based crossover to preserve the 1-to-1 constraint as much as possible.
        """
        point = random.randint(1, NUM_TASKS - 1)
        child = p1[:point] + p2[point:]

        # Fix duplicates: find duplicated and missing employees
        seen = {}
        for i, emp in enumerate(child):
            seen.setdefault(emp, []).append(i)

        duplicated_emps = {emp: idxs for emp, idxs in seen.items() if len(idxs) > 1}
        used = set(child)
        missing_emps = [e for e in all_employees if e not in used]
        random.shuffle(missing_emps)

        for emp, idxs in duplicated_emps.items():
            # Keep the first occurrence, replace the rest
            for idx in idxs[1:]:
                if missing_emps:
                    replacement = missing_emps.pop(0)
                    # Check eligibility, otherwise keep best available
                    eligible = set(get_eligible(idx))
                    if replacement in eligible:
                        child[idx] = replacement
                    else:
                        # Find any missing eligible employee
                        for j, e in enumerate(missing_emps):
                            if e in eligible:
                                child[idx] = e
                                missing_emps.pop(j)
                                missing_emps.append(replacement)
                                break
                        else:
                            child[idx] = replacement  # fallback

        return child

    def mutation(individual):
        """Swap-based mutation to preserve the 1-to-1 constraint."""
        individual = individual.copy()
        for i in range(NUM_TASKS):
            if random.random() < MUTATION_RATE:
                # Swap employee at position i with a random other position
                j = random.randint(0, NUM_TASKS - 1)
                individual[i], individual[j] = individual[j], individual[i]
        return individual

    # -----------------------
    # RUN GA
    # -----------------------
    all_solutions = []

    for run in range(NUM_RUNS):
        population = [create_individual() for _ in range(POP_SIZE)]

        for gen in range(GENERATIONS):
            selected = selection(population)
            new_population = selected.copy()
            while len(new_population) < POP_SIZE:
                p1, p2 = random.sample(selected, 2)
                child = mutation(crossover(p1, p2))
                new_population.append(child)
            population = new_population

        best = min(population, key=fitness)
        result = evaluate(best)
        all_solutions.append((best, result))

    # -----------------------
    # COMPARE SOLUTIONS
    # -----------------------
    scored = []
    for i, (sol, (total_time, time_std, task_std)) in enumerate(all_solutions):
        score = total_time + (time_std * 50) + (task_std * 500)
        scored.append((i + 1, sol, total_time, time_std, task_std, score))

    best_overall = min(scored, key=lambda x: x[5])

    # -----------------------
    # DETAIL OF BEST OVERALL
    # -----------------------
    best_sol = best_overall[1]
    employee_summary = {}

    for i, emp in enumerate(best_sol):
        machine, product = tasks[i]
        avg_time = fitness_dict[(machine, product)].get(emp, 0)
        if emp not in employee_summary:
            employee_summary[emp] = {"tasks": 0, "time": 0.0, "assignments": []}
        employee_summary[emp]["tasks"] += 1
        employee_summary[emp]["time"] += avg_time
        employee_summary[emp]["assignments"].append(f"{machine}/{product}")

    # Employees with no task
    assigned_employees = set(employee_summary.keys())
    unassigned_employees = sorted(set(all_employees) - assigned_employees)

    cursor.close()
    conn.close()

    assignments_list = [
        {
            "employee_id": emp,
            "tasks": data["tasks"],
            "total_time_min": round(data["time"], 2),
            "assignments": data["assignments"]
        }
        for emp, data in sorted(employee_summary.items())
    ]

    return {
        "diagnostics": {
            "unique_task_types": NUM_UNIQUE_PAIRS,
            "total_tasks": NUM_TASKS,
            "total_employees": NUM_EMPLOYEES,
            "avg_tasks_per_employee": round(NUM_TASKS / NUM_EMPLOYEES, 1),
            "unassigned_employees": unassigned_employees,
            "unassigned_count": len(unassigned_employees)
        },
        "solutions_summary": [
            {
                "solution": s[0],
                "total_time_min": round(s[2], 1),
                "time_std": round(s[3], 2),
                "task_std": round(s[4], 2),
                "score": round(s[5], 1)
            }
            for s in scored
        ],
        "best_solution": {
            "solution_id": best_overall[0],
            "total_time_min": round(best_overall[2], 1),
            "time_std": round(best_overall[3], 2),
            "task_std": round(best_overall[4], 2),
            "score": round(best_overall[5], 1)
        },
        "dispatching": assignments_list
    }



def run_dispatching_hungarian():
    # -----------------------
    # CONNECT TO MYSQL
    # -----------------------
    conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB")
    )
    cursor = conn.cursor(dictionary=True)

    # -----------------------
    # GET AVERAGE TIMES PER (machine, product, employee)
    # -----------------------
    cursor.execute("""
    SELECT machine_id, product, employee_id,
           AVG(task_duration_min) AS avg_time
    FROM factory_logs
    WHERE anomaly_flag = 0
    GROUP BY machine_id, product, employee_id;
    """)
    results = cursor.fetchall()

    # fitness_dict[machine_id][product][employee_id] = avg_time
    fitness_dict = {}
    machine_employees = {}  # machine_id -> set of employees

    for row in results:
        machine = row["machine_id"]
        product = row["product"]
        emp = row["employee_id"]
        avg_time = float(row["avg_time"])

        if machine not in fitness_dict:
            fitness_dict[machine] = {}
        if product not in fitness_dict[machine]:
            fitness_dict[machine][product] = {}
        fitness_dict[machine][product][emp] = avg_time

        if machine not in machine_employees:
            machine_employees[machine] = set()
        machine_employees[machine].add(emp)

    cursor.close()
    conn.close()

    # -----------------------
    # RUN HUNGARIAN PER MACHINE
    # -----------------------
    PENALTY = 999999  # cost for employee with no data for a product

    all_assignments = []
    all_unassigned = []
    total_time = 0.0

    machines = sorted(fitness_dict.keys())

    for machine in machines:
        products = sorted(fitness_dict[machine].keys())  # 5 products
        employees = sorted(machine_employees[machine])   # ~50 employees

        num_products = len(products)    # 5
        num_employees = len(employees)  # ~50

        # Build cost matrix: rows = employees, cols = products
        cost_matrix = np.full((num_employees, num_products), PENALTY, dtype=float)

        for i, emp in enumerate(employees):
            for j, product in enumerate(products):
                if emp in fitness_dict[machine].get(product, {}):
                    cost_matrix[i][j] = fitness_dict[machine][product][emp]

        # Transpose: (num_products x num_employees)
        # Assigns each product to its optimal employee
        row_ind, col_ind = linear_sum_assignment(cost_matrix.T)

        assigned_employees = set()

        for product_idx, emp_idx in zip(row_ind, col_ind):
            emp = employees[emp_idx]
            product = products[product_idx]
            time = cost_matrix[emp_idx][product_idx]

            if time >= PENALTY:
                all_unassigned.append({
                    "employee_id": emp,
                    "machine_id": machine,
                    "reason": f"No data for {product}"
                })
                continue

            all_assignments.append({
                "employee_id": emp,
                "machine_id": machine,
                "product": product,
                "avg_time_min": round(time, 2)
            })
            assigned_employees.add(emp)
            total_time += time

        

    # -----------------------
    # BUILD SUMMARY
    # -----------------------
    machine_summary = {}
    for a in all_assignments:
        m = a["machine_id"]
        if m not in machine_summary:
            machine_summary[m] = {"assigned": 0, "total_time_min": 0.0, "tasks": []}
        machine_summary[m]["assigned"] += 1
        machine_summary[m]["total_time_min"] += a["avg_time_min"]
        machine_summary[m]["tasks"].append(
            f"{a['employee_id']} -> {a['product']} ({a['avg_time_min']} min)"
        )

    return {
        "algorithm": "Hungarian (linear_sum_assignment)",
        "priority": "Minimize total time",
        "diagnostics": {
            "assigned_employees": len(all_assignments),
            "total_time_min": round(total_time, 2)
        },
        "assignments": all_assignments,
    }

def worst_real_dispatching(day: str):
    """
    Retourne le pire employé par machine/product pour une date donnée
    day format: YYYY-MM-DD
    """
    conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB")
    )
    cursor = conn.cursor(dictionary=True)

    query = f"""
    WITH avg_times AS (
        SELECT 
            machine_id,
            product,
            employee_id,
            ROUND(AVG(task_duration_min),2) AS avg_time
        FROM factory_logs
        WHERE tag_event_start >= '{day} 00:00:00'
          AND tag_event_start <  '{day} 23:59:59'
          AND anomaly_flag = 0
        GROUP BY machine_id, product, employee_id
    )
    SELECT machine_id,
           product,
           employee_id,
           avg_time
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (
                   PARTITION BY machine_id, product
                   ORDER BY avg_time DESC
               ) AS rn
        FROM avg_times
    ) ranked
    WHERE rn = 1
    ORDER BY machine_id, product;
    """

    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results