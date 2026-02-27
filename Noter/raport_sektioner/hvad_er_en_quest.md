## Hvad er en quest?


goto -> goto_atomic = {}

<goto> :=
    terminal
    explore
    <learn> goto
->
goto_terminal = {}
goto_expore = {
    explore : explore_atomic
}
goto_learn = {
    learn : learns
    goto : goto_atomic
}

gotos = union[goto_terminal, goto_explore, goto_learn]

fetch : <goto> <get> <goto> ->
fetch = {
    goto1 : gotos
    get : gets
    goto2 : gotos
}

def goto_handler (goto : gotos):
    match goto: