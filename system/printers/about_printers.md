# Base Printer Class

Define a common interface for printer integrations. Each supported printer type implements this interface, allowing `printer_monitor` to work with different printer systems in the same way.

For example, a `KlipperMoonrakerPrinter` class could implement the interface for a Klipper printer connected through Moonraker. A `MarlinPrinter` class could provide the same methods for a Marlin printer. The appropriate instance is then passed to `printer_monitor`.

## Methods

### `is_printing() -> bool`

Checks the printer’s current status. Returns `True` if a print is in progress and `False` otherwise.

### `stop_print() -> None`

Stops the current print. This method does not r
eturn a value.