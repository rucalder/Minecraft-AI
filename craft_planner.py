import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush
import heapq

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.

    def check(state):
        #print("Rule: " + str(rule))
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        if 'Consumes' in rule:
            consumableDic = rule['Consumes']
            for consumable in consumableDic:
                required_amount = consumableDic[consumable]
                if state[consumable] < required_amount:
                    return False
        if 'Requires' in rule:
            requiresDic = rule['Requires']
            for requirement in requiresDic:
                if state[requirement] == 0:
                    return False
        return True

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        next_state = None
        next_state = state.copy()
        if 'Produces' in rule:
            productionDic = rule['Produces']
            for produced_item in productionDic:
                next_state[produced_item] += productionDic[produced_item]

        if 'Consumes' in rule:
            consumeDic = rule['Consumes']
            for consumed_item in consumeDic:
                next_state[consumed_item] -= consumeDic[consumed_item]

        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        goalDic = goal
        for goal_item in goalDic:
            if state[goal_item] < goalDic[goal_item]:
                return False
        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        #print("R check:" + str(r.check(state)))
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def heuristic(state, prev_state):
    # Implement your heuristic here!
    # If rule['Produces'] is in state['items']
    #print("In heuristic")
    #print("State items: " + str(state['bench']))
    if state['bench'] > 1 or state['furnace'] > 1 or state['iron_axe'] > 1 or state['iron_pickaxe'] > 1 or state['stone_axe'] > 1 or state['stone_pickaxe'] > 1 or state['wooden_axe'] > 1 or state['wooden_pickaxe'] > 1 or state['cart'] > 1:
        return False
    if state['coal'] > 1 or state['cobble'] > 10 or state['ingot'] > 10 or state['ore'] > 1 or state['plank'] > 8 or state['stick'] > 5 or state['wood'] > 2:
        return False
    if state['bench'] == 0 and state['plank'] > 7:
        return False
    #if prev_state['ore'] > 0 and  prev_state['coal'] > 0 and prev_state['furnace'] > 0 and state['ingot'] == prev_state['ingot']:
    #    return False
    return True

def search(graph, state, is_goal, limit, heuristic):

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    source = state

    state_list = []
    #state_list.append((source, None))

    state_to_action = {}
    state_to_action[source] = None

    parent = {}
    parent[source] = None

    time_from_source = {}
    time_from_source[source] = 0

    queue = PriorityQueue()
    queue.put(source, time_from_source[source])

    start_time = time()
    

    while time() - start_time < limit and not queue.empty():

        #print("Queue: " + str(queue))

        current_state = queue.get()
        #print("Current state: " + str(current_state))
        #print("State to action: " + str(state_to_action))
        #state_list.append((current_state, state_to_action[current_state]))

        #print("Before is goal")

        # if current state contains goal, return list of states
        if is_goal(current_state):
            temp = current_state
            while temp != None:
                state_list.append((temp, state_to_action[temp]))
                temp = parent[temp]

            state_list.reverse()
            return state_list, time_from_source[current_state]

        # Check every available next_state using for loop
        iterator = graph(current_state)

        has_next = True

        #print("BEfore while")
        
        while has_next:

            #print("In while")

            try:
                #print("In try")
                rule, next_state, action_time = next(iterator)
                #print("Next state: " + str(next_state))

                #Use heuristic, if rule matches conditions, skip state/rule
                #pass
                if heuristic(next_state, current_state):
                    #print("after heuristic")
                    # Add time it takes to reach next_state (heuristic?)
                    true_time = time_from_source[current_state] + action_time
                    if next_state not in time_from_source or true_time < time_from_source[next_state]:
                        #print("In if in while")
                        time_from_source[next_state] = true_time
                        parent[next_state] = current_state
                        state_to_action[next_state] = rule

                        # Add state to priority queue based on time
                        queue.put(next_state, time_from_source[next_state])

                    rule, next_state, action_time = graph(current_state)
                    #print("Queue in while: " + str(queue))

            except:
                #print("In except")
                has_next = False

    #print("State list: " + str(state_list))

    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None

if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    print('All items:', Crafting['Items'])
    
    # # List of items in your initial inventory with amounts:
    print('Initial inventory:', Crafting['Initial'])
    
    # # List of items needed to be in your inventory at the end of the plan:
    print('Goal:',Crafting['Goal'])
    
    # # Dict of crafting recipes (each is a dict):
    print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])
    #print(state.keys())

    # Search for a solution
    resulting_plan, cost = search(graph, state, is_goal, 30, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t',state)
            print(action)

        print("Cost: " + str(cost))
        print("Length: " + str(len(resulting_plan)))
