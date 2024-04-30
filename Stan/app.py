from shiny.express import input, render, ui

ui.panel_title("Compliance Bot!")
ui.input_text("message", "Message", value="Hello World")


@render.ui
def result():
    x=input.message()

    return x

@render.text
def txt():
    return f"n*2 is {10 * 2}"