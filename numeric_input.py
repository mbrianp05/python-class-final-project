import customtkinter as ctk

from utilityclasses import FormState


class NumericInput(ctk.CTkEntry):
    def __init__(
        self,
        master,
        min=None,
        max=None,
        allow_float=True,
        allow_negatives=True,
        width=100,
        height=31,
        font=None,
        onchange=None,
        **kwargs,
    ):
        super().__init__(master, width=width, height=height, font=font, **kwargs)
        self.min = min
        self.max = max
        self.allow_float = allow_float
        self.allow_negatives = allow_negatives

        self.onchange = onchange

        if not allow_negatives and min is not None:
            raise ValueError(
                "Min value cannot be assigned when negative valus are not allowed"
            )

        if not self.allow_negatives:
            min = 0

        self.variable = ctk.StringVar()
        self.variable.trace_add("write", lambda *_: self.on_entry_change())
        self.configure(textvariable=self.variable)

    def on_entry_change(self):
        data = self.variable.get()

        if data == "" or data == "-":
            return

        can_have_decimals = (
            data.count(".") <= 1 if self.allow_float else data.count(".") == 0
        )

        if data != "":
            if not data.isdigit() and not can_have_decimals:
                self.variable.set(data[:-1])
                return

        if self.onchange:
            self.onchange(float(self.variable.get()))

    def get_value(self):
        if self.allow_float:
            return float(self.variable.get())

        return int(self.variable.get())

    def get_state(self) -> FormState:
        state = FormState(is_valid=False)
        value = self.variable.get()

        k = None

        try:
            k = float(value)
        except ValueError:
            state.error_message = "El valor introducido no es un número"

            return state

        if not self.allow_float:
            state.error_message = "Solo se permite valores enteros"

            return state

        if self.min is not None and k < self.min:
            state.error_message = f"El valor introducido debe ser mayor que {self.min}"

            return state

        if self.max is not None and k > self.max:
            state.error_message = f"El valor introducido debe ser mayor que {self.max}"

            return state

        state.is_valid = True

        return state
