from typing import List, Tuple, Dict

"""Implementação de autômatos finitos."""


def load_automata(filename):
    """
    Lê os dados de um autômato finito a partir de um arquivo.

    A estsrutura do arquivo deve ser:

    <lista de símbolos do alfabeto, separados por espaço (' ')>
    <lista de nomes de estados>
    <lista de nomes de estados finais>
    <nome do estado inicial>
    <lista de regras de transição, com "origem símbolo destino">

    Um exemplo de arquivo válido é:

    ```
    a b
    q0 q1 q2 q3
    q0 q3
    q0
    q0 a q1
    q0 b q2
    q1 a q0
    q1 b q3
    q2 a q3
    q2 b q0
    q3 a q1
    q3 b q2
    ```

    Caso o arquivo seja inválido uma exceção Exception é gerada.

    """

    with open(filename, 'r') as f:
        lines = f.read().splitlines()
    
    alphabet = set(lines[0].split())
    states = set(lines[1].split())
    final_states = set(lines[2].split())
    initial_state = lines[3]
    transitions = {}
    
    for line in lines[4:]:
        if line.strip():
            parts = line.split()
            state = parts[0]
            symbol = parts[1]
            next_state = parts[2]
            if state not in transitions:
                transitions[state] = {}
            if symbol not in transitions[state]:
                transitions[state][symbol] = []
            transitions[state][symbol].append(next_state)
    
    return states, alphabet, transitions, initial_state, final_states


def process(automata: Tuple[set, set, Dict[str, Dict[str, List[str]]], str, set], word: List[str]) -> Dict[str, str]:
    states, alphabet, transitions, initial_state, final_states = automata
    
    def process_state(state: str, word: List[str]) -> str:
        if not word:
            if state in final_states:
                return "ACEITA"
            else:
                return "REJEITA"
        
        symbol = word[0]
        if symbol not in alphabet:
            return "INVÁLIDA"
        
        next_states = transitions.get(state, {}).get(symbol, [])
        for next_state in next_states:
            result = process_state(next_state, word[1:])
            if result == "ACEITA":
                return result
        return "REJEITA"
    
    return process_state(initial_state, word)

def convert_to_dfa(automata: Tuple[set, set, Dict[str, Dict[str, List[str]]], str, set]) -> Tuple[set, set, Dict[str, Dict[str, str]], str, set]:
    states, alphabet, transitions, initial_state, final_states = automata
    
    def epsilon_closure(state):
        closure = {state}
        stack = [state]
        while stack:
            current = stack.pop()
            for next_state in transitions.get(current, {}).get('&', []):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    def move(states, symbol):
        new_states = set()
        for state in states:
            new_states.update(transitions.get(state, {}).get(symbol, []))
        return new_states

    dfa_states = {}
    dfa_initial_state = frozenset(epsilon_closure(initial_state))
    dfa_states[dfa_initial_state] = {}

    unmarked_states = [dfa_initial_state]
    dfa_final_states = set()
    
    while unmarked_states:
        current_state = unmarked_states.pop()
        if current_state & final_states:
            dfa_final_states.add(current_state)
        for symbol in alphabet:
            if symbol == '&':
                continue
            new_state = frozenset(epsilon_closure(move(current_state, symbol)))
            if new_state not in dfa_states:
                unmarked_states.append(new_state)
                dfa_states[new_state] = {}
            dfa_states[current_state][symbol] = new_state

    dfa_transitions = {}
    for state, transitions in dfa_states.items():
        state_name = str(state)
        dfa_transitions[state_name] = {symbol: str(dest) for symbol, dest in transitions.items()}

    return set(dfa_transitions.keys()), alphabet - {'&'}, dfa_transitions, str(dfa_initial_state), {str(s) for s in dfa_final_states}
