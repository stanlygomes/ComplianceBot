from shiny.express import input, render, ui
import utils
import asyncio

ui.panel_title("Compliance Bot!")
ui.input_text("message", "Ask Compliance Bot a question", 
              value="How many vacation days do I get?")


@render.ui
def result():
    x=input.message()
    asyncio.sleep(5)
    print(f"The input message is {x}")
    the_answer = utils.query_data(query_text=x)

    return the_answer
