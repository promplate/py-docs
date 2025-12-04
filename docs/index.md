---
title: Introduction
---

# Welcome to Promplate

[**`Promplate`**](http://promplate.dev/ "Interactive Tutorial - Promplate") is a **templating framework** that progressively enhances your **prompt engineering** workflow with minimal dependency.

```sh
pip install promplate #(1)!
```

1. If you want to run the example below, you need to install `openai` too.
   You can do so by `#!sh pip install promplate[openai]`.

!!! tip ""

    **`Promplate`** runs well on [python 3.8 - 3.14](https://github.com/promplate/core/actions/workflows/test.yml "test.yaml - promplate/core - GitHub"),
    and is [well-tested](https://promplate-python-coverage.onrender.com/ "Promplate Python Test Coverage") on [CPython](https://python.org/ "python.org - Official Python Website") and [PyPy](https://pypy.org/ "PyPy - A Fast Python Implementation").

## A simple example

Let's say I need to greet in foreign language. Let's compose two simple prompts that just work.

=== "main.py"

    ```py
    from promplate.llm.openai import ChatComplete #(1)!
    from promplate import Node

    reply = Node.read("reply.j2")
    translate = Node.read("translate.j2")

    translate.run_config["temperature"] = 0

    chain = reply + translate #(2)!

    complete = ChatComplete().bind(model="gpt-3.5-turbo")
    context = {"lang": "chinese"}
    ```

    1. **Importing an LLM is optional.** If you only use `promplate` as a templating engine,
       running `pip install promplate` needs ***no dependency***.
    2. **Chaining nodes is simply adding them together.**
       We believe that nice debug printing is a must for development experience.
       So, with some magic behind the scenes, **if you `#!py print(chain)`, you will get `#!jsx </reply/> + </translate/>`.**
       This is useful if you have a lot of prompt templates and always use `print` to debug.

=== "reply.j2"

    ```jinja hl_lines="3 6"
    {# import time #}

    <|system|>
    current time: {{ time.localtime() }}

    <|user|>
    Say happy new year to me in no more than 5 words.
    Note that you must include the year in the message.
    ```

    !!! note

        This shows some special markup syntax in `promplate`:

        - Inside `#!jinja {# ... #}` are python codes to run in the context.
          In this case, we want to use `#!py time.localtime()` to get the current time. So we import it in the template.
        - `<|user|>` and `<|assistant|>` are **chat markups**.
          It will be formatted into a `#!py list[Message]` object before being passed to the LLM.
        - Inside `#!jinja {{ ... }}` can be any python expressions.

=== "translate.j2"

    ```jinja
    Translate the following message into `{{ lang }}`:
    """
    {{ __result__ }}
    """
    ```

    !!! question "You may ask, what is `#!jinja {{ __result__ }}`?"

        In fact, `promplate` will automatically inject some variables into the context.
        Among them, **`__result__` is the LLM response of the previous node.**

    ---

Then call `#!py chain.invoke({"lang": "chinese"}, complete).result` to get a Chinese greeting relating with the time now.

## Why `promplate`?

I am a **prompt engineer** who suffered from the following problems:

### Problems

#### Writing prompts inside scripts is not elegant

- There is no syntax highlighting, no auto completion, no linting, etc.
- the indenting is ugly, or you have to bare with lots of spaces/tabs in your prompts
- Some characters must be escaped, like `"""` inside a python string, or <code>`</code> inside a JavaScript string.

**So in `promplate`, we support writing prompts in separate files.** Of course, you can still write prompts inside scripts too.

??? abstract "details"

    - [x] writing prompts in separate files

    === "read from file"

        ```py
        from promplate import Template

        foo = Template.read("path/to/some-template.j2")  // synchronous
        bar = await Template.aread("path/to/some-prompt.md")  // asynchronous
        ```

    === "fetch from http urls"

        ```py
        from promplate import Template

        foo = Template.fetch("https://your-domain.com/path/to/some-template.j2")  // synchronous
        bar = await Template.afetch("https://your-domain.com/path/to/some-prompt.md")  // asynchronous
        ```

    The template name will be their filenames.

    ```py
    >>> print(foo)
    <Template some-template>
    >>> print(bar)
    <Template some-prompt>
    ```

    ---

    - [x] writing short prompt through literals

    ```py
    from promplate import Template

    foo = Template('Translate this into {{ lang }}: \n"""{{ text }}"""')
    ```

    The template name will be the variable name.

    ```py
    >>> print(foo) #(1)!
    <Template foo> #(2)!
    ```

    1. `#!py repr(foo)` and `#!py str(foo)` are slightly different. `#!py repr(foo)` will output `#!jsx </foo/>`
    2. If you `#!py print(Template("..."))` so that there is no "variable name", it will be simply `#!py <Template>`.

    ---

    - [x] (new in `v0.3`) writing chat prompts through magic

    === "`user` / `assistant` / `system`"

        ```py
        >>> from promplate.prompt.chat import user, assistant, system
        >>> user > "hello"
        {'role': 'user', 'content': 'hello'}
        >>> assistant > "hi"
        {'role': 'assistant', 'content': 'hi'}
        ```
        ```py
        >>> from promplate.prompt.chat import user, assistant, system
        >>> [system > "...", user @ "example_user" > "hi"]
        [
            {'role': 'system', 'content': '...'},
            {'role': 'user', 'content': 'hi', 'name': 'example_user'}
        ]
        ```

    === "`U` / `A` / `S`"

        ```py
        >>> from promplate.prompt.chat import U, A, S
        >>> U > "hello"
        {'role': 'user', 'content': 'hello'}
        >>> A > "hi"
        {'role': 'assistant', 'content': 'hi'}
        ```
        ```py
        >>> from promplate.prompt.chat import U, A, S
        >>> [S > "...", U @ "example_user" > "hi"]
        [
            {'role': 'system', 'content': '...'},
            {'role': 'user', 'content': 'hi', 'name': 'example_user'}
        ]
        ```

#### Chaining prompts is somehow difficult

Often we need several LLM calls in a process.
[`LCEL`](https://python.langchain.com/docs/expression_language/ "LangChain Expression Language") is `langchain`'s solution.

Ours is like that, but everything unit is a `#!py promplate.Node` instance.
`Router` are implemented with 2-3 lines in `callback` functions through `#!py raise Jump(...)` statements.

Promplate `Node`s are just [**state machines**](https://en.wikipedia.org/wiki/Finite-state_machine "Finite-state machine - Wikipedia").

#### Chat templates are hard to read

Usually you need to manually construct the message list if you are using a chat model.
In `promplate`, you can write chat templates in separate files, and use a render it as a list.

#### Identical prompts are hard to reuse & maintain

Promplate has a **component** system (same meaning as in frontend ecosystem),
which enable you to reuse prompt template fragments in different prompts.

#### Callbacks and output parsers are hard to bind

In langchain, you can bind callback to a variety of event types.
Promplate has a flexible callback system similarly, but you can bind simple callbacks through decorators like `#!py @node.pre_process`.

### Features

- [x] more than templating: components, chat markup
- [x] more than LLM: callbacks, state machines
- [x] developer experience: full typing, good printing ...
- [x] flexibility: underlying ecosystem power

### Further reading

You can the [quick-start](./quick-start.md#make-llm-calls){ data-preview } tutorial, which is a more detailed explanation.
If you have any questions, feel free to ask on [GitHub Discussions](https://github.com/promplate/core/discussions/categories/q-a "Q&A - GitHub Discussions")!
