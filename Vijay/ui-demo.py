from shiny.express import input, render, ui
import utils
import asyncio

ui.panel_title("Wolfie Demo")
ui.input_text("message", "Ask compliance question", value="Am I entited for vacation?")

@render.ui
def display():
    x=input.message()
    asyncio.sleep(5)
    print("The input message is {x}")
    result = utils.query_data(query_text=x)

    return result
