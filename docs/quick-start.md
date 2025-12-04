---
description: Let's begin prompting in 1 minute
---

# Quick Start

## Installation with `pip install`

Directly install from [PyPI](https://pypi.org/project/promplate/ "promplate - PyPI"):

```sh
pip install promplate[openai]
```

We are using `OpenAI` just for demonstration. In fact, **you can use any LLM as you want**.

## Make LLM Calls

First, **Open a python REPL** 💻 (`ipython` or `jupyter` are OK. Just any REPL you like)

**All the code below should run "as is"**, which means you can copy and paste them in your terminal and it will work fine.

```py
>>> from promplate.llm.openai import ChatComplete # this simply wraps OpenAI's SDK
>>> complete = ChatComplete(api_key="...")
```

> The `api_key` should be filled with your API Key from [OpenAI Platform](https://platform.openai.com/account/api-keys "API Key Management - OpenAI Platform")

Then call it like this:

```py
>>> complete("hi", model="gpt-3.5-turbo-0125")
'Hello! How can I assist you today?'
```

Perhaps you don't want to provide `model` parameter everytime you call [`complete`][promplate.llm.openai.ChatComplete], so you can bind it like this:

```py
>>> complete = ChatComplete(api_key="...").bind(model="gpt-3.5-turbo-0125")
```

Then call it simply with a string:

```py
>>> complete("hi", model="gpt-3.5-turbo-0125")
'Hello! How can I assist you today?'
```

???+ tip "If you don't have an OpenAI API Key 🔑"

    You could use our FREE proxy site as `base_url` like this:

    ```py
    >>> from promplate.llm.openai import ChatComplete
    >>> complete = ChatComplete(base_url="https://promplate.dev", api_key="").bind(model="gpt-3.5-turbo-0125")
    >>> complete("hi")
    'Hello! How can I assist you today?'
    ```

??? note "If you want to use instruct models 🤔"

    Simply replace [`ChatComplete`][promplate.llm.openai.ChatComplete] by [`TextComplete`][promplate.llm.openai.TextComplete]:

    ```py
    >>> from promplate.llm.openai import TextComplete
    >>> complete = TextComplete(api_key="...").bind(model="gpt-3.5-turbo-instruct")
    >>> complete("I am")
    ' just incredibly proud of the team, and their creation of a brand new ship makes'
    ```

    And you can pass parameters when calling a [`Complete`][promplate.llm.base.Complete] instance:

    ```py
    >>> complete("1 + 1 = ", temperature=0, max_tokens=1)
    '2'
    ```

??? note "If you prefer to stream the response 👀"

    It is still super easy, just use [`ChatGenerate`][promplate.llm.openai.ChatGenerate]:

    ```py
    >>> from promplate.llm.openai import ChatGenerate
    >>> generate = ChatGenerate(api_key="...").bind(model="gpt-3.5-turbo-0125")
    >>> for i in generate("Explain why 1 + 1 = 2"):
    ...     print(i, end="", flush=True)  # this will print generated tokens gradually
    ...
    The equation 1 + 1 = 2 is a fundamental principle in mathematics and arithmetic. It represents the addition operation, which involves combining two quantities or numbers to find their sum.
    In this case, when we add 1 to another 1, we are essentially combining or merging two individual units or quantities. By doing this, we end up with a total count of two. Therefore, the result is 2.
    This principle is consistent and holds true in all contexts and across different number systems, whether it is in the base-10 decimal system, binary system, or any other number system.
    1 + 1 = 2 is considered a basic and universally accepted mathematical fact, forming the foundation for more complex mathematical operations and calculations.
    ```

## Prompting with Template

There must be something dynamic in your prompt, like **user queries**, **retrieved context**, **search results**, etc.
In **promplate**, simply use `{{ }}` to insert dynamic data.

```py
>>> import time
>>> from promplate import Template
>>> greet = Template("Greet me. It is {{ time.asctime() }} now.")
>>> greet.render(locals())
'Greet me. It is Sun Oct 1 03:56:02 2023 now.'
```

You can run the prompt by [`complete`][promplate.llm.openai.ChatComplete] we created before

```py
>>> complete(_)
'Good morning!'
```

Wow, it works fine. In fact, you can use any python expression inside `{{ }}`.

Tips: you can combine partial context to a template like this:

```py
>>> import time
>>> from promplate import Template
>>> greet = Template("Greet me. It is {{ time.asctime() }} now.", {"time": time}) # of course you can use locals() here too
>>> greet.render() # empty parameter is ok
'Greet me. It is Sun Oct 1 03:56:02 2023 now.'
```

## Turning a complex task into small pieces

Sometimes we don't use a single prompt to complete. Here are some reasons:

- Describing a complex task in a single prompt may be difficult
- Splitting big task into small ones maybe can reduce the total token usage
- If you need structural output, it is easier to specifying data formats separately
- We human can think quicker after breaking task into parts
- Breaking big tasks into sub tasks may enhance interpretability, reducing debugging time
- ...

In `promplate`, We use a [`Node`][promplate.Node] to represent a single "task". You can initialize a `Task` with a string like initiating a [`Template`][promplate.Template]:

```py
>>> from promplate import Node
>>> greet = Node("Greet me. It is {{ time.asctime() }} now.", locals())
>>> greet.render()
'Greet me. It is Sun Oct 1 04:16:04 2023 now.'
```

But **there are far more utilities**.

Such as, you can **add two nodes together** magically:

```py
>>> translate = Node('translate """{{ __result__ }}""" into {{ target_language }}')
>>> chain = greet + translate # this represents the pipeline of "greeting in another language"
>>> chain.invoke({"target_language": "zh_CN"}, complete).result
'早上好！'
```

??? question "Details"

    Mention that the return type of [`.invoke()`][promplate.chain.node.Interruptible.invoke] (/references/chain/#promplate.chain.node.AbstractNode.invoke "AbstractNode.invoke") is [`ChainContext`][promplate.chain.node.ChainContext] which combines the context passed everywhere in a right order.
    `__result__` is the output of last [`Node`][promplate.Node]. It is automatically assigned during `.invoke()`. You can access it inside the template.
    Outside the template, you can use [`.result`][promplate.ChainContext.result] of a `ChainContext` to get the last output.

    The following three expressions should return the same string:

    ```py
    >>> template = Template("...")
    >>> complete(template.render())
    ```

    ```py
    >>> Node("...").invoke()["__result__"]
    ```

    ```py
    >>> Node("...").invoke().result
    ```

    This part may be a bit more complex, but believe me, this enhances the flexibility of this framework and you will like it.

## Registering callbacks

**There are sometimes some work can't be done without our code.** such as:

- LLM returns string, while we may want to parse it into structural data format like `dict` or `list`
- We may need to log the intermediate variables to see whether the previous nodes work fine
- We may modify context dynamically during a chain running
- ...

In `promplate`, you can register a callback everytime before or after a node runs.

Besides manually implementing the [`Callback`][promplate.BaseCallback] interface, you can directly use decorators syntax like so:

```py
>>> @greet.end_process
... def log_greet_result(context):
...     print(context.result)
...     print(context["target_language"])
...
>>> chain.invoke({"target_language": "zh_CN"}, complete).result
Good morning!
zh_CN
'早上好！'
```

Congratulations 🎉 You've learnt the basic paradigm of using `promplate` for prompt engineering.

---

Thanks for reading. There are still lots of features not mentioned here. Learn more in other pages 🤗
If you have any questions, please feel free to ask us on [GitHub Discussions](https://github.com/promplate/core/discussions/categories/q-a "Q&A - GitHub Discussions").
