import random
import numpy as np
import sys
import math

N = 500  # Population size
generations = 100  # Number of generations
mutation_rate = 0.00  # Mutation rate
crossover_rate = 0.5

activities = ["SLA101A","SLA101B","SLA191A","SLA191B","SLA201","SLA291","SLA303","SLA304","SLA394","SLA449","SLA451"]  # List of activity names
rooms = ["Slater 003"
         ,"Roman 216"
         ,"Loft 206"
         ,"Roman 201"
         ,"Loft 310"
         ,"Beach 201"
         ,"Beach 301"
         ,"Logos 325"
         ,"Frank 119"
         ]  # List of room names
roomsNumber = {"Slater 003" : 45,
         "Roman 216" : 30,
         "Loft 206" : 75,
         "Roman 201" : 50,
         "Loft 310" : 108,
         "Beach 201" : 60,
         "Beach 301" : 75,
         "Logos 325"  : 450,
         "Frank 119" : 60,
         }  # List of room names
times = [10,11,12,13,14,15]  # List of available time slots
facilitators = ["Lock", "Glen", "Banks", "Richards", "Shaw", "Singer", "Uther", "Tyler", "Numen", "Zeldin"]  # List of facilitator names
courses = {
    "SLA101A": {
        "Expected Enrollment": 50,
        "Preferred Facilitators": ["Glen", "Lock", "Banks","Zeldin"],
        "Other Facilitators": ["Numen", "Richards"]
    },
    "SLA101B": {
        "Expected Enrollment": 50,
        "Preferred Facilitators": ["Glen", "Lock", "Banks","Zeldin"],
        "Other Facilitators": ["Numen", "Richards"]
    },
    "SLA191A": {
        "Expected Enrollment": 50,
        "Preferred Facilitators": ["Glen", "Lock", "Banks","Zeldin"],
        "Other Facilitators": ["Numen", "Richards"]
    },
    "SLA191B": {
        "Expected Enrollment": 50,
        "Preferred Facilitators": ["Glen", "Lock", "Banks","Zeldin"],
        "Other Facilitators": ["Numen", "Richards"]
    },
    "SLA201": {
        "Expected Enrollment": 50,
        "Preferred Facilitators": ["Glen","Banks","Zeldin", "Shaw"],
        "Other Facilitators": ["Numen", "Richards", "Singer"]
    },
    "SLA291": {
        "Expected Enrollment": 50,
        "Preferred Facilitators": ["Lock", "Banks","Zeldin","Singer"],
        "Other Facilitators": ["Numen", "Richards","Shaw","Tyler"]
    },
    "SLA303": {
        "Expected Enrollment": 60,
        "Preferred Facilitators": ["Glen", "Zeldin", "Banks"],
        "Other Facilitators": ["Numen", "Singer", "Shaw"]
    },
    "SLA304": {
        "Expected Enrollment": 25,
        "Preferred Facilitators": ["Glen", "Banks", "Tyler"],
        "Other Facilitators": ["Numen", "Singer", "Shaw", "Richards", "Uther", "Zeldin"]
    },
    "SLA394": {
        "Expected Enrollment": 20,
        "Preferred Facilitators": ["Tyler", "Singer"],
        "Other Facilitators": ["Richards", "Zeldin"]
    },
    "SLA449": {
        "Expected Enrollment": 60,
        "Preferred Facilitators": ["Tyler", "Singer", "Shaw"],
        "Other Facilitators": ["Zeldin", "Uther"]
    },
    "SLA451": {
        "Expected Enrollment": 100,
        "Preferred Facilitators": ["Tyler", "Singer", "Shaw"],
        "Other Facilitators": ["Zeldin", "Uther","Richards","Banks"]
    }
}

#--------------------------------------------------------------------------------------------------
# Initialize schedules with random assignments
def initialize_schedule():
    schedule = []
    for _ in activities:  # Assign 11 activities
        activity = _
        room = random.choice(rooms)
        time = random.choice(times)
        facilitator = random.choice(facilitators)
        schedule.append((activity, room, time, facilitator))
    return schedule
# Define a function to calculate the fitness of a schedule
def calculate_fitness(schedule):
    fitness = 0
    duplist = []
    for index, activity in enumerate(schedule):
     
        room_condition = room_size_condition(activity, courses, roomsNumber)
        if room_condition == -0.5:
            fitness -= 0.5
        elif room_condition == -0.2:
            fitness -= 0.2
        elif room_condition == -0.4:
            fitness -= 0.4
        else:
            fitness += 0.3

        if has_overlap(activity, duplist, index, schedule):
            fitness -= 0.5
        
        #Check facilitator conditions
        facilitator = activity[3]
        
        for x in courses[activity[0]]["Preferred Facilitators"]:
            for y in courses[activity[0]]["Other Facilitators"]:
                #print(f"faci: {facilitator} x: {x}, y: {y}")
                if facilitator == x:
                    fitness += 0.5
                elif facilitator == y:
                    fitness += 0.2
                else:
                    fitness -= 0.1
        
        fitness += calculate_facilitator_load(activity,schedule)
        fitness += facilitator_adjustment(activity, schedule)
        fitness += calculate_activity_adjustment(activity, schedule)
        
    return fitness

#--------------------------------------------------------------------------------------------------
def has_overlap(activity, duplist, index, schedule):
    # Check if this activity has the same time and room as another activity
    for i in range(index):
        other_activity = schedule[i]
        if (
            activity[1] == other_activity[1]  # Same room
            and activity[2] == other_activity[2]  # Same time slot
        ):
            duplist.append(activity[2])  # Record the time slot as duplicate
            return True
    return False

def room_size_condition(activity, courses, roomsNumber):
    activity_name = activity[0]
    enrollment = courses[activity_name]['Expected Enrollment']
    room_name = activity[1]
    room_capacity = roomsNumber[room_name]

    if enrollment * 6 <= room_capacity:
        return -0.4
    elif enrollment * 3 <= room_capacity:
        return -0.2
    elif enrollment > room_capacity:
        return -0.5
    else:
        return 0.3

def calculate_facilitator_load(activity, schedule):
    facilitator_load = {}
    for slot in schedule:
        if slot[2] == activity[2]:
            if slot[3] not in facilitator_load:
                facilitator_load[slot[3]] = 1
            else:
                facilitator_load[slot[3]] += 1

    activity_adjustment = 0.0

    # Activity facilitator is scheduled for only 1 activity in this time slot
    if activity[3] in facilitator_load and facilitator_load[activity[3]] == 1:
        activity_adjustment += 0.2

    # Activity facilitator is scheduled for more than one activity at the same time
    if activity[3] in facilitator_load and facilitator_load[activity[3]] > 1:
        activity_adjustment -= 0.2

    # Facilitator is scheduled to oversee more than 4 activities total
    total_facilitator_activities = sum(facilitator_load.values())
    if total_facilitator_activities > 4:
        activity_adjustment -= 0.5

    # Facilitator is scheduled to oversee 1 or 2 activities
    if activity[3] == "Tyler":
        # Exception for Dr. Tyler (committee chair)
        if total_facilitator_activities < 2:
            activity_adjustment -= 0
    else:
        if total_facilitator_activities < 2:
            activity_adjustment -= 0.4

    # If any facilitator scheduled for consecutive time slots
    if has_consecutive_time_slots(activity, schedule):
       if abs(activity[2] - slot[2]) == 1:
            
            # Check if one is in Roman or Beach while the other isn't
            if (activity[1] in ["Roman 201", "Beach 201","Roman 316", "Beach 301"] and slot[1] not in ["Roman 201", "Beach 201","Roman 316", "Beach 301"]) or \
               (activity[1] not in ["Roman 201", "Beach 201","Roman 316", "Beach 301"] and slot[1] in ["Roman 201", "Beach 201","Roman 316", "Beach 301"]):
                
                activity_adjustment -= 0.4  # One is in Roman or Beach while the other isn't
            activity_adjustment += 0.5
        
    return activity_adjustment

def has_consecutive_time_slots(activity, schedule):
    for slot in schedule:
        if slot[3] == activity[3] and abs(slot[2] - activity[2]) == 1:
            return True
    return False

def facilitator_adjustment(activity, all_activities):
    adjustment = 0.0

    for other_activity in all_activities:
        if activity != other_activity:
            if abs(activity[2] - other_activity[2]) == 1:  # Check for consecutive time slots
                if (activity[1] in ["Roman 201", "Beach 201","Roman 316", "Beach 301"] and other_activity[1] not in ["Roman 201", "Beach 201","Roman 316", "Beach 301"]) or \
                        (activity[1] not in ["Roman 201", "Beach 201","Roman 316", "Beach 301"] and other_activity[1] in ["Roman 201", "Beach 201","Roman 316", "Beach 301"]):
                    adjustment -= 0.4  # One activity is in Roman or Beach while the other isn't
                else:
                    adjustment += 0.5
    #print("faci adj con:", adjustment)
    return adjustment

def calculate_activity_adjustment(activity, schedule):
    adjustment = 0.0

    if activity[0] == "SLA101A" or "SLA101B":
        # Check for SLA 101 specific adjustments
        adjustment += sla101_adjustment(schedule, activity)
    elif activity[0] == "SLA191A" or "SLA191B":
        # Check for SLA 191 specific adjustments
        adjustment += sla191_adjustment(schedule, activity)
    #print("cal act con:", adjustment)
    return adjustment

def sla101_adjustment(schedule, activity):
    adjustment = 0.0

    # Find the other SLA 101 activities
    other_sla101_activities = [act for act in schedule if act[0] == "SLA101A" or "SLA101B" and act != activity]

    for other_activity in other_sla101_activities:
        # Check if the other SLA 101 activity is more than 4 hours apart
        time_difference = abs(activity[2] - other_activity[2])
        if time_difference > 4:
            adjustment += 0.5  # The 2 sections of SLA 101 are more than 4 hours apart

        # Check if there are any other SLA 101 activities in the same time slot
        if activity[2] == other_activity[2]:
            adjustment -= 0.5  # Both sections of SLA 101 are in the same time slot

    return adjustment

def sla191_adjustment(schedule, activity):
    adjustment = 0.0

    # Find the other SLA 191 activities
    other_sla191_activities = [act for act in schedule if act[0] == "SLA191A" or "SLA191B" and act != activity]

    for other_activity in other_sla191_activities:
        # Check if the other SLA 191 activity is more than 4 hours apart
        time_difference = abs(activity[2] - other_activity[2])
        if time_difference > 4:
            adjustment += 0.5  # The 2 sections of SLA 191 are more than 4 hours apart

        # Check if there are any other SLA 191 activities in the same time slot
        if activity[2] == other_activity[2]:
            adjustment -= 0.5  # Both sections of SLA 191 are in the same time slot

        # Check if SLA 191 and SLA 101 are overseen in consecutive time slots
        if abs(activity[2] - other_activity[2]) == 1:
            
            # Check if one is in Roman or Beach while the other isn't
            if (activity[1] in ["Roman 201", "Beach 201","Roman 316", "Beach 301"] and other_activity[1] not in ["Roman 201", "Beach 201","Roman 316", "Beach 301"]) or \
               (activity[1] not in ["Roman 201", "Beach 201","Roman 316", "Beach 301"] and other_activity[1] in ["Roman 201", "Beach 201","Roman 316", "Beach 301"]):
                
                adjustment -= 0.4  # One is in Roman or Beach while the other isn't
            adjustment += 0.5

        # Check if SLA 191 and SLA 101 are taught separated by 1 hour
        if abs(activity[2] - other_activity[2]) == 2:
            adjustment += 0.25

        # Check if SLA 191 and SLA 101 are taught in the same time slot
        if activity[2] == other_activity[2]:
            adjustment -= 0.25

    return adjustment

#--------------------------------------------------------------------------------------------------
def custom_softmax(fitness_scores, temperature=1.0):
    # Apply the softmax function with a specified temperature
    e_x = np.exp((fitness_scores - np.max(fitness_scores)) / temperature)
    total = sum(e_x)
    softmax_probabilities = e_x / total
    return softmax_probabilities

def crossover(parent1, parent2):
    # Choose a random crossover point
    crossover_point = random.randint(2, len(parent1) - 1)

    # Create two children by combining the parents at the crossover point
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]

    return child1, child2

def mutation(schedule, activities, rooms, times, facilitators, mutation_rate):
    mutated_schedule = schedule.copy()  # Create a copy of the original schedule to avoid modifying it directly

    for i in range(len(mutated_schedule)):
        if random.random() < mutation_rate:
            # Choose a random activity to mutate
            mutated_activity = random.choice(activities)
            
            # Randomly select a new room, time, or facilitator
            new_room = random.choice(rooms)
            new_time = random.choice(times)
            new_facilitator = random.choice(facilitators)
            
            # Apply the mutation by replacing the selected activity with new values
            mutated_schedule[i] = (mutated_schedule[i][0], new_room, new_time, new_facilitator)

    return mutated_schedule

def softmax_selection(population, softmax_probabilities):
    selected = random.uniform(0, 1)
    cumulative_probability = 0

    for i in range(len(population)):
        cumulative_probability += softmax_probabilities[i]
        if cumulative_probability > selected:
            return population[i]

def softmax_selection(population, fitness_scores, temperature=1.0):
    # Convert fitness scores to selection probabilities using the softmax function
    prob_weights = [math.exp(score / temperature) for score in fitness_scores]
    total_weight = sum(prob_weights)
    probabilities = [weight / total_weight for weight in prob_weights]

    # Select schedules based on the calculated probabilities
    selected_indices = random.choices(range(len(population)), weights=probabilities, k=len(population))
    selected_schedules = [population[i] for i in selected_indices]

    return selected_schedules

def crossover_population_with_softmax(population, softmax_probabilities, crossover_rate, mutation_rate):
    new_population = []

    for i in range(0, len(population), 2):
        if i + 1 < len(population):
            parent1 = softmax_selection(population, softmax_probabilities)
            parent2 = softmax_selection(population, softmax_probabilities)
            
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2

            mutated_child1 = mutation(child1, activities, rooms, times, facilitators, mutation_rate)
            mutated_child2 = mutation(child2, activities, rooms, times, facilitators, mutation_rate)
            
            new_population.extend([mutated_child1, mutated_child2])
    
    return new_population

#--------------------------------------------------------------------------------------------------
# Initialize the population with random schedules
population = [initialize_schedule() for _ in range(N)]

# Genetic Algorithm
fitness_field = []
fitness_gen = []
worst_score = 0
z=0

for generation in range(generations):
    z+=1
    # Evaluate the fitness of each schedule in the population
    fitness_scores = [calculate_fitness(schedule) for schedule in population]
    for i in fitness_scores:
        fitness_field.append((f"Gen {z}. fitness:",i))

    softmax_probabilities = custom_softmax(fitness_scores)

    # Select schedules for the next generation using softmax
    selected_individual = softmax_selection(population, softmax_probabilities)

    # Apply crossover and mutation to create the next generation
    new_population = crossover_population_with_softmax(population, softmax_probabilities, crossover_rate, mutation_rate)

    fitness_gen.append((fitness_scores))
    for x in fitness_gen:
        if worst_score > min(x):
            worst_score = min(x) 
    # Replace the old population with the new one
    population = new_population

#--------------------------------------------------------------------------------------------------
# Find the best schedule in the final population
best_schedule = max(population, key=calculate_fitness)
best_score = max(fitness_scores)

# Specify the file name you want to write to
output_file = "output (mutation 0).txt"

# Open the file in write mode and redirect the output to it
with open(output_file, "w") as file:
    sys.stdout = file  # Redirect standard output to the file

    # Your print statements will now write to the file
    for i in fitness_field:
        print(i)

    print(" ")
    print("Best Schedule:")
    for (activity, room, time, facilitator) in best_schedule:
        print(f"Activity: {activity}, Room: {room}, Time: {time}, Facilitator: {facilitator}")
    print(" ")
    print(f"Best all:",best_score)
    print(f"Worst all:",worst_score)
# Reset standard output to the console
sys.stdout = sys.__stdout__

# The file is automatically closed when you exit the "with" block
print("Success")