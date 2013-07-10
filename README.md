This is a little shell-building system. It lets you easily make your own
shell-like menu-based environment - great for custom tools.

The three main classes you'll use to build the shell are `Shell`, `Menu`, and
`Command`. A `Shell` consists of one or more `Menus`, which in turn consists
of one or more `Commands`.

* You can put stickers on the terminal
* You can set a custom header
* Command strings are automatically validated based on the definition
* Commands can run arbitary python via a callback
* Commands can lead to new menus selectively by using `constants.FAILURE`
* There are built-in command templates: `QuitCommand`, `RunScriptCommand`, `BackCommand`.

A `Menu` has a title and a list of `Commands`.

It supports up and down arrows for history
