# MessageFy Markup Guide

MessageFy supports Rich markup for text formatting in your messages. This guide shows you all the ways to style your text!

## Basic Text Styles

### Bold
```
[bold]This text is bold[/bold]
```

### Italic
```
[italic]This text is italic[/italic]
```

### Underline
```
[underline]This text is underlined[/underline]
```

### Strikethrough
```
[strike]This text is crossed out[/strike]
```

## Colors

### Basic Colors
```
[red]Red text[/red]
[green]Green text[/green]
[blue]Blue text[/blue]
[yellow]Yellow text[/yellow]
[magenta]Magenta text[/magenta]
[cyan]Cyan text[/cyan]
[white]White text[/white]
[black]Black text[/black]
```

### Bright Colors
```
[bright_red]Bright red text[/bright_red]
[bright_green]Bright green text[/bright_green]
[bright_blue]Bright blue text[/bright_blue]
[bright_yellow]Bright yellow text[/bright_yellow]
[bright_magenta]Bright magenta text[/bright_magenta]
[bright_cyan]Bright cyan text[/bright_cyan]
```

### Hex Colors
```
[#FF0000]Custom red[/#FF0000]
[#00FF00]Custom green[/#00FF00]
[#0000FF]Custom blue[/#0000FF]
```

### RGB Colors
```
[rgb(255,0,0)]Red using RGB[/rgb(255,0,0)]
[rgb(0,255,0)]Green using RGB[/rgb(0,255,0)]
```

## Background Colors

Add "on" before the color name for backgrounds:

```
[white on red]White text on red background[/white on red]
[black on yellow]Black text on yellow background[/black on yellow]
[cyan on blue]Cyan text on blue background[/cyan on blue]
```

## Combining Styles

You can combine multiple styles together:

```
[bold red]Bold and red[/bold red]
[italic blue]Italic and blue[/italic blue]
[bold underline green]Bold, underlined, and green[/bold underline green]
[bold italic yellow on blue]All styles combined![/bold italic yellow on blue]
```

## Special Effects

### Dim
```
[dim]This text is dimmed[/dim]
```

### Reverse
Swaps foreground and background colors:
```
[reverse]Reversed colors[/reverse]
```

### Blink
```
[blink]This text blinks[/blink]
```
*Note: Blink may not work in all terminals*

## Links

```
[link=https://example.com]Click here[/link]
```

## Escaping Markup

If you want to display brackets literally, escape them:

```
\[This won't be formatted]
```

## Examples

### Announcement
```
[bold yellow]⚠️ IMPORTANT ANNOUNCEMENT[/bold yellow]
[white on red] URGENT [/white on red] Please read carefully!
```

### Success Message
```
[bold green]✓[/bold green] Task completed successfully!
```

### Error Message
```
[bold red]✗[/bold red] [red]Something went wrong[/red]
```

### Code
```
[cyan]def hello():[/cyan]
    [green]print[/green]([yellow]"Hello, World!"[/yellow])
```

### Rainbow Text
```
[red]R[/red][yellow]a[/yellow][green]i[/green][cyan]n[/cyan][blue]b[/blue][magenta]o[/magenta][red]w[/red]
```

### Emphasis
```
This is [bold]really[/bold] important!
I [italic]strongly[/italic] disagree.
```

### Highlight
```
[black on yellow] HIGHLIGHTED TEXT [/black on yellow]
```

## Tips & Best Practices

1. **Always close your tags** - Every `[style]` needs a matching `[/style]`
2. **Nest properly** - `[bold][red]text[/red][/bold]` works better than overlapping tags
3. **Don't overuse** - Too much formatting can be distracting
4. **Test your message** - Complex formatting might not display as expected
5. **Be considerate** - Avoid hard-to-read color combinations
6. **Use sparingly** - Plain text is often clearer

## Color Combinations to Avoid

These combinations are hard to read:
- Yellow on white
- Light colors on light backgrounds
- Dark colors on dark backgrounds
- Red on green (colorblind accessibility)

## Quick Reference

| Style | Syntax | Example |
|-------|--------|---------|
| Bold | `[bold]text[/bold]` | **text** |
| Italic | `[italic]text[/italic]` | *text* |
| Color | `[red]text[/red]` | 🔴 text |
| Background | `[on blue]text[/on blue]` | 🔵 text |
| Combo | `[bold red]text[/bold red]` | **🔴 text** |

## Need Help?

If your markup isn't working:
1. Check that all tags are closed
2. Verify spelling of color names
3. Make sure brackets match
4. Try simpler formatting first

---

**Have fun styling your messages!** 🎨
